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
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 175)

os.system("cls")

bot_name = "J.A.M.E.S."  # Just A More Entitled System

botOnlineMessage = f"{bot_name} is online"

print(botOnlineMessage)

engine.say("JAMES is online")
engine.runAndWait()

time.sleep(2)

os.system("cls")

recogniser = sr.Recognizer()

hasSaidKeyWord = False

while True:
    botResponse = ''

    hasSpokenInCondition = False

    try:
        with sr.Microphone() as mic:
            print("Calibrating...")
            recogniser.adjust_for_ambient_noise(mic, duration=1)
            os.system("CLS")
            print("You: ", end='')
            audio = recogniser.listen(mic, 2)

            textOutput = recogniser.recognize_houndify(audio, "QfvPyIr8VwJKynBIDHuYCA==", "AWA3XHDtcTBwiH5P7cBsqBWjf1-ufxsnzu0h-azroCwmjcjdE7I9IPemoHkDkaX9Qa4hs49Gful2cN55d-Mh5g==")
            textOutput = textOutput.lower()
            print(textOutput)
    except sr.WaitTimeoutError:
        textOutput = ""
    except Exception as exception:
        botResponse = exception
        print(exception)
        engine.say(str(botResponse))
        engine.runAndWait()
        hasSpokenInCondition = True

        textOutput = ""

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

    if prob.item() > .70:
        for intent in intents['intents']:

            if tag == "Wake Up" or hasSaidKeyWord:

                hasSaidKeyWord = True

                if tag == intent["tag"]:
                    botResponse = random.choice(intent['responses'])

                if tag == "quit":
                    botResponse = "Goodbye for now"
                    print(botResponse)
                    engine.say(botResponse)
                    engine.runAndWait()
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
                    url = "https://google.com/search?q=Weather at my location"
                    r = requests.get(url)
                    data = BeautifulSoup(r.text, "html.parser")
                    result = data.find("div", class_="BNeawe").text
                    botResponse = result
                    break

                if tag == "thanks":
                    botResponse = random.choice(intent["responses"])
                    hasSaidKeyWord = False

                if tag == "search Google":
                    n = 2
                    query = ''
                    while n < len(sentence) - 1:
                        n += 1
                        query += sentence[n]
                        query += ' '

                    url = f"https://google.com/search?q={query}"

                    botResponse = random.choice(intents['intents'][9]['responses'])

                    engine.say(botResponse)
                    engine.runAndWait()

                    print(f"Querying for: {url}")

                    r = requests.get(url)
                    data = BeautifulSoup(r.text, "html.parser")
                    result = data.find("div", class_="BNeawe").text
                    botResponse = result
                    break

    if not hasSpokenInCondition:
        print(f"{bot_name}: {botResponse}.")
        engine.say(botResponse)
        engine.runAndWait()
