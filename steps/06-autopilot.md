# Step 6 — Autopilot: let it manage your ads while you sleep (optional)

← [Step 5](05-ask-your-agent.md) · Next: [Step 7 — Run it every night](07-run-every-night.md)

Every night `autopilot.py` looks at the last 3 days and follows **your** rules:

- **Pauses** an ad that spent money with no results, or costs far more than your target.
- **Raises** the daily budget of an ad set that is cheaper than your target (+20%, never above your cap).
- **Lowers** the budget of an ad set that is too expensive (-20%).

It never turns anything on, never deletes, never creates ads, never touches audiences or creatives. Every change goes into `autopilot-log.csv` with how to undo it.

⚠️ This step **changes your live ads and your spend**. Go slowly: dry runs first, small cap, read the log every morning.

## 6.1 Make a second token that can manage ads

Same as [step 2](02-make-a-token.md), but tick **`ads_management`** (instead of `ads_read`).
- Route B (system user): give it **Manage campaigns** on the ad account (not full control).

Add it to `.env` as a **second line**. Keep the read-only one for everything else:
```
META_TOKEN=EAA...read only...
META_WRITE_TOKEN=EAA...can manage...
```

## 6.2 Write your rules

```bash
python scripts/autopilot.py
```
First run creates **`rules.json`**. Open it and set at least:

| Rule | Meaning | Example |
|---|---|---|
| `account` | your `act_...` id | `"act_1234567890"` |
| `result` | what you pay for: `messages`, `leads`, `purchases`, `page_views` | `"messages"` |
| `target_cost` | the most one result is worth to you (your currency) | `15` |
| `max_daily_budget` | hard cap per ad set per day | `300` |
| `never_touch` | name parts to skip | `["brand", "test"]` |

Other rules (defaults are sensible): `days` 3, `kill_zero_after_x` 2.5 (pause after spending 2.5x target with 0 results), `kill_cost_x` 2, `min_results` 3, `scale_cost_x` 0.7, `cut_cost_x` 1.5, `scale_step` 0.2, `max_changes_per_night` 5.

## 6.3 Dry run (changes nothing)

```bash
python scripts/autopilot.py
```
It prints `WOULD pause ...` / `WOULD budget ...` with the reason. Read every line. Would you have done the same? If not, change the rules and run again.

Do dry runs for **3-5 days** before going live.

## 6.4 Go live

```bash
python scripts/autopilot.py --apply
```
Check `autopilot-log.csv` and Ads Manager afterwards. To undo a change, the `undo` column says how.

Budgets: an ad set with no daily budget (budget set on the campaign) is left alone.

✅ **Done when:** a manual `--apply` run did what the dry run said, and the log shows it.
