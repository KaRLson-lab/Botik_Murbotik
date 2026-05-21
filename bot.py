import telebot
from telebot.types import Message, CallbackQuery
from apscheduler.schedulers.background import BackgroundScheduler
from config import BOT_TOKEN, REMINDER_HOUR, REMINDER_MINUTE
from db_handler import (init_db, save_entry, get_all_entries, clear_entries,
                        get_reminder, set_reminder, get_all_users)
from analyzer import get_stats
from keyboards import (main_menu, mood_keyboard, work_keyboard,
                       sleep_keyboard, skip_keyboard, stats_keyboard,
                       confirm_clear_keyboard)

bot = telebot.TeleBot(BOT_TOKEN)


user_state = {}  

def reset_state(uid):
    user_state[uid] = {"step": None, "data": {}}



@bot.message_handler(commands=["start"])
def cmd_start(msg: Message):
    reset_state(msg.from_user.id)
    bot.send_message(
        msg.chat.id,
        "👋 Привет! Я помогу отслеживать твоё самочувствие и продуктивность.\n\n"
        "Каждый день записывай:\n"
        "• 😊 Настроение (1–5)\n"
        "• 📚 Часы учёбы/работы\n"
        "• 🌙 Часы сна\n\n"
        "Через неделю я покажу закономерности в твоих данных.\n"
        "Используй меню ниже 👇",
        reply_markup=main_menu()
    )
    set_reminder(msg.from_user.id, REMINDER_HOUR, REMINDER_MINUTE)

@bot.message_handler(commands=["help"])
@bot.message_handler(func=lambda m: m.text == "❓ Помощь")
def cmd_help(msg: Message):
    bot.send_message(
        msg.chat.id,
        "📖 *Команды бота:*\n"
        "/add или ➕ — записать сегодняшний день\n"
        "/stats или 📊 — статистика и инсайты\n"
        "/history или 📜 — история записей\n"
        "/settings или ⚙️ — время напоминания\n"
        "/clear — очистить все данные\n"
        "/help — эта справка",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )


def start_add(chat_id, user_id):
    reset_state(user_id)
    user_state[user_id]["step"] = "mood"
    bot.send_message(
        chat_id,
        "Шаг 1/4 — Оцени настроение сегодня:",
        reply_markup=mood_keyboard()
    )

@bot.message_handler(commands=["add"])
@bot.message_handler(func=lambda m: m.text == "➕ Записать день")
def cmd_add(msg: Message):
    start_add(msg.chat.id, msg.from_user.id)


@bot.message_handler(commands=["stats"])
@bot.message_handler(func=lambda m: m.text == "📊 Статистика")
def cmd_stats(msg: Message):
    bot.send_message(msg.chat.id, "Что хочешь узнать?", reply_markup=stats_keyboard())



@bot.message_handler(commands=["history"])
@bot.message_handler(func=lambda m: m.text == "📜 История")
def cmd_history(msg: Message):
    rows = get_all_entries(msg.from_user.id)
    if not rows:
        bot.send_message(msg.chat.id, "Записей пока нет. Добавь первую! ➕")
        return
    text = "📜 *История записей:*\n\n"
    for r in rows[:15]:
        emojis = ["","😞","😐","🙂","😊","🤩"]
        text += (f"📅 {r['created_at'][:10]}  "
                 f"{emojis[r['mood']]} {r['mood']}  "
                 f"📚 {r['work_hours']}ч  🌙 {r['sleep_hours']}ч")
        if r["comment"]:
            text += f"\n💬 {r['comment']}"
        text += "\n\n"
    bot.send_message(msg.chat.id, text, parse_mode="Markdown")



@bot.message_handler(commands=["settings"])
@bot.message_handler(func=lambda m: m.text == "⚙️ Настройки")
def cmd_settings(msg: Message):
    uid = msg.from_user.id
    rem = get_reminder(uid)
    cur = f"{rem[0]:02d}:{rem[1]:02d}" if rem else "21:00"
    user_state.setdefault(uid, {"step": None, "data": {}})
    user_state[uid]["step"] = "settings_time"
    bot.send_message(
        msg.chat.id,
        f"⏰ Текущее время напоминания: *{cur}*\n\nВведи новое время в формате ЧЧ:ММ (например, 20:30):",
        parse_mode="Markdown"
    )



@bot.message_handler(commands=["clear"])
def cmd_clear(msg: Message):
    bot.send_message(
        msg.chat.id,
        "⚠️ Удалить все твои записи? Это действие нельзя отменить.",
        reply_markup=confirm_clear_keyboard()
    )



