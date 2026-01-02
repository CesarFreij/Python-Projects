#   ____                       _____         _  _ 
#  / ___|___  ___  __ _ _ __  |  ___| __ ___(_)(_)
# | |   / _ \/ __|/ _` | '__| | |_ | '__/ _ \ || |
# | |__|  __/\__ \ (_| | |    |  _|| | |  __/ || |
#  \____\___||___/\__,_|_|    |_|  |_|  \___|_|/ |
#                                            |__/

from tkinter import *
from gtts import gTTS
from playsound import playsound
import os

# قائمة اللغات المدعومة
languages = {
    "العربية": "ar",
    "الإنجليزية": "en",
    "الفرنسية": "fr",
    "الإسبانية": "es"
}

def speak_text():
    text = entry.get()
    if text.strip() == "":
        status_label.config(text="يرجى إدخال نص أولاً", fg="red")
        return

    lang_code = languages[lang_var.get()]
    tts = gTTS(text=text, lang=lang_code)

    filename = "output.mp3"
    try:
        tts.save(filename)
        playsound(filename)
        status_label.config(text="✅ تم تشغيل الصوت", fg="green")
    except Exception as e:
        status_label.config(text=f"حدث خطأ: {e}", fg="red")

# واجهة المستخدم
root = Tk()
root.title("تحويل النص إلى كلام")
root.geometry("450x300")
root.resizable(False, False)

# عنوان
label = Label(root, text="🗣️ أدخل النص الذي تريد تحويله إلى كلام", font=("Arial", 14))
label.pack(pady=10)

# مربع إدخال النص
entry = Entry(root, width=40, font=("Arial", 12))
entry.pack(pady=5)

# قائمة اختيار اللغة
lang_var = StringVar(root)
lang_var.set("العربية")  # القيمة الافتراضية
lang_menu = OptionMenu(root, lang_var, *languages.keys())
lang_menu.config(font=("Arial", 12))
lang_menu.pack(pady=5)

# زر التشغيل
button = Button(root, text="🔊 تشغيل الصوت", command=speak_text, font=("Arial", 12), bg="#90ee90")
button.pack(pady=15)

# حالة التشغيل
status_label = Label(root, text="", font=("Arial", 12))
status_label.pack()

root.mainloop()
