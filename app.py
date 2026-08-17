from flask import Flask, request, jsonify
import datetime
import os
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h2>🌐 خادم جمع البيانات المتقدم - تجربة تعليمية</h2>
    <p>هذا الخادم يجمع بيانات متعددة عن الزوار</p>
    <p>للاختبار، أضف <code>/collect</code> إلى نهاية الرابط</p>
    <hr>
    <p>📱 افتح هذا الرابط من هاتفك:</p>
    <code>https://flask-log-collector.onrender.com/collect</code>
    '''

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
    
    # صفحة HTML مع JavaScript لجمع بيانات إضافية
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>جمع البيانات - تجربة تعليمية</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Arial, sans-serif;
                padding: 20px;
                background: #f0f4f8;
                margin: 0;
            }}
            .container {{
                max-width: 600px;
                margin: auto;
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 2px 15px rgba(0,0,0,0.1);
            }}
            h2 {{ color: #2c3e50; }}
            h4 {{ color: #34495e; margin-bottom: 5px; }}
            ul {{
                list-style: none;
                padding: 0;
            }}
            li {{
                padding: 8px 12px;
                background: #ecf0f1;
                margin: 5px 0;
                border-radius: 5px;
                font-size: 14px;
            }}
            .badge {{
                display: inline-block;
                background: #3498db;
                color: white;
                padding: 2px 10px;
                border-radius: 10px;
                font-size: 12px;
            }}
            hr {{ border: 1px solid #ecf0f1; }}
            .footer {{
                font-size: 12px;
                color: #7f8c8d;
                text-align: center;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>✅ تم تسجيل زيارتك</h2>
            <p>تم جمع البيانات التالية من جهازك:</p>
            <hr>
            
            <h4>🌐 البيانات الأساسية</h4>
            <ul>
                <li><strong>IP:</strong> {client_ip}</li>
                <li><strong>نظام التشغيل:</strong> {os_info}</li>
                <li><strong>الموقع التقريبي:</strong> {location}</li>
                <li><strong>مزود الخدمة:</strong> {isp}</li>
            </ul>
            
            <h4>🖥️ بيانات المتصفح الإضافية</h4>
            <div id="browser-data">
                <p style="color: #7f8c8d;">جاري جمع بيانات المتصفح...</p>
            </div>
            
            <h4>📍 الموقع الدقيق (GPS)</h4>
            <div id="gps-data">
                <p style="color: #7f8c8d;">جاري طلب الموقع...</p>
            </div>
            
            <hr>
            <div class="footer">
                🔒 هذه تجربة تعليمية على خادم آمن<br>
                يتم جمع البيانات لأغراض تعليمية فقط
            </div>
        </div>
        
        <script>
            // جمع بيانات المتصفح
            function collectBrowserData() {{
                const data = {{
                    screenWidth: window.screen.width,
                    screenHeight: window.screen.height,
                    colorDepth: window.screen.colorDepth,
                    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                    language: navigator.language,
                    platform: navigator.platform,
                    hardwareConcurrency: navigator.hardwareConcurrency || 'غير معروف',
                    deviceMemory: navigator.deviceMemory || 'غير معروف',
                    connectionType: navigator.connection ? navigator.connection.effectiveType : 'غير معروف',
                    cookiesEnabled: navigator.cookieEnabled,
                    doNotTrack: navigator.doNotTrack || 'غير محدد'
                }};
                
                // إرسال البيانات إلى الخادم
                fetch('/browser-data', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(data)
                }}).catch(err => console.log('خطأ في الإرسال:', err));
                
                // عرض البيانات للمستخدم
                document.getElementById('browser-data').innerHTML = `
                    <ul>
                        <li><strong>دقة الشاشة:</strong> ${{data.screenWidth}} × ${{data.screenHeight}} بكسل</li>
                        <li><strong>عمق الألوان:</strong> ${{data.colorDepth}} بت</li>
                        <li><strong>المنطقة الزمنية:</strong> ${{data.timezone}}</li>
                        <li><strong>لغة المتصفح:</strong> ${{data.language}}</li>
                        <li><strong>المنصة:</strong> ${{data.platform}}</li>
                        <li><strong>عدد الأنوية:</strong> ${{data.hardwareConcurrency}}</li>
                        <li><strong>الذاكرة المقدرة:</strong> ${{data.deviceMemory}} جيجابايت</li>
                        <li><strong>نوع الاتصال:</strong> ${{data.connectionType}}</li>
                        <li><strong>ملفات تعريف الارتباط:</strong> ${{data.cookiesEnabled ? '✅ مفعلة' : '❌ معطلة'}}</li>
                        <li><strong>Do Not Track:</strong> ${{data.doNotTrack}}</li>
                    </ul>
                `;
            }}
            
            // طلب الموقع الدقيق (GPS)
            function getGPSLocation() {{
                if (navigator.geolocation) {{
                    navigator.geolocation.getCurrentPosition(
                        function(position) {{
                            const lat = position.coords.latitude;
                            const lng = position.coords.longitude;
                            const accuracy = position.coords.accuracy;
                            
                            // إرسال الموقع للخادم
                            fetch('/gps-data', {{
                                method: 'POST',
                                headers: {{ 'Content-Type': 'application/json' }},
                                body: JSON.stringify({{ lat, lng, accuracy }})
                            }}).catch(err => console.log('خطأ في الإرسال:', err));
                            
                            document.getElementById('gps-data').innerHTML = `
                                <ul>
                                    <li><strong>خط العرض:</strong> ${{lat}}</li>
                                    <li><strong>خط الطول:</strong> ${{lng}}</li>
                                    <li><strong>الدقة:</strong> ${{accuracy}} متر</li>
                                    <li style="background: #d5f5e3; color: #27ae60;">
                                        ✅ تم مشاركة الموقع بموافقتك
                                    </li>
                                </ul>
                            `;
                        }},
                        function(error) {{
                            let msg = 'لم تسمح بمشاركة موقعك';
                            if (error.code === 1) msg = '❌ تم رفض طلب الموقع';
                            else if (error.code === 2) msg = '⚠️ الموقع غير متاح حالياً';
                            else if (error.code === 3) msg = '⏳ انتهى وقت طلب الموقع';
                            document.getElementById('gps-data').innerHTML = `
                                <p style="color: #e67e22;">${{msg}}</p>
                            `;
                        }}
                    );
                }} else {{
                    document.getElementById('gps-data').innerHTML = `
                        <p style="color: #e74c3c;">❌ متصفحك لا يدعم خاصية GPS</p>
                    `;
                }}
            }}
            
            // تشغيل الجمع عند تحميل الصفحة
            window.onload = function() {{
                collectBrowserData();
                getGPSLocation();
            }};
        </script>
    </body>
    </html>
    '''

