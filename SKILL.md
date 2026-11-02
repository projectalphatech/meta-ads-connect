---
name: meta-ads-connect
description: Connect Facebook and Instagram ads to your AI agent through the Meta Marketing API with a step-by-step walkthrough for beginners - create a Meta app, make a read-only token, pull ad results to CSV, answer questions like "which ad is wasting my money?", and optionally run a nightly autopilot that pauses losing ads and shifts budget by the user's own rules. Use when the user wants to connect Meta / Facebook / Instagram ads to Claude Code or any agent, read Ads Manager data by API, get an ads report, automate or manage ads overnight, or build an ads dashboard or daily summary.
---

# meta-ads-connect

`SKILL` = this folder. The walkthrough is `SKILL/steps/01-...07-*.md`; follow those files, in order. Scripts: `python SKILL/scripts/meta_ads.py` (read-only) and `python SKILL/scripts/autopilot.py` (manages ads). Python 3.9+, no installs.

## How to guide

1. **One step at a time.** Find where the user is (step 0: do they have an app? a token? a Business portfolio?). Give one step from the step file, wait for "done", then the next. Never dump all steps at once.
2. Run the commands for them when you can (`check`, `accounts`, `insights`, autopilot dry run). They do the clicking in Meta's screens.
3. Meta renames buttons. If what they see differs, ask what is on screen and adapt.
4. Run the scripts from the folder that holds their `.env` (their project folder or this repo).

## Rules

1. **Never ask for the token in chat**, and never for their Facebook password. They paste the token into `.env` themselves. Check `.env` is in `.gitignore` first. If they paste a token in chat, tell them to revoke it and make a new one.
2. **Steps 1-5 are read-only.** Use `META_TOKEN` with `ads_read`. If `check` warns the token can change ads, help them make a read-only one for daily use.
3. **Step 6 (autopilot) only when the user asks for it.** Explain plainly that it changes live ads and spend. Then:
   - separate `META_WRITE_TOKEN` with `ads_management`;
   - fill `rules.json` with them: `target_cost` and `max_daily_budget` are their numbers, never yours;
   - dry runs for several days, read each `WOULD` line together, then the first `--apply` by hand, then schedule (step 7).
   - Never add `--apply` to a schedule before a manual `--apply` run worked.
4. **You never change ads yourself** outside `autopilot.py` and its rules. Any other change (turn on, new ad, audience, creative, budget above the cap) needs the user's explicit yes for that one change, and new objects are created PAUSED.
5. **Numbers come from the CSV / API, never from memory.** Quote the rows you used. Never promise a cost per result.

## Answering questions (step 5)

- Compare ads on the result they were made for (WhatsApp ad → messages, form ad → leads). Don't add different result types.
- Zero results is a verdict only after spend ≥ 2-3x what one result is worth to them. Below that: "not enough data yet".
- High CTR with no results points at the page or offer, not the ad.
- Meta counts are not sales. If they track customers, join on ad name and judge by paying customers.

## Commands

```bash
python SKILL/scripts/meta_ads.py check | accounts | selftest
python SKILL/scripts/meta_ads.py insights --account act_123 --days 7 [--level ad|adset|campaign] [--out ads.csv]
python SKILL/scripts/autopilot.py            # dry run (creates rules.json on first run)
python SKILL/scripts/autopilot.py --apply    # acts, logs to autopilot-log.csv
python SKILL/scripts/autopilot.py selftest
```
API version: `META_API_VERSION` in `.env` (default `v26.0`, checked 2026-11-02).
