#!/usr/bin/env python3
"""Read your Facebook + Instagram ads through the Meta Marketing API. Read-only.

Python 3.9+, standard library only. The token comes from the env var META_TOKEN
or a `.env` file next to where you run it (META_TOKEN=...). Never pass it on the
command line: it would land in your shell history.

  python meta_ads.py check                         token valid? which permissions?
  python meta_ads.py accounts                      list ad accounts the token can read
  python meta_ads.py insights --account act_123 --days 7 [--level ad|adset|campaign] [--out ads.csv]
  python meta_ads.py selftest                      offline test of the parsing code
"""
import argparse, csv, json, os, sys, time, urllib.error, urllib.parse, urllib.request
from datetime import date, timedelta

def read_env():
    """Load .env from the current folder into os.environ (real env vars win)."""
    if os.path.exists(".env"):
        for line in open(".env", encoding="utf-8-sig"):
            k, _, v = line.strip().partition("=")
            if k and not k.startswith("#"):
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


read_env()
API_VERSION = os.environ.get("META_API_VERSION", "v26.0")  # newest as of 2026-11; check the changelog
BASE = f"https://graph.facebook.com/{API_VERSION}/"

# action_type -> short column name. Meta returns many; these are the ones people ask about.
RESULTS = {
    "lead": "leads",
    "onsite_conversion.messaging_conversation_started_7d": "messages",
    "omni_purchase": "purchases",
    "link_click": "link_clicks",
    "landing_page_view": "page_views",
}
RETRY_CODES = {4, 17, 32, 613, 80000, 80003, 80004, 80014}  # rate limits: wait and retry
HINTS = {
    190: "Token expired or invalid. Make a new one (see steps/02-make-a-token.md).",
    200: "Missing permission. The token needs ads_read, and the ad account must be assigned to it.",
    10: "Missing permission. The token needs ads_read.",
    100: "Bad parameter. Check the account id looks like act_1234567890.",
    2635: "API version too old. Set META_API_VERSION to the newest version.",
}


def load_token(name="META_TOKEN"):
    tok = os.environ.get(name)
    if not tok:
        sys.exit(f"No token. Put {name}=... in a .env file here (and add .env to .gitignore).")
    return tok


