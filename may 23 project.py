import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import firebase_admin
from firebase_admin import credentials, db
import threading
import time
import pygame
from datetime import datetime


# === Firebase Setup ===
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://mai-21-project-default-rtdb.firebaseio.com/'
})

# === Pygame Music Setup ===
pygame.mixer.init()
pygame.mixer.music.load("your lie in april orange.wav")  # Your music file here
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)  # Loop forever

click_sound = pygame.mixer.Sound("ui-cartoon-button-press-gfx-sounds-1-00-00.mp3")  # Your click sound here
click_sound.set_volume(0.4)

def load_avatar_image(mood, who="me"):
    filename = f"{mood.lower()}_{who}.png"
    try:
        img = Image.open(filename).resize((150, 200))
        return ImageTk.PhotoImage(img)
    except:
        fallback = f"happy_{who}.png"
        img = Image.open(fallback).resize((150, 200))
        return ImageTk.PhotoImage(img)

def update_mood(mood_text, avatar_label, mood_var, who="me"):
    click_sound.play()
    if mood_text:
        mood_var.set(mood_text)
        new_img = load_avatar_image(mood_text, who)
        avatar_label.configure(image=new_img)
        avatar_label.image = new_img
        db.reference(who).update({
            "mood": mood_text,
            "last_update": time.time()
        })

def update_status(status_text, status_var, who="me"):
    click_sound.play()
    if status_text:
        status_var.set(status_text)
        db.reference(who).update({
            "status": status_text,
            "last_update": time.time()
        })

def send_heart():
    click_sound.play()
    sent_time = time.time()
    db.reference("me").update({
        "sent_heart": True,
        "sent_heart_time": sent_time,
        "last_update": sent_time
    })
    messagebox.showinfo("Sent", "💌 Heart sent!")
    threading.Thread(target=clear_heart_flag, args=(sent_time,), daemon=True).start()

def clear_heart_flag(sent_time):
    time.sleep(10)
    ref = db.reference("me")
    data = ref.get()
    if data and data.get("sent_heart_time") == sent_time:
        ref.update({
            "sent_heart": False,
            "sent_heart_time": None
        })

def format_time(ts):
    return datetime.fromtimestamp(ts).strftime("%H:%M")

def sync_partner():
    while True:
        partner_data = db.reference("partner").get()
        if partner_data:
            partner_mood.set(partner_data.get("mood", "Happy"))
            partner_status.set(partner_data.get("status", "Studying"))
            new_img = load_avatar_image(partner_data.get("mood", "Happy"), "partner")
            partner_avatar_label.configure(image=new_img)
            partner_avatar_label.image = new_img

            if partner_data.get("sent_heart", False):
                ts = partner_data.get("sent_heart_time", None)
                time_str = format_time(ts) if ts else ""
                partner_heart_label.config(text=f"💌 Heart received! Sent {time_str}", fg="red")
            else:
                partner_heart_label.config(text="")
        else:
            partner_heart_label.config(text="")
        time.sleep(5)

def on_enter(e):
    e.widget['background'] = '#ffb6c1'  # Light pink

def on_leave(e):
    e.widget['background'] = '#ffe4e1'  # Misty rose

def create_animated_button(parent, text, command):
    btn = tk.Button(parent, text=text, font=("Arial", 12, "bold"),
                    bg='#ffe4e1', fg='black', relief='raised', bd=3,
                    activebackground='#ff69b4', activeforeground='white',
                    command=command, cursor="hand2")
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

# GUI Setup
root = tk.Tk()
root.title("🦦💞🦄")
root.geometry("720x700")
root.configure(bg="#fff0f5")

my_mood = tk.StringVar(value="Happy")
my_status = tk.StringVar(value="Studying")
partner_mood = tk.StringVar(value="Happy")
partner_status = tk.StringVar(value="Studying")

avatar_frame = tk.Frame(root, bg="#fff0f5")
avatar_frame.pack(pady=20)

my_section = tk.Frame(avatar_frame, bg="#fff0f5")
my_section.grid(row=0, column=0, padx=40, sticky="n")

tk.Label(my_section, text="You", font=("Arial", 16, "bold"), bg="#fff0f5", fg="#c71585").pack()
my_avatar_label = tk.Label(my_section, bg="#fff0f5")
my_avatar_img = load_avatar_image(my_mood.get(), "me")
my_avatar_label.configure(image=my_avatar_img)
my_avatar_label.pack()
tk.Label(my_section, textvariable=my_mood, fg="#db7093", font=("Arial", 14, "italic"), bg="#fff0f5").pack()
tk.Label(my_section, textvariable=my_status, fg="#ff69b4", font=("Arial", 14), bg="#fff0f5").pack()
my_heart_label = tk.Label(my_section, text="", font=("Arial", 9), fg="red", bg="#fff0f5")
my_heart_label.pack(pady=5)

partner_section = tk.Frame(avatar_frame, bg="#fff0f5")
partner_section.grid(row=0, column=1, padx=40, sticky="n")

tk.Label(partner_section, text="Partner", font=("Arial", 16, "bold"), bg="#fff0f5", fg="#4169e1").pack()
partner_avatar_label = tk.Label(partner_section, bg="#fff0f5")
partner_avatar_img = load_avatar_image(partner_mood.get(), "partner")
partner_avatar_label.configure(image=partner_avatar_img)
partner_avatar_label.pack()
tk.Label(partner_section, textvariable=partner_mood, fg="#483d8b", font=("Arial", 14, "italic"), bg="#fff0f5").pack()
tk.Label(partner_section, textvariable=partner_status, fg="#1e90ff", font=("Arial", 14), bg="#fff0f5").pack()
partner_heart_label = tk.Label(partner_section, text="", font=("Arial", 9), fg="red", bg="#fff0f5")
partner_heart_label.pack(pady=5)

buttons_frame = tk.Frame(root, bg="#fff0f5")
buttons_frame.pack(pady=20)

tk.Label(buttons_frame, text="Select Your Mood:", font=("Arial", 14, "bold"), bg="#fff0f5").grid(row=0, column=0, columnspan=4, pady=5)
moods = ["Happy", "Sad", "Angry", "Tired"]
for i, mood in enumerate(moods):
    btn = create_animated_button(buttons_frame, mood, 
                                 lambda m=mood: update_mood(m, my_avatar_label, my_mood, "me"))
    btn.grid(row=1, column=i, padx=8, pady=8)

tk.Label(buttons_frame, text="Select Your Status:", font=("Arial", 14, "bold"), bg="#fff0f5").grid(row=2, column=0, columnspan=4, pady=5)
statuses = ["Studying", "Working", "Chilling", "Eating", "Out"]
for i, status in enumerate(statuses):
    btn = create_animated_button(buttons_frame, status, 
                                 lambda s=status: update_status(s, my_status, "me"))
    btn.grid(row=3, column=i, padx=8, pady=8)

send_heart_btn = create_animated_button(root, "💌 Send Heart", send_heart)
send_heart_btn.pack(pady=20)

def update_my_heart_label():
    while True:
        my_data = db.reference("me").get()
        if my_data and my_data.get("sent_heart", False):
            ts = my_data.get("sent_heart_time", None)
            time_str = format_time(ts) if ts else ""
            my_heart_label.config(text=f"💌 Heart sent! Sent {time_str}")
        else:
            my_heart_label.config(text="")
        time.sleep(3)

threading.Thread(target=sync_partner, daemon=True).start()
threading.Thread(target=update_my_heart_label, daemon=True).start()

root.mainloop()
