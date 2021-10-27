from telegram.client import Telegram
# importContacts()
import signal
response = tg.call_method('importContacts', {
    'contacts': [
        {'phone_number': '+57 555 123 4567'},
    ]
})

response.wait()

user_ids = response.update['user_ids']

if user_ids[0] == 0:
    print('This contact is NOT using Telegram.')
else:
    print(f'¡This contact({user_ids[0]}) uses Telegram!')