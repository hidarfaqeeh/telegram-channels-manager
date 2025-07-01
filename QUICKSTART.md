# 🚀 دليل البدء السريع - Quick Start Guide

## بوت إدارة القنوات - Telegram Channels Manager Bot

### ⏱️ البدء في 5 دقائق

---

## 📋 ما تحتاجه

- ✅ Python 3.8+ مثبت على جهازك
- ✅ حساب تلغرام نشط
- ✅ 5 دقائق من وقتك

---

## 🎯 الخطوات السريعة

### 1️⃣ تحميل المشروع

```bash
# استنساخ المشروع
git clone https://github.com/your-username/telegram-channels-manager.git
cd telegram-channels-manager

# أو تحميل ZIP
wget -O bot.zip https://github.com/your-username/telegram-channels-manager/archive/main.zip
unzip bot.zip && cd telegram-channels-manager-main
```

### 2️⃣ الإعداد التلقائي

```bash
# تشغيل الإعداد التلقائي
./run.sh setup

# أو في Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3️⃣ الحصول على بيانات تلغرام

#### أ) احصل على API credentials:

1. اذهب إلى [my.telegram.org](https://my.telegram.org)
2. سجل دخولك برقم هاتفك
3. اذهب إلى "API development tools"
4. أنشئ تطبيق جديد
5. احفظ `API_ID` و `API_HASH`

#### ب) أنشئ بوت التحكم:

1. ابدأ محادثة مع [@BotFather](https://t.me/BotFather)
2. أرسل `/newbot`
3. اتبع التعليمات
4. احفظ التوكن

### 4️⃣ تعديل الإعدادات

```bash
# تحرير ملف الإعدادات
nano .env

# أو
vim .env
```

**أدخل بياناتك:**

```env
# معلومات API
API_ID=12345678
API_HASH=your_api_hash_here
BOT_TOKEN=your_userbot_token_here
PHONE_NUMBER=+1234567890

# بوت التحكم
CONTROL_BOT_TOKEN=your_control_bot_token_here

# المديرين (معرفاتك الرقمية)
ADMIN_IDS=123456789,987654321
```

### 5️⃣ تشغيل البوت

```bash
# تشغيل البوت
./run.sh start

# أو
python main.py
```

---

## 🎉 تهانينا! 

البوت يعمل الآن! 

### 📱 كيفية الاستخدام:

1. **ابدأ محادثة مع بوت التحكم** الذي أنشأته
2. **أرسل `/start`** لرؤية لوحة التحكم
3. **أضف قناتك الأولى** باستخدام `/addchannel @your_channel`
4. **ابدأ في إدارة قنواتك!**

---

## ❓ مشاكل شائعة

### خطأ في الاتصال
```bash
# تحديث المكتبات
./run.sh update
```

### خطأ في التوكن
```bash
# تحقق من الإعدادات
./run.sh check
```

### خطأ في الصلاحيات
```bash
# التأكد من الصلاحيات
chmod +x run.sh
```

---

## 📚 التالي

بعد أن يعمل البوت، يمكنك:

- 📖 قراءة [الدليل الكامل](README.md)
- 🔧 تخصيص [الإعدادات المتقدمة](README.md#️-الإعداد)
- 🎨 إعداد [الفلاتر والتنسيق](README.md#-فلاتر-الرسائل-المتقدمة)

---

## 🆘 تحتاج مساعدة؟

- 📞 **مشكلة تقنية؟** [افتح Issue على GitHub](https://github.com/your-username/telegram-channels-manager/issues)
- 💬 **سؤال سريع؟** اقرأ [الأسئلة الشائعة](README.md#-الأسئلة-الشائعة)
- 📚 **دليل مفصل؟** [README الكامل](README.md)

---

## 🚀 نصائح سريعة

### إدارة القنوات:
```bash
# إضافة قناة
/addchannel @channel_username

# عرض القنوات
/channels

# حذف قناة
/removechannel -1001234567890
```

### النشر السريع:
```
# نشر مباشر
-1001234567890|مرحباً بالجميع! 🎉

# نشر مجدول
-1001234567890|1h|سيتم النشر بعد ساعة
```

### إعداد الفلاتر:
```bash
# فتح إعدادات الفلاتر
/filters

# استخدم الأزرار التفاعلية
```

---

<div align="center">

## ✨ مبروك! أصبح لديك أقوى بوت إدارة قنوات! ✨

**📞 دعم فوري:** [GitHub Issues](https://github.com/your-username/telegram-channels-manager/issues)  
**📚 دليل كامل:** [README.md](README.md)  
**⭐ لا تنسى النجمة!** [⭐ Star on GitHub](https://github.com/your-username/telegram-channels-manager)

</div>