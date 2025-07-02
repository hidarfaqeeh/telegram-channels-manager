# دليل تشغيل بوت إدارة القنوات باستخدام Docker 🐳

## نظرة عامة

هذا الدليل يوضح كيفية تنصيب وتشغيل بوت إدارة القنوات باستخدام Docker، مما يوفر:

- ✅ تنصيب سهل ومعزول
- ✅ إدارة مبسطة للمتطلبات
- ✅ قابلية النقل بين الأنظمة
- ✅ مراقبة وإدارة احترافية
- ✅ نسخ احتياطية آمنة

---

## المتطلبات الأساسية 📋

### 1. تثبيت Docker
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# أو باستخدام package manager
sudo apt-get update
sudo apt-get install docker.io docker-compose
```

### 2. تحقق من التثبيت
```bash
docker --version
docker-compose --version
```

---

## التنصيب السريع ⚡

### 1. تحضير الملفات
```bash
# تأكد من وجود ملف .env
cp .env.example .env

# حرر الإعدادات (مطلوب!)
nano .env
```

### 2. التشغيل السريع
```bash
# الطريقة الأسهل - إعداد تفاعلي
./docker-run.sh setup

# أو التشغيل المباشر
./docker-run.sh build
./docker-run.sh start
```

---

## طرق التشغيل المختلفة 🚀

### 1. البوت فقط (الأساسي)
```bash
./docker-run.sh start
```

### 2. البوت مع المراقبة
```bash
./docker-run.sh monitoring
# يشمل: Prometheus + Grafana
# الوصول: http://localhost:3000
```

### 3. البوت مع واجهة الويب
```bash
./docker-run.sh web
# يشمل: Nginx proxy
# الوصول: http://localhost
```

### 4. جميع الخدمات
```bash
./docker-run.sh full
# يشمل: البوت + المراقبة + واجهة الويب
```

---

## أوامر الإدارة 🛠️

### إدارة أساسية
```bash
# بناء الـ Image
./docker-run.sh build

# تشغيل الخدمات
./docker-run.sh start

# إيقاف الخدمات
./docker-run.sh stop

# إعادة التشغيل
./docker-run.sh restart

# حالة الخدمات
./docker-run.sh status
```

### عرض السجلات
```bash
# آخر 100 رسالة
./docker-run.sh logs

# متابعة مباشرة
./docker-run.sh logs --follow
```

### إدارة متقدمة
```bash
# فتح shell في الحاوية
./docker-run.sh shell

# فحص صحة الخدمات
./docker-run.sh health

# تنظيف الحاويات والبيانات
./docker-run.sh clean --force
```

---

## الإعداد التفصيلي ⚙️

### 1. ملف .env
```env
# بيانات Telegram API (مطلوب)
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
PHONE_NUMBER=your_phone_number

# بوت التحكم
CONTROL_BOT_TOKEN=your_control_bot_token

# المشرفين
ADMIN_IDS=123456789,987654321

# إعدادات قاعدة البيانات
DATABASE_URL=sqlite:///data/bot.db

# Redis (للتخزين المؤقت)
REDIS_URL=redis://redis:6379/0

# إعدادات أخرى
LOG_LEVEL=INFO
TIMEZONE=Asia/Riyadh
```

### 2. تخصيص الموارد
يمكنك تعديل `docker-compose.yml` لتخصيص:

```yaml
deploy:
  resources:
    limits:
      memory: 1G        # حد الذاكرة
      cpus: '1.0'       # حد المعالج
    reservations:
      memory: 512M      # الحد الأدنى
      cpus: '0.5'
```

---

## المراقبة والإحصائيات 📊

### 1. Prometheus (مراقبة)
- **الرابط:** http://localhost:9090
- **الوصف:** جمع وتخزين المقاييس
- **المقاييس المتاحة:**
  - استخدام الذاكرة والمعالج
  - عدد الرسائل المعالجة
  - أداء قاعدة البيانات
  - إحصائيات الترجمة

### 2. Grafana (لوحة المراقبة)
- **الرابط:** http://localhost:3000
- **المستخدم:** admin
- **كلمة المرور:** admin123
- **الميزات:**
  - لوحات مراقبة بصرية
  - تنبيهات تلقائية
  - تقارير مفصلة
  - رسوم بيانية تفاعلية

---

## إدارة البيانات 💾

### 1. النسخ الاحتياطية
```bash
# نسخ احتياطي لقاعدة البيانات
docker exec telegram-channels-bot sqlite3 /app/data/bot.db ".backup /app/data/backup.db"

