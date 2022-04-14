from google.oauth2 import service_account
import google.cloud.dialogflow_v2 as dialogflow
from google.api_core.exceptions import InvalidArgument
import os

import telebot
from db import Database, Pairs, Marriages
import get_persons
import random
from datetime import datetime
from telebot import types
import wikipedia
import re
import locale
from commands import commands, triggers
import requests
import random
import time
import json
import random
import string
import webbrowser
from googlesearch import search
from vk import SearchVK


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "small-talk-nswb-7d4deae25c93.json"

credentials = service_account.Credentials.from_service_account_file(
    'small-talk-nswb-7d4deae25c93.json')

DIALOGFLOW_PROJECT_ID = 'small-talk-nswb'
DIALOGFLOW_LANGUAGE_CODE = 'ru-RU'
SESSION_ID = 'current-user-id'

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
bot = telebot.TeleBot('5157878096:AAFEIL4sVL-gkz2kL7nqj-dbtokHYITehYI')
group_id = '-1001178704810'
news_api_key = "1f169624b3mshca61b9482614219p16ea1cjsn0886c17ea21f"
weather_api_key = "d98344b5408f6523638d6932c483b253"

wikipedia.set_lang("ru")

x = 0


def chat_ai(message):
    try:
        text_to_be_analyzed = message.text
        session_client = dialogflow.SessionsClient(credentials=credentials)
        session = session_client.session_path(
            DIALOGFLOW_PROJECT_ID, SESSION_ID)
        text_input = dialogflow.types.TextInput(
            text=text_to_be_analyzed, language_code=DIALOGFLOW_LANGUAGE_CODE)
        query_input = dialogflow.types.QueryInput(text=text_input)
        try:
            response = session_client.detect_intent(
                session=session, query_input=query_input)
        except InvalidArgument:
            raise

        print("Query text:", response.query_result.query_text)
        print("Detected intent:", response.query_result.intent.display_name)
        print("Detected intent confidence:",
              response.query_result.intent_detection_confidence)
        resp = response.query_result.fulfillment_text
        bot.reply_to(message,
                     resp, parse_mode="Markdown")
    except:
        pass


def get_weather():
    api_key = weather_api_key
    city = "1508291"
    res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                       params={'id': city, 'units': 'metric', 'lang': 'ru', 'APPID': api_key})
    data = res.json()
    status = data['weather'][0]['description']
    temp = data['main']['temp']
    weath = []
    weath.append(status)
    weath.append(temp)
    return data


def vk_analize_person(message, name):
    try:
        result = SearchVK().get_vk_info(name)
        res = str(name)
        try:
            sex = result['response'][0]['sex']
            res += sex
        except:
            pass
        try:
            bdate = result['response'][0]['bdate']
            res += '\nРодился:'+str(bdate)
        except:
            pass
        try:
            city = result['response'][0]['city']['title']
            res += '\nПроживает в:'+str(city)
        except:
            pass
        try:
            country = result['response'][0]['country']['title']
            res += '\nСтрана:'+str(country)
        except:
            pass
        try:
            country = result['response'][0]['id']
            res += f'\n\nСсылка на вк: http://vk.com/id{country}'
        except:
            pass
        print(res)
        bot.reply_to(message,
                     res, parse_mode="Markdown")
    except:
        bot.reply_to(message,
                     'Такой человек не найден', parse_mode="Markdown")


def create_intent(display_name, training_phrases_parts, message_texts):
    """Create an intent of the given intent type."""
    intents_client = dialogflow.IntentsClient(credentials=credentials)

    parent = dialogflow.AgentsClient.agent_path(DIALOGFLOW_PROJECT_ID)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(
            text=training_phrases_part)
        # Here we create a new training phrase for each provided part.
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name, training_phrases=training_phrases, messages=[
            message]
    )

    response = intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )

    print("Intent created: {}".format(response))