def get(path, params, token, tries=4, data=None):
    url = path if path.startswith("http") else BASE + path + ("" if data else "?" + urllib.parse.urlencode(params))
    body = urllib.parse.urlencode(data).encode() if data else None  # data = POST (only autopilot.py writes)
    req = urllib.request.Request(url, data=body, headers={"Authorization": f"Bearer {token}"})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            err = json.loads(e.read() or b"{}").get("error", {})
            code = err.get("code")
            if code in RETRY_CODES and attempt < tries - 1:
                wait = 30 * (attempt + 1)
                print(f"Rate limited (code {code}). Waiting {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            hint = HINTS.get(code, "")
            sys.exit(f"Meta API error {code}: {err.get('message', e.reason)}\n{hint}".strip())
        except urllib.error.URLError as e:
            if attempt < tries - 1:
                time.sleep(5)
                continue
            sys.exit(f"Network error: {e.reason}")


def get_all(path, params, token):
    """Follow paging.next until the end."""
    page = get(path, params, token)
    rows = page.get("data", [])
    while page.get("paging", {}).get("next"):
        page = get(page["paging"]["next"], {}, token)
        rows += page.get("data", [])
    return rows


def flatten(row):
    """One insights row -> flat dict with result counts and cost per result."""
    out = {k: row.get(k, "") for k in ("campaign_name", "adset_name", "ad_name", "adset_id", "ad_id", "date_start", "date_stop")}
    spend = float(row.get("spend") or 0)
    out.update(spend=round(spend, 2), impressions=int(row.get("impressions") or 0),
               reach=int(row.get("reach") or 0), ctr=row.get("inline_link_click_ctr", ""), cpm=row.get("cpm", ""))
    acts = {a["action_type"]: float(a["value"]) for a in row.get("actions", [])}
    for action_type, col in RESULTS.items():
        n = acts.get(action_type, 0)
        out[col] = int(n)
        out[f"cost_per_{col}"] = round(spend / n, 2) if n else ""
    return out


def cmd_check(token):
    me = get("me", {"fields": "id,name"}, token)
    perms = get_all("me/permissions", {}, token)
    granted = sorted(p["permission"] for p in perms if p.get("status") == "granted")
    print(f"Token OK. Belongs to: {me.get('name')} ({me.get('id')})")
    print("Permissions:", ", ".join(granted) or "(none listed; system user tokens may show none)")
    write = [p for p in granted if p in ("ads_management", "business_management")]
    if write:
        print(f"WARNING: this token can CHANGE ads ({', '.join(write)}). For reading, make one with ads_read only.")
    elif "ads_read" in granted:
        print("Read-only: this token can read ads but cannot change or spend anything.")


def cmd_accounts(token):
    rows = get_all("me/adaccounts", {"fields": "name,account_id,currency,account_status,amount_spent", "limit": 100}, token)
    if not rows:
        print("No ad accounts visible. Assign the ad account to this user/system user (steps/02-make-a-token.md).")
    status = {1: "active", 2: "disabled", 3: "unsettled", 7: "pending review", 9: "grace period", 101: "closed"}
    for a in rows:
        print(f"act_{a['account_id']}  {a.get('name')}  {a.get('currency')}  {status.get(a.get('account_status'), a.get('account_status'))}")


def cmd_insights(token, account, days, level, out):
    if not account.startswith("act_"):
        account = "act_" + account
    until = date.today() - timedelta(days=1)  # yesterday: today is still incomplete
    since = until - timedelta(days=days - 1)
    fields = "campaign_name,adset_name,ad_name,adset_id,ad_id,spend,impressions,reach,inline_link_click_ctr,cpm,actions"
    params = {"level": level, "fields": fields, "limit": 200,
              "time_range": json.dumps({"since": str(since), "until": str(until)})}
    rows = [flatten(r) for r in get_all(f"{account}/insights", params, token)]
    if not rows:
        print(f"No delivery between {since} and {until}.")
        return
    rows.sort(key=lambda r: r["spend"], reverse=True)
    with open(out, "w", newline="", encoding="utf-8-sig") as f:  # utf-8-sig so Excel shows Arabic names
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    total = sum(r["spend"] for r in rows)
    name_key = {"ad": "ad_name", "adset": "adset_name", "campaign": "campaign_name"}[level]
    print(f"{len(rows)} {level}s, {since} to {until}, total spend {total:.2f}. Saved {out}")
    for r in rows[:10]:
        res = ", ".join(f"{r[c]} {c}" for c in RESULTS.values() if r[c] and c != "link_clicks") or "no results"
        print(f"  {r['spend']:>10.2f}  {r[name_key][:45]:<45}  {res}")


def selftest():
    row = {"ad_name": "Reel A", "spend": "100.00", "impressions": "5000", "reach": "4000",
           "actions": [{"action_type": "lead", "value": "4"}, {"action_type": "link_click", "value": "50"}]}
    f = flatten(row)
    assert f["spend"] == 100.0 and f["leads"] == 4 and f["cost_per_leads"] == 25.0, f
    assert f["messages"] == 0 and f["cost_per_messages"] == "", f
    assert flatten({"spend": "0"})["leads"] == 0
    print("selftest ok")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check"); sub.add_parser("accounts"); sub.add_parser("selftest")
    i = sub.add_parser("insights")
    i.add_argument("--account", required=True)
    i.add_argument("--days", type=int, default=7)
    i.add_argument("--level", choices=["ad", "adset", "campaign"], default="ad")
    i.add_argument("--out", default="ads.csv")
    a = p.parse_args()
    if a.cmd == "selftest":
        return selftest()
    token = load_token()
    if a.cmd == "check":
        cmd_check(token)
    elif a.cmd == "accounts":
        cmd_accounts(token)
    else:
        cmd_insights(token, a.account, a.days, a.level, a.out)


if __name__ == "__main__":
    main()
