import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("BUAT LAPORAN BANDING", callback_data="buat")]]
    await update.message.reply_text(
        "Selamat datang di IbnuOfficialBot.\n"
        "Bot ini membantu membuat draf permohonan peninjauan akun WhatsApp milik sendiri.",
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
    if not nomor.isdigit() or len(nomor) < 9 or len(nomor) > 15:
        await update.message.reply_text("Format nomor belum benar. Coba lagi.")
        return

    context.user_data["nomor"] = nomor
    context.user_data["menunggu_nomor"] = False

    keyboard = [[InlineKeyboardButton("BUAT DRAF", callback_data="draf")]]
    await update.message.reply_text(
        f"Nomor: {nomor}\nTekan tombol untuk membuat draf permohonan.",
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
        "Jika terjadi kesalahan, saya mohon bantuan untuk memulihkan akses.\n\n"
        "Terima kasih."
    )
    await query.message.reply_text(
        "Berikut draf permohonanmu. Periksa dahulu, lalu kirim sendiri "
        "melalui kanal dukungan resmi WhatsApp:\n\n" + teks
    )

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN belum diatur")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buat, pattern="^buat$"))
    app.add_handler(CallbackQueryHandler(draf, pattern="^draf$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, nomor))
    app.run_polling()

if __name__ == "__main__":
    main()
