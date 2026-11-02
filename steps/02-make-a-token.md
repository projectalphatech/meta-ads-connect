# Step 2 — Make a read-only token (5 min)

← [Step 1](01-create-a-meta-app.md) · Next: [Step 3 — Save it and test](03-save-and-test.md)

The token is the password your agent uses to read your ads. This one gets **`ads_read` only**: it can read numbers, it cannot change or spend anything.

Pick one route:

| Route | Use it if | Token lasts |
|---|---|---|
| **A. Quick** | You run ads from your personal ad account | ~60 days, then make a new one |
| **B. Business** | Your ad account is inside a Business portfolio (business.facebook.com) | Never expires |

Not sure? Start with **A**. You can switch later.

## Route A — Quick (Graph API Explorer)

1. Open **https://developers.facebook.com/tools/explorer**
2. Top right: **Meta App** = the app from step 1. **User or Page** = **User Token**.
3. **Add a permission** → type `ads_read` → select it. Add nothing else.
4. Click **Generate Access Token** → approve the pop-up.
5. Make it last longer: open **https://developers.facebook.com/tools/debug/accesstoken**, paste the token, **Debug**, then **Extend Access Token** at the bottom. Copy the new, longer token.

## Route B — Business (system user)

1. Open **https://business.facebook.com/settings** → **Users** → **System users** → **Add**.
   Name: `ads-reader`. Role: **Employee**.
2. Click the system user → **Assign assets** → **Ad accounts** → pick your ad account → turn on **View performance** only → **Save**.
3. Still on the system user → **Generate new token** → pick your app → expiry **Never** → tick **`ads_read`** only → **Generate**.
4. Copy it now. Meta shows it once.

✅ **Done when:** you have a long token copied (starts with `EAA...`).

🔒 Do not paste it into the chat, a screenshot, or a commit. Step 3 saves it safely.
