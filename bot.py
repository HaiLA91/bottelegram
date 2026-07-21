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
    
    await event.respond(f"⏳ Đang lên lịch 12 tin cho cell [{device_id}]...")
    now = datetime.datetime.now()
    
    for i in range(12):
        scheduled_time = now + datetime.timedelta(minutes=1 + (15 * i))
        await client.send_message(TARGET_GROUP, full_command, schedule=scheduled_time)
        
    await event.respond(f"✅ Đã lên lịch xong 8 lần gửi vào nhóm!")


# ==========================================
# 3.2 LẮNG NGHE LỆNH KHỞI CHẠY /noise2g
# ==========================================
@client.on(events.NewMessage(pattern=r'(?i)^/noise2g\s+(.+)', chats='me'))
async def handler(event):
    device_id = event.pattern_match.group(1).strip().upper()
    full_command = f"/noise2g {device_id}" 
    
    await event.respond(f"⏳ Đang lên lịch 8 tin cho cell [{device_id}]...")
    now = datetime.datetime.now()
    
    for i in range(8):
        scheduled_time = now + datetime.timedelta(minutes=1 + (60 * i))
        await client.send_message(TARGET_GROUP, full_command, schedule=scheduled_time)
        
    await event.respond(f"✅ Đã lên lịch xong 8 lần gửi vào nhóm!")

# ==========================================
# 4. LỆNH XUẤT FILE THỦ CÔNG (QUÉT 800 TIN NHẮN)
# ==========================================
@client.on(events.NewMessage(pattern=r'(?i)^/export\s+(.+)', chats='me'))
async def export_handler(event):
    device_id = event.pattern_match.group(1).strip().upper()
    await event.respond(f"🔍 Đang gom dữ liệu cho trạm {device_id}...")
    
    try:
        await client.get_dialogs(limit=20)
        collected_texts = []
        
        # Quét 500 tin nhắn theo yêu cầu
        async for message in client.iter_messages(TARGET_GROUP, limit=800):
            if message.text and device_id in message.text.upper() and not message.text.strip().startswith('/'):
                log_entry = message.text.strip()
                collected_texts.append(log_entry)
        
        if collected_texts:
            collected_texts.reverse()
            vn_now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
            
            file_content = f"BÁO CÁO KẾT QUẢ THỐNG KÊ CELL: {device_id}\n"
            file_content += f"Ngày xuất file: {vn_now.strftime('%d/%m/%Y %H:%M:%S')}\n"
            
            file_content += "="*44 + "\n"
            file_content += f"\n{'='*44}\n".join(collected_texts)
            file_content += "\n" + "="*44 + "\n"
            
            file_data = io.BytesIO(file_content.encode('utf-8'))
            file_data.name = f"BaoCao_{device_id}.txt"
            
            await client.send_message('me', f"📄 Đã quét xong File kết quả thông số của {device_id} đây nhé.", file=file_data)
        else:
            await event.respond(f"❌ Không tìm thấy kết quả nào trả về cho mã '{device_id}'")
            
    except Exception as e:
        await event.respond(f"⚠️ Máy chủ báo lỗi trong lúc quét: {str(e)}")
        print(f"LỖI EXPORT: {str(e)}")

print("Bot đang khởi động...")
client.start()
client.run_until_disconnected()
