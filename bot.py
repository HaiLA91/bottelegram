import datetime
import threading
import os
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# ==========================================
# 1. WEB SERVER ẢO (Lách luật kiểm tra của Koyeb)
# ==========================================
app = Flask(__name__)
@app.route('/')
def home():
    return "✅ Máy chủ Web đang hoạt động! Userbot đang chạy ngầm."

def run_web():
    # Lấy Port của Render cấp, nếu không có thì dùng 10000
    port = int(os.environ.get('PORT', 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()

# ==========================================
# 2. CẤU HÌNH THÔNG TIN BOT (BẢO MẬT)
# ==========================================
# Lấy thông tin từ Biến môi trường thay vì ghi trực tiếp
API_ID = int(os.environ.get('API_ID', 0)) 
API_HASH = os.environ.get('API_HASH', '')
SESSION_STRING = os.environ.get('SESSION_STRING', '')
TARGET_GROUP = -1587192974
# Khởi tạo Client bằng StringSession (Không cần file .session nữa)
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# ==========================================
# 3. XỬ LÝ LỆNH ĐỘNG TỪ BẠN
# ==========================================
# Lắng nghe mọi tin nhắn bắt đầu bằng /noise4g (không phân biệt chữ hoa thường)
@client.on(events.NewMessage(pattern=r'(?i)^/noise4g\s+(.+)', chats='me'))
async def handler(event):
    # Lấy CHÍNH XÁC toàn bộ câu bạn vừa gõ (vd: "/noise4g ehi6989")
    full_command = event.raw_text
    
    await event.respond(f"⏳ Nhận lệnh. Đang lên lịch 8 tin nhắn: '{full_command}'...")
    now = datetime.datetime.now()
    
    # Lặp 8 lần, cách nhau 15 phút
    for i in range(8):
        scheduled_time = now + datetime.timedelta(minutes=1 + (15 * i))
        
        # Đẩy lịch hẹn gửi tin nhắn vào Group
        await client.send_message(TARGET_GROUP, full_command, schedule=scheduled_time)
        
    await event.respond(f"✅ Xong! Đã lên lịch 8 lần '{full_command}' vào nhóm.")

print("Bot đang khởi động...")
client.start()
client.run_until_disconnected()
