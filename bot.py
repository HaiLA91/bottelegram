import os
import datetime
import threading
import io
from flask import Flask
from telethon import TelegramClient, events

# ==========================================
# 1. WEB SERVER ẢO (Giữ Render luôn thức)
# ==========================================
app = Flask(__name__)
@app.route('/')
def home():
    return "✅ Máy chủ Web đang hoạt động! Userbot đang chạy ngầm."

def run_web():
    port = int(os.environ.get('PORT', 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()

# ==========================================
# 2. CẤU HÌNH THÔNG TIN BOT
# ==========================================
API_ID = int(os.environ.get('API_ID', 0))
API_HASH = os.environ.get('API_HASH', '')
SESSION_STRING = os.environ.get('SESSION_STRING', '')

# Đã cập nhật ID nhóm lớn bắt buộc có đầu số -100
TARGET_GROUP = -1001587192974 

# Kho lưu trữ dữ liệu tạm thời trong bộ nhớ
# Cấu trúc: { 'EHC0155911IB': ["nội dung tin 1", "nội dung tin 2"] }
collected_logs = {}

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) if 'StringSession' in globals() else TelegramClient('my_account_session', API_ID, API_HASH)
# Lưu ý: Dòng trên tự tương thích môi trường, nếu dùng StringSession trên Render
from telethon.sessions import StringSession
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# ==========================================
# 3. LẮNG NGHE LỆNH KHỞI CHẠY /noise4g
# ==========================================
@client.on(events.NewMessage(pattern=r'(?i)^/noise4g\s+(.+)', chats='me'))
async def handler(event):
    device_id = event.pattern_match.group(1).strip()
    full_command = event.raw_text
    
    # Khởi tạo kho lưu trữ riêng cho mã thiết bị này
    collected_logs[device_id] = []
    
    await event.respond(f"⏳ Nhận lệnh. Đang lên lịch 8 tin cho thiết bị [{device_id}]...")
    now = datetime.datetime.now()
    
    for i in range(8):
        scheduled_time = now + datetime.timedelta(minutes=1 + (15 * i))
        await client.send_message(TARGET_GROUP, full_command, schedule=scheduled_time)
        
    await event.respond(f"✅ Đã lên lịch thành công 8 lệnh vào nhóm! Hệ thống bắt đầu tự động thu thập kết quả trả về...")

# ==========================================
# 4. TỰ ĐỘNG THU THẬP TIN NHẮN KẾT QUẢ TỪ GROUP
# ==========================================
@client.on(events.NewMessage(chats=TARGET_GROUP))
async def group_listener(event):
    text = event.raw_text
    
    # Kiểm tra xem tin nhắn mới trong nhóm có chứa mã thiết bị nào đang được theo dõi không
    for device_id in list(collected_logs.keys()):
        if device_id in text or "cảnh báo lỗi" in text.lower():
            # Thêm mốc thời gian nhận và nội dung tin nhắn vào kho
            time_str = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            log_entry = f"--- THỜI GIAN NHẬN: {time_str} ---\n{text}\n"
            
            collected_logs[device_id].append(log_entry)
            print(f"🔹 Đã thu thập 1 tin nhắn cho thiết bị {device_id}")

# ==========================================
# 5. LỆNH XUẤT FILE .TXT TỪ ĐIỆN THOẠI
# ==========================================
@client.on(events.NewMessage(pattern=r'(?i)^/export\s+(.+)', chats='me'))
async def export_handler(event):
    device_id = event.pattern_match.group(1).strip()
    
    if device_id in collected_logs and collected_logs[device_id]:
        # Tạo nội dung file text văn bản
        file_content = f"BÁO CÁO DỮ LIỆU THU THẬP THIẾT BỊ: {device_id}\n"
        file_content += f"Xuất bản lúc: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        file_content += "="*50 + "\n\n"
        file_content += "\n==================================================\n\n".join(collected_logs[device_id])
        
        # Chuyển đổi chuỗi thành file dạng nhị phân trong bộ nhớ (không tốn dung lượng ổ cứng Render)
        file_data = io.BytesIO(file_content.encode('utf-8'))
        file_data.name = f"BaoCao_{device_id}.txt"
        
        # Gửi file trực tiếp vào Saved Messages cho bạn
        await event.respond(file=file_data, caption=f"📄 File dữ liệu tổng hợp của thiết bị {device_id}")
    else:
        await event.respond(f"❌ Hiện chưa có dữ liệu thu thập cho thiết bị '{device_id}'. Vui lòng kiểm tra lại mã hoặc đợi bot gom tin.")

print("Bot đang khởi động...")
client.start()
client.run_until_disconnected()