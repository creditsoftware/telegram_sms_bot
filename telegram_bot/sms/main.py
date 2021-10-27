#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import menu
import settings
import functions as func
from functions import rl
import telebot
from telebot import types
import time
import datetime
import random
import threading
import config

import traceback

buy_dict = {}
balance_dict = {}
admin_sending_messages_dict = {}
product_dict = {}
download_dict = {}


def start_bot():
    bot = telebot.TeleBot(config.config('bot_token'), threaded=True, num_threads=300)

    # Command start
    @bot.message_handler(commands=['start'])
    def handler_start(message):
        chat_id = message.chat.id
        resp = func.first_join(user_id=chat_id, name=message.from_user.username, code=message.text[7:])

        with open('welcome.jpg', 'rb') as photo:
            bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption='- Bem-vindo {}\n- Seu ID - {}\n- 💵 @adicionar_saldo_bot '.format(message.from_user.first_name,
                                                                    chat_id,),
                reply_markup=menu.main_menu()
            )

    # Command adminkelri3759
    @bot.message_handler(commands=['adminkelri3759'])
    def handler_admin(message):
        chat_id = message.chat.id
        if str(chat_id) in func.admin_id_manager():
            bot.send_message(chat_id, 'Você foi ao menu de administração', reply_markup=menu.admin_menu)


    @bot.message_handler(content_types=['text'])
    def send_message(message):

        if str(message.chat.id) in func.ban():
            print('spam')
        else:
            chat_id = message.chat.id
            first_name = message.from_user.first_name
            username = message.from_user.username

            if message.text in func.btn_menu_list():
                conn = sqlite3.connect('base.db')
                cursor = conn.cursor()

                base = cursor.execute(f'SELECT * FROM buttons WHERE name = "{message.text}"').fetchone()

                with open(f'{base[2]}.jpg', 'rb') as photo:
                    bot.send_photo(
                        chat_id=chat_id,
                        photo=photo,
                        caption=base[1]
                    )

            if message.text == menu.main_menu_btn[0]:
                try:
                    bot.send_message(
                            chat_id=chat_id,
                            text=func.info_numbers(chat_id),
                            reply_markup=func.buy_number_menu()
                        )
                except: pass

            if message.text == menu.main_menu_btn[1]:
                try:
                    info = func.profile(chat_id)
                    msg = settings.profile.format(
                            id=info[0],
                            login=f'@{info[1]}',
                            data=info[2][:19],
                            balance=rl(info[5])
                        ),
                    bot.send_message(
                        chat_id=chat_id,
                        text=msg)
                except Exception as e: pass

            if message.text == func.get_info_pr:
                bot.send_message(
                    chat_id=chat_id,
                    text=func.get_info_pr1()
                )


            if message.text == menu.main_menu_btn[2]:
                bot.send_message(
                    chat_id=chat_id,
                    text=settings.info,
                    reply_markup=menu.main_menu(),
                    parse_mode='html'
                )

            if message.text == menu.main_menu_btn[3]:
                try:
                    resp = func.replenish_balance(chat_id)
                    bot.send_message(chat_id=chat_id,
                                        text=resp[0],
                                        reply_markup=resp[1],
                                        parse_mode='html')
                except: pass

            if message.text == menu.main_menu_btn[4]:
                try:
                    ref_code = func.check_ref_code(chat_id)
                    bot.send_message(
                        chat_id=chat_id,
                        text='''⚙️ Informações

🔻Depósito mínimo R$ 7,20
⚠️ Pague só quando chega o código
⚙️ Atendemos até as 21 hrs
⏰ Não precisa esperar o reembolso
💰 Recargas feitas via pix Copia e Cola
♻️ Todo dia são adicionados Chips
💵 Aceitamos picpay e Mercado Pago
💰 Picpay.me/meunumerovirtual
💰 MP: pagae@meunumerovirtual.com
💵 Pagando p/ Picpay|Mercado Pago
👇🏽 Comprovante p/ o nosso suporte

⚙️ Nosso suporte: @suporte_numero 
                      ''',
                        reply_markup=menu.main_menu(),
                        parse_mode='html'                        )
                except Exception as e: print(e)

    # Обработка данных
    @bot.callback_query_handler(func=lambda call: True)
    def handler_call(call):
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        try:

            if call.data in ['adds2', 'adds1', 'adds3', 'buy_numbers', 'info', 'profile', 'replenish_balance', 'referral_web']:
                bot.send_message(
                    chat_id=chat_id,
                    text='Temos um novo menu 👇',
                    reply_markup=menu.main_menu()
                )

            if call.data == 'email_sending':
                    bot.send_message(
                        chat_id=chat_id,
                        text='Selecione uma opção de envio',
                        reply_markup=menu.email_sending()
                    )

            if call.data == 'email_sending_photo':
                    msg = bot.send_message(
                        chat_id=chat_id,
                        text='Mande uma foto para o bot, só uma foto!',
                        )

                    bot.clear_step_handler_by_chat_id(chat_id)
                    bot.register_next_step_handler(msg, email_sending_photo)

            if call.data == 'email_sending_text':
                    msg = bot.send_message(
                        chat_id=chat_id,
                        text='Digite o seu texto de envio',
                        )

                    bot.clear_step_handler_by_chat_id(chat_id)
                    bot.register_next_step_handler(msg, admin_sending_messages)

            if 'get_code_' in call.data:
                code = func.get_code(call.data[9:])
                if str(code[0]) == 'STATUS_OK':
                    bot.send_message(
                        chat_id=chat_id,
                        text=f'СТАТУС: {code[0]}\n'
                            f'O código: <code>{code[1]}</code>',
                        reply_markup=code[2],
                        parse_mode='html'
                    )
                else:
                    bot.send_message(
                        chat_id=chat_id,
                        text='O SMS não veio'
                    )

            if 'buynum_' in call.data:
                if func.check_balance(chat_id, func.check_price_number(call.data[7:])) == 1:
                    info = func.Buy(chat_id)
                    buy_dict[chat_id] = info
                    info = buy_dict[chat_id]
                    info.code = call.data[7:]

                    try:
                        info = buy_dict[chat_id]
                        resp = func.buy_number(info)

                        if resp[0] == True:
                            bot.send_message(
                                chat_id=chat_id,
                                text=f'País: {func.get_country_name(call.data[10:])}\nServiço: {func.get_service_name(call.data[7:])}\nNúmero  : {resp[1]}\nStatus : Aguardando SMS\nTime de reembolso: 7 Min',
                                parse_mode='html'
                            )
                            threading.Thread(target=buy_th(chat_id, resp[2], resp[1], resp[3], call.from_user.first_name, call.from_user.username, info.code))
                        else:
                            bot.send_message(
                                chat_id=chat_id,
                                text=f'<i>Não há números disponiveis no momento, espere Reabastecermos!</i>',
                                parse_mode='html'
                            )
                    except Exception as e:
                        print(e)
                else:
                    bot.send_message(
                        chat_id=chat_id,
                        text='Não há saldo suficiente. '
                    )

            if call.data == 'exit_to_menu':
                bot.send_message(
                    chat_id=chat_id,
                    text='Você voltou ao menu principal',
                    reply_markup=menu.main_menu()
                )

            if call.data == 'btn_ok':
                bot.delete_message(chat_id, message_id)

            # Admin menu
            if call.data == 'admin_info':
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=func.admin_info(),
                    reply_markup=menu.admin_menu
                )

            if call.data == 'exit_admin_menu':
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text='Você saiu do menu de administração',
                    reply_markup=menu.main_menu()
                )

            if call.data == 'back_to_admin_menu':
                bot.send_message(
                    chat_id=chat_id,
                    text='Você foi ao menu de administração'
                )

            if call.data == 'cancel_payment':
                func.cancel_payment(chat_id)
                bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text='❕ Добро пожаловать!')

            if call.data == 'check_payment':
                check = func.check_payment(chat_id)
                if check[0] == 1:
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=f'✅ Pagamento aprovado\nСумма - {check[1]} руб')

                if check[0] == 0:
                    bot.send_message(chat_id=chat_id,
                                    text='❌ Оплата не найдена',
                                    reply_markup=menu.to_close)

            if call.data == 'to_close':
                bot.delete_message(chat_id=chat_id,
                                message_id=message_id)

            if call.data == 'give_balance':
                msg = bot.send_message(chat_id=chat_id,
                                    text='Insira o ID para quem o saldo será alterado')

                bot.register_next_step_handler(msg, give_balance)

            if call.data == 'admin_sending_messages':
                msg = bot.send_message(chat_id,
                                    text='Digite o seu texto de envio')
                bot.register_next_step_handler(msg, admin_sending_messages)

            if call.data == 'admin_top_ref':
                bot.send_message(
                    chat_id=chat_id,
                    text=func.admin_top_ref(),
                    parse_mode='html'
                )

            if 'num_end_' in call.data:
                if func.cancel_number(call.data[8:]) == True:
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text='✅ O trabalho foi concluido'
                    )

            if 'num_req_' in call.data:
                code = call.data.split('_')[2]
                number = call.data.split('_')[3]
                if func.number_iteration(code) == True:
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=f'Para o número <code>+{number}</code> foi solicitado um novo código.',
                        parse_mode='html'
                    )

                    threading.Thread(target=buy_th_2(chat_id, code, number, call.from_user.first_name, call.from_user.username))

            if call.data in func.service_list():
                bot.send_message(
                    chat_id=chat_id,
                    text=func.get_info_number(call.data, chat_id),
                    reply_markup=func.get_menu(call.data)
                )

            if call.data == 'admin_buttons':
                bot.send_message(
                        chat_id=chat_id,
                        text='Configurações de botão',
                        reply_markup=menu.admin_buttons
                    )


            if call.data == 'admin_buttons_del':
                msg = bot.send_message(
                        chat_id=chat_id,
                        text=f'Selecione o número do botão que deseja excluir\n{func.list_btns()}'
                    )

                bot.clear_step_handler_by_chat_id(chat_id)
                bot.register_next_step_handler(msg, admin_buttons_del)


            if call.data == 'admin_buttons_add':
                msg = bot.send_message(
                        chat_id=chat_id,
                        text='Insira o nome do botão'
                    )

                bot.clear_step_handler_by_chat_id(chat_id)
                bot.register_next_step_handler(msg, admin_buttons_add)


            if call.data == 'admin_numbers':
                bot.send_message(
                        chat_id=chat_id,
                        text='⚙️ Configurações da sala',
                        reply_markup=menu.admin_numbers
                    )


            if call.data == 'admin_numbers_set_price':
                msg = bot.send_message(
                        chat_id=chat_id,
                        text=f'Digite o número do serviço:\n\n{func.service_list_name()}'
                    )

                bot.clear_step_handler_by_chat_id(chat_id)
                bot.register_next_step_handler(msg, admin_numbers_set_price)


            if call.data == 'email_sending_info':
                bot.send_message(
                    chat_id=chat_id,
                    text="""
Use a seguinte sintaxe para destacar o texto em uma lista de e-mails:

1 | <b>bold</b>, <strong>bold</strong>
2 | <i>italic</i>, <em>italic</em>
3 | <u>underline</u>, <ins>underline</ins>
4 | <s>strikethrough</s>, <strike>strikethrough</strike>, <del>strikethrough</del>
5 | <b>bold <i>italic bold <s>italic bold strikethrough</s> <u>underline italic bold</u></i> bold</b>
6 | <a href="http://www.example.com/">inline URL</a>
7 | <a href="tg://user?id=123456789">inline mention of a user</a>
8 | <code>inline fixed-width code</code>
9 | <pre>pre-formatted fixed-width code block</pre>
10 | <pre><code class="language-python">pre-formatted fixed-width code block written in the Python programming language</code></pre>
""")
                bot.send_message(
                        chat_id=chat_id,
                        text="""
É assim que vai ficar na lista de e-mails:

1 | <b>bold</b>, <strong>bold</strong>
2 | <i>italic</i>, <em>italic</em>
3 | <u>underline</u>, <ins>underline</ins>
4 | <s>strikethrough</s>, <strike>strikethrough</strike>, <del>strikethrough</del>
5 | <b>bold <i>italic bold <s>italic bold strikethrough</s> <u>underline italic bold</u></i> bold</b>
6 | <a href="http://www.example.com/">inline URL</a>
7 | <a href="tg://user?id=123456789">inline mention of a user</a>
8 | <code>inline fixed-width code</code>
9 | <pre>pre-formatted fixed-width code block</pre>
10 | <pre><code class="language-python">pre-formatted fixed-width code block written in the Python programming language</code></pre>
""",
                    parse_mode='html'
                    )

            if call.data == 'admin_settings':
                if str(chat_id) in func.admin_id_own():
                    bot.send_message(
                            chat_id=chat_id,
                            text=f'⚙️ Configurações do bot',
                            reply_markup=menu.admin_bot_settings
                        )

            if call.data == 'admin_bot_settings_ref':
                if str(chat_id) in func.admin_id_own():
                    msg = bot.send_message(
                            chat_id=chat_id,
                            text=f'🔧 Insira a nova porcentagem de ref. sistemas'
                        )

                    bot.clear_step_handler_by_chat_id(chat_id)
                    bot.register_next_step_handler(msg, admin_bot_settings_ref)


            if call.data == 'admin_bot_settings_api_sms':
                if str(chat_id) in func.admin_id_own():
                    msg = bot.send_message(
                            chat_id=chat_id,
                            text=f'🔧 Inserir novo codigo de api'
                        )

                    bot.clear_step_handler_by_chat_id(chat_id)
                    bot.register_next_step_handler(msg, admin_bot_settings_api_sms)


            if call.data == 'admin_bot_settings_qiwi':
                if str(chat_id) in func.admin_id_own():
                    bot.send_message(
                            chat_id=chat_id,
                            text=f'⚙️ Настройка QIWI',
                            reply_markup=menu.admin_bot_settings_qiwi_menu
                        )


            if call.data == 'admin_bot_settings_qiwi_number':
                if str(chat_id) in func.admin_id_own():
                    msg = bot.send_message(
                            chat_id=chat_id,
                            text=f'🔧 Введите новый QIWI номер'
                        )

                    bot.clear_step_handler_by_chat_id(chat_id)
                    bot.register_next_step_handler(msg, admin_bot_settings_qiwi_number)


            if call.data == 'admin_bot_settings_qiwi_token':
                if str(chat_id) in func.admin_id_own():
                    msg = bot.send_message(
                            chat_id=chat_id,
                            text=f'🔧 Введите новый QIWI токен'
                        )

                    bot.clear_step_handler_by_chat_id(chat_id)
                    bot.register_next_step_handler(msg, admin_bot_settings_qiwi_token)

        except Exception as e:
            print('CRASH')
            print(str(e))
            print(traceback.format_exc())
            #traceback.print_exc(e)


    def admin_bot_settings_qiwi_token(message):
        try:
            config.edit_config('qiwi_token', message.text)

            bot.send_message(
                chat_id=message.chat.id,
                text=f'🔧 QIWI токен изменен на {message.text}',
                reply_markup=menu.admin_bot_settings_qiwi_menu
            )
        except Exception as e:
            bot.send_message(
                chat_id=message.chat.id,
                text='⚠️ Algo deu errado')


    def admin_bot_settings_qiwi_number(message):
        try:
            config.edit_config('qiwi_number', message.text)

            bot.send_message(
                chat_id=message.chat.id,
                text=f'🔧 QIWI номер изменен на {message.text}',
                reply_markup=menu.admin_bot_settings_qiwi_menu
            )
        except Exception as e:
            bot.send_message(
                chat_id=message.chat.id,
                text='⚠️ Algo deu errado')


    def admin_bot_settings_api_sms(message):
        try:
            config.edit_config('api_smshub', message.text)

            bot.send_message(
                chat_id=message.chat.id,
                text=f'🔧 API SMSHUB alterada para {message.text}',
                reply_markup=menu.admin_bot_settings
            )
        except Exception as e:
            bot.send_message(
                chat_id=message.chat.id,
                text='⚠️ Algo deu errado')


    def admin_bot_settings_ref(message):
        try:
            ref = int(message.text)
            config.edit_config('ref_percent', message.text)

            bot.send_message(
                chat_id=message.chat.id,
                text=f'🔧 Процент реф. системы изменен на {message.text}',
                reply_markup=menu.admin_bot_settings
            )
        except Exception as e:
            bot.send_message(
                chat_id=message.chat.id,
                text='⚠️ Algo deu errado')


    def sending_check():
        while True:
            try:
                info = func.sending_check()

                if info != False:
                    conn = sqlite3.connect('base.db')
                    cursor = conn.cursor()

                    cursor.execute(f'SELECT * FROM users')
                    row = cursor.fetchall()

                    start_time = time.time()
                    amount_message = 0
                    amount_bad = 0

                    if info[0] == 'text':
                        try:
                            bot.send_message(
                                chat_id=func.admin_id_manager().split(':')[0],
                                text=f'✅ Comece a enviar')
                        except: pass

                        for i in range(len(row)):
                            try:
                                bot.send_message(row[i][0], info[1], parse_mode='html')
                                amount_message += 1
                            except Exception as e:
                                amount_bad += 1

                        sending_time = time.time() - start_time

                        try:
                            bot.send_message(
                                chat_id=func.admin_id_manager().split(':')[0],
                                text=f'✅ A correspondência acabou\n'
                                f'❕ Enviado: {amount_message}\n'
                                f'❕ Não enviado: {amount_bad}\n'
                                f'🕐 Prazo de entrega de correspondência - {sending_time} секунд'

                                )
                        except:
                            print('ERROR ADMIN SENDING')
                        try:
                            bot.send_message(
                                chat_id=func.admin_id_manager().split(':')[1],
                                text=f'✅ A correspondência acabou\n'
                                f'❕ Enviado: {amount_message}\n'
                                f'❕ Não enviado: {amount_bad}\n'
                                f'🕐 Prazo de entrega de correspondência - {sending_time} секунд'

                                )
                        except:
                            print('ERROR ADMIN SENDING')

                    elif info[0] == 'photo':
                        try:
                            bot.send_message(
                                chat_id=func.admin_id_manager().split(':')[0],
                                text=f'✅ Comece a enviar')
                        except: pass


                        for i in range(len(row)):
                            try:
                                with open(f'photo/{info[2]}.jpg', 'rb') as photo:
                                    bot.send_photo(
                                        chat_id=row[i][0],
                                        photo=photo,
                                        caption=info[1],
                                        parse_mode='html')
                                amount_message += 1
                            except:
                                amount_bad += 1

                        sending_time = time.time() - start_time

                        try:
                            bot.send_message(
                                chat_id=func.admin_id_manager().split(':')[0],
                                text=f'✅ A correspondência acabou\n'
                                f'❕ Enviado: {amount_message}\n'
                                f'❕ Não enviado: {amount_bad}\n'
                                f'🕐 Prazo de entrega de correspondência - {sending_time} секунд'

                                )
                        except:
                            print('ERROR ADMIN SENDING')
                        try:
                            bot.send_message(
                                chat_id=func.admin_id_manager().split(':')[1],
                                text=f'✅ A correspondência acabou\n'
                                f'❕ Enviado: {amount_message}\n'
                                f'❕ Não enviado: {amount_bad}\n'
                                f'🕐 Prazo de entrega de correspondência - {sending_time} секунд'

                                )
                        except:
                            print('ERROR ADMIN SENDING')
                else:
                    time.sleep(15)
            except Exception as e: pass


    def buy_th_2(chat_id, cd, number, first_name, username):
        try:
            start_time = time.time()
            while True:
                code = func.get_code(cd)
                if str(code[0]) == 'STATUS_OK':
                    bot.send_message(
                        chat_id=chat_id,
                        text=f'Número: <code>{number}</code>\n'
                            f'Código de repetição: <code>{code[1]}</code>',
                        reply_markup=menu.back_to_m_menu,
                        parse_mode='html'
                    )
                    print('buy_th_2 good')

                    break
                else:
                    time.sleep(3)

                sending_time = time.time() - start_time

                print(f'buy_th_2 bad | time {sending_time}')

                if sending_time >= 420:
                    bot.send_message(
                        chat_id=chat_id,
                        text=f'O novo código solicitado para o número <code>{number}</code> não veio, o trabalho com o número está concluído',
                        reply_markup=menu.back_to_m_menu,
                        parse_mode='html'
                    )

                    if func.cancel_number(cd) == True:
                        print('buy_th_2 CANCEL')

                    break

        except:
            print('buy_th_2 ERROR')


    def buy_th(chat_id, cd, number, price, first_name, username, info_code):
        try:
            start_time = time.time()
            while True:
                code = func.get_code(cd)
                if str(code[0]) == 'STATUS_OK':
                    bot.send_message(
                        chat_id=chat_id,
                        text=f'Numero: <code>{number}</code>\n'
                            f'O código: <code>{code[1]}</code>',
                        reply_markup=menu.buy_num_menu(cd, number),
                        parse_mode='html'
                    )
                    print('buy_th good')

                    try:
                        func.number_logs(chat_id, first_name, username, f'+{number}', price, info_code, info_code)
                    except Exception as e: print(e)

                    break
                else:
                    time.sleep(3)

                sending_time = time.time() - start_time

                print(f'buy_th bad | time {sending_time}')

                if sending_time >= 420:
                    bot.send_message(
                        chat_id=chat_id,
                        text=f'O código do número <code>{number}</code> não veio, você foi reembolsado',
                        reply_markup=menu.back_to_m_menu,
                        parse_mode='html'
                    )

                    if func.cancel_number(cd) == True:
                        func.update_user_balance(chat_id, price)
                        print('buy_th CANCEL')


                    try:
                        func.number_logs(chat_id, first_name, username, f'+{number}', 0, info_code, 0)
                    except Exception as e: traceback.print_exc(e)
                    break

        except:
            print('buy_th ERROR')


    def give_balance(message):
        try:
            balance = func.GiveBalance(message.text)
            balance_dict[message.chat.id] = balance

            msg = bot.send_message(chat_id=message.chat.id,
                                   text='Insira o valor a ser adicionado')

            bot.register_next_step_handler(msg, give_balance_2)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='⚠️ Algo deu errado',
                             reply_markup=menu.main_menu())

    def give_balance_2(message):
        try:
            balance = balance_dict[message.chat.id]
            balance.balance = message.text
            msg = bot.send_message(chat_id=message.chat.id,
                                   text=f'ID - {balance.login}\n'
                                        f'Será adicionado R$ {balance.balance}\n'
                                        f'Digite ok para confirmar')

            bot.register_next_step_handler(msg, give_balance_3)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='⚠️ Algo deu errado',
                             reply_markup=menu.main_menu())

    def give_balance_3(message):
        try:
            balance = balance_dict[message.chat.id]
            if message.text == 'ok':
                func.give_balance(balance)
                bot.send_message(chat_id=message.chat.id,
                                 text='✅ Saldo alterado com sucesso')

        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='⚠️ Algo deu errado',
                             reply_markup=menu.main_menu())


    def email_sending_photo(message):
        chat_id = message.chat.id
        try:
            file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            admin_sending = func.Admin_sending_messages(message.chat.id)
            func.admin_sending_messages_dict[message.chat.id] = admin_sending

            admin_sending = func.admin_sending_messages_dict[message.chat.id]
            admin_sending.photo = random.randint(111111, 999999)
            admin_sending.type_sending = 'photo'

            with open(f'photo/{admin_sending.photo}.jpg', 'wb') as new_file:
                new_file.write(downloaded_file)

            msg = bot.send_message(
                chat_id=chat_id,
                text='Digite o seu texto de envio'
            )

            bot.register_next_step_handler(msg, email_sending_photo2)
        except Exception as e:
            traceback.print_exc(e)
            bot.send_message(
                chat_id=message.chat.id,
                text='⚠️ Algo deu errado')


    def email_sending_photo2(message):
        chat_id = message.chat.id
        try:

            admin_sending = func.admin_sending_messages_dict[message.chat.id]
            admin_sending.text = message.text

            with open(f'photo/{admin_sending.photo}.jpg', 'rb') as photo:
                bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=admin_sending.text
                )

            msg = bot.send_message(
                chat_id=chat_id,
                text='Escolha outra ação',
                reply_markup=menu.admin_sending
            )

            bot.register_next_step_handler(msg, email_sending_photo3)
        except:
            bot.send_message(
                chat_id=message.chat.id,
                text='⚠️ Algo deu errado')


    def email_sending_photo3(message):
        chat_id = message.chat.id
        try:
            admin_sending = func.admin_sending_messages_dict[message.chat.id]
            if message.text in menu.admin_sending_btn:
                if message.text == menu.admin_sending_btn[0]: # Начать
                    conn = sqlite3.connect('base.db')
                    cursor = conn.cursor()
                    cursor.execute(f'SELECT * FROM users')
                    row = cursor.fetchall()
                    start_time = time.time()
                    amount_message = 0
                    amount_bad = 0

                    try:
                        bot.send_message(
                            chat_id=func.admin_id_manager().split(':')[0],
                            text=f'✅ Você lançou uma lista de discussão',
                            reply_markup=menu.admin_menu)
                    except: pass


                    for i in range(len(row)):
                        try:
                            with open(f'photo/{admin_sending.photo}.jpg', 'rb') as photo:
                                bot.send_photo(
                                    chat_id=row[i][0],
                                    photo=photo,
                                    caption=admin_sending.text,
                                    parse_mode='html')
                            amount_message += 1
                        except:
                            amount_bad += 1

                    sending_time = time.time() - start_time

                    try:
                        bot.send_message(
                            chat_id=func.admin_id_manager().split(':')[0],
                            text=f'✅ A correspondência acabou\n'
                            f'❕ Enviado: {amount_message}\n'
                            f'❕ Não enviado: {amount_bad}\n'
                            f'🕐 Prazo de entrega de correspondência - {sending_time} секунд'

                            )
                    except:
                        print('ERROR ADMIN SENDING')
                    try:
                        bot.send_message(
                            chat_id=func.admin_id_manager().split(':')[1],
                            text=f'✅ A correspondência acabou\n'
                            f'❕ Enviado: {amount_message}\n'
                            f'❕ Não enviado: {amount_bad}\n'
                            f'🕐 Prazo de entrega de correspondência - {sending_time} секунд'

                            )
                    except:
                        print('ERROR ADMIN SENDING')
                elif message.text == menu.admin_sending_btn[1]: # Отложить
                    msg = bot.send_message(
                        chat_id=chat_id,
                        text="""
Вinsira a data de início do envio no formato: DIA: HORAS: MINUTOS\n

Нpor exemplo 18:14:10 - o envio será feito no dia 18 às 14:10
"""
                    )

                    bot.register_next_step_handler(msg, set_down_sending)
                elif message.text == menu.admin_sending_btn[2]:
                    bot.send_message(
                        message.chat.id,
                        text='Newsletter cancelada',
                        reply_markup=menu.main_menu
                    )
                    bot.send_message(
                        message.chat.id,
                        text='Menu de administração',
                        reply_markup=menu.admin_menu
                    )
            else:
                msg = bot.send_message(
                    message.chat.id,
                    text='Comando inválido, tente novamente.',
                    reply_markup=menu.admin_sending)

                bot.register_next_step_handler(msg, email_sending_photo3)
        except Exception as e:
            bot.send_message(
                chat_id=message.chat.id,
                text='⚠️ Algo deu errado')


    def set_down_sending(message):
        admin_sending = func.admin_sending_messages_dict[message.chat.id]
        date = message.text
        admin_sending.date = date

        if int(date.split(':')[0]) > 0 and int(date.split(':')[0]) < 33:
            if int(date.split(':')[1]) >= 0 and int(date.split(':')[1]) <= 24:
                if int(date.split(':')[2]) >= 0 and int(date.split(':')[2]) < 61:
                    msg = bot.send_message(
                        chat_id=message.chat.id,
                        text=f'Para confirmar o envio em {date} mandar +'
                    )

                    bot.register_next_step_handler(msg, set_down_sending_2)

    def set_down_sending_2(message):
        if message.text == '+':
            admin_sending = func.admin_sending_messages_dict[message.chat.id]

            func.add_sending(admin_sending)

            bot.send_message(
                chat_id=message.chat.id,
                text=f'O boletim informativo está agendado para {admin_sending.date}',
                reply_markup=menu.admin_menu
            )
        else:
            bot.send_message(message.chat.id, text='Рассылка отменена', reply_markup=menu.admin_menu)

    def admin_sending_messages(message):
        admin_sending = func.Admin_sending_messages(message.chat.id)
        func.admin_sending_messages_dict[message.chat.id] = admin_sending

        admin_sending = func.admin_sending_messages_dict[message.chat.id]
        admin_sending.text = message.text

        msg = bot.send_message(
            chat_id=message.chat.id,
            text='Escolha outra ação',
            reply_markup=menu.admin_sending)

        bot.register_next_step_handler(msg, admin_sending_messages_2)


    def admin_sending_messages_2(message):
        chat_id = message.chat.id

        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()

        admin_sending = func.admin_sending_messages_dict[message.chat.id]
        admin_sending.type_sending = 'text'

        if message.text in menu.admin_sending_btn:
            if message.text == menu.admin_sending_btn[0]: # Начать
                cursor.execute(f'SELECT * FROM users')
                row = cursor.fetchall()
                start_time = time.time()
                amount_message = 0
                amount_bad = 0

                try:
                    bot.send_message(
                        chat_id=func.admin_id_manager().split(':')[0],
                        text=f'✅ Вы запустили рассылку',
                        reply_markup=menu.admin_menu)
                except: pass

                for i in range(len(row)):
                    try:
                        bot.send_message(row[i][0], admin_sending.text, parse_mode='html')
                        amount_message += 1
                    except Exception as e:
                        amount_bad += 1

                sending_time = time.time() - start_time

                try:
                    bot.send_message(
                        chat_id=func.admin_id_manager().split(':')[0],
                        text=f'✅ A correspondência acabou\n'
                        f'❕ Enviado: {amount_message}\n'
                        f'❕ Não enviado: {amount_bad}\n'
                        f'🕐 Prazo de entrega de correspondência - {sending_time} секунд'

                        )
                except:
                    print('ERROR ADMIN SENDING')
                try:
                    bot.send_message(
                        chat_id=func.admin_id_manager().split(':')[1],
                        text=f'✅ Рассылка окончена\n'
                        f'❕ Enviado: {amount_message}\n'
                        f'❕ Não enviado: {amount_bad}\n'
                        f'🕐 Prazo de entrega de correspondência - {sending_time} секунд'

                        )
                except:
                    print('ERROR ADMIN SENDING')
            elif message.text == menu.admin_sending_btn[1]: # Отложить
                msg = bot.send_message(
                    chat_id=chat_id,
                    text="""
Insira a data de início do envio no formato: DIA: HORAS: MINUTOS\n

Por exemplo 18:14:10 - o envio será feito no dia 18 às 14:10
"""
                )

                bot.register_next_step_handler(msg, set_down_sending)
            elif message.text == menu.admin_sending_btn[2]:
                bot.send_message(
                    message.chat.id,
                    text='Newsletter cancelada',
                    reply_markup=menu.main_menu
                )
                bot.send_message(
                    message.chat.id,
                    text='Menu de administração',
                    reply_markup=menu.admin_menu
                )
            else:
                msg = bot.send_message(
                    message.chat.id,
                    text='Comando inválido, tente novamente',
                    reply_markup=menu.admin_sending)

    def admin_buttons_add(message):
        try:
            btn_dict = func.AdminButtons(message.chat.id)
            func.admin_buttons_dict[message.chat.id] = btn_dict
            btn_dict = func.admin_buttons_dict[message.chat.id]
            btn_dict.name = message.text

            msg = bot.send_message(
                chat_id=message.chat.id,
                text='Digite o texto')

            bot.register_next_step_handler(msg, admin_buttons_add2)

        except Exception as e:
            pass
            bot.send_message(
                chat_id=message.chat.id,
                text='⚠️ Algo deu errado')


    def admin_buttons_add2(message):
        try:
            btn_dict = func.admin_buttons_dict[message.chat.id]
            btn_dict.info = message.text

            msg = bot.send_message(
                chat_id=message.chat.id,
                text='Envie uma foto')

            bot.register_next_step_handler(msg, admin_buttons_add3)

        except Exception as e:
            bot.send_message(
                chat_id=message.chat.id,
                text='⚠️ Algo deu errado')


    def admin_buttons_add3(message):
        try:
            btn_dict = func.admin_buttons_dict[message.chat.id]
            btn_dict.photo = str(random.randint(11111, 99999))

            file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            with open(f'{btn_dict.photo}.jpg', 'wb') as new_file:
                new_file.write(downloaded_file)

            msg = bot.send_message(
                chat_id=message.chat.id,
                text='Para criar um botão escreva +')

            bot.register_next_step_handler(msg, admin_buttons_add4)

        except Exception as e:
            pass
            bot.send_message(
                chat_id=message.chat.id,
                text='⚠️ Algo deu errado')


    def admin_buttons_add4(message):
        try:
            btn_dict = func.admin_buttons_dict[message.chat.id]

            func.admin_add_btn(btn_dict.name, btn_dict.info, btn_dict.photo)

            bot.send_message(
                chat_id=message.chat.id,
                text='Botão criado',
                reply_markup=menu.admin_menu)

        except Exception as e:
            bot.send_message(
                chat_id=message.chat.id,
                text='⚠️ Algo deu errado')


    def admin_buttons_del(message):
        try:
            func.admin_del_btn(message.text)

            bot.send_message(
                chat_id=message.chat.id,
                text='Botão removido',
                reply_markup=menu.admin_menu)

        except Exception as e:
            print(e)
            bot.send_message(
                chat_id=message.chat.id,
                text='⚠️ Algo deu errado')


    def admin_numbers_set_price(message):
        try:
            set_price = func.Admin_set_price(message.chat.id)
            func.admin_set_price[message.chat.id] = set_price
            set_price = func.admin_set_price[message.chat.id]

            info = func.get_countries_list(int(message.text))

            set_price.service = info[0]

            msg = bot.send_message(
                chat_id=message.chat.id,
                text=f'Insira o número do país para o qual deseja alterar o preço:\n\n{info[1]}'
            )
            bot.register_next_step_handler(msg, admin_numbers_set_price_2)
        except Exception as e:
            bot.send_message(
                chat_id=message.chat.id,
                text='⚠️ Algo deu errado')


    def admin_numbers_set_price_2(message):
        try:
            set_price = func.admin_set_price[message.chat.id]
            set_price.country = int(message.text)

            msg = bot.send_message(
                chat_id=message.chat.id,
                text=f'Insira o preço'
            )
            bot.register_next_step_handler(msg, admin_numbers_set_price_3)

        except Exception as e:
            bot.send_message(
                chat_id=message.chat.id,
                text='⚠️ Algo deu errado')


    def admin_numbers_set_price_3(message):
        try:
            set_price = func.admin_set_price[message.chat.id]
            set_price.price = float(message.text)

            if func.change_price_number(set_price) == True:
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f'✅ O preço foi alterado com sucesso para {set_price.price} ₽',
                    reply_markup=menu.admin_numbers
                )
        except Exception as e:
            bot.send_message(
                chat_id=message.chat.id,
                text='⚠️ Algo deu errado')



    threading.Thread(target=sending_check).start()

    bot.polling(none_stop=True)



start_bot()