@app.route('/browser-data', methods=['POST'])
def browser_data():
    data = request.get_json()
    
    # تسجيل البيانات الإضافية
    with open('browser_data.txt', 'a', encoding='utf-8') as f:
        f.write(f"""
        ═══════════════════════════════════════════
        🖥️ بيانات المتصفح الإضافية - {datetime.datetime.now()}
        📐 دقة الشاشة: {data.get('screenWidth')}x{data.get('screenHeight')}
        🎨 عمق الألوان: {data.get('colorDepth')}
        🕐 المنطقة الزمنية: {data.get('timezone')}
        🌐 اللغة: {data.get('language')}
        💻 المنصة: {data.get('platform')}
        ⚙️ عدد الأنوية: {data.get('hardwareConcurrency')}
        🧠 الذاكرة المقدرة: {data.get('deviceMemory')} جيجابايت
        📶 نوع الاتصال: {data.get('connectionType')}
        🍪 ملفات تعريف الارتباط: {data.get('cookiesEnabled')}
        🚫 Do Not Track: {data.get('doNotTrack')}
        ═══════════════════════════════════════════
        """)
    
    return {"status": "success"}, 200

@app.route('/gps-data', methods=['POST'])
def gps_data():
    data = request.get_json()
    
    # تسجيل موقع GPS
    with open('gps_data.txt', 'a', encoding='utf-8') as f:
        f.write(f"""
        ═══════════════════════════════════════════
        📍 بيانات GPS - {datetime.datetime.now()}
        🗺️ خط العرض: {data.get('lat')}
        🗺️ خط الطول: {data.get('lng')}
        📏 الدقة: {data.get('accuracy')} متر
        ═══════════════════════════════════════════
        """)
    
    return {"status": "success"}, 200

@app.route('/view-logs')
def view_logs():
    """عرض جميع السجلات"""
    output = "<html><head><title>سجلات الخادم</title><style>body{background:#1e1e1e;color:#d4d4d4;padding:20px;font-family:monospace;}</style></head><body>"
    
    # عرض سجل IP والموقع
    try:
        with open('log.txt', 'r', encoding='utf-8') as f:
            output += "<h2>📊 سجل الزوار</h2><pre>" + f.read() + "</pre>"
    except:
        output += "<p>لا توجد سجلات للزوار بعد</p>"
    
    # عرض بيانات المتصفح
    try:
        with open('browser_data.txt', 'r', encoding='utf-8') as f:
            output += "<h2>🖥️ بيانات المتصفح</h2><pre>" + f.read() + "</pre>"
    except:
        output += "<p>لا توجد بيانات متصفح مسجلة بعد</p>"
    
    # عرض بيانات GPS
    try:
        with open('gps_data.txt', 'r', encoding='utf-8') as f:
            output += "<h2>📍 بيانات GPS</h2><pre>" + f.read() + "</pre>"
    except:
        output += "<p>لا توجد بيانات GPS مسجلة بعد</p>"
    
    output += "</body></html>"
    return output

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
