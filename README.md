# meta-ads-connect

**English** · [العربي ↓](#بالعربي)

Connect your Facebook + Instagram ads to Claude Code (or any AI agent) through Meta's official Marketing API, step by step.
Then ask it in plain words, *"which ad is spending and bringing nothing?"*, and, if you want, let it manage your ads every night by **your** rules while you sleep.

- No coding needed. You copy and paste a few commands.
- Needs: a Facebook account that runs ads, a computer with **Python 3.9+**, about **20 minutes**.
- Free. Talks to Meta directly. No third-party server, no subscription.

---

## What you get

1. **Read your ads with an agent** (steps 1-5). A read-only token pulls your real numbers (spend, messages, leads, cost per result, CTR) into `ads.csv`. Your agent answers questions from that file and shows the rows that prove it.
2. **Autopilot** (steps 6-7, optional). A nightly script that follows your rules:
   - pauses ads that burn money with no results, or cost far more than your target;
   - raises the daily budget of ad sets cheaper than your target (+20% a night, never above your cap);
   - lowers the budget of ad sets that are too expensive (-20%).

   It runs as a **dry run** first and logs every change with how to undo it.

## Quick start with Claude Code (recommended)

```bash
git clone https://github.com/projectalphatech/meta-ads-connect ~/.claude/skills/meta-ads-connect
```

Open Claude Code in any folder and say **"connect my Meta ads"**. It walks you through the steps below, one at a time, and waits for you at each one.

Using another agent (Cursor, Codex, ChatGPT…) or none? Clone the repo anywhere and follow the steps yourself:

```bash
git clone https://github.com/projectalphatech/meta-ads-connect
cd meta-ads-connect
```

## The steps

| # | Step | Time | You end with |
|---|---|---|---|
| 1 | [Create a Meta app](steps/01-create-a-meta-app.md) | 5 min | An **App ID** (your key holder; no app review needed to read your own ads) |
| 2 | [Make a read-only token](steps/02-make-a-token.md) | 5 min | A token with **`ads_read`** only: it can read, never change or spend |
| 3 | [Save it and test](steps/03-save-and-test.md) | 2 min | Token in `.env`, `check` passes, your `act_...` ad account id |
| 4 | [Pull your ads](steps/04-pull-your-ads.md) | 1 min | `ads.csv` with spend and cost per message / lead per ad |
| 5 | [Ask your agent](steps/05-ask-your-agent.md) | — | Answers from your real numbers |
| 6 | [Autopilot while you sleep](steps/06-autopilot.md) *(optional)* | 10 min | Your `rules.json`, dry runs, then `--apply` |
| 7 | [Run it every night](steps/07-run-every-night.md) *(optional)* | 5 min | A 3 AM scheduled run + a log to read in the morning |

Stuck? See [Troubleshooting](steps/troubleshooting.md) (expired token, permission errors, empty results, wrong account id).

### The commands, in one place

```bash
python scripts/meta_ads.py check                                   # is the token OK?
python scripts/meta_ads.py accounts                                # list your act_... ad accounts
python scripts/meta_ads.py insights --account act_XXXX --days 7    # -> ads.csv  (--level ad|adset|campaign)
python scripts/meta_ads.py selftest                                # offline test, no API calls

python scripts/autopilot.py                                        # dry run: prints what it WOULD do
python scripts/autopilot.py --apply                                # does it, logs to autopilot-log.csv
python scripts/autopilot.py selftest                               # offline test of the rules
```

On Mac/Linux use `python3` if `python` is not found.

### Questions to ask your agent

- Which ad spent the most last week, and what did it bring?
- Which ads spent money and brought zero messages? Is that enough spend to judge?
- Rank my ads by cost per message. Which 2 should I keep?
- Which ad has a good CTR but no results? What does that tell me?
- Read `autopilot-log.csv` and `ads.csv`: what changed last night, and did it help?

## Autopilot rules (`rules.json`)

The first run of `autopilot.py` creates `rules.json`. Set at least `account`, `result`, `target_cost` and `max_daily_budget`.

| Rule | Default | Meaning |
|---|---|---|
| `account` | — | Your `act_...` id |
| `result` | `messages` | What you pay for: `messages`, `leads`, `purchases`, `page_views` |
| `target_cost` | `10` | The most one result is worth to you, in your account currency |
| `days` | `3` | Look-back window |
| `kill_zero_after_x` | `2.5` | Pause an ad with 0 results after it spent 2.5× `target_cost` |
| `kill_cost_x` | `2.0` | Pause an ad whose cost per result is over 2× target… |
| `min_results` | `3` | …but only once it has at least 3 results |
| `scale_cost_x` | `0.7` | Raise an ad set's budget when cost per result is under 0.7× target |
| `cut_cost_x` | `1.5` | Lower an ad set's budget when cost per result is over 1.5× target |
| `scale_step` | `0.2` | Budget change per night (20%) |
| `max_daily_budget` | `500` | Hard cap per ad set per day |
| `max_changes_per_night` | `5` | Stops after this many changes |
| `never_touch` | `[]` | Name parts to skip, e.g. `["brand", "retargeting"]` |

Do dry runs for 3-5 days before `--apply`. Ad sets with no daily budget (budget set on the campaign) are left alone.

## Safety

- Steps 1-5 use a token with **`ads_read` only**. It cannot change ads or spend money.
- Step 6 uses a **second** token (`META_WRITE_TOKEN`, scope `ads_management`). The autopilot can only **pause ads** and **change ad set daily budgets**, capped by you. It never turns ads on, never deletes, never creates, never touches audiences or creatives.
- Every change goes into `autopilot-log.csv` with an `undo` column.
- Tokens live in `.env` on your machine. `.env`, `rules.json` and your CSV files are git-ignored, so they are never pushed.
- **Never paste a token into a chat, a screenshot, a GitHub issue or a public repo.** If one leaks, remove it in Meta and make a new one.
- Results depend on your offer, creative and market. The autopilot follows rules; it does not guarantee a cost per result.

## FAQ

**Does it cost anything?** No. The Marketing API is free for your own ad accounts.

**Do I need Meta app review?** No. Reading and managing your own ad accounts works without review.

**My token expired.** A quick token (route A in step 2) lasts about 60 days after you extend it; then make a new one. A Business system-user token (route B) never expires.

**Can it run on my server instead of my PC?** Yes. Any machine with Python and a scheduler (cron) works. Copy the folder and your `.env`.

**Does it work for Google or TikTok ads?** No. Meta only (Facebook, Instagram, click-to-WhatsApp ads).

## Files

| File | What |
|---|---|
| `steps/` | The walkthrough, steps 01-07 + troubleshooting |
| `scripts/meta_ads.py` | `check`, `accounts`, `insights` → CSV, `selftest` (read-only) |
| `scripts/autopilot.py` | Nightly rules: dry run by default, `--apply` to act, `selftest` |
| `SKILL.md` | How the agent guides you |

---

<div dir="rtl" align="right">

## بالعربي

اربط إعلانات فيسبوك وإنستجرام بـ Claude Code (أو أي AI agent) عن طريق الـ Marketing API الرسمي بتاع Meta، خطوة بخطوة.
بعد كده اسأله بكلامك العادي: *«أنهي إعلان بيصرف ومش بيجيب حاجة؟»*، ولو حابب، خلّيه يدير إعلاناتك كل ليلة بـ**قواعدك إنت** وإنت نايم.

- مش محتاج تعرف برمجة. هتعمل copy و paste لكام أمر بس.
- محتاج: حساب فيسبوك بيعمل إعلانات، كمبيوتر عليه **Python 3.9 أو أحدث**، وحوالي **20 دقيقة**.
- مجاني. بيكلّم Meta مباشرة. مفيش سيرفر وسيط ولا اشتراك.

### هتاخد إيه

1. **الـ agent يقرأ إعلاناتك** (الخطوات 1-5): token للقراءة بس بيسحب أرقامك الحقيقية (الصرف، الرسايل، الـ leads، تكلفة النتيجة، الـ CTR) في ملف `ads.csv`، والـ agent بيجاوبك منه وبيوريك الصفوف اللي تثبت كلامه.
2. **Autopilot** (الخطوات 6-7، اختياري): سكريبت بيشتغل كل ليلة بقواعدك:
   - يقفل الإعلان اللي بيصرف ومش بيجيب نتايج، أو تكلفته أعلى بكتير من هدفك.
   - يزوّد ميزانية الـ ad set اللي أرخص من هدفك (+20% في الليلة، ومش هيعدّي الحد اللي إنت حاطه).
   - يقلّل ميزانية الـ ad set الغالي (-20%).

   بيشتغل **تجربة (dry run)** الأول، وبيسجّل كل تغيير وإزاي ترجّعه.

### أسرع طريقة: مع Claude Code

</div>

```bash
git clone https://github.com/projectalphatech/meta-ads-connect ~/.claude/skills/meta-ads-connect
```

<div dir="rtl" align="right">

افتح Claude Code في أي فولدر وقوله **«connect my Meta ads»** أو **«اربطلي إعلانات Meta»**. هيمشي معاك في الخطوات واحدة واحدة، ويستناك في كل خطوة.

بتستخدم agent تاني أو مش بتستخدم خالص؟ نزّل الريبو في أي مكان وامشي على الخطوات بنفسك.

### الخطوات

| # | الخطوة | الوقت | هتخلص بإيه |
|---|---|---|---|
| 1 | [اعمل Meta app](steps/01-create-a-meta-app.md) | 5 دقايق | **App ID** (ده بس شايل المفاتيح، ومش محتاج مراجعة من Meta عشان تقرأ إعلاناتك) |
| 2 | [اعمل token للقراءة بس](steps/02-make-a-token.md) | 5 دقايق | token بصلاحية **`ads_read`** بس: يقرأ، ومينفعش يغيّر أو يصرف |
| 3 | [احفظه وجرّبه](steps/03-save-and-test.md) | دقيقتين | الـ token في `.env`، أمر `check` شغال، ورقم حسابك `act_...` |
| 4 | [اسحب إعلاناتك](steps/04-pull-your-ads.md) | دقيقة | ملف `ads.csv` فيه الصرف وتكلفة الرسالة / الـ lead لكل إعلان |
| 5 | [اسأل الـ agent](steps/05-ask-your-agent.md) | — | إجابات من أرقامك الحقيقية |
| 6 | [Autopilot وإنت نايم](steps/06-autopilot.md) *(اختياري)* | 10 دقايق | ملف `rules.json`، تجارب dry run، وبعدين `--apply` |
| 7 | [شغّله كل ليلة](steps/07-run-every-night.md) *(اختياري)* | 5 دقايق | تشغيل تلقائي الساعة 3 الفجر + log تقرأه الصبح |

واقف في حتة؟ شوف [حل المشاكل](steps/troubleshooting.md) (token خلص، مشكلة صلاحيات، نتايج فاضية، رقم حساب غلط).

> الخطوات مكتوبة بالإنجليزي عشان أسماء الزراير في Meta بالإنجليزي. لو مش فاهم حاجة، اسأل الـ agent بالعربي وهو هيشرحلك.

### أسئلة تسألها للـ agent

- أنهي إعلان بيصرف ومش بيجيب رسايل؟
- رتّبلي الإعلانات من الأرخص للأغلى في تكلفة الرسالة.
- لو هقفل إعلان واحد النهارده، أقفل مين وليه؟
- أنهي إعلان الـ CTR بتاعه كويس بس مش بيجيب نتايج؟ ده معناه إيه؟
- اقرأ `autopilot-log.csv` و `ads.csv` وقولّي إيه اللي اتغيّر امبارح، وهل فرق؟

### قواعد الـ Autopilot

أول مرة تشغّل `autopilot.py` هيعمل ملف `rules.json`. لازم تظبط على الأقل:

| القاعدة | معناها | مثال |
|---|---|---|
| `account` | رقم حسابك `act_...` | `"act_1234567890"` |
| `result` | بتدفع على إيه: `messages` أو `leads` أو `purchases` أو `page_views` | `"messages"` |
| `target_cost` | أقصى سعر تدفعه في نتيجة واحدة (بعملة حسابك) | `15` |
| `max_daily_budget` | أقصى ميزانية يومية لأي ad set | `300` |
| `never_touch` | أجزاء من أسماء متلمسهاش | `["brand", "test"]` |

باقي القواعد ليها قيم افتراضية معقولة (شوف الجدول الإنجليزي فوق). اعمل dry run من 3 لـ 5 أيام قبل ما تشغّل `--apply`.

### الأمان

- الخطوات 1-5 بتستخدم token بصلاحية **`ads_read` بس**. مينفعش يغيّر إعلان أو يصرف جنيه.
- الخطوة 6 بتستخدم token **تاني** (`META_WRITE_TOKEN` بصلاحية `ads_management`). الـ autopilot يقدر بس **يقفل إعلانات** و**يغيّر الميزانية اليومية للـ ad set** في حدود اللي إنت حاطه. عمره ما هيشغّل إعلان، ولا يمسح، ولا يعمل جديد، ولا يلمس الجمهور أو التصميمات.
- كل تغيير بيتسجّل في `autopilot-log.csv` ومعاه عمود `undo` يقولك ترجّعه إزاي.
- الـ tokens بتفضل في ملف `.env` على جهازك. ملف `.env` و `rules.json` وملفات الـ CSV متجاهَلين في git، يعني عمرهم ما هيترفعوا.
- **متحطّش الـ token أبدًا في شات، أو screenshot، أو GitHub issue، أو ريبو public.** لو اتسرّب، شيله من Meta واعمل واحد جديد.
- النتايج بتعتمد على العرض بتاعك والتصميم والسوق. الـ autopilot بيمشي على قواعد، ومش بيضمن تكلفة معيّنة للنتيجة.

### أسئلة شائعة

**بيكلّف فلوس؟** لأ. الـ Marketing API مجاني لحساباتك الإعلانية.

**محتاج مراجعة من Meta (app review)؟** لأ. قراءة وإدارة حساباتك إنت شغالة من غير مراجعة.

**الـ token خلص.** الـ token السريع (الطريقة A في الخطوة 2) بيعيش حوالي 60 يوم بعد ما تمدّه، وبعدين اعمل واحد جديد. الـ token بتاع الـ Business (system user، الطريقة B) مبيخلصش.

**ينفع يشتغل على سيرفر بدل الكمبيوتر؟** آه. أي جهاز عليه Python و cron هيشتغل. انسخ الفولدر وملف `.env`.

**بيشتغل مع إعلانات Google أو TikTok؟** لأ. Meta بس (فيسبوك، إنستجرام، وإعلانات واتساب).

</div>

---

MIT licence. Made by [@sharkawyai](https://instagram.com/sharkawyai) · Project Alpha Tech.
