# Step 4 — Pull your ads into a file (1 min)

← [Step 3](03-save-and-test.md) · Next: [Step 5 — Ask your agent](05-ask-your-agent.md)

```bash
python scripts/meta_ads.py insights --account act_1234567890 --days 7
```

This writes **`ads.csv`**: one row per ad, last 7 days up to yesterday (today's numbers are still coming in).

Columns: spend, impressions, reach, CTR, CPM, and for each result type the count and the cost per result: `leads`, `messages` (WhatsApp/Messenger), `purchases`, `link_clicks`, `page_views`.

It also prints the top 10 ads by spend.

Options:
- `--days 30` for a longer window
- `--level adset` or `--level campaign` to group
- `--out last-month.csv` to name the file

✅ **Done when:** `ads.csv` opens in Excel / Google Sheets with your ads in it (Arabic names show fine).
