# Step 7 — Run it every night (5 min)

← [Step 6](06-autopilot.md) · [Back to the steps](../README.md)

Pick your system. Replace the folder path with where this repo lives. 3 AM is a good time: yesterday is complete and you are asleep.

## Windows (Task Scheduler)

Open **Command Prompt** and run (one line):
```bat
schtasks /create /tn "ads-autopilot" /sc daily /st 03:00 /tr "cmd /c cd /d C:\path\to\meta-ads-connect && python scripts\autopilot.py --apply >> autopilot-run.txt 2>&1"
```
Test it now: `schtasks /run /tn "ads-autopilot"`, then open `autopilot-run.txt`.
Stop it: `schtasks /delete /tn "ads-autopilot" /f`

The PC must be on (sleep is fine if you allow wake timers; shut down is not).

## Mac / Linux (cron)

```bash
crontab -e
```
Add:
```
0 3 * * * cd /path/to/meta-ads-connect && python3 scripts/autopilot.py --apply >> autopilot-run.txt 2>&1
```

## Every morning

1. Open `autopilot-log.csv`: what changed and why.
2. Glance at Ads Manager.
3. Rules too aggressive or too slow? Edit `rules.json`. Next night uses the new rules.

Want a summary instead? Ask your agent: "read autopilot-log.csv and ads.csv and tell me what changed last night and if it helped."
