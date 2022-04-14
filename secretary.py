import requests
import json
import random
from modules import Modules, response
import enchant
from enchant.checker import SpellChecker
import difflib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from dotenv import load_dotenv
from config import *


class VoiceAssistant:
    name = ""
    sex = ""
    speech_language = ""
    recognition_language = ""
    auth_life = 0


def spell_checker(text):
    # checker = SpellChecker("ru_RU")
    # dictionary = enchant.Dict("ru_RU")
    # checker.set_text(text)
    # for i in checker:
    #     spell = i.word
    #     suggestions = set(dictionary.suggest(spell))
    #     sim = dict()
    #     for word in suggestions:
    #         measure = difflib.SequenceMatcher(None, spell, word).ratio()
    #         sim[measure] = word
    #     correct_spell = sim[max(sim.keys())]
    #     text = text.replace(spell, correct_spell)
    return text


def prepare_corpus():
    corpus = []
    target_vector = []
    for intent_name, intent_data in commands["intents"].items():
        for example in intent_data["examples"]:
            corpus.append(example)
            target_vector.append(intent_name)
    training_vector = vectorizer.fit_transform(corpus)
    classifier_probability.fit(training_vector, target_vector)
    classifier.fit(training_vector, target_vector)


def make_preparations():
    global assistant, vectorizer, classifier_probability, classifier, activated, settings
    assistant = VoiceAssistant()
    assistant.name = ["сынок, Сынок"]
    assistant.sex = "female"
    assistant.speech_language = "ru"
    assistant.auth_life = 60
    load_dotenv()
    vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2, 3))
    classifier_probability = LogisticRegression()
    classifier = LinearSVC()
    prepare_corpus()


def get_intent(request):
    best_intent = classifier.predict(vectorizer.transform([request]))[0]
    index_of_best_intent = list(
        classifier_probability.classes_).index(best_intent)
    probabilities = classifier_probability.predict_proba(
        vectorizer.transform([request]))[0]
    best_intent_probability = probabilities[index_of_best_intent]
    return (best_intent, request, best_intent_probability)


class Secretary:
    def secretarys(self, voice_input_parts):
        check_auth = getattr(Modules, 'auth')
        if len(voice_input_parts) == 1:
            intent = get_intent(voice_input_parts[0])
            if check_auth():
                try:
                    if intent:
                        resp = commands["intents"][intent[0]]["responses"]
                        f = getattr(Modules, resp)
                        f()
                    else:
                        resp = commands["failure_phrases"]
                        f = getattr(Modules, resp)
                        f()
                except:
                    resp = commands["failure_phrases"]
                    f = getattr(Modules, resp)
                    f()
        if len(voice_input_parts) > 1:
            try:
                intents_prob = []
                for guess in range(len(voice_input_parts)+1):
                    intent = get_intent(
                        (" ".join(voice_input_parts[0:guess])).strip())
                    if intent[1]:
                        intents_prob.append(intent)
                print(intents_prob)
                fin_intents = max(intents_prob, key=lambda item: item[2])
                module = fin_intents[0]
                req = fin_intents[1]
                req = req.split(" ")
                if check_auth():
                    try:
                        for el in req:
                            voice_input_parts.remove(el)
                        resp = commands["intents"][module]["responses"]
                        f = getattr(Modules, resp)
                        f(voice_input_parts)
                    except:
                        resp = intents['intents'][module]['responses']
                        resp = resp[random.randint(0, len(resp) - 1)]
                        response(resp)
            except:
                resp = commands["failure_phrases"]
                f = getattr(Modules, resp)
                f()

    def check_name(self, text):
        for name in assistant.name:
            if name in text:
                text = text.split(" ")
                text.pop(text.index(name))
                text = " ".join(text)
                settings.activated = 1
                return text
        return False

    def main(self, message):
        # voice = str(json.loads(voice)['text'])
        make_preparations()
        txt = message.text
        # check = self.check_name(txt)
        # print(check)
        # if check:
        #     voice = check
        # if settings.activated:
        print(txt)
        voice_input = spell_checker(txt)
        voice_input_parts = voice_input.split(" ")
        self.secretarys(voice_input_parts)
