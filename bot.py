import datetime
import threading
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
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_web).start()

# ==========================================
# 2. CẤU HÌNH THÔNG TIN BOT
# ==========================================
API_ID = 33464486  # Đổi thành API_ID của bạn (viết dạng số, không có dấu nháy)
API_HASH = '250243bb2640592eee140795c11bd16c' # Đổi thành API_HASH của bạn
SESSION_STRING = 'ĐIỀN_CHUỖI_MÃ_SESSION_VÀO_ĐÂY' # (Sẽ lấy ở bước sau)

TARGET_GROUP = '@username_cua_nhom' # ID hoặc username của Group bạn muốn gửi lệnh tới

# Khởi tạo Client bằng StringSession (Không cần file .session nữa)
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# ==========================================
# 3. XỬ LÝ LỆNH ĐỘNG TỪ BẠN
# ==========================================
# Lắng nghe mọi tin nhắn bắt đầu bằng /noise4g (không phân biệt chữ hoa thường)
@client.on(events.NewMessage(pattern=r'(?i)^/noise4g\s+(.+)', incoming=True, chats='me'))
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