from flask import Flask, request
import datetime
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h2>🌐 خادم جمع البيانات - تجربة تعليمية</h2>
    <p>هذا الخادم يعمل على Render</p>
    <p>للاختبار، أضف <code>/collect</code> إلى نهاية الرابط</p>
    <hr>
    <p>📱 افتح هذا الرابط من هاتفك:</p>
    <code>https://[اسم-تطبيقك].onrender.com/collect</code>
    '''

@app.route('/collect')
def collect():
    # استخراج بيانات الطلب
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
    
    # تسجيل البيانات في ملف (في بيئة Render)
    log_entry = f"""
    ═══════════════════════════════════════════
    📅 الوقت: {datetime.datetime.now()}
    🌐 IP المصدر: {client_ip}
    📱 نظام التشغيل: {os_info}
    🌍 اللغة: {accept_lang}
    🔧 الترميز: {accept_encoding}
    🔗 الصفحة السابقة: {referer}
    📝 User-Agent كامل:
       {user_agent}
    ═══════════════════════════════════════════
    """
    
    # حفظ في ملف (سيظهر في لوحة تحكم Render)
    with open('log.txt', 'a', encoding='utf-8') as f:
        f.write(log_entry)
    
    # عرض النتيجة للمستخدم
    return f'''
    <html>
    <head>
        <title>تم التسجيل</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Arial; padding: 20px; background: #f0f0f0;">
        <div style="max-width: 500px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h2 style="color: #2c3e50;">✅ تم تسجيل زيارتك</h2>
            <p>تم تسجيل بيانات جهازك في الخادم</p>
            <hr>
            <h4>📊 البيانات التي تم جمعها:</h4>
            <ul style="list-style: none; padding: 0;">
                <li style="padding: 8px; background: #ecf0f1; margin: 5px 0; border-radius: 5px;">
                    <strong>🌐 IP:</strong> {client_ip}
                </li>
                <li style="padding: 8px; background: #ecf0f1; margin: 5px 0; border-radius: 5px;">
                    <strong>📱 نظام التشغيل:</strong> {os_info}
                </li>
                <li style="padding: 8px; background: #ecf0f1; margin: 5px 0; border-radius: 5px;">
                    <strong>🌍 اللغة:</strong> {accept_lang}
                </li>
            </ul>
            <hr>
            <p style="font-size: 12px; color: #7f8c8d;">🔒 هذه تجربة تعليمية على خادم آمن</p>
            <p style="font-size: 12px; color: #7f8c8d;">📅 الوقت: {datetime.datetime.now()}</p>
        </div>
    </body>
    </html>
    '''

@app.route('/view-logs')
def view_logs():
    """مسار لعرض السجلات (اختياري)"""
    try:
        with open('log.txt', 'r', encoding='utf-8') as f:
            logs = f.read()
        return f'<pre style="white-space: pre-wrap; padding: 20px; background: #1e1e1e; color: #d4d4d4; min-height: 100vh;">{logs}</pre>'
    except:
        return "لا توجد سجلات حتى الآن"

if __name__ == '__main__':
    # Render يوفر المنفذ تلقائياً عبر PORT
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)