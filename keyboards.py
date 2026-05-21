from telebot.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("➕ Записать день"), KeyboardButton("📊 Статистика"))
    kb.row(KeyboardButton("📜 История"),       KeyboardButton("⚙️ Настройки"))
    kb.row(KeyboardButton("❓ Помощь"))
    return kb

def mood_keyboard():
    kb = InlineKeyboardMarkup()
    emojis = ["😞","😐","🙂","😊","🤩"]
    buttons = [InlineKeyboardButton(f"{i+1} {emojis[i]}", callback_data=f"mood_{i+1}") for i in range(5)]
    kb.row(*buttons)
    return kb

def work_keyboard():
    kb = InlineKeyboardMarkup()
    options = [("0.5 ч","0.5"),("1 ч","1"),("2 ч","2"),("4 ч","4"),("Другое...","work_other")]
    kb.row(*[InlineKeyboardButton(label, callback_data=f"work_{val}") for label, val in options])
    return kb

def sleep_keyboard():
    kb = InlineKeyboardMarkup()
    options = [("6 ч","6"),("7 ч","7"),("8 ч","8"),("9 ч","9"),("Другое...","sleep_other")]
    kb.row(*[InlineKeyboardButton(label, callback_data=f"sleep_{val}") for label, val in options])
    return kb

def skip_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Пропустить", callback_data="skip_comment"))
    return kb

def stats_keyboard():
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("📅 За неделю",  callback_data="stats_7"),
        InlineKeyboardButton("🗓 За месяц",   callback_data="stats_30")
    )
    kb.row(InlineKeyboardButton("🔍 Мои инсайты", callback_data="stats_insights"))
    return kb

def confirm_clear_keyboard():
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("✅ Да, удалить", callback_data="clear_yes"),
        InlineKeyboardButton("❌ Отмена",      callback_data="clear_no")
    )
    return kb