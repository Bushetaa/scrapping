# تعليمات تشغيل بوت مراقبة وسائل التواصل الاجتماعي

## الوضع الحالي ✅

### ما يعمل:
- **Discord Bot**: متصل بنجاح (media#2523)
- **Web Dashboard**: متاح على http://localhost:5000
- **نظام المراقبة**: يعمل ويفحص كل 5 دقائق
- **قاعدة البيانات**: تحفظ البيانات بنجاح

### نتائج الفحص الأخير:
- **LinkedIn**: ✅ يعمل (معرف البوست: db540cc595)
- **TikTok**: ✅ يعمل (معرف البوست: c0a06119b2)  
- **X (Twitter)**: ✅ يعمل (معرف البوست: 4fe0244f8a)
- **Facebook**: ❌ محظور (خطأ 400)

## المطلوب لاكتمال الإعداد:

### 1. إعداد Discord Channel ID
**المشكلة**: البوت لا يرسل إشعارات لأن رقم القناة غير صحيح

**الحل**:
1. اذهب إلى Discord
2. انقر بالزر الأيمن على القناة المطلوبة
3. اختر "Copy Channel ID"
4. ضع هذا الكود في terminal:
```bash
export DISCORD_CHANNEL_ID="your_channel_id_here"
```

### 2. اختبر البوست الجديد
بعد إعداد Channel ID، ضع بوست جديد على LinkedIn وانتظر 5 دقائق أو شغل الفحص اليدوي:

```bash
python3 -c "
from scraper_backup import SimpleScraper
from database import update_post_status, get_last_post

scraper = SimpleScraper()
last_post = get_last_post('LinkedIn')
current_post = scraper.scrape_platform('LinkedIn', 'https://www.linkedin.com/company/solidpointai/')

is_new = last_post is None or (last_post['post_id'] != current_post['post_id'])
print(f'بوست جديد: {is_new}')
print(f'معرف البوست الحالي: {current_post[\"post_id\"]}')
print(f'معرف البوست السابق: {last_post[\"post_id\"] if last_post else \"لا يوجد\"}')

update_post_status('LinkedIn', 'https://www.linkedin.com/company/solidpointai/', current_post, is_new=is_new)
"
```

## الملفات المهمة:

### config.py
- **DISCORD_TOKEN**: ✅ معرف صحيح  
- **DISCORD_CHANNEL_ID**: ❌ يحتاج إعداد
- **SOCIAL_MEDIA_URLS**: ✅ الروابط صحيحة

### scraper_backup.py  
- **النظام البديل**: يعمل بنجاح
- **يفحص**: LinkedIn, TikTok, X (Twitter)
- **Facebook**: محظور (يحتاج VPN أو طريقة أخرى)

### الداشبورد
- **الرابط**: http://localhost:5000
- **يعرض**: حالة كل منصة في الوقت الفعلي
- **يحدث**: كل 10 ثوان تلقائياً

## استكشاف الأخطاء:

### إذا لم يكتشف البوست الجديد:
1. تأكد أن البوست public وليس private
2. انتظر 5 دقائق للفحص التالي
3. أو شغل الفحص اليدوي (الكود أعلاه)

### إذا لم تأت إشعارات Discord:
1. تأكد من Discord Channel ID
2. تأكد أن البوت له صلاحية الكتابة في القناة
3. تحقق من logs في terminal

## الخلاصة:
النظام يعمل بنجاح ويكتشف التغييرات، فقط يحتاج إعداد Discord Channel ID لإرسال الإشعارات.