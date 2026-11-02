#!/usr/bin/env python3
"""Nightly ads autopilot: pause ads that burn money, move budget to the ones that work.

Follows YOUR rules in rules.json. It can only:
  - pause an ad
  - raise or lower an ad set's daily budget, never above max_daily_budget
It never turns anything on, never deletes, never creates, never touches audiences or creatives.

  python autopilot.py                 dry run: prints what it WOULD do, changes nothing
  python autopilot.py --apply         does it, and logs every change to autopilot-log.csv
  python autopilot.py selftest

Needs META_WRITE_TOKEN (scope ads_management) in .env. Keep META_TOKEN (ads_read) for everything else.
"""
import csv, json, os, sys
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from meta_ads import RESULTS, flatten, get, get_all, load_token

LOG = "autopilot-log.csv"
DEFAULT_RULES = {
    "result": "messages",          # what you pay for: messages | leads | purchases | page_views
    "target_cost": 10,             # what one result is worth to you, in your account currency
    "days": 3,                     # look-back window
    "kill_zero_after_x": 2.5,      # pause an ad with 0 results after spending 2.5x target_cost
    "kill_cost_x": 2.0,            # pause an ad whose cost per result is over 2x target...
    "min_results": 3,              # ...but only once it has at least this many results
    "scale_cost_x": 0.7,           # raise an ad set's budget when cost per result is under 0.7x target
    "scale_step": 0.2,             # by 20% a night
    "cut_cost_x": 1.5,             # lower an ad set's budget when cost per result is over 1.5x target
    "max_daily_budget": 500,       # hard cap per ad set, account currency
    "max_changes_per_night": 5,
    "never_touch": [],             # name parts to skip, e.g. ["brand", "retargeting"]
}


def decide(ads, adsets, r):
    """Pure: insight rows + current ad set budgets -> list of actions. No API calls."""
    col, target = r["result"], r["target_cost"]
    skip = lambda name: any(s.lower() in (name or "").lower() for s in r["never_touch"])
    acts = []
    for a in ads:
        if skip(a["ad_name"]) or skip(a["adset_name"]):
            continue
        n, spend = a[col], a["spend"]
        if n == 0 and spend >= r["kill_zero_after_x"] * target:
            acts.append(("pause", a["ad_id"], a["ad_name"], f"spent {spend} with 0 {col}"))
        elif n >= r["min_results"] and spend / n > r["kill_cost_x"] * target:
            acts.append(("pause", a["ad_id"], a["ad_name"], f"{spend / n:.2f} per {col[:-1]} (> {r['kill_cost_x']}x target)"))
    for s in adsets:
        if skip(s["adset_name"]) or not s.get("budget"):
            continue  # no ad set budget = budget lives on the campaign; left alone
        n, spend, b = s[col], s["spend"], s["budget"]
        if n >= r["min_results"] and spend / n < r["scale_cost_x"] * target:
            new = min(round(b * (1 + r["scale_step"]), 2), r["max_daily_budget"])
            if new > b:
                acts.append(("budget", s["adset_id"], s["adset_name"], f"{b} -> {new}: {spend / n:.2f} per {col[:-1]}", new))
        elif n >= r["min_results"] and spend / n > r["cut_cost_x"] * target:
            new = round(b * (1 - r["scale_step"]), 2)
            acts.append(("budget", s["adset_id"], s["adset_name"], f"{b} -> {new}: {spend / n:.2f} per {col[:-1]}", new))
    return acts[: r["max_changes_per_night"]]