def get_username(message):
    first_person_username = ''
    first_person_uid = ''

    second_person_username = ''
    second_person_uid = ''

    try:
        first_person_username += message.from_user.first_name
    except:
        pass
    try:
        first_person_username += ' '+message.from_user.last_name
    except:
        pass
    if first_person_username == '' or first_person_username == None or first_person_username == 'None' or first_person_username == 'None None':
        try:
            first_person_username = message.from_user.username
        except:
            pass
    try:
        first_person_uid = message.from_user.id
    except:
        pass

    try:
        second_person_username += message.reply_to_message.from_user.first_name
    except:
        pass
    try:
        second_person_username += ' '+message.reply_to_message.from_user.last_name
    except:
        pass
    if second_person_username == '' or second_person_username == None or second_person_username == 'None' or second_person_username == 'None None':
        try:
            second_person_username = message.reply_to_message.from_user.username
        except:
            pass
    try:
        second_person_uid = message.reply_to_message.from_user.id
    except:
        pass

    return ([str(first_person_username), str(second_person_username)])


def check_admin(message):
    x = bot.get_chat_member(group_id, message.from_user.id)
    status = x.status
    if status == 'administrator':
        return True
    else:
        return False

 # Парсинг участников группы


def parse_persons():
    persons = get_persons.main()
    for person in persons:
        username = ''
        uid = ''
        if person:
            uid = person.id
            try:
                if person.first_name:
                    first_name = str(person.first_name)
                if person.last_name:
                    last_name = str(person.last_name)
            except:
                pass
            if person.username:
                username = person.username
            elif person.first_name:
                username = first_name+' '+last_name
        Database().add_person(username, uid)

# Создание пары дня


def create_pair():
    Pairs().delete_pair()
    members = Database().get_persons()
    first_person = random.choice(members)
    try:
        second_person_t = Database().search_gender(0)
        second_person_t = random.choice(second_person)
    except:
        pass
    x = 1
    while x:
        try:
            if second_person_t:
                second_person = second_person_t
            else:
                second_person = random.choice(members)
            if first_person['uid'] != second_person['uid']:
                x = 0
        except:
            pass
    if first_person['uid'] == '1870643543':
        Pairs().add_pair(first_person['username'],
                         first_person['uid'], 'Colorless', '1883563833')
    else:
        Pairs().add_pair(first_person['username'], first_person['uid'],
                         second_person['username'], second_person['uid'])

# Википедия


def generate_random_string(length):

    letters = string.ascii_lowercase
    rand_string = ''.join(random.choice(letters) for i in range(length))
    return rand_string


def getwiki(s):
    try:
        ny = wikipedia.page(s)
        wikitext = ny.content[:1000]
        wikimas = wikitext.split('.')
        wikimas = wikimas[:-1]
        wikitext2 = ''
        for x in wikimas:
            if not('==' in x):
                if(len((x.strip())) > 3):
                    wikitext2 = wikitext2+x+'.'
            else:
                break
        wikitext2 = re.sub('\([^()]*\)', '', wikitext2)
        wikitext2 = re.sub('\([^()]*\)', '', wikitext2)
        wikitext2 = re.sub('\{[^\{\}]*\}', '', wikitext2)
        return wikitext2
    except Exception as e:
        return 'В энциклопедии нет информации об этом'


# Добавление в бд нового человека


@bot.message_handler(content_types=["new_chat_members"])
def handler_new_member(message):
    try:
        new_member = message.json['new_chat_member']
        usernam = ''
        first_name = ''
        last_name = ''
        username = ''
        try:
            usernam = new_member['username']
        except:
            pass
        try:
            first_name = new_member['first_name']
            last_name = new_member['last_name']
        except:
            pass
        uid = new_member['id']

        try:
            usernam += first_name
        except:
            pass
        try:
            usernam += last_name
        except:
            pass
        if usernam == '' or usernam == None or usernam == 'None' or usernam == 'None None':
            try:
                usernam = new_member['username']
            except:
                pass
        new_person = "["+usernam+"](tg://user?id="+str(uid)+")"
        txt = f'Привет, {new_person}. ты очень красивая'
        bot.send_message(message.chat.id, txt, parse_mode="Markdown")
        Database().add_person(usernam, uid)
    except:
        pass


