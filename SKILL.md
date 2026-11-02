---
name: meta-ads-connect
description: Connect your Facebook and Instagram ads to your AI agent through the Meta Marketing API, step by step, read-only. Walks a beginner through creating a Meta app, a read-only token (ads_read), finding the ad account id, pulling ad results into a CSV, and asking plain-language questions like "which ad is wasting my money?". Use when the user wants to connect Meta / Facebook / Instagram ads to Claude Code or any agent, read Ads Manager data by API, get an ads report, or build an ads dashboard or daily ads summary.
---

# meta-ads-connect

Goal: the user's agent can read their Facebook + Instagram ad results and answer questions about them. Read-only: nothing in this skill can change a campaign or spend money.

`SKILL` = this folder. Script: `python SKILL/scripts/meta_ads.py` (Python 3.9+, no installs).

## Rules

1. **Read-only by design.** The token gets `ads_read` only. If `check` says the token has `ads_management`, stop and help the user make a read-only one. This skill never creates, edits, pauses or deletes anything in an ad account.
2. **Never ask for the token in chat.** The user pastes it into a `.env` file themselves (`META_TOKEN=...`). Make sure `.env` is in `.gitignore` before they save it. If they paste it in chat anyway, tell them to make a new one later (step 4) and not to reuse that one.
3. **Never ask for their Facebook password**, and never log in for them. They click through Meta's screens; you guide.
4. **One step at a time.** Give one step, wait until they say it worked, then the next. Beginners get lost when given ten steps at once.
5. **Meta changes screens and versions often.** If a button name does not match, ask what they see and adapt. The API version lives in one place: `API_VERSION` in the script (or env `META_API_VERSION`).
6. **Numbers come from the API, never from memory.** When you answer questions, quote the CSV rows you used.

## Walkthrough

Full click-by-click steps and fixes for common errors: `references/setup.md`. Summary:

| Step | What the user does | Done when |
|---|---|---|
| 0 | Say which ad account they use and whether they have a Business portfolio (business.facebook.com) | You know which route: **fast** (personal, ~60-day token) or **solid** (system user, no expiry) |
| 1 | Create a Meta app at developers.facebook.com (use case: Marketing API / ads) | They have an App ID |
| 2 | (solid route) Create a system user in Business settings | System user exists |
| 3 | Give the system user (or themselves) the ad account with view-only access | Account assigned |
| 4 | Generate a token with **ads_read** only, paste it into `.env` | `.env` holds `META_TOKEN=` |
| 5 | Run `check`, then `accounts` | Script prints "Read-only" and their `act_...` id |
| 6 | Run `insights --account act_... --days 7` | `ads.csv` exists |
| 7 | Ask questions (below) | They got a useful answer |

## Commands

```bash
python SKILL/scripts/meta_ads.py check                          # token valid? read-only?
python SKILL/scripts/meta_ads.py accounts                       # list act_ ids
python SKILL/scripts/meta_ads.py insights --account act_123 --days 7 --level ad --out ads.csv
python SKILL/scripts/meta_ads.py selftest                       # offline test
```

`insights` writes one row per ad (or ad set / campaign) with spend, impressions, reach, CTR, CPM, and for each result type (leads, messages, purchases, link clicks, page views) the count and cost per result. It covers up to yesterday, because today's numbers are still coming in.

## Answering questions

Read the CSV, then answer in the user's language with the rows that prove it. Good first questions: `references/questions.md`.

How to judge, briefly:
- Compare ads on the result that ad was made for (a WhatsApp ad on messages, a form ad on leads). Do not add different result types together.
- Spend with zero results is only a verdict once the ad has spent about 2-3x what one result is worth to the user. Below that, say "not enough data yet".
- High CTR with no results points at the page or the offer, not the ad.
- Meta's counts are not sales. If they have a CRM or sales sheet, join on the ad name and judge by paying customers.

## Next steps (only if the user asks)

- **Daily summary**: schedule `insights --days 1` (Task Scheduler / cron) and send the top lines to them.
- **Dashboard / sheet**: import `ads.csv` into Google Sheets, or load it into SQLite/D1 daily.
- **Making changes by AI**: Meta's official ads MCP server can create and edit ads. It needs a token with write access. Explain the risk, keep new ads PAUSED, and confirm every single change with the user before it runs. That is outside this skill's read-only promise.
