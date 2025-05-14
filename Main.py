from pyrogram import Client, filters
from pyrogram.types import Message
import requests
import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
STREAMUP_API_KEY = os.getenv("STREAMUP_API_KEY")

app = Client("streamup_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.private & (filters.video | filters.document))
async def upload_file(client: Client, message: Message):
    msg = await message.reply_text("Downloading file...")

    try:
        media = message.video or message.document
        file_name = media.file_name or f"{media.file_id}.mp4"
        path = await client.download_media(message, file_name)

        await msg.edit("Uploading to StreamUP...")

        with open(path, "rb") as f:
            files = {"videoFile": (file_name, f, "video/mp4")}
            headers = {
                "Origin": "https://streamup.cc",
                "Referer": "https://streamup.cc/",
                "User-Agent": "Mozilla/5.0"
            }
            response = requests.post(
                "https://e1.beymtv.com/upload.php?id=1254",
                files=files,
                headers=headers
            )

        if response.ok:
            api_url = f"https://api.streamup.cc/v1/data?api_key={STREAMUP_API_KEY}&page=1"
            api_response = requests.get(api_url)
            data = api_response.json()

            if "videos" in data and len(data["videos"]) > 0:
                latest_video = data["videos"][0]
                filecode = latest_video.get("Filecode")
                streamup_link = f"https://streamup.ws/{filecode}"
                await msg.edit(f"Upload successful!\n{streamup_link}")
            else:
                await msg.edit("Upload successful, but no link found in API data.")

        else:
            await msg.edit(f"Upload failed: {response.text}")

    except Exception as e:
        await msg.edit(f"Error: {str(e)}")

    finally:
        if 'path' in locals() and os.path.exists(path):
            os.remove(path)

@app.on_message(filters.command("start") & filters.private)
async def start(client, message: Message):
    await message.reply_text("Send a video or document. I’ll upload it to StreamUP and send back the link.")

print("Bot Started!")
app.run()
