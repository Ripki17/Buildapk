#!/usr/bin/env python3
"""
TeleBuild APK - 24/7 Telegram Bot
Mendukung:
1. Otomatis deteksi file lampiran ZIP (Native Android & Flutter).
2. Live log preview streaming saat proses build.
3. Otomatis kirim file .APK hasil kompilasi ke Telegram.
"""

import os
import zipfile
import io
import logging
import asyncio
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7824380847:AAGJ6ahNX4PtyDEw9LHSEgUF0KErzgcvyh0")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER", "rkarifqi")
GITHUB_REPO = os.getenv("GITHUB_REPO", "apk-builder-runner")
WORKFLOW_ID = os.getenv("WORKFLOW_ID", "build-apk.yml")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🤖 *Selamat Datang di TeleBuild APK 24/7 Engine!*\n\n"
        "✨ *Fitur Otomatis:*\n"
        "📁 *Kirim File ZIP Project:* Cukup kirim/lampirkan file `.zip` project "
        "Native Android atau Flutter Anda ke chat ini, bot akan *otomatis mendeteksi* "
        "dan langsung mengompilasi APK!\n\n"
        "🔗 *Kirim Link Git:* `/build <URL_GITHUB> [release|debug]`\n\n"
        "📊 *Live Preview Log:* Anda akan melihat progress log kompilasi secara real-time!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_document_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mendeteksi lampiran file ZIP di Telegram dan memulai build otomatis"""
    doc = update.message.document
    chat_id = update.effective_chat.id
    file_name = doc.file_name or "project.zip"

    if not file_name.lower().endswith(".zip"):
        await update.message.reply_text(
            "⚠️ Harap kirimkan file berekstensi *.ZIP* yang memuat project Native Android (build.gradle) atau Flutter (pubspec.yaml).",
            parse_mode="Markdown"
        )
        return

    # Kirim status awal
    status_msg = await update.message.reply_text(
        f"📥 *Menerima File ZIP:* `{file_name}` ({round(doc.file_size / (1024*1024), 2)} MB)\n"
        "🔍 *Menganalisis struktur file project...*",
        parse_mode="Markdown"
    )

    try:
        # Ambil link download langsung file dari Telegram API
        tg_file = await context.bot.get_file(doc.file_id)
        direct_download_url = tg_file.file_path

        # Unduh header ZIP untuk mendeteksi framework (Flutter vs Native Android)
        detected_framework = "auto"
        async with httpx.AsyncClient() as client:
            resp = await client.get(direct_download_url, headers={"Range": "bytes=0-65536"})
            # Cek string nama file di arsip zip
            content_str = str(resp.content)
            if "pubspec.yaml" in content_str:
                detected_framework = "Flutter 💙"
            elif "build.gradle" in content_str or "settings.gradle" in content_str:
                detected_framework = "Native Android (Kotlin/Java) 🤖"

        # Update log preview
        await status_msg.edit_text(
            f"✅ *Analisis Selesai!*\n"
            f"📦 *File:* `{file_name}`\n"
            f"🛠 *Framework:* `{detected_framework}`\n"
            f"⏳ *Status:* Mendaftarkan job ke Cloud Runner Matrix...\n\n"
            f"📡 _Mempersiapkan live preview terminal..._",
            parse_mode="Markdown"
        )

        # Trigger GitHub Actions runner
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        payload = {
            "ref": "main",
            "inputs": {
                "source_type": "zip_url",
                "source_url": direct_download_url,
                "build_type": "release",
                "chat_id": str(chat_id),
                "status_message_id": str(status_msg.message_id)
            }
        }

        url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/workflows/{WORKFLOW_ID}/dispatches"

        async with httpx.AsyncClient() as client:
            dispatch_resp = await client.post(url, headers=headers, json=payload, timeout=20.0)
            if dispatch_resp.status_code == 204:
                # Update status message with live instructions
                await status_msg.edit_text(
                    f"🚀 *Build Dimulai di Cloud Runner!*\n\n"
                    f"📦 *Project:* `{file_name}` (`{detected_framework}`)\n"
                    f"⚙️ *Varian:* `RELEASE APK`\n\n"
                    f"🔄 *Live Log Preview:* Pesan ini akan terus di-update otomatis seiring berjalannya kompilasi.\n"
                    f"📱 APK akan dikirim langsung ke chat ini begitu selesai (~2-3 menit)!",
                    parse_mode="Markdown"
                )
            else:
                await status_msg.edit_text(
                    f"❌ Gagal memicu GitHub Actions runner: HTTP {dispatch_resp.status_code}\n`{dispatch_resp.text}`"
                )
    except Exception as e:
        logger.error(f"Error handling zip: {e}")
        await status_msg.edit_text(f"❌ Terjadi kesalahan saat memproses file: {str(e)}")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    # Otomatis tangkap dokumen berekstensi zip
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document_upload))

    logger.info("Bot TeleBuild APK 24/7 (ZIP Auto-Detect & Live Logs) running...")
    app.run_polling()

if __name__ == "__main__":
    main()