def pull(account, r, token):
    until = date.today() - timedelta(days=1)
    since = until - timedelta(days=r["days"] - 1)
    base = {"fields": "adset_name,ad_name,adset_id,ad_id,spend,impressions,actions", "limit": 200,
            "time_range": json.dumps({"since": str(since), "until": str(until)})}
    active = lambda lvl: json.dumps([{"field": f"{lvl}.effective_status", "operator": "IN", "value": ["ACTIVE"]}])
    ads = [flatten(x) for x in get_all(f"{account}/insights", {**base, "level": "ad", "filtering": active("ad")}, token)]
    adsets = [flatten(x) for x in get_all(f"{account}/insights", {**base, "level": "adset", "filtering": active("adset")}, token)]
    # ponytail: budgets are in the currency's minor unit (EGP/USD/EUR = /100). Currencies like JPY/KRW use 1; handle if needed.
    for s in adsets:
        b = get(s["adset_id"], {"fields": "daily_budget"}, token).get("daily_budget")
        s["budget"] = int(b) / 100 if b else None
    return ads, adsets


def apply(acts, token):
    new_file = not os.path.exists(LOG)
    with open(LOG, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["time", "action", "id", "name", "why", "undo"])
        for x in acts:
            if x[0] == "pause":
                get(x[1], {}, token, data={"status": "PAUSED"})
                undo = "set status ACTIVE in Ads Manager"
            else:
                old = get(x[1], {"fields": "daily_budget"}, token)["daily_budget"]
                get(x[1], {}, token, data={"daily_budget": int(round(x[4] * 100))})
                undo = f"set daily budget back to {int(old) / 100}"
            w.writerow([datetime.now().isoformat(timespec="seconds"), x[0], x[1], x[2], x[3], undo])


def selftest():
    r = {**DEFAULT_RULES, "target_cost": 10}
    row = lambda name, spend, n, **k: {"ad_name": name, "adset_name": k.get("s", "set"), "ad_id": name, "adset_id": name,
                                       "spend": spend, "messages": n, "budget": k.get("b")}
    ads = [row("burner", 30, 0), row("young", 20, 0), row("pricey", 90, 3), row("good", 40, 8), row("brand ad", 99, 0)]
    r["never_touch"] = ["brand"]
    acts = decide(ads, [row("cheap", 30, 6, b=100), row("costly", 80, 4, b=100), row("capped", 30, 6, b=500), row("cbo", 30, 6)], r)
    got = {(x[0], x[1]) for x in acts}
    assert ("pause", "burner") in got and ("pause", "pricey") in got, acts
    assert ("pause", "young") not in got and ("pause", "good") not in got and ("pause", "brand ad") not in got, acts
    assert ("budget", "cheap") in got and [x[4] for x in acts if x[1] == "cheap"] == [120.0], acts
    assert [x[4] for x in acts if x[1] == "costly"] == [80.0], acts
    assert ("budget", "capped") not in got and ("budget", "cbo") not in got, acts
    assert len(decide(ads * 5, [], {**r, "max_changes_per_night": 2})) == 2
    print("autopilot selftest ok")


def main():
    if "selftest" in sys.argv:
        return selftest()
    if not os.path.exists("rules.json"):
        json.dump({"account": "act_YOUR_ID", **DEFAULT_RULES}, open("rules.json", "w"), indent=2)
        sys.exit("Made rules.json. Fill in account and target_cost, then run again (dry run).")
    r = {**DEFAULT_RULES, **json.load(open("rules.json", encoding="utf-8"))}
    if r["result"] not in RESULTS.values():
        sys.exit(f"result must be one of: {', '.join(RESULTS.values())}")
    token = load_token("META_WRITE_TOKEN")
    acts = decide(*pull(r["account"], r, token), r)
    if not acts:
        print("Nothing to change tonight.")
    for x in acts:
        print(f"{'DO' if '--apply' in sys.argv else 'WOULD'} {x[0]:<6} {x[2][:40]:<40} {x[3]}")
    if acts and "--apply" in sys.argv:
        apply(acts, token)
        print(f"Done. Logged to {LOG} with how to undo each change.")
    elif acts:
        print("Dry run. Nothing changed. Add --apply to do it.")


if __name__ == "__main__":
    main()
