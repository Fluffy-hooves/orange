import streamlit as st
from PIL import Image
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import time
import pygame

# Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate("/Users/sana/Desktop/python/mood-app.py/firebase_key.json")  # <-- update with your actual path
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://mai-21-project-default-rtdb.firebaseio.com/'  # <-- update with your Firebase Realtime Database URL (no trailing slash)
    })

# Start music in background (only once)
if 'music_started' not in st.session_state:
    pygame.mixer.init()
    pygame.mixer.music.load("your lie in april orange.wav")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
    st.session_state.music_started = True

# Variables
moods = ["Happy", "Sad", "Angry", "Tired"]
statuses = ["Studying", "Working", "Chilling", "Eating", "Out"]

# Simple login
st.title("💖 Mood Mirror App")
user = st.selectbox("Who are you?", ["sana", "michael"])
is_me = user == "sana"
partner = "michael" if is_me else "sana"

# Avatar image loader
def load_image(mood, who):
    try:
        return Image.open(f"{mood.lower()}_{who}.png").resize((150, 200))
    except:
        return Image.open(f"happy_{who}.png").resize((150, 200))

# Display self
st.header("You")
current_mood = st.selectbox("Select your mood", moods, key="mood")
current_status = st.selectbox("Select your status", statuses, key="status")
st.image(load_image(current_mood, user))
st.write(f"**Mood:** {current_mood}")
st.write(f"**Status:** {current_status}")

if st.button("💌 Send Heart"):
    now = int(time.time())
    try:
        db.reference(user).update({
            "sent_heart": True,
            "sent_heart_time": now,
            "last_update": now
        })
        st.success("Heart sent!")
    except Exception as e:
        st.error(f"Failed to send heart: {e}")

# Debug print variables before update
print("user:", user)
print("current_mood:", current_mood)
print("current_status:", current_status)

# Update Firebase with error handling
try:
    db.reference(user).update({
        "mood": current_mood,
        "status": current_status,
        "last_update": int(time.time())
    })
    print("Update successful!")
except Exception as e:
    print("Failed to update Firebase:", e)

# Display partner
st.header("Your Partner")
partner_data = db.reference(partner).get()

if partner_data:
    st.image(load_image(partner_data.get("mood", "Happy"), partner))
    st.write(f"**Mood:** {partner_data.get('mood', '')}")
    st.write(f"**Status:** {partner_data.get('status', '')}")

    if partner_data.get("sent_heart"):
        ts = partner_data.get("sent_heart_time")
        time_str = datetime.fromtimestamp(ts).strftime("%H:%M") if ts else "Unknown"
        st.markdown(f"💌 Heart received at **{time_str}**")
else:
    st.info("Waiting for partner to join...")