@bot.message_handler(func=lambda m: True)
def handle_text(msg: Message):
    uid = msg.from_user.id
    state = user_state.get(uid, {})
    step = state.get("step")

    if step == "work_other":
        try:
            hours = float(msg.text.replace(",", "."))
            assert 0 <= hours <= 24
        except:
            bot.send_message(msg.chat.id, "Введи число от 0 до 24, например: 3.5")
            return
        user_state[uid]["data"]["work_hours"] = hours
        user_state[uid]["step"] = "sleep"
        bot.send_message(msg.chat.id, "Шаг 3/4 — Сколько часов спал?", reply_markup=sleep_keyboard())

    elif step == "sleep_other":
        try:
            hours = float(msg.text.replace(",", "."))
            assert 0 <= hours <= 24
        except:
            bot.send_message(msg.chat.id, "Введи число от 0 до 24, например: 7.5")
            return
        user_state[uid]["data"]["sleep_hours"] = hours
        user_state[uid]["step"] = "comment"
        bot.send_message(msg.chat.id, "Шаг 4/4 — Хочешь добавить комментарий?", reply_markup=skip_keyboard())

    elif step == "comment":
        user_state[uid]["data"]["comment"] = msg.text
        _save_and_finish(msg.chat.id, uid)

    elif step == "settings_time":
        try:
            h, m = map(int, msg.text.strip().split(":"))
            assert 0 <= h <= 23 and 0 <= m <= 59
        except:
            bot.send_message(msg.chat.id, "Неверный формат. Введи время как ЧЧ:ММ, например 20:30")
            return
        set_reminder(uid, h, m)
        user_state[uid]["step"] = None
        bot.send_message(msg.chat.id, f"✅ Напоминание установлено на {h:02d}:{m:02d}", reply_markup=main_menu())

def _save_and_finish(chat_id, uid):
    d = user_state[uid]["data"]
    save_entry(uid, d["mood"], d["work_hours"], d["sleep_hours"], d.get("comment", ""))
    reset_state(uid)
    bot.send_message(
        chat_id,
        "✅ Запись сохранена! Возвращайся завтра 🙂",
        reply_markup=main_menu()
    )



@bot.callback_query_handler(func=lambda c: True)
def handle_callback(call: CallbackQuery):
    uid = call.from_user.id
    data = call.data
    state = user_state.get(uid, {"step": None, "data": {}})

    if data.startswith("mood_"):
        mood = int(data.split("_")[1])
        user_state.setdefault(uid, {"step": None, "data": {}})
        user_state[uid]["data"]["mood"] = mood
        user_state[uid]["step"] = "work"
        bot.edit_message_text(f"Настроение: {'😞😐🙂😊🤩'[mood-1]} {mood}", call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Шаг 2/4 — Сколько часов потратил на учёбу/работу?", reply_markup=work_keyboard())

    elif data.startswith("work_"):
        val = data[5:]
        if val == "other":
            user_state[uid]["step"] = "work_other"
            bot.send_message(call.message.chat.id, "Введи количество часов (например 3 или 1.5):")
        else:
            user_state[uid]["data"]["work_hours"] = float(val)
            user_state[uid]["step"] = "sleep"
            bot.edit_message_text(f"Учёба/работа: {val} ч", call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, "Шаг 3/4 — Сколько часов спал?", reply_markup=sleep_keyboard())


    elif data.startswith("sleep_"):
        val = data[6:]
        if val == "other":
            user_state[uid]["step"] = "sleep_other"
            bot.send_message(call.message.chat.id, "Введи количество часов сна (например 6.5):")
        else:
            user_state[uid]["data"]["sleep_hours"] = float(val)
            user_state[uid]["step"] = "comment"
            bot.edit_message_text(f"Сон: {val} ч", call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, "Шаг 4/4 — Хочешь добавить комментарий?", reply_markup=skip_keyboard())

    elif data == "skip_comment":
        user_state[uid]["data"]["comment"] = ""
        bot.edit_message_text("Комментарий: —", call.message.chat.id, call.message.message_id)
        _save_and_finish(call.message.chat.id, uid)

    elif data in ("stats_7", "stats_30", "stats_insights"):
        days = 7 if data == "stats_7" else 30
        s = get_stats(uid, days)
        if not s:
            bot.answer_callback_query(call.id, "Нет данных за этот период")
            return
        period = "неделю" if days == 7 else "месяц"
        text = (
            f"📊 *Статистика за {period}* ({s['count']} записей)\n\n"
            f"😊 Среднее настроение: *{s['avg_mood']}* / 5\n"
            f"📚 Средняя учёба/работа: *{s['avg_work']}* ч\n"
            f"🌙 Средний сон: *{s['avg_sleep']}* ч\n\n"
            f"🏆 Лучший день: {s['best_day']}\n"
            f"😔 Худший день: {s['worst_day']}\n\n"
            f"🔍 *Инсайты:*\n"
            f"• Настроение при сне ≥7 ч: *{s['mood_good_sleep']}*\n"
            f"• Настроение при сне <7 ч: *{s['mood_bad_sleep']}*"
        )
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown")


    elif data == "clear_yes":
        clear_entries(uid)
        bot.edit_message_text("🗑 Все данные удалены.", call.message.chat.id, call.message.message_id)
    elif data == "clear_no":
        bot.edit_message_text("Отмена. Данные сохранены.", call.message.chat.id, call.message.message_id)

    bot.answer_callback_query(call.id)

def send_reminders():
    from datetime import datetime
    now = datetime.now()
    for uid in get_all_users():
        rem = get_reminder(uid)
        if rem and rem[0] == now.hour and rem[1] == now.minute:
            try:
                bot.send_message(uid, "🔔 Не забудь записать сегодняшний день! Нажми ➕ Записать день")
            except:
                pass


if __name__ == "__main__":
    init_db()
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_reminders, "cron", minute="*")
    scheduler.start()
    print("Бот запущен...")
    bot.infinity_polling()