import json
import requests
import pyttsx3
import datetime
import queue
import sounddevice as sd
import vosk
import os

# 📢 Инициализация синтеза речи
engine = pyttsx3.init()
engine.setProperty('rate', 160)

def speak(text):
    print("Ассистент:", text)
    engine.say(text)
    engine.runAndWait()

# 🎙 Настройка модели Vosk
MODEL_PATH = "vosk-model-small-ru-0.22"

if not os.path.exists(MODEL_PATH):
    speak("Модель Vosk не найдена. Скачай её с официального сайта Vosk.")
    exit(1)

model = vosk.Model(MODEL_PATH)
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

def listen():
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        recognizer = vosk.KaldiRecognizer(model, 16000)
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                return result.get("text", "").strip()

# 🌐 Получение праздников (фиксированный URL для Австрии, 2025)
def get_holidays():
    url = "https://date.nager.at/api/v3/publicholidays/2025/AT"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        speak("Ошибка при получении данных.")
        print("Ошибка запроса:", e)
        return []

# 🧠 Главная логика ассистента
def main():
    speak("Загружаю праздники 2025 года для Австрии.")
    holidays = get_holidays()

    if not holidays:
        return

    while True:
        speak("Слушаю команду.")
        command = listen()
        print("Распознано:", command)

        if "перечислить" in command:
            for h in holidays:
                speak(h["localName"])

        elif "сохранить" in command:
            with open("holidays.txt", "w", encoding="utf-8") as f:
                for h in holidays:
                    f.write(h["localName"] + "\n")
            speak("Список праздников сохранён в файл.")

        elif "подробно" in command:
            with open("holidays_full.txt", "w", encoding="utf-8") as f:
                for h in holidays:
                    f.write(f'{h["date"]} — {h["localName"]}\n')
            speak("Подробная информация о праздниках сохранена.")

        elif "ближайший" in command:
            today = datetime.date.today()
            upcoming = [h for h in holidays if datetime.date.fromisoformat(h["date"]) >= today]
            if upcoming:
                nearest = min(upcoming, key=lambda x: datetime.date.fromisoformat(x["date"]))
                speak(f"Ближайший праздник {nearest['localName']} {nearest['date']}")
            else:
                speak("Нет предстоящих праздников.")

        elif "количество" in command:
            speak(f"Всего праздников: {len(holidays)}")

        elif "выход" in command or "стоп" in command:
            speak("До свидания!")
            break

        else:
            speak("Команда не распознана. Повтори, пожалуйста.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        speak("Ассистент завершает работу.")