@bot.message_handler(commands=["wiki"])
def handler_new_member(message):
    text = message.text
    try:
        text = text.replace('/wiki@batin_sin_bot ', '')
    except:
        pass
    try:
        text = text.replace('/wiki ', '')
    except:
        pass
    ans = getwiki(text)
    bot.reply_to(message, ans)


@bot.message_handler(commands=["gadat"])
def handler_new_member(message):
    try:
        text = message.text.split(maxsplit=1)[1]
        result = requests.get('https://yesno.wtf/api')
        result = result.json()
        pict = result['image']
        if result['answer'] == 'no':
            answ = 'Нет'
        elif result['answer'] == 'yes':
            answ = 'Да'
        else:
            answ = 'Не знаю'
        bot.send_animation(message.chat.id, pict, caption=answ)
    except:
        bot.reply_to(message, 'Задайте вопрос. Введите  "/gadat ваш вопрос"')


@bot.message_handler(commands=["weather"])
def handler_new_member(message):
    data = get_weather()
    stat = data['weather'][0]['description']
    temp = data['main']['temp']
    feels = data['main']['feels_like']
    humidity = data['main']['humidity']
    w_speed = data['wind']['speed']
    print(data)
    txt = f'На данный момент в Челябинске: {temp} °C \nОщущается как: {feels} °C\n Влажность: {humidity}%\nСкорость ветра: {w_speed} м/с\n{stat}\n '
    bot.reply_to(message, txt)


@bot.message_handler(commands=["news"])
def handler_new_member(message):
    txt = 'Раздел новостей еще в разработке.'
    bot.reply_to(message, txt)

# Гугл


@bot.message_handler(commands=["google_it"])
def handler_new_member(message):
    text = message.text
    try:
        text = text.replace('/google_it@batin_sin_bot ', '')
    except:
        pass
    try:
        text = text.replace('/google_it ', '')
    except:
        pass
    text2 = text.replace(' ', '+')
    ans = 'https://google.com/search?q=' + text2
    link = "[{text}]({ans})".format(text=text, ans=ans)
    bot.reply_to(message, link, parse_mode="Markdown")

# Пара дня


@bot.message_handler(commands=["pair"])
def handler_new_member(message):
    now = datetime.now()
    date_now = str(now.strftime("%d"))
    try:
        pair = Pairs().get_pair()
    except:
        create_pair()
        pair = Pairs().get_pair()
    date = str(pair[0]['date'])
    if date == date_now:
        first_person = "["+pair[0]['first_person'] + \
            "](tg://user?id="+str(pair[0]['first_person_uid'])+")"
        second_person = "["+pair[0]['second_person'] + \
            "](tg://user?id="+str(pair[0]['second_person_uid'])+")"
        txt = "❤️ Пара дня: {first_person} с {second_person} ❤️".format(
            first_person=first_person, second_person=second_person)
        bot.send_message(message.chat.id, txt, parse_mode="Markdown")
    else:
        create_pair()
        pair = Pairs().get_pair()
        first_person = "["+pair[0]['first_person'] + \
            "](tg://user?id="+str(pair[0]['first_person_uid'])+")"
        second_person = "["+pair[0]['second_person'] + \
            "](tg://user?id="+str(pair[0]['second_person_uid'])+")"
        txt = "❤️ Пара дня: {first_person} с {second_person} ❤️".format(
            first_person=first_person, second_person=second_person)
        bot.send_message(message.chat.id, txt, parse_mode="Markdown")

# Смена полаё


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    uid = call.from_user.id
    gender = call.data
    Database().update_person(uid, gender)
    bot.send_message(call.from_user.id,
                     text="Ваш пол успешно изменен", reply_markup='')

# Заключение брака


