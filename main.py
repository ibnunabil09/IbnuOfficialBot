import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def log_message(self, *args):
        pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(
        "BUAT LAPORAN BANDING", callback_data="buat"
    )]]
    await update.message.reply_text(
        "Selamat datang di IbnuOfficialBot.\n"
        "Bot ini membantu membuat draf permohonan peninjauan "
        "akun WhatsApp milik sendiri.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["menunggu_nomor"] = True
    await query.message.reply_text(
        "Kirim nomor WhatsApp milikmu dengan kode negara.\n"
        "Contoh: 6281234567890"
    )

async def nomor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("menunggu_nomor"):
        return

    nomor = update.message.text.strip().replace("+", "").replace(" ", "")
    if not nomor.isdigit() or not 9 <= len(nomor) <= 15:
        await update.message.reply_text("Format nomor belum benar. Coba lagi.")
        return

    context.user_data["nomor"] = nomor
    context.user_data["menunggu_nomor"] = False

    keyboard = [[InlineKeyboardButton("BUAT DRAF", callback_data="draf")]]
    await update.message.reply_text(
        f"Nomor: {nomor}\nTekan tombol untuk membuat draf.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def draf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    nomor = context.user_data.get("nomor")
    if not nomor:
        await query.message.reply_text("Ketik /start untuk mulai lagi.")
        return

    teks = (
        "Kepada Tim Dukungan WhatsApp,\n\n"
        f"Saya pemilik nomor WhatsApp +{nomor}.\n"
        "Mohon tinjau kembali status akun saya. "
        "Jika terjadi kesalahan, saya mohon bantuan pemulihan akses.\n\n"
        "Terima kasih."
    )
    await query.message.reply_text(
        "Periksa draf berikut, lalu kirim sendiri melalui "
        "kanal dukungan resmi WhatsApp:\n\n" + teks
    )

def main():
    token = os.environ["BOT_TOKEN"]
    port = int(os.environ.get("PORT", "10000"))

    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buat, pattern="^buat$"))
    app.add_handler(CallbackQueryHandler(draf, pattern="^draf$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, nomor))

    app.run_polling()

if __name__ == "__main__":
    main()
