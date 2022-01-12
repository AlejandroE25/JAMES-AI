import json
import os
import random
import time
import webbrowser

import pyttsx3
import torch
import wikipedia
import wolframalpha

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

wolframClient = wolframalpha.Client("5LKAYP-7HAK325VV6")

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)


def openURL(url):
    webbrowser.get().open(url)


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

while True:
    # sentence = "do you use credit cards?"
    sentence = input("You: ")

    hasSpokenInCondition = False

    sentence = tokenize(sentence)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.99:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                botResponse = random.choice(intent['responses'])
            if tag == "quit":
                botResponse = "Goodbye for now"
                print(botResponse)
                engine.say(botResponse)
                engine.runAndWait()
                exit()

            if tag == "Greet Stephan":
                botResponse = "Hey Stephan"
                print(f"{bot_name}: {botResponse}")
                engine.say("Hey Steff on")
                engine.runAndWait()
                hasSpokenInCondition = True
                break

            if tag == "Check time":
                from datetime import datetime
                now = datetime.now()
                currentHour = now.hour
                currentMinute = now.minute

                if currentHour > 12:
                    currentHour = currentHour % 12
                    currentTime = str(currentHour) + ":" + str(currentMinute) + " PM"
                else:
                    currentHour = str(currentHour) + ":" + str(currentTime) + " AM"

                botResponse = "The current time is: " + str(currentTime)

            if tag == "search Google":
                n = 2
                search_term = ''
                while n < len(sentence) - 1:
                    n += 1
                    search_term += sentence[n]
                    search_term += ' '
                url = f"https://google.com/search?q={search_term}"
                botResponse = f'Here is what I found for {search_term} on google'
                openURL(url)
                break



    else:

        i = -1
        query = ''
        while i < len(sentence) - 1:
            i += 1
            query += sentence[i]
            query += ' '

        print(query)

        try:
            botResponse[0] = wikipedia.summary(query, sentences=2)
            botResponse[1] = next(wolframClient.query(query).results).text
        except wikipedia.exceptions.DisambiguationError:
            botResponse = next(wolframClient.query(sentence).results).text
        except wikipedia.exceptions.PageError:
            botResponse = next(wolframClient.query(query).results).text
        except:
            botResponse = "I can't understand that"

    if not hasSpokenInCondition:
        print(f"{bot_name}: {botResponse}")
        engine.say(botResponse)
        engine.runAndWait()
