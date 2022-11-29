import json
import os
import logging
import redis
import telegram
import api_store_methods as api
from textwrap import dedent

from pprint import pprint
from environs import Env
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Filters, Updater, CallbackContext
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler

_database = None


def get_markup_and_data_products(context: CallbackContext):
    products = api.method_api(api.get_products)
    data_products = {}
    custom_keyboard = []
    for product in products['data']:
        data_products.update(
            {
                product['id']: {
                    'name': product['attributes']['name'],
                    'price': product['meta']['display_price']['without_tax']['formatted'],
                    'description': product['attributes'].get('description', 'Описание не задано'),
                    'sku': product['attributes']['sku'],
                    'main_image_id': product['relationships']['main_image']['data']['id']
                }
            }
        )
        custom_keyboard.append(
            [InlineKeyboardButton(product['attributes']['name'], callback_data=product['id'])]
        )
    custom_keyboard.append([InlineKeyboardButton('Корзина', callback_data='/cart')])
    redis_connect = context.dispatcher.redis
    redis_connect.set('data_products', json.dumps(data_products))

    return InlineKeyboardMarkup(
        inline_keyboard=custom_keyboard,
        resize_keyboard=True
    )


def start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Please choose:',
        reply_markup=get_markup_and_data_products(context)
    )

    return "HANDLE_MENU"


def send_info_product(update: Update, context: CallbackContext):
    message_id = update.effective_message.message_id
    chat_id = update.effective_chat.id
    product_id = update.callback_query.data
    redis_connect = context.dispatcher.redis
    data_products = json.loads(redis_connect.get('data_products'))
    price = data_products[product_id]['price']
    name = data_products[product_id]['name']
    description = data_products[product_id]['description']
    main_image_id = data_products[product_id]['main_image_id']
    link_image = api.method_api(api.get_file, file_id=main_image_id)['data']['link']['href']
    msg = f'''
        {name}
        {price} per kg
        {description}
        '''
    custom_keyboard = [
        [
            InlineKeyboardButton('1 кг', callback_data=f'1_{product_id}'),
            InlineKeyboardButton('5 кг', callback_data=f'5_{product_id}'),
            InlineKeyboardButton('10 кг', callback_data=f'10_{product_id}'),
        ],
        [
            InlineKeyboardButton('Корзина', callback_data='/cart')
        ],
        [
            InlineKeyboardButton('Меню', callback_data='/start')
        ],

    ]
    context.bot.send_photo(
        chat_id,
        photo=link_image,
        caption=dedent(msg),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=custom_keyboard, resize_keyboard=True)
    )
    context.bot.delete_message(chat_id, message_id)

    return "HANDLE_DESCRIPTION"


def handle_description(update: Update, context: CallbackContext):
    callback_data = update.callback_query.data
    quantity = int(callback_data.split('_')[0])
    product_id = callback_data.split('_')[1]
    api.method_api(api.get_cart, reference=update.effective_user.id)
    api.method_api(
        api.add_product_to_cart,
        product_id=product_id,
        quantity=quantity,
        reference=update.effective_user.id
    )
    return "HANDLE_DESCRIPTION"


def get_cart_info(update: Update, context: CallbackContext):
    total_value = (
        api.method_api(api.get_cart, update.effective_user.id)
        ['data']['meta']['display_price']['without_tax']['formatted']
    )
    cart_items = api.method_api(api.get_cart_items, update.effective_user.id)
    msg = ''
    custom_keyboard = []
    for item in cart_items['data']:
        msg += f'''
        {item['name']}
        {item['description']}
        {item['meta']['display_price']['without_tax']['unit']['formatted']} per kg
        {item['quantity']}kg in cart for {item['meta']['display_price']['without_tax']['value']['formatted']}
        '''
        custom_keyboard.append(
            [InlineKeyboardButton(f'Убрать из корзины {item["name"]}', callback_data=item['id'])]
        )
    custom_keyboard.append([InlineKeyboardButton('В меню', callback_data='/start')])
    custom_keyboard.append([InlineKeyboardButton('Оплата', callback_data='/pay')])
    msg = f'''
        {msg}        
        Total: {total_value}
        '''
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=dedent(msg),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=custom_keyboard, resize_keyboard=True)
    )

    return 'HANDLER_CART'


