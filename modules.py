from googlesearch import search
from datetime import datetime
from dotenv import load_dotenv
from googletrans import Translator
import time
import wikipediaapi
import random
import webbrowser
import traceback
import json
import requests
import telebot

from vk import SearchVK
from secretary_shedule import task_push, tasks_get
from config import *

bot = telebot.TeleBot('5157878096:AAFEIL4sVL-gkz2kL7nqj-dbtokHYITehYI')
group_id = '-1001178704810'


def response(resp):
    bot.send_message(group_id, resp, parse_mode="Markdown")
    resp = {"device": 'secretary', "title": "secretary", "content": resp}
    print('1', resp)
    # requests.post('http://127.0.0.1:9000/modules', json=json.dumps(resp))


def reques():
    req = input().capitalize()
    return req


class OwnerPerson:
    name = ""
    fullname = ""
    secondname = ""
    social_networks = []
    main_info = ""
    gender = 0
    interests = ""
    family = []
    bdate = ""
    access = ""
    home_city = ""


def end_reg():
    pass


def checkNet():
    try:
        requests.get("http://www.google.com")
        return True
    except requests.ConnectionError:
        return False


global person
person = OwnerPerson()


def test():

    print(person.name)
    print(person.fullname)
    print(person.secondname)
    print(person.social_networks)
    print(person.main_info)
    print(person.gender)
    print(person.interests)
    print(person.family)
    print(person.bdate)
    print(person.access)
    print(person.home_city)


def registration(name):
    while True:
        meeting = intents['intents']['first_meeting']['responses']
        meeting = meeting[random.randint(0, len(meeting) - 1)]
        response(meeting.format(name))
        resp = reques()
        if 'Нет' in resp:
            break
        if 'Да' in resp:
            person.name = name
            reg = intents['intents']['reg']['responses']
            reg = reg[random.randint(0, len(reg) - 1)]
            response(reg.format(name))
            response('Ваша фамилия?')
            req = reques()
            if req == 'Пропустить':
                req = ''
            person.fullname = req
            response('Ваше отчество?')
            req = reques()
            if req == 'Пропустить':
                req = ''
            person.secondname = req
            response('Расскажите о себе?')
            req = reques()
            if req == 'Пропустить':
                req = ''
            person.main_info = req
            response('ваш пол?')
            req = reques()
            if req == 'Пропустить':
                req = ''
            person.gender = req
            response('Что вам интересно?')
            req = reques()
            if req == 'Пропустить':
                req = ''
            person.interests = req
            response('В каком городе вы живете?')
            req = reques()
            if req == 'Пропустить':
                req = ''
            person.home_city = req
            end_reg()
            response('Регистрация успешно завершена, приятного пользования.')
            break


class Modules:
    def auth():
        # if person.name != "":
        return True
        # else:
        #     meeting = intents['intents']['meeting']['responses']
        #     meeting = meeting[random.randint(0, len(meeting) - 1)]
        #     response(meeting)
        #     name = reques()
        #     for profile in profiles['profiles']:
        #         try:
        #             if profile['name'] == name:
        #                 person.name = profile['name']
        #                 person.fullname = profile['fullname']
        #                 person.secondname = profile['secondname']
        #                 person.social_networks = profile['social_networks']
        #                 person.main_info = profile['main_info']
        #                 person.gender = profile['gender']
        #                 person.interests = profile['interests']
        #                 person.family = profile['family']
        #                 person.bdate = profile['bdate']
        #                 person.access = profile['access']
        #                 person.home_city = profile['home_city']
        #                 return True
        #         except:pass
        #     registration(name)

    def change_user(*args: tuple):
        name = args
        for profile in profiles['profiles']:
            try:
                if profile['name'] == name:
                    person.name = profile['name']
                    person.fullname = profile['fullname']
                    person.secondname = profile['secondname']
                    person.social_networks = profile['social_networks']
                    person.main_info = profile['main_info']
                    person.gender = profile['gender']
                    person.interests = profile['interests']
                    person.family = profile['family']
                    person.bdate = profile['bdate']
                    person.access = profile['access']
                    person.home_city = profile['home_city']
                    return True
            except:
                pass

    def play_failure_phrase(*args: tuple):
        failure = intents['intents']['failure']['responses']
        failure = failure[random.randint(0, len(failure) - 1)]
        failure = failure.format(person.name)
        response(failure)

    def play_greetings(*args: tuple):
        print('testtttttttttttttttttt')
        greetings = intents['intents']['greeting']['responses']
        greeting = greetings[random.randint(0, len(greetings) - 1)]
        greeting = greeting.format(person.name)
        response(greeting)

    def farewell(*args: tuple):
        fare = intents['intents']['farewell']['responses']
        fare = fare[random.randint(0, len(fare) - 1)]
        fare = fare.format(person.name)
        settings.activated = 0
        response(fare)

    def vk_search_person(*args: tuple):
        if checkNet():
            if not args[0]:
                return
            vk_search_term = " ".join(args[0])
            vk_url = search("site:vk.com "+vk_search_term, num_results=0)
            webbrowser.get().open(vk_url[0])
            vk_search = intents['intents']['vk_search_person']['responses']
            vk_search = vk_search[random.randint(0, len(vk_search) - 1)]
            result = vk_search.format(vk_search_term)
            response(result)
        else:
            response(intents['disconnected'])

    def vk_analize_person(*args: tuple):
        if checkNet():
            vk_search_term = " ".join(args[0])
            result = SearchVK().get_vk_info(vk_search_term)
            sex = result['response'][0]['sex']
            bdate = result['response'][0]['bdate']
            city = result['response'][0]['city']['title']
            country = result['response'][0]['country']['title']
            greetings = intents['intents']['vk_search_person']['responses']
            greeting = greetings[random.randint(0, len(greetings) - 1)]
            greeting_translate = greeting.format(
                vk_search_term, bdate, city, country)
            response(greeting_translate)
        else:
            response(intents['disconnected'])

    def toss_coin(*args: tuple):
        flips_count, heads, tails = 3, 0, 0
        for flip in range(flips_count):
            if random.randint(0, 1) == 0:
                heads += 1
        tails = flips_count - heads
        winner = "Орёл" if tails > heads else "Решка"
        response("{} выиграл".format(winner))

    def time(*args: tuple):
        time_term = datetime.now().strftime('%H:%M:%S')
        greetings = intents['intents']['time']['responses']
        greeting = greetings[random.randint(0, len(greetings) - 1)]
        greeting = greeting.format(time_term)
        greeting_translate = greeting
        response(greeting_translate)

    def howisgoing(*args: tuple):
        greetings = intents['intents']['howisgoing']['responses']
        greeting = greetings[random.randint(0, len(greetings) - 1)]
        greeting_translate = greeting
        response(greeting_translate)

    def taxi_order(*args: tuple):
        pass

    def food_order(*args: tuple):
        pass

    def change_section(*args: tuple):
        pass

    def get_tasks(*args: tuple):
        tasks = tasks_get()
        response(tasks)

    def push_task(*args: tuple):
        task = task_push(args)
        response(task)
