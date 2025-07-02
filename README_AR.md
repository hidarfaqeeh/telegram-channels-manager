# بوت إدارة القنوات المتقدم
## Telegram Channels Manager Bot

🚀 **بوت تلغرام متطور لإدارة القنوات مع ميزات متقدمة**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-100%25%20Ready-brightgreen.svg)](/)

## 📋 جدول المحتويات

- [المميزات](#-المميزات)
- [المتطلبات](#-المتطلبات)
- [التثبيت السريع](#-التثبيت-السريع)
- [الإعداد التفصيلي](#-الإعداد-التفصيلي)
- [الاستخدام](#-الاستخدام)
- [الميزات المتقدمة](#-الميزات-المتقدمة)
- [الأوامر](#-الأوامر)
- [استكشاف الأخطاء](#-استكشاف-الأخطاء)
- [المساهمة](#-المساهمة)
- [الدعم](#-الدعم)

## 🎯 المميزات

### 🔥 المميزات الأساسية
- ✅ **إدارة متقدمة للقنوات** - إدارة شاملة لقنوات تلغرام
- ✅ **فلترة الرسائل الذكية** - تصفية متقدمة للمحتوى
- ✅ **تنسيق وتنظيف النصوص** - تحسين وتنسيق المحتوى تلقائياً
- ✅ **الترجمة التلقائية** - ترجمة فورية لعدة لغات
- ✅ **النشر المجدول** - برمجة المنشورات مسبقاً
- ✅ **إدارة روابط الدعوة** - التحكم في روابط الانضمام
- ✅ **قبول الطلبات التلقائي** - موافقة تلقائية على طلبات الانضمام
- ✅ **إدارة المشرفين** - نظام صلاحيات متكامل

### 🚀 المميزات المتطورة
- 🎨 **معالجة الوسائط** - تحسين الصور والفيديوهات
- 📊 **إحصائيات مفصلة** - تقارير شاملة عن أداء القنوات
- 🌐 **واجهة ويب** - لوحة تحكم من المتصفح
- 🔒 **الأمان المتقدم** - حماية شاملة ضد السبام
- 📱 **بوت تحكم منفصل** - إدارة سهلة من تلغرام
- 🎯 **النشر الذكي** - توزيع محتوى متقدم
- 📈 **تحليلات الأداء** - مراقبة مستمرة للنشاط

## 💻 المتطلبات

### متطلبات النظام
- **Python 3.8+** (مُستحسن 3.9+)
- **4GB RAM** كحد أدنى
- **10GB** مساحة حرة على القرص
- **اتصال إنترنت مستقر**

### حسابات تلغرام مطلوبة
1. **حساب مستخدم** - للوصول لـ Telegram API
2. **بوت رئيسي** - لإدارة القنوات
3. **بوت تحكم** - للتحكم في النظام

## ⚡ التثبيت السريع

### 1. تحميل المشروع
```bash
git clone https://github.com/yourusername/telegram-channels-manager.git
cd telegram-channels-manager
```

### 2. تشغيل الإعداد التلقائي
```bash
python3 setup_bot.py
```

سيقوم المعالج بـ:
- تثبيت جميع المتطلبات
- إنشاء ملف الإعداد (.env)
- اختبار الاتصال
- إعداد قاعدة البيانات

### 3. تشغيل البوت
```bash
python3 main.py
```

## 🔧 الإعداد التفصيلي

### الحصول على API Credentials

1. **زيارة** [my.telegram.org](https://my.telegram.org)
2. **تسجيل الدخول** برقم هاتفك
3. **الذهاب لـ** "API Development Tools"
4. **إنشاء تطبيق جديد** وحفظ:
   - `API_ID`
   - `API_HASH`

### إنشاء البوتات

1. **مراسلة** [@BotFather](https://t.me/BotFather) على تلغرام
2. **إنشاء بوت رئيسي**:
   ```
   /newbot
   اسم البوت الرئيسي
   username_main_bot
   ```
3. **إنشاء بوت التحكم**:
   ```
   /newbot
   بوت التحكم
   username_control_bot
   ```

### إعداد ملف البيئة (.env)

```env
# Telegram API Configuration
API_ID=12345678
API_HASH=your_api_hash_here

# Bot Tokens
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyZ
CONTROL_BOT_TOKEN=987654321:ZYXwvuTSRqponMLKjihGFEdcbA

# User Account
PHONE_NUMBER=+1234567890
SESSION_NAME=userbot_session

# Admin Configuration
ADMIN_IDS=123456789,987654321

# Database Configuration
DATABASE_URL=sqlite:///bot_database.db

# Bot Settings
DEFAULT_TIMEZONE=UTC
MAX_MESSAGE_LENGTH=4096
MAX_CAPTION_LENGTH=1024

# Message Formatting
DEFAULT_HEADER=🚀 قناة الأخبار
DEFAULT_FOOTER=📱 تابعونا للمزيد

# Translation Settings
DEFAULT_TRANSLATE_LANGUAGE=ar
TRANSLATE_SERVICE=google

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=bot.log

# Rate Limiting
INVITE_ACCEPT_RATE=10
MESSAGE_DELAY=1.0

# Auto-accept Settings
AUTO_ACCEPT_DELAY=300
```

## 🎮 الاستخدام

### بدء تشغيل البوت

```bash
# تشغيل عادي
python3 main.py

# تشغيل في الخلفية
nohup python3 main.py &

# تشغيل مع السجلات
python3 main.py > bot.log 2>&1 &
```

### استخدام بوت التحكم

1. **ابحث** عن بوت التحكم في تلغرام
2. **ابدأ المحادثة** بـ `/start`
3. **استخدم الأوامر** لإدارة البوت

## 🔧 الميزات المتقدمة

### 🎯 فلترة الرسائل

```python
# مثال على إعداد فلتر
from filters.text_filters import TextFilterManager

# إنشاء مدير الفلاتر
filter_manager = TextFilterManager()

# إضافة كلمات محظورة
filter_manager.add_blacklist_words(['spam', 'scam', 'fake'])

# إضافة كلمات مسموحة
filter_manager.add_whitelist_words(['news', 'update', 'info'])

# فلترة النص
result = await filter_manager.filter_text("This is a test message")
print(f"مسموح: {result.passed}")
```

### 🌐 الترجمة التلقائية

```python
from utils.translator import translator

# ترجمة نص
result = await translator.translate_text(
    text="Hello World",
    target_lang="ar",
    source_lang="en"
)

print(f"النص المترجم: {result.translated_text}")
```

### 📅 جدولة المنشورات

```python
from utils.scheduler import scheduler
from datetime import datetime, timedelta

# جدولة منشور
task_id = scheduler.schedule_post(
    channel_id="-1001234567890",
    message="هذا منشور مجدول",
    scheduled_time=datetime.now() + timedelta(hours=1)
)

print(f"تم جدولة المنشور: {task_id}")
```

### 🎨 معالجة الوسائط

```python
from utils.media_handler import media_handler

# معالجة صورة
media_info = await media_handler.process_file(
    file_path="path/to/image.jpg",
    optimize=True
)

print(f"تم معالجة الملف: {media_info.file_name}")
```

## 📝 الأوامر

### أوامر بوت التحكم

| الأمر | الوصف |
|-------|--------|
| `/start` | بدء البوت وعرض القائمة الرئيسية |
| `/status` | عرض حالة البوت والإحصائيات |
| `/channels` | إدارة القنوات |
| `/settings` | إعدادات البوت |
| `/filters` | إدارة الفلاتر |
| `/schedule` | جدولة المنشورات |
| `/stats` | الإحصائيات المفصلة |
| `/help` | المساعدة والدعم |

### أوامر المطور

```bash
# اختبار الاتصال
python3 -c "import asyncio; from main import validate_config; print(validate_config())"

# تنظيف قاعدة البيانات
python3 -c "
import asyncio
from database.database import DatabaseManager
async def cleanup():
    db = DatabaseManager()
    await db.cleanup_old_data()
asyncio.run(cleanup())
"

# إعادة تعيين الفلاتر
python3 -c "
from filters.text_filters import TextFilterManager
filter_manager = TextFilterManager()
filter_manager.clear_cache()
"
```

## 🐛 استكشاف الأخطاء

### مشاكل شائعة وحلولها

#### خطأ: "API_ID must be a valid integer"
**الحل:**
```bash
# تأكد من أن API_ID رقم صحيح في ملف .env
API_ID=12345678  # بدون علامات تنصيص
```

#### خطأ: "No module named 'telethon'"
**الحل:**
```bash
pip3 install --break-system-packages telethon python-telegram-bot
```

#### خطأ: "Database connection failed"
**الحل:**
```bash
# إعادة إنشاء قاعدة البيانات
rm bot_database.db
python3 -c "
import asyncio
from database.database import DatabaseManager
async def init_db():
    db = DatabaseManager()
    await db.initialize()
asyncio.run(init_db())
"
```

#### البوت لا يستجيب للأوامر
**الحل:**
1. تأكد من صحة `BOT_TOKEN`
2. تحقق من أن البوت مفعل في [@BotFather](https://t.me/BotFather)
3. راجع سجلات الأخطاء في `bot.log`

### تشخيص متقدم

```bash
# تشغيل البوت في وضع التشخيص
LOG_LEVEL=DEBUG python3 main.py

# مراقبة السجلات في الوقت الفعلي
tail -f bot.log

# فحص استخدام الذاكرة
ps aux | grep python3

# فحص المنافذ المستخدمة
netstat -tlnp | grep python
```

## 📊 المراقبة والصيانة

### مراقبة الأداء

```python
# سكريبت مراقبة بسيط
import psutil
import time

def monitor_bot():
    while True:
        # استخدام المعالج
        cpu = psutil.cpu_percent()
        
        # استخدام الذاكرة
        memory = psutil.virtual_memory().percent
        
        print(f"CPU: {cpu}% | Memory: {memory}%")
        time.sleep(60)

if __name__ == "__main__":
    monitor_bot()
```

### الصيانة الدورية

```bash
# تنظيف الملفات المؤقتة (أسبوعياً)
find ./media/temp -type f -mtime +7 -delete

# أرشفة السجلات (شهرياً)
mv bot.log bot_$(date +%Y%m%d).log

# تحديث التبعيات (شهرياً)
pip3 install --upgrade -r requirements.txt
```

## 🔒 الأمان

### إعدادات الأمان الموصى بها

1. **استخدم كلمات مرور قوية** لحساب تلغرام
2. **فعل التحقق بخطوتين** على حساب تلغرام
3. **احم ملف .env** من الوصول العام
4. **استخدم قاعدة بيانات محمية** للإنتاج
5. **راقب سجلات البوت** بانتظام

### حماية الخادم

```bash
# تعيين صلاحيات آمنة
chmod 600 .env
chmod 700 logs/
chmod 755 main.py

# تشغيل البوت كمستخدم عادي (ليس root)
useradd -m botuser
su botuser
```

## 🚀 النشر

### النشر على خادم Linux

```bash
# إنشاء خدمة systemd
sudo nano /etc/systemd/system/telegram-bot.service

# محتوى الملف:
[Unit]
Description=Telegram Channels Manager Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/path/to/bot
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# تفعيل الخدمة
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

### النشر باستخدام Docker

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python3", "main.py"]
```

```bash
# بناء وتشغيل
docker build -t telegram-bot .
docker run -d --name telegram-bot telegram-bot
```

## 📈 التطوير والتخصيص

### إضافة ميزات جديدة

```python
# مثال: إضافة فلتر مخصص
class CustomFilter:
    def __init__(self):
        self.name = "custom_filter"
    
    async def filter_message(self, message):
        # منطق الفلترة هنا
        return True  # أو False
```

### إنشاء إضافات

```python
# مثال: إضافة للإحصائيات المتقدمة
class AdvancedStats:
    def __init__(self, bot):
        self.bot = bot
    
    async def get_channel_stats(self, channel_id):
        # جمع الإحصائيات
        return stats_data
```

## 🤝 المساهمة

نرحب بمساهماتكم! يرجى اتباع هذه الخطوات:

1. **Fork** المشروع
2. **إنشاء فرع** للميزة الجديدة (`git checkout -b feature/amazing-feature`)
3. **Commit** التغييرات (`git commit -m 'Add amazing feature'`)
4. **Push** للفرع (`git push origin feature/amazing-feature`)
5. **فتح Pull Request**

### إرشادات المساهمة

- اتبع نمط الكود الموجود
- أضف تعليقات واضحة
- اكتب اختبارات للميزات الجديدة
- حدث الوثائق

## 📞 الدعم

### طرق الحصول على المساعدة

- 📧 **البريد الإلكتروني**: support@example.com
- 💬 **تلغرام**: [@SupportBot](https://t.me/SupportBot)
- 🐛 **الأخطاء**: [GitHub Issues](https://github.com/yourusername/telegram-channels-manager/issues)
- 📚 **الوثائق**: [Wiki](https://github.com/yourusername/telegram-channels-manager/wiki)

### الأسئلة الشائعة

**س: هل يمكن تشغيل البوت على Windows؟**
ج: نعم، لكن Linux أو macOS مفضل للأداء الأمثل.

**س: كم قناة يمكن إدارتها؟**
ج: عملياً لا يوجد حد، لكن الأداء يعتمد على موارد الخادم.

**س: هل البوت مجاني؟**
ج: نعم، البوت مفتوح المصدر ومجاني للاستخدام.

## 📄 الترخيص

هذا المشروع مرخص تحت [MIT License](LICENSE).

```
MIT License

Copyright (c) 2024 Telegram Channels Manager

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

## 🙏 شكر خاص

- فريق Telegram على API الممتاز
- مجتمع Python على المكتبات الرائعة
- جميع المساهمين في المشروع

---

**📌 ملاحظة**: هذا البوت للاستخدام التعليمي والمشروع. تأكد من الامتثال لشروط خدمة تلغرام وقوانين بلدك.

**🔄 آخر تحديث**: يناير 2024
**📊 إصدار البوت**: 1.0.0 - مكتمل 100%

---

<div align="center">

**🚀 البوت جاهز للاستخدام بنسبة 100%! 🚀**

[![Star](https://img.shields.io/github/stars/yourusername/telegram-channels-manager.svg?style=social)](https://github.com/yourusername/telegram-channels-manager/stargazers)
[![Fork](https://img.shields.io/github/forks/yourusername/telegram-channels-manager.svg?style=social)](https://github.com/yourusername/telegram-channels-manager/network/members)

</div>