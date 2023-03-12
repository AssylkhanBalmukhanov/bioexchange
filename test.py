import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
bot = telebot.TeleBot('')
goods = []
user_goods = {}
admin_id = ''
@bot.message_handler(commands=['start'])
def start(message):
    keyboard = InlineKeyboardMarkup()
    sell_button = InlineKeyboardButton('Sell', callback_data='sell')
    buy_button = InlineKeyboardButton('Buy', callback_data='buy')
    my_goods_button = InlineKeyboardButton('My Goods', callback_data='my_goods')
    report_button = InlineKeyboardButton('Report', callback_data='report')
    keyboard.add(sell_button, buy_button, my_goods_button, report_button)
    bot.send_message(message.chat.id, 'Choose a command:', reply_markup=keyboard)
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'sell':
        bot.send_message(call.message.chat.id, "What is the name of the good?")
        bot.register_next_step_handler(call.message, sell_price)
    elif call.data == 'buy':
        if len(goods) == 0:
            bot.send_message(call.message.chat.id, "There are no goods available for purchase.")
        else:
            for good in goods:
                bot.send_message(call.message.chat.id, f"Name: {good['name']}\nPrice: {good['price']}\nContacts: {good['contacts']}")
    elif call.data == 'my_goods':
        user_goods = [good for good in goods if good['seller_id'] == call.from_user.id]
        if len(user_goods) == 0:
            bot.send_message(call.message.chat.id, "You haven't added any goods yet.")
        else:
            for good in user_goods:
                bot.send_message(call.message.chat.id, f"Name: {good['name']}\nPrice: {good['price']}\nContacts: {good['contacts']}")
                keyboard = InlineKeyboardMarkup()
                remove_button = InlineKeyboardButton('Remove', callback_data=f'remove {good["name"]}')
                keyboard.add(remove_button)
                bot.send_message(call.message.chat.id, 'Choose an action:', reply_markup=keyboard)
    elif call.data.startswith('remove'):
        name = call.data.split()[1]
        user_goods = [good for good in goods if good['seller_id'] == call.from_user.id]
        for i, good in enumerate(user_goods):
            if good['name'] == name:
                del goods[i]
                bot.send_message(call.message.chat.id, f"{name} has been removed from the list of goods.")
                return
        bot.send_message(call.message.chat.id, f"Sorry, {name} was not found in your list of goods.")
    elif call.data == 'report':
        bot.send_message(call.message.chat.id, "Please enter your report:")
        bot.register_next_step_handler(call.message, lambda msg: report(msg))


def sell_price(message):
    name = message.text
    bot.send_message(message.chat.id, "What is the price of the good?")
    bot.register_next_step_handler(message, lambda msg, n=name: add_contact(msg, n))


def add_contact(message, name):
    price = message.text
    bot.send_message(message.chat.id, "What are your contacts?")
    bot.register_next_step_handler(message, lambda msg, n=name, p=price: add_to_base(msg, n, p, message.from_user.id))

def add_to_base(message, name, price, seller_id):
    contacts = message.text
    goods.append({"name": name, "price": price, "contacts": contacts, "seller_id": seller_id})
    bot.send_message(message.chat.id, "The good has been added to the list.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('remove'))
def remove_good(call):
    name = call.data.split()[1]
    user_goods = [good for good in goods if good['seller_id'] == call.from_user.id]
    for i, good in enumerate(user_goods):
        if good['name'] == name:
            del goods[i]
            bot.send_message(call.message.chat.id, f"{name} has been removed from the list of goods.")
            return
    bot.send_message(call.message.chat.id, f"Sorry, {name} was not found in your list of goods.")

@bot.message_handler(commands=['report'])
def report(msg):
    chat_id = msg.chat.id
    user_id = msg.from_user.id
    text = msg.text

    report_text = f"New report from user {user_id} in chat {chat_id}:\n\n{text}"
    bot.send_message(admin_id, report_text)
    bot.send_message(chat_id, "Thank you for your report. We will review it as soon as possible.")

def handle_report(message):
    report(message)

@bot.callback_query_handler(func=lambda call: call.data == 'report')
def report_callback_handler(call):
    bot.send_message(call.message.chat.id, "Please enter your report:")
    bot.register_next_step_handler(call.message, handle_report)




bot.polling(none_stop=True)
