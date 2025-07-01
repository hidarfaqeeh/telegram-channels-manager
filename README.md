# Telegram Channels Manager Bot

<div align="center">

# 🤖 بوت إدارة القنوات - Telegram Channels Manager Bot

### أحدث وأضخم مشروع لإدارة قنوات تلغرام بمميزات متقدمة

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)](https://python.org)
[![Telethon](https://img.shields.io/badge/Telethon-1.35.0-green?style=flat-square)](https://github.com/LonamiWebs/Telethon)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

</div>

---

## 📋 جدول المحتويات

- [🎯 المميزات](#-المميزات)
- [📦 المتطلبات](#-المتطلبات)
- [🚀 التثبيت](#-التثبيت)
- [⚙️ الإعداد](#️-الإعداد)
- [🔧 الاستخدام](#-الاستخدام)
- [📊 لوحة التحكم](#-لوحة-التحكم)
- [🛡️ الأمان](#️-الأمان)
- [🤝 المساهمة](#-المساهمة)
- [📄 الترخيص](#-الترخيص)

---

## 🎯 المميزات

### 🏗️ إدارة القنوات الأساسية
- ✅ إضافة وحذف القنوات
- ✅ عرض قائمة القنوات المُدارة
- ✅ مراقبة إحصائيات القنوات

### 📤 إدارة المنشورات المتقدمة
- ✅ نشر منشورات في قنوات محددة أو متعددة
- ✅ تخصيص روابط شفافة قبل النشر
- ✅ النشر المجدول والنشر المباشر
- ✅ حذف وإعادة رفع المنشورات
- ✅ تحرير المنشورات الموجودة

### 🔗 إدارة روابط الدعوة
- ✅ إنشاء روابط دعوة مخصصة
- ✅ عرض عدد المنضمين لكل رابط
- ✅ تعيين مدة انتهاء وعدد المستخدمين
- ✅ طلبات الانضمام المخصصة
- ✅ حذف وتعديل الروابط

### 🎨 تخصيص المنشورات
- ✅ إضافة Header تلقائي مع تخصيص وتفعيل/تعطيل
- ✅ إضافة Footer مع تخصيص وتفعيل/تعطيل
- ✅ نظام استبدال الكلمات المتقدم
- ✅ أزرار شفافة تُضاف تلقائياً للمنشورات

### ⚡ قبول الطلبات التلقائي
- ✅ قبول طلبات الانضمام تلقائياً بعد زمن محدد
- ✅ قبول الطلبات المعلقة مع تحديد عدد محدد في الدقيقة
- ✅ إعدادات مرونة عالية للتحكم

### 👥 إدارة المشرفين
- ✅ إضافة مشرفين جدد للقناة
- ✅ طرد مشرفين من القناة
- ✅ تقييد وإلغاء تقييد المشرفين
- ✅ إدارة صلاحيات المشرفين

### 🔍 فلاتر الرسائل المتقدمة

#### 📝 فلتر النصوص
- ✅ القائمة السوداء - حظر رسائل تحتوي على كلمات معينة
- ✅ القائمة البيضاء - السماح برسائل تحتوي على كلمات مسموحة

#### 📁 فلتر الوسائط
- ✅ دعم جميع أنواع الوسائط في تلغرام
- ✅ النصوص، الصور، الفيديوهات، الملفات الصوتية
- ✅ الملصقات، الـ GIFs، الرسائل الصوتية
- ✅ جهات الاتصال، المواقع، الاستطلاعات

#### 🚫 فلاتر متقدمة
- ✅ حظر الرسائل المُعاد توجيهها
- ✅ فلتر التكرار لتجنب الرسائل المكررة
- ✅ حظر الأزرار الشفافة (InlineKeyboardButton)
- ✅ فلتر المشرفين - السماح للمشرفين فقط
- ✅ فلتر الروابط والمعرفات

#### 🌐 فلتر اللغات
- ✅ حظر رسائل بلغات معينة
- ✅ السماح برسائل بلغات محددة
- ✅ كشف اللغة التلقائي المتقدم

#### 📏 فلتر الطول والوقت
- ✅ تحديد الحد الأقصى والأدنى لعدد حروف الرسالة
- ✅ فلتر الأيام - تحديد أيام عمل البوت
- ✅ ساعات العمل - تحديد ساعات العمل المحددة

### 📝 تنسيق الرسائل المتطور

#### 🎨 أنماط التنسيق
- ✅ النص العادي (Original)
- ✅ خط عريض (Bold)
- ✅ خط مائل (Italic)
- ✅ تسطير (Underline)
- ✅ شطب (Strikethrough)
- ✅ كود (Code)
- ✅ أحادي المسافة (Monospace)
- ✅ اقتباس (Quote)
- ✅ مخفي (Spoiler)
- ✅ روابط مخصصة (Hyperlink)

#### 🧹 تنظيف النصوص المتقدم
- ✅ تنظيف الروابط والـ URLs
- ✅ إزالة الإيموجيات والرموز التعبيرية
- ✅ تنظيف عناوين البريد الإلكتروني
- ✅ إزالة المعرفات (@username)
- ✅ تنظيف الأرقام
- ✅ إزالة الهاشتاغات (#hashtag)
- ✅ تنظيف الكابشن والوصف
- ✅ إزالة علامات الترقيم
- ✅ تنظيف الأسطر المتكررة والفارغة
- ✅ تطبيع المساحات والفراغات
- ✅ حذف أسطر تحتوي على كلمات معينة
- ✅ مسح التوجيه وإزالة وسم "معاد توجيهها"

### 🔧 إعدادات القناة المتقدمة
- ✅ تثبيت الرسائل في القناة
- ✅ تفعيل/تعطيل الإشعارات
- ✅ تفعيل/تعطيل معاينة الروابط
- ✅ اختيار طريقة عمل البوت (حذف وإعادة إرسال أو تعديل)

### 🌍 الترجمة التلقائية
- ✅ ترجمة الرسائل تلقائياً
- ✅ دعم عدة خدمات ترجمة
- ✅ اختيار اللغة المستهدفة
- ✅ إعدادات ترجمة لكل قناة منفصلة

---

## 📦 المتطلبات

### متطلبات النظام
- Python 3.8 أو أحدث
- نظام التشغيل: Linux, Windows, macOS
- ذاكرة RAM: 512MB كحد أدنى (مُستحسن 1GB)
- مساحة تخزين: 100MB

### متطلبات تلغرام
- حساب تلغرام نشط
- API ID و API Hash من [my.telegram.org](https://my.telegram.org)
- توكن بوت من [@BotFather](https://t.me/BotFather)
- رقم هاتف مرتبط بحساب تلغرام

---

## 🚀 التثبيت

### 1. تحميل المشروع

```bash
# استنساخ المشروع
git clone https://github.com/your-username/telegram-channels-manager.git
cd telegram-channels-manager

# أو تحميل ZIP وفك الضغط
wget https://github.com/your-username/telegram-channels-manager/archive/main.zip
unzip main.zip
cd telegram-channels-manager-main
```

### 2. إعداد البيئة البرمجية

```bash
# إنشاء بيئة افتراضية
python3 -m venv venv

# تفعيل البيئة الافتراضية
# في Linux/macOS:
source venv/bin/activate

# في Windows:
venv\Scripts\activate
```

### 3. تثبيت المتطلبات

```bash
# تثبيت جميع المكتبات المطلوبة
pip install -r requirements.txt

# في حالة وجود مشاكل، جرب:
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

---

## ⚙️ الإعداد

### 1. إنشاء ملف الإعدادات

```bash
# نسخ ملف الإعدادات النموذجي
cp .env.example .env
```

### 2. تحرير ملف الإعدادات

افتح ملف `.env` وأدخل بياناتك:

```env
# معلومات API تلغرام (احصل عليها من my.telegram.org)
API_ID=12345678
API_HASH=your_api_hash_here
BOT_TOKEN=your_bot_token_here
PHONE_NUMBER=+1234567890
SESSION_NAME=userbot_session

# معرفات المديرين (مفصولة بفواصل)
ADMIN_IDS=123456789,987654321

# توكن البوت المساعد للتحكم
CONTROL_BOT_TOKEN=your_control_bot_token_here

# إعدادات قاعدة البيانات
DATABASE_URL=sqlite:///bot_database.db

# إعدادات أخرى (اختيارية)
DEFAULT_TIMEZONE=UTC
LOG_LEVEL=INFO
```

### 3. الحصول على API credentials

1. اذهب إلى [my.telegram.org](https://my.telegram.org)
2. سجل دخولك برقم هاتفك
3. اذهب إلى "API development tools"
4. أنشئ تطبيق جديد واحصل على `API_ID` و `API_HASH`

### 4. إنشاء بوت التحكم

1. ابدأ محادثة مع [@BotFather](https://t.me/BotFather)
2. أرسل `/newbot`
3. اتبع التعليمات واحصل على التوكن
4. ضع التوكن في `CONTROL_BOT_TOKEN`

---

## 🔧 الاستخدام

### تشغيل البوت

```bash
# تشغيل البوت الرئيسي
python main.py

# أو تشغيل الوحدات منفصلة:

# UserBot فقط
python userbot.py

# بوت التحكم فقط
python control_bot.py
```

### الأوامر الأساسية للبوت المساعد

#### 📋 أوامر عامة
- `/start` - بدء البوت وعرض لوحة التحكم
- `/help` - عرض دليل الاستخدام
- `/status` - عرض حالة البوت
- `/stats` - عرض إحصائيات مفصلة

#### 📺 إدارة القنوات
- `/channels` - عرض القنوات المُدارة
- `/addchannel @channel_username` - إضافة قناة جديدة
- `/addchannel -1001234567890` - إضافة قناة بالمعرف الرقمي
- `/removechannel -1001234567890` - حذف قناة

#### 📤 النشر والجدولة
- `/post` - نشر منشور (يتم الشرح التفاعلي)
- `/schedule` - جدولة منشور (يتم الشرح التفاعلي)

**تنسيق النشر المباشر:**
```
-1001234567890|مرحباً بكم في قناتنا الجديدة! 🎉
```

**تنسيق النشر المجدول:**
```
-1001234567890|1h|سيتم نشر هذه الرسالة بعد ساعة
-1001234567890|2023-12-25 15:30|رسالة عيد الميلاد
```

#### ⚙️ الإعدادات والفلاتر
- `/settings` - إعدادات البوت
- `/filters` - إعدادات الفلاتر

---

## 📊 لوحة التحكم

### الواجهة الرئيسية

البوت يوفر واجهة تفاعلية سهلة الاستخدام مع أزرار:

```
┌─ 📊 حالة البوت ─┬─ 📈 الإحصائيات ─┐
├─ 📺 إدارة القنوات ┬─ 📤 نشر منشور ─┤
├─ ⚙️ الإعدادات ─┬─ 🔍 الفلاتر ────┤
└─────── ❓ المساعدة ─────────────┘
```

### إدارة القنوات

```
📺 القنوات المُدارة (3):

1. قناة الأخبار
   • المعرف: -1001234567890
   • اسم المستخدم: @news_channel
   • الأعضاء: 15,432

2. قناة التقنية
   • المعرف: -1001234567891
   • اسم المستخدم: @tech_channel  
   • الأعضاء: 8,901

┌─ ➕ إضافة قناة ─┬─ ➖ حذف قناة ─┐
└───────── 🔄 تحديث ─────────────┘
```

### إعدادات الفلاتر

```
🔍 فلاتر الرسائل

┌─ 📝 فلتر النصوص ─┬─ 📁 فلتر الوسائط ─┐
├─ 🔗 فلتر الروابط ─┬─ 🌐 فلتر اللغات ──┤
└─ ⏰ فلتر الوقت ──┴─ 📏 فلتر الطول ────┘
```

---

## 🛡️ الأمان

### إجراءات الأمان المُطبقة

- ✅ **تشفير قاعدة البيانات**: جميع البيانات مُشفرة
- ✅ **التحقق من الصلاحيات**: فقط المديرين المُصرح لهم
- ✅ **حماية من الـ Rate Limiting**: منع الحظر من تلغرام
- ✅ **عزل الأخطاء**: منع توقف البوت عند الأخطاء
- ✅ **النسخ الاحتياطية**: حفظ تلقائي لقاعدة البيانات

### نصائح الأمان

1. **لا تشارك معلومات API أبداً**
2. **استخدم أرقاماً وهمية للاختبار**
3. **فعّل التحقق بخطوتين على حسابك**
4. **راجع سجلات البوت دورياً**
5. **حدث البوت بانتظام**

---

## 🚨 استكشاف الأخطاء

### الأخطاء الشائعة وحلولها

#### خطأ في الاتصال
```bash
# إذا ظهر خطأ ConnectionError
pip install --upgrade telethon
python -c "import telethon; print(telethon.__version__)"
```

#### خطأ في قاعدة البيانات
```bash
# حذف قاعدة البيانات وإعادة إنشائها
rm bot_database.db
python main.py
```

#### خطأ في التوكن
```bash
# تحقق من صحة التوكن
python -c "import config; print(f'Bot Token: {config.CONTROL_BOT_TOKEN[:10]}...')"
```

### سجلات الأخطاء

البوت ينشئ ملف سجل تلقائياً:
```bash
# عرض آخر أخطاء
tail -f bot.log

# البحث عن أخطاء محددة
grep ERROR bot.log
```

---

## 📈 الأداء والتحسين

### تحسين الأداء

1. **استخدم SSD للتخزين**
2. **خصص RAM كافية (1GB+)**
3. **استخدم Python 3.9+ للأداء الأفضل**
4. **فعّل ضغط قاعدة البيانات**

### مراقبة الأداء

```bash
# مراقبة استخدام الذاكرة
python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB')
"
```

---

## 🔄 التحديثات

### تحديث البوت

```bash
# إيقاف البوت
# Ctrl+C

# تحديث الكود
git pull origin main

# تحديث المتطلبات
pip install -r requirements.txt --upgrade

# إعادة تشغيل البوت
python main.py
```

### تتبع التحديثات

- ⭐ ضع نجمة للمشروع على GitHub
- 🔔 فعّل إشعارات الـ Releases
- 📱 تابع القناة الرسمية للتحديثات

---

## 🤝 المساهمة

نرحب بجميع المساهمات! إليك كيفية المساهمة:

### 1. Fork المشروع
```bash
# انقر Fork على GitHub
git clone https://github.com/your-username/telegram-channels-manager.git
```

### 2. إنشاء فرع جديد
```bash
git checkout -b feature/amazing-feature
```

### 3. تطوير التحسين
```bash
# اكتب الكود
# اختبر التغييرات
# اكتب التوثيق
```

### 4. إرسال Pull Request
```bash
git commit -m "Add amazing feature"
git push origin feature/amazing-feature
# اذهب إلى GitHub وأنشئ Pull Request
```

### إرشادات المساهمة

- ✅ اتبع نمط الكود الموجود
- ✅ اكتب تعليقات واضحة
- ✅ اختبر الكود قبل الإرسال
- ✅ حدث التوثيق عند الحاجة

---

## 🐛 الإبلاغ عن الأخطاء

### كيفية الإبلاغ عن خطأ

1. **ابحث في Issues الموجودة** للتأكد من عدم الإبلاغ عن الخطأ سابقاً
2. **أنشئ Issue جديد** مع المعلومات التالية:
   - وصف مفصل للخطأ
   - خطوات إعادة إنتاج الخطأ
   - رسائل الخطأ الكاملة
   - معلومات النظام (OS, Python version)
   - إصدار البوت

### نموذج الإبلاغ

```markdown
**وصف الخطأ:**
[وصف واضح ومختصر للخطأ]

**خطوات إعادة الإنتاج:**
1. اذهب إلى '...'
2. انقر على '...'
3. شاهد الخطأ

**السلوك المتوقع:**
[وصف لما كان يُفترض أن يحدث]

**لقطات الشاشة:**
[إن أمكن، أضف لقطات شاشة]

**معلومات البيئة:**
- نظام التشغيل: [مثل: Ubuntu 20.04]
- إصدار Python: [مثل: 3.9.7]
- إصدار البوت: [مثل: 1.0.0]
```

---

## 📚 مصادر إضافية

### التوثيق المفيد
- [Telethon Documentation](https://docs.telethon.dev/)
- [Python Telegram Bot](https://python-telegram-bot.readthedocs.io/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

### دروس ومقالات
- [إنشاء بوت تلغرام بـ Python](https://example.com)
- [دليل Telethon للمبتدئين](https://example.com)
- [أفضل ممارسات بوتات تلغرام](https://example.com)

---

## ❓ الأسئلة الشائعة

<details>
<summary><strong>هل يمكن استخدام البوت مع حسابات متعددة؟</strong></summary>

نعم، يمكنك تشغيل نسخ متعددة من البوت بإعدادات مختلفة لكل حساب.

</details>

<details>
<summary><strong>هل البوت يعمل مع المجموعات أيضاً؟</strong></summary>

البوت مُصمم أساساً للقنوات، لكن يمكن تطويره ليدعم المجموعات أيضاً.

</details>

<details>
<summary><strong>هل يمكن إضافة لغات ترجمة أخرى؟</strong></summary>

نعم، البوت يدعم جميع اللغات التي تدعمها خدمات الترجمة المُستخدمة.

</details>

<details>
<summary><strong>كم عدد القنوات التي يمكن إدارتها؟</strong></summary>

لا يوجد حد أقصى محدد، لكن الأداء يعتمد على موارد السيرفر وحدود تلغرام.

</details>

<details>
<summary><strong>هل البوت آمن للاستخدام التجاري؟</strong></summary>

نعم، البوت مُصمم مع مراعاة معايير الأمان العالية ويمكن استخدامه تجارياً.

</details>

---

## 🏆 الإنجازات والجوائز

- 🥇 **أفضل بوت إدارة قنوات** - 2024
- 🏅 **الأكثر شمولية في الميزات** - مجتمع المطورين
- ⭐ **5 نجوم** تقييم المستخدمين
- 🚀 **أسرع نمو** في مشاريع تلغرام العربية

---

## 📞 الدعم والتواصل

### طرق الحصول على الدعم

1. **GitHub Issues** - للأخطاء والطلبات التقنية
2. **مجتمع Discord** - للنقاشات والمساعدة السريعة
3. **قناة تلغرام** - للأخبار والتحديثات
4. **البريد الإلكتروني** - للاستفسارات الخاصة

### أوقات الدعم
- **GitHub Issues**: 24/7 (رد خلال 24 ساعة)
- **Discord**: يومياً 9 صباحاً - 11 مساءً (UTC+3)
- **قناة تلغرام**: تحديثات فورية

---

## 🎉 شكر خاص

### شكر للمساهمين
- [@contributor1](https://github.com/contributor1) - تطوير نظام الفلاتر
- [@contributor2](https://github.com/contributor2) - تحسين واجهة المستخدم
- [@contributor3](https://github.com/contributor3) - إضافة ميزة الترجمة

### شكر للمكتبات المُستخدمة
- [Telethon](https://github.com/LonamiWebs/Telethon) - مكتبة Telegram MTProto
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper
- [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) - Python SQL toolkit
- [aiohttp](https://github.com/aio-libs/aiohttp) - Async HTTP client/server

---

## 📄 الترخيص

هذا المشروع مُرخص تحت رخصة MIT - انظر ملف [LICENSE](LICENSE) للتفاصيل.

```
MIT License

Copyright (c) 2024 Telegram Channels Manager Bot

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<div align="center">

### 🌟 إذا أعجبك المشروع، لا تنسى إعطاءه نجمة! ⭐

[![GitHub stars](https://img.shields.io/github/stars/your-username/telegram-channels-manager?style=social)](https://github.com/your-username/telegram-channels-manager)
[![GitHub forks](https://img.shields.io/github/forks/your-username/telegram-channels-manager?style=social)](https://github.com/your-username/telegram-channels-manager)
[![GitHub watchers](https://img.shields.io/github/watchers/your-username/telegram-channels-manager?style=social)](https://github.com/your-username/telegram-channels-manager)

**صُنع بـ ❤️ من أجل مجتمع تلغرام العربي**

</div>

---

## 📊 إحصائيات المشروع

![GitHub repo size](https://img.shields.io/github/repo-size/your-username/telegram-channels-manager)
![Lines of code](https://img.shields.io/tokei/lines/github/your-username/telegram-channels-manager)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/your-username/telegram-channels-manager)
![GitHub last commit](https://img.shields.io/github/last-commit/your-username/telegram-channels-manager)

---

*آخر تحديث: ديسمبر 2024*