@bot.message_handler(commands=["brak"])
def handler_new_member(message):
    print(message.from_user)
    if message.reply_to_message:
        first_person_usernam = ''
        first_person_first_name = ''
        first_person_last_name = ''
        first_person_uid = ''
        second_person_usernam = ''
        second_person_first_name = ''
        second_person_last_name = ''
        second_person_uid = ''
        print('0')
        try:
            first_person_usernam = message.from_user.username
        except:
            pass
        print('1')
        try:
            first_person_first_name = message.from_user.first_name
            first_person_last_name = message.from_user.last_name
        except:
            pass
        print('2')
        first_person_uid = message.from_user.id
        try:
            second_person_usernam = message.reply_to_message.from_user.username
        except:
            pass
        print('3')
        try:
            second_person_first_name = message.reply_to_message.from_user.first_name
            second_person_last_name = message.reply_to_message.from_user.last_name
        except:
            pass
        print('4')
        second_person_uid = message.reply_to_message.from_user.id
        if first_person_usernam:
            first_username = first_person_usernam
        else:
            first_username = str(first_person_first_name) + \
                " "+str(first_person_last_name)
        print('5')
        if second_person_usernam:
            second_username = second_person_usernam
        else:
            second_username = str(second_person_first_name) + \
                " "+str(second_person_last_name)
        print('6')
        res = True
        try:
            if Marriages().check_mariage(first_person_uid):
                if Marriages().check_mariage(second_person_uid):
                    res = False
            if res:
                print('7')
                first_person = "["+first_username + \
                    "](tg://user?id="+str(first_person_uid)+")"
                second_person = "["+second_username + \
                    "](tg://user?id="+str(second_person_uid)+")"
                print('8')
                txt = "💍 {first_person} делает предложение {second_person} 💍 \n{second_person}, вы согласны? \nДа или Нет".format(
                    first_person=first_person, second_person=second_person)
                bot.send_message(message.chat.id, txt, parse_mode="Markdown")
                Marriages().add_mariage(first_username, first_person_uid,
                                        second_username, second_person_uid)
            else:
                bot.send_message(
                    message.chat.id, 'Брак невозможен', parse_mode="Markdown")
        except:
            pass


@bot.message_handler(commands=["all"])
def handler_new_member(message):
    if check_admin(message):
        x = Database().get_persons()
        calleds = ''

        f = 0
        for user in x:
            calleds += "["+user['username'] + \
                "](tg://user?id="+str(user['uid'])+") "
            f += 1
            if f == 60:
                msg = bot.send_message(
                    message.chat.id, calleds, parse_mode="Markdown")
                f = 0
                calleds = ''
                time.sleep(0.5)
    else:
        bot.reply_to(message, 'У вас недостаточно прав.')


@bot.message_handler(commands=["info"])
def handler_new_member(message):
    command = ''
    actions = ''
    for action in commands:
        command += (str(action['action']).replace("'",
                    '').replace('{', '').replace('}', '')) + '\n'
    for action in triggers:
        actions += (str(action['action']).replace("'",
                    '').replace('{', '').replace('}', '')) + '\n'
    txt = '\
    👌 Ответьте на сообщение пользователя.с которым хотите совершить действие используя 👉:\n\n '+command+' \n \
    \nТакже вы можете написать одну из следующих команд для действия 👉:\n\n '+actions+' \n \
    \nСписок команд бота 👉:\n\n\
    /braki - список браков\n\
    /pair - пара дня\n\
    /match_info - помощь\n\
    /wiki <текст> - узнать информацию из википедии\n\
    /google_it <запрос> - загуглить \n\
    /gadat <запрос> - шар судьбы\
    \n\n Также вы можете написать мне и мы сможем поговорить\n\n\
    '

    bot.send_message(message.chat.id, txt)

# Список браков


