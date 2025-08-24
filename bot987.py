import telebot
from telebot import types
from datetime import datetime, timedelta
import json
import os

# 🔑 Твой токен и чат админа
TOKEN = "8264888146:AAFNqMNQUIDPOoNZYuQ2mnhFIIV0ECOA2BY"
ADMIN_CHAT_ID = -1002939358940

bot = telebot.TeleBot(TOKEN)

# 📂 Файл для хранения подписок
SUB_FILE = "subscriptions.json"

# Завантаження підписок з файла
def load_subscriptions():
    if os.path.exists(SUB_FILE):
        with open(SUB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {int(uid): datetime.fromisoformat(date) for uid, date in data.items()}
    return {}

# Збереження підписок у файл
def save_subscriptions():
    with open(SUB_FILE, "w", encoding="utf-8") as f:
        json.dump({uid: date.isoformat() for uid, date in subscriptions.items()}, f, ensure_ascii=False, indent=2)

# 📦 Підписки користувачів
subscriptions = load_subscriptions()

# 📂 Каталог послуг
catalog = {
    "🤖 Простий бот (разова послуга)": {
        "price": "50₴",
        "desc": "Бот з простим меню та автоматичними відповідями."
    },
    "💵 Бот з оплатою та адмін-чатом": {
        "price": "120₴",
        "desc": "Бот з інтегрованою оплатою та пересиланням чеків в адмін-чат."
    },
    "🛒 Магазин/каталог у Telegram": {
        "price": "200₴",
        "desc": "Повноцінний магазин у Telegram з категоріями та товарами."
    },
    "⚙️ Встановлення і запуск": {
        "price": "30₴",
        "desc": "Ми допоможемо встановити і запустити бота на вашому сервері/ПК."
    },
    "⚙️ Щомісячна підтримка": {
        "price": "80₴",
        "desc": "Підтримка та оновлення всіх сервісів протягом місяця."
    },
    "🚀 Реклама в каналах": {
        "price": "50₴",
        "desc": "Розміщення реклами у Telegram каналах з невеликою аудиторією."
    },
    "📅 Підписка на 30 днів": {
        "price": "100₴",
        "desc": "Дає доступ до всіх сервісів компанії протягом 30 днів."
    }
}

# 🏠 Стартове меню
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📂 Каталог")
    btn2 = types.KeyboardButton("👑 Моя підписка")
    btn3 = types.KeyboardButton("📖 FAQ")
    btn4 = types.KeyboardButton("🆘 Підтримка")
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id,
                     "👋 Вітаємо у *NEXTBOT COMPANY*!\n\nОберіть дію нижче:",
                     reply_markup=markup, parse_mode="Markdown")

# 📂 Каталог
@bot.message_handler(func=lambda message: message.text == "📂 Каталог")
def show_catalog(message):
    markup = types.InlineKeyboardMarkup()
    for item, data in catalog.items():
        markup.add(types.InlineKeyboardButton(
            text=f"{item} — {data['price']}", callback_data=f"info_{item}"
        ))
    bot.send_message(message.chat.id, "📂 Наш каталог послуг:", reply_markup=markup)

# 📌 Показ описания услуги
@bot.callback_query_handler(func=lambda call: call.data.startswith("info_"))
def service_info(call):
    service = call.data.replace("info_", "")
    data = catalog[service]
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🛒 Купити", callback_data=f"order_{service}"),
        types.InlineKeyboardButton("🔙 Назад", callback_data="back_catalog")
    )
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"*{service}*\n\n{data['desc']}\n💵 Ціна: {data['price']}",
        parse_mode="Markdown",
        reply_markup=markup
    )

# 🔙 Назад в каталог
@bot.callback_query_handler(func=lambda call: call.data == "back_catalog")
def back_to_catalog(call):
    show_catalog(call.message)

# 📌 Обработка заказа
@bot.callback_query_handler(func=lambda call: call.data.startswith("order_"))

def order_service(call):
    service = call.data.replace("order_", "")
    bot.send_message(
        call.message.chat.id,
        f"✅ Ви обрали: *{service}*\n\n"
        f"💵 Для оплати використайте карту:\n"
        f"4242 4242 4242 4242\n\n"
        f"📩 Після оплати прикріпіть чек, і ми одразу підтвердимо замовлення.",
        parse_mode="Markdown"
    )

# 👑 Перевірка підписки
@bot.message_handler(func=lambda message: message.text == "👑 Моя підписка")
def my_subscription(message):
    user_id = message.chat.id
    if user_id in subscriptions and subscriptions[user_id] > datetime.now():
        end_date = subscriptions[user_id].strftime("%d.%m.%Y %H:%M")
        bot.send_message(user_id, f"✅ Ваша підписка активна до: *{end_date}*", parse_mode="Markdown")
    else:
        bot.send_message(user_id, "❌ У вас немає активної підписки.\nОформіть через каталог.")

# 📖 FAQ
@bot.message_handler(func=lambda message: message.text == "📖 FAQ")
def faq(message):
    text = (
        "📖 *Часті питання:*\n\n"
        "❓ *Як замовити?*\n"
        "— Оберіть послугу у каталозі, оплатіть та прикріпіть чек.\n\n"
        "❓ *Скільки часу займає виконання?*\n"
        "— Від 1 до 3 днів залежно від складності.\n\n"
        "❓ *Чи можна надіслати приклад?*\n"
        "— Так, напишіть у підтримку.\n"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# 🆘 Підтримка
@bot.message_handler(func=lambda message: message.text == "🆘 Підтримка")
def support(message):
    bot.send_message(
        message.chat.id,
        "🆘 Зверніться до нашої підтримки:\n\n@NextBot_SupportTeam"
    )

# 📩 Пересилка чеків
@bot.message_handler(content_types=['photo', 'document'])
def handle_payment_proof(message):
    bot.forward_message(ADMIN_CHAT_ID, message.chat.id, message.message_id)
    bot.send_message(
        message.chat.id,
        "✅ Чек отримано! Ми перевіримо та зв’яжемося з вами найближчим часом."
    )

# 👑 Адмін підтверджує підписку командою
@bot.message_handler(commands=['approve'])
def approve_subscription(message):
    if message.chat.id == ADMIN_CHAT_ID:
        try:
            args = message.text.split()
            if len(args) != 3:
                bot.send_message(ADMIN_CHAT_ID, "❌ Формат: /approve user_id днів")
                return

            user_id = int(args[1])
            days = int(args[2])
            subscriptions[user_id] = datetime.now() + timedelta(days=days)

            save_subscriptions()  # 🔥 Зберігаємо у файл

            end_date = subscriptions[user_id].strftime("%d.%m.%Y %H:%M")
            bot.send_message(user_id, f"🎉 Ваша підписка активована на {days} днів!\nДо: *{end_date}*", parse_mode="Markdown")
            bot.send_message(ADMIN_CHAT_ID, f"✅ Підписка активована для {user_id} на {days} днів")

        except Exception as e:
            bot.send_message(ADMIN_CHAT_ID, f"❌ Помилка: {e}")

# ▶️ Запуск
print("✅ Бот запускається...")
bot.polling(none_stop=True)

# 📌 Команда для получения ID пользователя
@bot.message_handler(commands=['myid'])
def my_id(message):
    bot.send_message(message.chat.id, f"🆔 Ваш user_id: {message.chat.id}", parse_mode="Markdown")