def handler_cart(update: Update, context: CallbackContext):
    id_cart_item = update.callback_query.data
    api.method_api(api.remove_cart_item, update.effective_user.id, id_cart_item)
    total_value = (
        api.method_api(api.get_cart, update.effective_user.id)
        ['data']['meta']['display_price']['without_tax']['formatted']
    )
    cart_items = api.method_api(api.get_cart_items, update.effective_user.id)
    msg = ''
    custom_keyboard = []
    for item in cart_items['data']:
        msg += f'''
            {item['name']}
            {item['description']}
            {item['meta']['display_price']['without_tax']['unit']['formatted']} per kg
            {item['quantity']}kg in cart for {item['meta']['display_price']['without_tax']['value']['formatted']}
            '''
        custom_keyboard.append(
            [InlineKeyboardButton(f'Убрать из корзины {item["name"]}', callback_data=item['id'])]
        )
    custom_keyboard.append([InlineKeyboardButton('В меню', callback_data='/start')])
    msg = f'''
            {msg}        
            Total: {total_value}
            '''
    context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id,
        text=dedent(msg),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=custom_keyboard, resize_keyboard=True)
    )
    return 'HANDLER_CART'


def waiting_email(update: Update, context: CallbackContext):
    if update.callback_query and update.callback_query.data == '/pay':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Введите ваш email',
        )
        return 'WAITING_EMAIL'
    else:
        email_user = update.message.text
        print(email_user)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Спасибо. Мы свяжемся с Вами!\nPlease choose:',
            reply_markup=get_markup_and_data_products(context)
        )
        return 'HANDLE_MENU'


def handle_users_reply(update: Update, context: CallbackContext):
    """
    Функция, которая запускается при любом сообщении от пользователя и решает как его обработать.
    Эта функция запускается в ответ на эти действия пользователя:
        * Нажатие на inline-кнопку в боте
        * Отправка сообщения боту
        * Отправка команды боту
    Она получает стейт пользователя из базы данных и запускает соответствующую функцию-обработчик (хэндлер).
    Функция-обработчик возвращает следующее состояние, которое записывается в базу данных.
    Если пользователь только начал пользоваться ботом, Telegram форсит его написать "/start",
    поэтому по этой фразе выставляется стартовое состояние.
    Если пользователь захочет начать общение с ботом заново, он также может воспользоваться этой командой.
    """
    db = get_database_connection(context.dispatcher.redis)
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    elif user_reply == '/cart':
        user_state = 'CART_INFO'
    elif user_reply == '/pay':
        user_state = 'WAITING_EMAIL'
    else:
        user_state = db.get(chat_id).decode("utf-8")

    states_functions = {
        'START': start,
        'HANDLE_MENU': send_info_product,
        'HANDLE_DESCRIPTION': handle_description,
        'CART_INFO': get_cart_info,
        'HANDLER_CART':  handler_cart,
        'WAITING_EMAIL': waiting_email
    }
    state_handler = states_functions[user_state]
    # Если вы вдруг не заметите, что python-telegram-bot перехватывает ошибки.
    # Оставляю этот try...except, чтобы код не падал молча.
    # Этот фрагмент можно переписать.
    try:
        next_state = state_handler(update, context)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)


def get_database_connection(redis_db):
    """
    Возвращает конекшн с базой данных Redis, либо создаёт новый, если он ещё не создан.
    """
    global _database
    if _database is None:
        _database = redis_db
    return _database


if __name__ == '__main__':
    env = Env()
    env.read_env()
    token = env('TELEGRAM_TOKEN')
    database_password = env('DATABASE_PASSWORD')
    database_host = env('DATABASE_HOST')
    database_port = env('DATABASE_PORT')
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.redis = redis.Redis(host=database_host, port=database_port, password=database_password)
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()
