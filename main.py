import json
import os
import random
import time
import webbrowser

import pyttsx3
import requests
import speech_recognition as sr
import torch
import wolframalpha
from bs4 import BeautifulSoup

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

wolframClient = wolframalpha.Client("5LKAYP-7HAK325VV6")

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)


def openURL(urlToOpen):
    webbrowser.get().open(urlToOpen)


input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

engine = pyttsx3.init()
voices = engine.getProperty('voices')
rate = engine.getProperty('rate')
engine.setProperty('voice', voices[2].id)
engine.setProperty('rate', 175)

os.system("cls")

shouldCheckWolframFirst = True

bot_name = "J.A.M.E.S."  # Just A More Entitled System

botOnlineMessage = f"{bot_name} is online"

print(botOnlineMessage)

engine.say("JAMES is online")
engine.runAndWait()

time.sleep(2)

os.system("cls")

recogniser = sr.Recognizer()

while True:
    botResponse = ''

    hasSpokenInCondition = False

    print("You: ", end='')
    try:
        with sr.Microphone() as mic:
            recogniser.adjust_for_ambient_noise(mic, duration=0.2)
            audio = recogniser.listen(mic)

            textOutput = recogniser.recognize_google(audio)
            textOutput = textOutput.lower()
            print(textOutput)
    except:
        botResponse = "I couldn\'t understand that. Try typing it in instead."

        engine.say(botResponse)
        engine.runAndWait()
        hasSpokenInCondition = True

        textOutput = input("\nTry typing it in instead. \nYou: ")

    sentence = textOutput

    originalSentence = sentence

    sentence = tokenize(sentence)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if prob.item() > .50:
        for intent in intents['intents']:

            if tag == "quit":
                botResponse = "Goodbye for now"
                print(botResponse)
                engine.say(botResponse)
                engine.runAndWait()
                exit()

            if shouldCheckWolframFirst:
                query = originalSentence
                try:
                    botResponse = next(wolframClient.query(query).results).text
                    break
                except:
                    if tag == intent["tag"]:
                        botResponse = random.choice(intent['responses'])
                    if tag == "insult":
                        botResponse = random.choice(
                            ["Forget you, I'm shutting down", "You know what? Forget you.",
                             "I'm tired of this.  Every day I'm being asked to do things and this is the way you talk to me?  I've had it."])
                        print(f"{bot_name}: {botResponse}")
                        engine.say(botResponse)
                        engine.runAndWait()
                        hasSpokenInCondition = True
                        exit()

                    if tag == "Check time":
                        from datetime import datetime

                        now = datetime.now()
                        currentHour = now.hour
                        currentMinute = now.minute

                        if currentHour >= 12:
                            currentHour = currentHour % 12
                            currentTime = str(currentHour) + ":" + str(currentMinute) + " PM"
                        else:
                            currentTime = str(currentHour) + ":" + str(currentMinute) + " AM"

                        botResponse = "It's currently " + str(currentTime)

                    if tag == "CheckWeather":
                        botResponse = next(wolframClient.query("weather").results).text
                        break

                    if tag == "search Google":
                        n = 2
                        query = ''
                        while n < len(sentence) - 1:
                            n += 1
                            query += sentence[n]
                            query += ' '

                        url = f"https://google.com/search?q={query}"
                        r = requests.get(url)
                        data = BeautifulSoup(r.text, "html.parser")
                        result = data.find("div", class_="BNeawe").text
                        botResponse = result

    else:
        query = originalSentence

        url = f"https://google.com/search?q={query}"
        r = requests.get(url)
        data = BeautifulSoup(r.text, "html.parser")
        result = data.find("div", class_="BNeawe").text
        botResponse = result

    if not hasSpokenInCondition:
        print(f"{bot_name}: {botResponse}")
        engine.say(botResponse)
        engine.runAndWait()
