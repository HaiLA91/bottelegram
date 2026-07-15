import os
import datetime
import threading
import io
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession

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
TARGET_GROUP = -1001587192974 

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# ==========================================
# 3. LẮNG NGHE LỆNH KHỞI CHẠY /noise4g
# ==========================================
@client.on(events.NewMessage(pattern=r'(?i)^/noise4g\s+(.+)', chats='me'))
async def handler(event):
    device_id = event.pattern_match.group(1).strip().upper()
    full_command = f"/noise4g {device_id}" 
    
    await event.respond(f"⏳ Nhận lệnh. Đang lên lịch 8 tin cho thiết bị [{device_id}]...")
    now = datetime.datetime.now()
    
    for i in range(8):
        scheduled_time = now + datetime.timedelta(minutes=1 + (15 * i))
        await client.send_message(TARGET_GROUP, full_command, schedule=scheduled_time)
        
    await event.respond(f"✅ Xong! Đã lên lịch 8 lần '{full_command}' vào nhóm. Cứ yên tâm tắt máy, khi nào cần lấy dữ liệu thì gõ lệnh /export nhé.")

# ==========================================
# 4. LỆNH XUẤT FILE TỪ LỊCH SỬ GROUP (BẤT TỬ)
# ==========================================
@client.on(events.NewMessage(pattern=r'(?i)^/export\s+(.+)', chats='me'))
async def export_handler(event):
    device_id = event.pattern_match.group(1).strip().upper()
    await event.respond(f"🔍 Đang quét 1000 tin nhắn gần nhất để gom dữ liệu cho trạm {device_id}...")
    
    collected_texts = []
    
    # Lướt tìm trong 1000 tin nhắn gần nhất
    async for message in client.iter_messages(TARGET_GROUP, limit=1000):
        if message.text and device_id in message.text.upper():
            # Chuyển đổi sang giờ Việt Nam (Render dùng giờ hệ thống UTC)
            vn_time = message.date + datetime.timedelta(hours=7)
            time_str = vn_time.strftime('%d/%m/%Y %H:%M:%S')
            
            log_entry = f"--- THỜI GIAN TRẢ VỀ: {time_str} ---\n{message.text}\n"
            collected_texts.append(log_entry)
    
    if collected_texts:
        # Lật ngược danh sách để tin nhắn cũ hiển thị trước
        collected_texts.reverse()
        
        file_content = f"BÁO CÁO KẾT QUẢ THỐNG KÊ TRẠM: {device_id}\n"
        file_content += f"Ngày xuất file: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        file_content += "="*50 + "\n\n"
        file_content += "\n==================================================\n\n".join(collected_texts)
        
        file_data = io.BytesIO(file_content.encode('utf-8'))
        file_data.name = f"BaoCao_{device_id}.txt"
        
        await event.respond(file=file_data, caption=f"📄 Đã quét xong! File kết quả thông số của {device_id} đây nhé.")
    else:
        await event.respond(f"❌ Không tìm thấy kết quả nào trả về cho mã '{device_id}' trong lịch sử gần đây của nhóm.")

print("Bot đang khởi động...")
client.start()
client.run_until_disconnected()