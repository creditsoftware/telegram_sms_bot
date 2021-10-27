from telebot import types

import sqlite3

main_menu_btn = [
    '🔥 Comprar',
    '👤 Minha conta',
    '💵 Depositar',
    'skip',
    '👥 Informações',
]

admin_sending_btn = [
    '✅ Iniciar', # 0
    '🔧 Prorrogar', # 1
    '❌ Cancelar' # 2
]

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(
        main_menu_btn[0],
        main_menu_btn[4],
    )
    markup.add(
        main_menu_btn[1],
        main_menu_btn[2],
        #main_menu_btn[3],
    )

    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    base = cursor.execute(f'SELECT * FROM buttons').fetchall()

    for i in base:
        markup.add(i[0])

    return markup


btn_purchase = types.InlineKeyboardMarkup(row_width=2)
btn_purchase.add(
    types.InlineKeyboardButton(text='Buy', callback_data='buy'),
    types.InlineKeyboardButton(text='Cancel', callback_data='exit_to_menu')
)


# Admin menu
admin_menu = types.InlineKeyboardMarkup(row_width=1)
admin_menu.add(
    types.InlineKeyboardButton(text='ℹ️ Estatisticas', callback_data='admin_info'),
    types.InlineKeyboardButton(text='🔧 Adicionar saldo', callback_data='give_balance'),
    types.InlineKeyboardButton(text='⚙️ Enviar', callback_data='email_sending'),
    types.InlineKeyboardButton(text='⚙️ Botões', callback_data='admin_buttons'),
    types.InlineKeyboardButton(text='⚙️ Números', callback_data='admin_numbers'),
    types.InlineKeyboardButton(text='⚙️ Configurações', callback_data='admin_settings')
    )


admin_buttons = types.InlineKeyboardMarkup(row_width=2)
admin_buttons.add(
    types.InlineKeyboardButton(text='🔧 Adicionar', callback_data='admin_buttons_add'),
    types.InlineKeyboardButton(text='🔧 Deletar', callback_data='admin_buttons_del'),
    types.InlineKeyboardButton(text='❌ Cancelar', callback_data='back_to_admin_menu')
)


admin_numbers = types.InlineKeyboardMarkup(row_width=1)
admin_numbers.add(
    types.InlineKeyboardButton(text='🔧 Alterar preço', callback_data='admin_numbers_set_price'),
    types.InlineKeyboardButton(text='❌ Cancelar', callback_data='back_to_admin_menu')
)


admin_sending = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
admin_sending.add(
    admin_sending_btn[0],
    admin_sending_btn[1],
    admin_sending_btn[2],
)


admin_bot_settings = types.InlineKeyboardMarkup(row_width=1)
admin_bot_settings.add(
    types.InlineKeyboardButton(text='⚙️ QIWI', callback_data='admin_bot_settings_qiwi'),
    types.InlineKeyboardButton(text='🔧 Referral percent', callback_data='admin_bot_settings_ref'),
    types.InlineKeyboardButton(text='🔧 API SMS ACTIVATE.RU', callback_data='admin_bot_settings_api_sms'),
    types.InlineKeyboardButton(text='❌ Cancelar', callback_data='back_to_admin_menu')
    )

admin_bot_settings_qiwi_menu = types.InlineKeyboardMarkup(row_width=1)
admin_bot_settings_qiwi_menu.add(
    types.InlineKeyboardButton(text='🔧 QIWI num', callback_data='admin_bot_settings_qiwi_number'),
    types.InlineKeyboardButton(text='🔧 QIWI api', callback_data='admin_bot_settings_qiwi_token'),
    types.InlineKeyboardButton(text='❌ Cancelar', callback_data='back_to_admin_menu')
    )

# Back to admin menu
back_to_admin_menu = types.InlineKeyboardMarkup(row_width=1)
back_to_admin_menu.add(
    types.InlineKeyboardButton(text='Voltar ao Menu', callback_data='back_to_admin_menu')
)


back_to_m_menu = types.InlineKeyboardMarkup(row_width=1)
back_to_m_menu.add(
    types.InlineKeyboardButton(text='Voltar ao Menu', callback_data='exit_to_menu')
)


btn_ok = types.InlineKeyboardMarkup(row_width=3)
btn_ok.add(
    types.InlineKeyboardButton(text='Understand', callback_data='btn_ok')
)


to_close = types.InlineKeyboardMarkup(row_width=3)
to_close.add(
    types.InlineKeyboardButton(text='❌', callback_data='to_close')
)

def get_code_menu(code):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='Get Code', callback_data=f'get_code_{code}'),
    )

    return markup


def good_code(code):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='Confirm getting a code', callback_data=f'good_code_{code}'),
    )

    return markup


def email_sending():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='✔️ Enviar(Apenas texto)', callback_data='email_sending_text'),
        types.InlineKeyboardButton(text='✔️ Enviar(Texto + imgagem)', callback_data='email_sending_photo'),
        types.InlineKeyboardButton(text='ℹ️ syntax info', callback_data='email_sending_info')
    )

    return markup


def payment_menu(url):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='👉 Depositar 👈', url=url),
    )
    markup.add(
        types.InlineKeyboardButton(text='🔄 Checar', callback_data='check_payment'),
        types.InlineKeyboardButton(text='❌ Cancelar', callback_data='cancel_payment'),
    )

    return markup


def buy_num_menu(code, number):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(text='✅ Concluido', callback_data=f'num_end_{code}'),
        types.InlineKeyboardButton(text='🔄 Solicitar novo SMS', callback_data=f'num_req_{code}_{number}')
    )

    return markup
