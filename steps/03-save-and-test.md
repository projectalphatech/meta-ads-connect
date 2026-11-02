# Step 3 — Save the token and test (2 min)

← [Step 2](02-make-a-token.md) · Next: [Step 4 — Pull your ads](04-pull-your-ads.md)

1. Open a terminal **inside this repo folder** (`meta-ads-connect`).
2. Create a file named `.env` (it is already in `.gitignore`, so git never uploads it). Put one line in it, your token after the `=`:
   ```
   META_TOKEN=EAA...your token...
   ```
3. Test it:
   ```bash
   python scripts/meta_ads.py check
   ```
   You should see `Token OK` and `Read-only: this token can read ads but cannot change or spend anything.`
4. Find your ad account id:
   ```bash
   python scripts/meta_ads.py accounts
   ```
   You get lines like `act_1234567890  My Ads  EGP  active`. Copy the `act_...` part.

✅ **Done when:** `accounts` prints your ad account.

No Python? Install it from **https://python.org** (3.9 or newer; on Windows tick **Add to PATH**). Nothing else to install.

Errors? See [troubleshooting](troubleshooting.md).