# نسخ احتياطي للملفات
docker cp telegram-channels-bot:/app/data ./backup/

# نسخ احتياطي للجلسات
docker cp telegram-channels-bot:/app/sessions ./backup/
```

### 2. استرداد البيانات
```bash
# استرداد قاعدة البيانات
docker cp backup.db telegram-channels-bot:/app/data/

# استرداد الملفات
docker cp ./backup/data telegram-channels-bot:/app/
```

### 3. Volumes المستخدمة
```
telegram-bot-data      # قاعدة البيانات والملفات
telegram-bot-logs      # ملفات السجلات
telegram-bot-sessions  # جلسات Telegram
telegram-bot-media     # الوسائط المرفوعة
telegram-bot-redis     # بيانات التخزين المؤقت
```

---

## استكشاف الأخطاء 🔧

### 1. مشاكل شائعة

#### البوت لا يبدأ
```bash
# فحص السجلات
./docker-run.sh logs

# فحص الإعدادات
docker exec telegram-channels-bot cat /app/.env

# فحص الصحة
./docker-run.sh health
```

#### مشاكل الذاكرة
```bash
# فحص استخدام الموارد
docker stats

# زيادة حد الذاكرة في docker-compose.yml
```

#### مشاكل قاعدة البيانات
```bash
# فتح shell والفحص
./docker-run.sh shell
sqlite3 /app/data/bot.db ".tables"
```

### 2. أوامر التشخيص
```bash
# فحص شامل للنظام
docker system df
docker system info

# فحص الشبكات
docker network ls

# فحص الـ volumes
docker volume ls
```

---

## الأمان 🔒

### 1. إعدادات الأمان
- ✅ تشغيل بمستخدم غير root
- ✅ فصل الشبكات
- ✅ تشفير البيانات الحساسة
- ✅ تحديد حدود الموارد

### 2. نصائح الأمان
```bash
# تغيير كلمات المرور الافتراضية
# في docker-compose.yml غير:
GF_SECURITY_ADMIN_PASSWORD=your_secure_password

# حماية الملفات الحساسة
chmod 600 .env

# تحديث منتظم للـ images
docker-compose pull
./docker-run.sh build --no-cache
```

---

## التحديث 🔄

### 1. تحديث البوت
```bash
# إيقاف الخدمات
./docker-run.sh stop

# سحب آخر التحديثات
git pull

# بناء image جديد
./docker-run.sh build --no-cache

# إعادة التشغيل
./docker-run.sh start
```

### 2. تحديث التبعيات
```bash
# تحديث Docker images
docker-compose pull

# تحديث Python packages
# (سيحدث تلقائياً مع build جديد)
```

---

## الاستخدام المتقدم 🎯

### 1. Environment مختلفة
```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

### 2. Scale الخدمات
```bash
# تشغيل عدة instances
docker-compose up --scale telegram-bot=3
```

### 3. تخصيص الشبكة
```bash
# استخدام شبكة خارجية
docker network create telegram-net
# ثم تعديل docker-compose.yml
```

---

## الدعم والمساعدة 🆘

### 1. فحص الحالة الكاملة
```bash
./docker-run.sh health
```

### 2. جمع معلومات التشخيص
```bash
# معلومات النظام
docker system info > system-info.txt

# سجلات مفصلة
./docker-run.sh logs > bot-logs.txt

# حالة الخدمات
./docker-run.sh status > services-status.txt
```

### 3. روابط مفيدة
- 📖 [Docker Documentation](https://docs.docker.com/)
- 🐙 [Docker Hub](https://hub.docker.com/)
- 📊 [Grafana Dashboards](https://grafana.com/dashboards/)
- 🔍 [Prometheus Metrics](https://prometheus.io/docs/)

---

## أمثلة للاستخدام 📝

### بداية سريعة كاملة
```bash
# 1. استنساخ المشروع
git clone <repository>
cd telegram-channels-bot

# 2. إعداد البيئة
cp .env.example .env
nano .env  # أدخل بياناتك

# 3. تشغيل تفاعلي
./docker-run.sh setup

# 4. فحص الحالة
./docker-run.sh health
```

### مراقبة مستمرة
```bash
# تشغيل مع المراقبة
./docker-run.sh monitoring

# فتح المراقبة في المتصفح
open http://localhost:3000

# متابعة السجلات
./docker-run.sh logs --follow
```

---

**🎉 تهانينا! البوت الآن يعمل بنجاح على Docker**

للمساعدة أو الدعم، يرجى مراجعة السجلات أو استخدام أوامر التشخيص المذكورة أعلاه.