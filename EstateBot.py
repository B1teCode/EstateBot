import telebot
import re
from telebot import types

bot = telebot.TeleBot('TOKEN')

user_data = {}

# Стартовая команда
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Валюта TJS")
    btn2 = types.KeyboardButton("Валюта USD")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Добрый день! Этот бот поможет вам рассчитать общую стоимость недвижимости. Пожалуйста, выберите валюту, в которой хотите произвести расчет:", reply_markup=markup)

def create_currency_markup(selected_currency=None):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1_text = "Валюта TJS ✅" if selected_currency == "TJS" else "Валюта TJS"
    btn2_text = "Валюта USD ✅" if selected_currency == "USD" else "Валюта USD"
    btn1 = types.KeyboardButton(btn1_text)
    btn2 = types.KeyboardButton(btn2_text)
    btn_new_calc = types.KeyboardButton("Новый расчет")
    markup.add(btn1, btn2)
    markup.add(btn_new_calc)
    return markup

# Обработка выбора валюты
@bot.message_handler(regexp="Валюта (TJS|USD)")
def currency_choice(message):
    chat_id = message.chat.id
    currency = message.text.split()[1]
    if chat_id not in user_data:
        user_data[chat_id] = {}
    user_data[chat_id]['currency'] = currency
    markup = create_currency_markup(currency)
    bot.send_message(chat_id, f"Вы выбрали валюту {currency}. Пожалуйста, введите площадь дома в квадратных метрах:", reply_markup=markup)

# Обработка команды "Новый расчет"
@bot.message_handler(regexp="Новый расчет")
def new_calculation(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        currency = user_data[chat_id].get('currency', None)
        user_data[chat_id] = {'currency': currency}
    markup = create_currency_markup(currency)
    bot.send_message(chat_id, "Пожалуйста, введите площадь дома в квадратных метрах:", reply_markup=markup)

# Обработка текстовых сообщений
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    chat_id = message.chat.id
    text = message.text

    if chat_id not in user_data or 'currency' not in user_data[chat_id]:
        bot.send_message(chat_id, "Пожалуйста, сначала выберите валюту, отправив /start.")
        return

    def extract_number(text):
        match = re.search(r'(\d+(\.\d+)?)', text)
        return float(match.group(1)) if match else None

    if 'square_meters' not in user_data[chat_id]:
        square_meters = extract_number(text)
        if square_meters is not None:
            user_data[chat_id]['square_meters'] = square_meters
            bot.send_message(chat_id, "Площадь дома успешно принята. Теперь введите цену за один квадратный метр:")
        else:
            bot.send_message(chat_id, "Пожалуйста, введите корректное число для площади дома.")
    elif 'price_per_square_meter' not in user_data[chat_id]:
        price_per_square_meter = extract_number(text)
        if price_per_square_meter is not None:
            user_data[chat_id]['price_per_square_meter'] = price_per_square_meter

            # Вычисление общей стоимости
            total_price = user_data[chat_id]['square_meters'] * user_data[chat_id]['price_per_square_meter']
            currency = user_data[chat_id]['currency']
            bot.send_message(chat_id, f"Общая стоимость недвижимости составляет: {total_price} {currency}.")

            # Сброс данных пользователя, оставляя выбранную валюту
            currency = user_data[chat_id]['currency']
            user_data[chat_id] = {'currency': currency}
            markup = create_currency_markup(currency)
            bot.send_message(chat_id, "Если вам нужно произвести новый расчет, введите площадь дома в квадратных метрах:", reply_markup=markup)
        else:
            bot.send_message(chat_id, "Пожалуйста, введите корректное число для цены за квадратный метр.")
    else:
        bot.send_message(chat_id, "Пожалуйста, введите корректные данные.")

bot.polling(none_stop=True, interval=0, timeout=20)
