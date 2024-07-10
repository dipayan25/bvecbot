from flask import Flask, request, jsonify, render_template
import random
import json
import pickle
import numpy as np
import tensorflow as tf
from keras.models import load_model
import mysql.connector
import nltk
from nltk.stem import WordNetLemmatizer

app = Flask(__name__)

lemmatizer = WordNetLemmatizer()

# Load intents file
intents = json.loads(open('D:\cdac chatbot\intents.json').read())

# Load words and classes
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))

# Load the trained model
model = load_model('chatbot_model.h5')

# Database connection
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='1234',
        database='chatbot'
    )
    return connection

# Clean up sentence
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words

# Bag of words
def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

# Predict class
def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list

# Get response from intents
def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            if tag == 'faculty':
                return get_faculty_names()
            else:
                result = random.choice(i['responses'])
            break
    return result

# Function to retrieve faculty names from the database
def get_faculty_names():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT Name FROM faculty")
    faculty_names = cursor.fetchall()
    connection.close()
    return 'Faculty Members: ' + ', '.join([Name[0] for Name in faculty_names])

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def get_bot_response():
    message = request.json.get("message")
    ints = predict_class(message)
    res = get_response(ints, intents)
    return jsonify({"response": res})

if __name__ == "__main__":
    app.run(debug=True)
