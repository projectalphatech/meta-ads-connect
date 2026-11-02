# Setup, click by click

Checked 2026-11-02 against Marketing API v26.0. Meta renames buttons often; if a name differs, look for the closest match.

## Step 0: pick the route

| Route | For | Token lasts |
|---|---|---|
| **Fast** | Ads run from a personal ad account, no Business portfolio | ~1-2 hours, extendable to ~60 days |
| **Solid** | Ad account lives in a Business portfolio (business.facebook.com) | Does not expire (until revoked) |

Fast is fine to try today. Move to Solid before building anything that runs daily.

## Step 1: create a Meta app

1. Open https://developers.facebook.com/apps and log in with your Facebook account. First time: accept the developer terms and verify your account.
2. **Create app**. Use case: the one about ads / **Marketing API** (if none fits, choose "Other", then type **Business**).
3. Name it anything ("my ads reader"). Connect it to your Business portfolio if asked (Solid route).
4. Inside the app, add the **Marketing API** product if it is not already there.

You do not need app review to read your own ad accounts.

## Fast route: token from Graph API Explorer

1. Open https://developers.facebook.com/tools/explorer
2. Top right: pick your app. Token type: **User Token**.
3. Add permission **ads_read**. Nothing else. Click **Generate Access Token** and approve.
4. To extend it: open https://developers.facebook.com/tools/debug/accesstoken, paste the token, click **Extend Access Token**. Copy the new long token.
5. Go to step 4b below.

## Solid route: system user

### Step 2: create a system user
Business settings (business.facebook.com/settings) → **Users** → **System users** → **Add**. Name it, role **Employee** is enough.

### Step 3: give it the ad account
On the system user: **Assign assets** → **Ad accounts** → pick yours → turn on **view performance** only (no manage). Also assign the app you made in step 1 to the business if it is not yet.

### Step 4: generate the token
On the system user: **Generate new token** → pick your app → expiry **Never** → tick **ads_read** only → Generate. Copy it once; Meta will not show it again.

### Step 4b: save it (both routes)
In your project folder:
```bash
echo ".env" >> .gitignore
```
Then open `.env` in a text editor and add one line, with your token after the `=`:
```
META_TOKEN=paste_here
```
Do not paste the token into the chat, a commit, or a screenshot. If it ever leaks, revoke it (system user → **Revoke tokens**; fast route → Facebook Settings → **Business integrations** → remove the app) and make a new one.

## Step 5-6: test

```bash
python scripts/meta_ads.py check
python scripts/meta_ads.py accounts
python scripts/meta_ads.py insights --account act_YOUR_ID --days 7
```

## Common errors

| Error | Cause | Fix |
|---|---|---|
| `190` Invalid / expired token | Copy mistake, or the fast token expired | Make a new token (step 4 or Fast route) |
| `200` / `10` permission | Token lacks `ads_read`, or the account is not assigned | Re-do step 3, regenerate with `ads_read` |
| `100` bad parameter | Account id wrong | Use the `act_...` id from `accounts`, not the business id |
| `accounts` shows nothing | Ad account not assigned to this user / system user | Step 3 |
| `17` / `613` / `80004` rate limit | Too many calls | The script waits and retries; for many accounts, run less often |
| `2635` version | API version retired | Set `META_API_VERSION` to the newest (see developers.facebook.com/docs/graph-api/changelog) |
| Numbers differ from Ads Manager | Different date range or attribution setting, or today included | The script stops at yesterday; compare the same dates |
