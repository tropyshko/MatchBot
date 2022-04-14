import json
with open('commands.json', encoding='utf8') as json_file:
    commands = json.load(json_file)
with open('intents.json', encoding='utf8') as json_file:
    intents = json.load(json_file)
with open('profiles.json', encoding='utf8') as json_file:
    profiles = json.load(json_file)


class Settings:
    activated = 0


settings = Settings()
