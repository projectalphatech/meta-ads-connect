# meta-ads-connect

Connect your Facebook + Instagram ads to Claude Code (or any AI agent) with the Meta Marketing API, step by step.
Then ask it in plain words, *"which ad is spending and bringing nothing?"*, and, if you want, let it manage your ads every night with your own rules.

No coding needed. Python 3.9+ and about 20 minutes.

## The steps

| # | Step | Time | What you get |
|---|---|---|---|
| 1 | [Create a Meta app](steps/01-create-a-meta-app.md) | 5 min | An App ID |
| 2 | [Make a read-only token](steps/02-make-a-token.md) | 5 min | A token that can read, not change |
| 3 | [Save it and test](steps/03-save-and-test.md) | 2 min | Your `act_...` ad account id |
| 4 | [Pull your ads](steps/04-pull-your-ads.md) | 1 min | `ads.csv` with cost per message / lead |
| 5 | [Ask your agent](steps/05-ask-your-agent.md) | — | Answers from your real numbers |
| 6 | [Autopilot while you sleep](steps/06-autopilot.md) *(optional)* | 10 min | Pauses losers, moves budget to winners, by your rules |
| 7 | [Run it every night](steps/07-run-every-night.md) *(optional)* | 5 min | A 3 AM scheduled run + a log to read in the morning |

Stuck? [Troubleshooting](steps/troubleshooting.md).

## Use it with Claude Code (recommended)

```bash
git clone https://github.com/projectalphatech/meta-ads-connect ~/.claude/skills/meta-ads-connect
```
Open Claude Code in any folder and say **"connect my Meta ads"**. It walks you through the same steps, one at a time, and waits for you at each one.

Without an agent: clone anywhere and follow the steps above yourself.

## Safety

- Steps 1-5 use a token with **`ads_read` only**: it can't change ads or spend money.
- Step 6 uses a second token that can manage ads. The autopilot can only **pause ads** and **change ad set budgets** (capped by you). It never turns ads on, deletes, or creates anything, and it logs every change with how to undo it. Do dry runs first.
- Tokens live in `.env` on your machine (git-ignored). Never paste them into a chat.
- Talks to Meta's official Graph API directly. No third-party server sees your data.
- Results depend on your offer, creative and market. The autopilot follows rules; it doesn't guarantee a cost per result.

## Files

| File | What |
|---|---|
| `steps/` | The walkthrough |
| `scripts/meta_ads.py` | `check`, `accounts`, `insights` → CSV, `selftest` (read-only) |
| `scripts/autopilot.py` | Nightly rules: dry run by default, `--apply` to act, `selftest` |
| `SKILL.md` | How the agent guides you |

MIT licence. Made by [@sharkawyai](https://instagram.com/sharkawyai) · Project Alpha Tech.
