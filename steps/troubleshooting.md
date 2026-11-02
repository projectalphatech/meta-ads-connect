# Troubleshooting

← [Back to the steps](../README.md)

| You see | Why | Fix |
|---|---|---|
| `No token. Put META_TOKEN=...` | No `.env`, or you ran the command from another folder | Run from inside the repo folder; check the `.env` line has no spaces around `=` |
| `190` Invalid / expired token | Copy mistake, or the quick token expired | Make a new one ([step 2](02-make-a-token.md)) |
| `200` or `10` permission | Token lacks `ads_read` (or `ads_management` for autopilot), or the ad account is not assigned | Redo step 2; for route B check **Assign assets** |
| `100` bad parameter | Wrong account id | Use the `act_...` from `accounts`, not the business id |
| `accounts` prints nothing | Ad account not assigned to this user / system user | Step 2, route B, point 2 |
| `17` / `613` / `80004` rate limit | Too many calls | The script waits and retries by itself |
| `2635` version | API version retired | Set `META_API_VERSION=v27.0` (or newest) in `.env`; see developers.facebook.com/docs/graph-api/changelog |
| Numbers differ from Ads Manager | Different dates or attribution setting | The script stops at yesterday; compare the same dates |
| Autopilot says "Nothing to change" every night | Rules too loose, or not enough results yet | Check `target_cost`; lower `min_results` only if you understand the risk |
| `python` not found | Python not installed / not on PATH | Install from python.org, tick **Add to PATH**, reopen the terminal |

Token leaked? Revoke it (route B: system user → **Revoke tokens**; route A: Facebook Settings → **Business integrations** → remove the app) and make a new one.
