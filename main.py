import random
import json
import pyttsx3
import discord
import asyncio
import wikipedia
import webbrowser

import wolframalpha

wolframClient = wolframalpha.Client("5LKAYP-7HAK325VV6")

from discord.ext import commands

import torch

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

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

bot_name = "J.A.M.E.S."  # Just A More Entitled System
print("Let's chat! (type 'quit' to exit)")
while True:
    # sentence = "do you use credit cards?"
    sentence = input("You: ")

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
                engine.say(botResponse)
                engine.runAndWait()
                exit()
            if tag == "search Google":
                n = 2
                search_term = ''
                while n < len(sentence) - 1:
                    n += 1
                    search_term += sentence[n]
                    search_term += ' '
                url = f"https://google.com/search?q={search_term}"
                openURL(url)
                botResponse = f'Here is what I found for {search_term} on google'

    else:
        try:
            botResponse[1] = wikipedia.summary(sentence[0], sentences=2)
            botResponse[0] = next(wolframClient.query(sentence[0]).results).text
        except wikipedia.exceptions.DisambiguationError:
            botResponse = next(wolframClient.query(sentence[0]).results).text
        except wikipedia.exceptions.PageError:
            botResponse = next(wolframClient.query(sentence[0]).results).text
        except:
            botResponse = f"I couldn't find a good result for {sentence}"

    print(f"{bot_name}: {botResponse}")
    engine.say(botResponse)
    engine.runAndWait()
