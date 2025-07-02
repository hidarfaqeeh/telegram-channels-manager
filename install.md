# دليل تثبيت وإعداد بوت إدارة القنوات

## 📋 المتطلبات

- Python 3.8 أو أحدث
- حساب تليجرام
- API credentials من [my.telegram.org](https://my.telegram.org)
- بوت تليجرام من [@BotFather](https://t.me/BotFather)

## 🚀 التثبيت السريع

### 1. تحميل المشروع
```bash
git clone <repository-url>
cd telegram-channels-manager
```

### 2. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 3. إعداد ملف التكوين
```bash
cp .env.example .env
```

### 4. تحرير ملف .env
افتح ملف `.env` وأدخل بياناتك:

```env
# Telegram API Credentials
API_ID=12345678
API_HASH=your_api_hash_here

# Bot Tokens
BOT_TOKEN=your_bot_token_here
CONTROL_BOT_TOKEN=your_control_bot_token_here

# User Account
PHONE_NUMBER=+1234567890

# Admin IDs
ADMIN_IDS=123456789,987654321
```

### 5. تشغيل البوت
```bash
python start_bot.py
```

## 📱 الحصول على البيانات المطلوبة

### API Credentials
1. اذهب إلى [my.telegram.org](https://my.telegram.org)
2. سجل دخولك برقم هاتفك
3. اذهب إلى "API Development Tools"
4. أنشئ تطبيق جديد
5. احفظ `API_ID` و `API_HASH`

### Bot Token
1. تحدث مع [@BotFather](https://t.me/BotFather)
2. أرسل `/newbot`
3. اختر اسماً لبوتك
4. اختر معرفاً (username) لبوتك
5. احفظ الـ Token المُعطى

### Control Bot Token
- كرر نفس خطوات إنشاء البوت لبوت التحكم
- هذا البوت سيُستخدم للتحكم في البوت الرئيسي

### Admin IDs
1. أرسل رسالة لـ [@userinfobot](https://t.me/userinfobot)
2. احفظ الـ User ID الخاص بك
3. يمكنك إضافة عدة معرفات مفصولة بفواصل

## ⚙️ الإعداد المتقدم

### إعداد قاعدة البيانات
البوت يستخدم SQLite افتراضياً. لاستخدام قاعدة بيانات أخرى:

```env
DATABASE_URL=postgresql://user:password@localhost/dbname
# أو
DATABASE_URL=mysql://user:password@localhost/dbname
```

### إعدادات إضافية
```env
# Logging
LOG_LEVEL=INFO
LOG_FILE=bot.log

# Message Settings
MAX_MESSAGE_LENGTH=4096
DEFAULT_TRANSLATE_LANGUAGE=ar

# Rate Limiting
MESSAGE_DELAY=1.0
INVITE_ACCEPT_RATE=10
```

## 🔧 استكشاف الأخطاء

### خطأ في الاتصال
```bash
# تأكد من صحة API credentials
python -c "import config; print(f'API_ID: {config.API_ID}, API_HASH: {config.API_HASH[:10]}...')"
```

### خطأ في قاعدة البيانات
```bash
# إعادة تهيئة قاعدة البيانات
python setup_bot.py
```

### مشاكل في الأذونات
- تأكد من أن البوت مشرف في القنوات
- تأكد من أن User ID صحيح في ADMIN_IDS

## 📚 الاستخدام الأساسي

### إضافة قناة
```
/addchannel @channel_username
```

### عرض القنوات
```
/channels
```

### نشر منشور
```
/post
```

### جدولة منشور
```
/schedule
```

## 🛡️ الأمان

- لا تشارك ملف `.env` أبداً
- احتفظ بنسخة احتياطية من قاعدة البيانات
- استخدم أذونات محدودة للبوت
- راجع سجلات البوت بانتظام

## 🆘 الحصول على المساعدة

إذا واجهت أي مشاكل:

1. تحقق من ملف `bot.log`
2. تأكد من صحة التكوين
3. تحقق من الأذونات
4. راجع الوثائق