@bot.message_handler(commands=["braki"])
def handler_new_member(message):
    print('0')
    marriages = Marriages().all_mariages()
    txt = 'Список браков:\n\n'
    print('1')
    for marriage in marriages:
        first_person = marriage['first_person']
        second_person = marriage['second_person']
        # first_person_uid = marriage['first_person_uid']
        # second_person_uid = marriage['second_person_uid']
        date = marriage['date']
        current_date = datetime.now()
        marriage_time = str(current_date - date)
        marriage_time = marriage_time.rsplit('.', 1)
        marriage_time = marriage_time[0].replace('days', 'дней')
        txt += "💍{first_person} и {second_person} женаты уже {date} часов\n".format(
            first_person=first_person, second_person=second_person, date=marriage_time)
    if txt == '':
        txt = 'Браки отсутствуют'
    bot.send_message(message.chat.id, txt, parse_mode="Markdown")

# Согласие на брак


msg_count = 0


@bot.message_handler(content_types=["text"])
def handle_text(message):

    global msg_count
    if msg_count > 50:
        msg_count = 0
        chat_ai(message)
    text = str(message.text).lower()
    if 'сынок' in text:
        text = text.replace('сынок', '')
        chat_ai(message)
    if 'пробей человека' in text:
        person = text.replace('пробей человека', '')
        vk_analize_person(message, person)
    if 'реклама' in text:
        text = text.replace('реклама', '')
        chat_ai(message)

    uid = message.from_user.id
    usernames = get_username(message)
    test_name = ''
    test_name += str(message.from_user.first_name)
    test_name += ' '+str(message.from_user.last_name)
    test_name = str(test_name).replace('None', ' ')
    if test_name == '':
        test_name = message.from_user.username
    test_name = str(test_name).replace(' ', '')
    fn = ''
    ln = ''
    us = ''
    uid = message.from_user.id
    try:
        fn = message.from_user.first_name
    except:
        pass
    try:
        ln = message.from_user.last_name
    except:
        pass
    try:
        us = message.from_user.username
    except:
        pass
    try:
        print(str(uid)+' : ' + str(fn)+' : ' +
              str(ln)+' : ' + str(us)+' : ' + text + '\n')
    except:
        pass
    if message.reply_to_message:
        try:
            first_msg = message.reply_to_message.text
            second_msg = message.text
            create_intent(str(first_msg)+'_'+str(generate_random_string(15)),
                          [first_msg], [second_msg])

        except:
            pass
        try:
            target_uid = message.reply_to_message.from_user.id
            person_username = usernames[0]
            target_username = usernames[1]
            first_person = "["+person_username+"](tg://user?id="+str(uid)+")"
            second_person = "["+target_username + \
                "](tg://user?id="+str(target_uid)+")"
            for action in commands:
                if text in action['action']:
                    bot.send_message(message.chat.id, action['response'].format(
                        first_person, second_person), parse_mode="Markdown")
        except:
            pass
        try:
            if message.reply_to_message.from_user.username == 'batin_sin_bot':
                msg = message.text
                chat_ai(message)
        except:
            pass

    if 'batin_sin_bot' in text:
        try:
            msg = str(message.text).replace('@batin_sin_bot', '')
        except:
            msg = str(message.text).replace('batin_sin_bot', '')
        chat_ai(message)

    if message.from_user.id == message.chat.id:
        chat_ai(message)
    for action in triggers:
        if text in action['action']:
            resp = random.choice(action['response'])
            txt = resp.format(test_name)
            bot.send_message(message.chat.id, txt, parse_mode="Markdown")
# Действия


# Развод


# Смена пола


@bot.message_handler(commands=["gender"])
def handler_new_member(message):
    if message.from_user.id == message.chat.id:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(
            text='Мужской', callback_data=1))
        markup.add(telebot.types.InlineKeyboardButton(
            text='Женский', callback_data=2))
        bot.send_message(
            message.chat.id, text="Выберите ваш пол", reply_markup=markup)
    else:
        bot.send_message(
            message.chat.id, text="Для смены пола напишите мне в лс '/gender'")


bot.polling(none_stop=True)
