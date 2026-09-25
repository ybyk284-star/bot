import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# خادم وهمي عشان رندر ما يعطي خطأ Web Service
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_web():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

def main() -> None:
    # تشغيل الخادم الوهمي في الخلفية
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()

    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(back_to_start, pattern="^back$"))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    application.run_polling()

if __name__ == "__main__":
    main()
    
