import telebot
from telebot import types
import requests
import re
from bs4 import BeautifulSoup
from openai import OpenAI
import json
import os
import time
from urllib.parse import quote

# 🔑 Токены
BOT_TOKEN = "8423562795:AAEucyAssbf--3Kv-y9fTP_ho9xN6Daqzyw"
OPENAI_API_KEY = "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"

# 📂 Файл для хранения пользователей
USERS_FILE = r"C:\Users\user\Desktop\ALTRON\users.json"

# ✅ Загружаем пользователей (исправлено)
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        try:
            content = f.read().strip()
            users = set(json.loads(content)) if content else set()
        except json.JSONDecodeError:
            users = set()
else:
    users = set()

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(list(users), f)

# --- Клиенты
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
client = OpenAI(api_key=OPENAI_API_KEY)

# --- GPT (улучшен стиль ответа)
def ask_gpt(prompt: str) -> str:
    try:
        system_prompt = (
            "Ты — дружелюбный, умный и человечный помощник по имени ALTRON. "
            "Ты отвечаешь естественно, как человек: добавляешь эмоции, простые слова, "
            "объясняешь понятно, иногда с лёгким юмором, если это уместно. "
            "Не используй сухие фразы вроде 'как ИИ-модель', просто говори как человек."
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Ошибка GPT: {e}"

# --- Погода для любого города с автоопределением
def get_weather_auto(message_text):
    try:
        parts = message_text.lower().split("погода")
        city = parts[1].strip() if len(parts) > 1 and parts[1].strip() else "Andijan"
        city_encoded = quote(city)
        url = f"https://wttr.in/{city_encoded}?format=3"
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if res.status_code == 200 and "Unknown location" not in res.text:
            return f"📍 Погода для {city.title()}: {res.text}"
        else:
            return f"⚠️ Не удалось получить погоду для города: {city}"
    except Exception as e:
        return f"⚠️ Ошибка погоды: {e}"

# --- Поиск видео YouTube без API
def search_youtube(query):
    try:
        query = query.replace(" ", "+")
        url = f"https://www.youtube.com/results?search_query={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers).text
        match = re.search(r"\/watch\?v=(\S{11})", res)
        if match:
            video_id = match.group(1)
            return f"🎬 Результат поиска:\nhttps://www.youtube.com/watch?v={video_id}"
        else:
            return "⚠️ Видео не найдено"
    except Exception as e:
        return f"⚠️ Ошибка поиска видео: {e}"

# --- Поиск информации через Google
def search_google(query):
    try:
        query = query.replace(" ", "+")
        url = f"https://www.google.com/search?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        result = soup.find("div", class_="BNeawe vvjwJb AP7Wnd")
        if result:
            return f"🔎 Результат поиска: {result.text}\nСсылка: https://www.google.com/search?q={query}"
        else:
            return "⚠️ Ничего не найдено"
    except Exception as e:
        return f"⚠️ Ошибка поиска: {e}"

# --- /start
@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.chat.id
    welcome_text = (
        "👋 Привет! Я ALTRON GPT — твой умный помощник 🤖\n\n"
        "Могу делать многое:\n"
        "• 🧠 Общаться как человек (GPT-4)\n"
        "• 🌤 Узнать погоду — просто напиши 'погода Андижан'\n"
        "• 🎬 Найти видео — напиши 'youtube коты'\n"
        "• 🔍 Найти инфо — 'найди что такое ИИ'\n\n"
        "Попробуй прямо сейчас!"
    )
    try:
        with open(r"C:\Users\user\Desktop\CHAT GPT BOT\KUAF_GPT_logo.jpg", "rb") as photo:
            bot.send_photo(user_id, photo, caption=welcome_text)
    except:
        bot.send_message(user_id, welcome_text)

# --- /stats
@bot.message_handler(commands=["stats"])
def show_stats(message):
    total_users = len(users)
    bot.send_message(message.chat.id, f"👥 Botdan foydalangan foydalanuvchilar soni: {total_users}")

# --- Обработка сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    users.add(message.chat.id)
    save_users()
    user_text = message.text.strip()
    bot.send_chat_action(message.chat.id, "typing")

    # --- Погода
    if "погода" in user_text.lower():
        bot.reply_to(message, get_weather_auto(user_text))
        return

    # --- YouTube
    if user_text.lower().startswith("youtube") or user_text.lower().startswith("ютуб"):
        query = user_text.lower().replace("youtube", "").replace("ютуб", "").strip()
        bot.reply_to(message, search_youtube(query))
        return

    # --- Google поиск
    if user_text.lower().startswith("найди") or user_text.lower().startswith("search"):
        query = user_text.lower().replace("найди", "").replace("search", "").strip()
        bot.reply_to(message, search_google(query))
        return

    # --- GPT (теперь отвечает "по-человечески")
    answer = ask_gpt(user_text)
    bot.reply_to(message, answer, parse_mode=None)

# --- Запуск
while True:
    try:
        bot.polling(non_stop=True, interval=0, timeout=60)
    except Exception as e:
        print(f"[Ошибка] {e}")
        time.sleep(5)
