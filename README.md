# meta-ads-connect

Connect your Facebook + Instagram ads to Claude Code (or any AI agent) through the Meta Marketing API, step by step. **Read-only**: the token can read results but cannot change ads or spend money.

Then ask in plain words: "which ad is spending and bringing nothing?"

## Install (Claude Code)

```bash
git clone https://github.com/projectalphatech/meta-ads-connect ~/.claude/skills/meta-ads-connect
```

Then tell Claude: **"connect my Meta ads"**. It walks you through one step at a time.

Other agents: point them at `SKILL.md`.

## What you need

- A Facebook account with an ad account that has run ads
- Python 3.9+ (no packages to install)
- ~15 minutes the first time

## What is inside

| File | What |
|---|---|
| `SKILL.md` | The walkthrough the agent follows |
| `references/setup.md` | Click-by-click setup + fixes for common errors |
| `references/questions.md` | Good questions to ask once connected |
| `scripts/meta_ads.py` | `check`, `accounts`, `insights` → CSV, `selftest` |

## Safety

- Token with `ads_read` only. The script warns if yours can write.
- Token lives in `.env` on your machine. Never paste it into chat or commit it.
- Uses Meta's official Graph API directly. No third-party server sees your data.

MIT licence. Made by [@sharkawyai](https://instagram.com/sharkawyai) · Project Alpha Tech.
