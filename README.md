# بوت المواقع: نموذج أولي

نموذج أولي لنظام يربط مواقع البناء بالمكتب عن طريق واتساب. المهندس يبعت رسالة لرقم الشركة، والبوت يصنّفها بالذكاء الاصطناعي (Claude)، ويسجّلها، ويوصلها للشخص المعني، وكل مسا يطلّع تقرير يومي.

- وثيقة المتطلبات الكاملة: https://claude.ai/artifact/RfcCfBKFvRpYUPJ7dM5eFQ
- العرض التفاعلي للإدارة: [`docs/site-system.html`](docs/site-system.html)

## شو بيعمل هالنموذج

| الميزة | الحالة |
| --- | --- |
| استقبال رسائل واتساب (نص، صور، فويس) والتحقق من توقيعها | جاهز |
| رفض الأرقام غير المسجلة، ومعالجة كل رسالة مرة وحدة | جاهز |
| التصنيف: تقدّم، طلب مواد، مشكلة، سلامة، عمالة، استفسار | جاهز (Claude، أو كلمات مفتاحية بدون إنترنت) |
| استخراج المادة والكمية والمواصفة والبلوك والطابق والموعد | جاهز |
| طلب مواد برقم مرجعي، وموافقة أو رفض من مدير المشروع بالواتساب، وإشعار المهندس والمشتريات | جاهز |
| تنبيه فوري للإدارة عند بلاغ سلامة | جاهز |
| ربط التقدّم ببنود جدول الكميات وتحديث الكمية المنجزة | جاهز |
| حفظ الرسالة قبل التصنيف، وإعادة معالجتها إذا تعطّل الذكاء الاصطناعي | جاهز |
| تقرير يومي لكل مشروع وتقرير مجمّع للإدارة | جاهز |
| تذكير الساعة 5 للمهندس اللي ما بعت تحديث | جاهز |
| استيراد جدول الكميات من إكسل (محفوظ كـ CSV) | جاهز |
| تحويل الفويس لنص | **مش مفعّل**: البوت بيحفظ الفويس وبيطلب من المهندس يكتبها |
| عروض الأسعار، أوامر الشراء، المخزون، لوحة التحكم | المرحلة الجاية |

## التجربة على جهازك (بدون واتساب وبدون مفتاح API)

```bash
pip install -r requirements.txt
export SITE_BOT_OFFLINE=1           # تصنيف بالكلمات المفتاحية بدل Claude
python -m site_bot seed             # 3 مشاريع و6 مستخدمين كأمثلة
python -m site_bot simulate 10000000001 "بدنا 20 طن حديد قطر 12 لبكرا الصبح"
python -m site_bot simulate 10000000010 "موافق MR-2026-0001"
python -m site_bot simulate 10000000001 "عامل وقع عن السقالة بالطابق الأول"
python -m site_bot report
```

بدون إعدادات واتساب، الرسائل اللي كانت رح تنبعت بتنطبع على الشاشة.

لتشغيل التصنيف الحقيقي بـ Claude، احذف `SITE_BOT_OFFLINE` وحط `ANTHROPIC_API_KEY`.

## إعداد البيانات الحقيقية

```bash
python -m site_bot add-project P01 "اسم المشروع"
python -m site_bot add-user "م. الاسم" 9627XXXXXXXX engineer --projects P01
python -m site_bot add-user "مدير المشاريع" 9627XXXXXXXX manager --projects P01,P02
python -m site_bot add-user "المشتريات" 9627XXXXXXXX procurement
python -m site_bot add-user "المدير العام" 9627XXXXXXXX management
python -m site_bot import-boq P01 boq.csv     # أعمدة: code,description,unit,qty
```

أرقام الهواتف بالصيغة الدولية بدون `+`، متل ما بيبعتها واتساب. مثال على ملف الكميات: [`examples/boq_sample.csv`](examples/boq_sample.csv).

## التشغيل مع واتساب

1. أنشئ تطبيق على Meta for Developers وفعّل WhatsApp Business Platform (Cloud API)، وسجّل رقم الشركة.
2. شغّل الخادم على عنوان HTTPS عام:
   ```bash
   uvicorn site_bot.server:app --host 0.0.0.0 --port 8000
   ```
3. بإعدادات الـ Webhook عند Meta: العنوان `https://<الدومين>/webhook`، ونفس قيمة `WHATSAPP_VERIFY_TOKEN`، واشترك بحقل `messages`.
4. جدولة المهام (cron):
   ```
   0 17 * * *    python -m site_bot remind
   0 19 * * *    python -m site_bot report
   */10 * * * *  python -m site_bot reprocess
   ```

| متغيّر البيئة | الوظيفة |
| --- | --- |
| `ANTHROPIC_API_KEY` | مفتاح Claude |
| `SITE_BOT_MODEL` | النموذج، الافتراضي `claude-opus-5-5` |
| `SITE_BOT_DB` | ملف قاعدة البيانات، الافتراضي `site_bot.sqlite3` |
| `WHATSAPP_TOKEN` | توكن الوصول من Meta |
| `WHATSAPP_PHONE_NUMBER_ID` | معرّف رقم الشركة |
| `WHATSAPP_VERIFY_TOKEN` | كلمة تختارها للتحقق من الـ Webhook |
| `WHATSAPP_APP_SECRET` | سر التطبيق، للتحقق من توقيع كل رسالة واردة |
| `WHATSAPP_API_VERSION` | نسخة Graph API، الافتراضي `v21.0` |

ملاحظة: الـ API الرسمي ما بيقرأ قروبات واتساب العادية. المهندسين بيبعتوا لرقم الشركة مباشرة.

## الاختبارات

```bash
SITE_BOT_OFFLINE=1 python -m pytest -q
```

## هيكل الكود

| الملف | الوظيفة |
| --- | --- |
| `site_bot/server.py` | استقبال الـ Webhook من واتساب |
| `site_bot/pipeline.py` | مسار الرسالة: حفظ، تصنيف، تسجيل، موافقات، إشعارات |
| `site_bot/classifier.py` | التصنيف بـ Claude (مخرجات JSON مضبوطة) وبديل الكلمات المفتاحية |
| `site_bot/report.py` | التقرير اليومي والتذكير |
| `site_bot/db.py` | جداول SQLite |
| `site_bot/whatsapp.py` | قراءة الرسائل الواردة والتحقق من التوقيع والإرسال |
| `site_bot/__main__.py` | أوامر الطرفية |
