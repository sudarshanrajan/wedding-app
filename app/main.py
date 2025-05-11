# wedding_rsvp_app/main.py

import streamlit as st
import datetime
import os
import json
import csv
from pathlib import Path
from urllib.parse import urlencode

# Config
USERS_CSV = Path("data/users.csv")
RSVP_DIR = Path("data/rsvps")
INVITE_FILE = Path("static/wedding_invite.pdf")
EVENT_DATE = datetime.datetime(2025, 12, 15, 18, 0, 0)

st.set_page_config(page_title="Wedding RSVP", layout="centered")

# Ensure directories exist
RSVP_DIR.mkdir(parents=True, exist_ok=True)
USERS_CSV.parent.mkdir(parents=True, exist_ok=True)

# Load user data from CSV (Party, WhatsApp No)
def load_users():
    users = {}
    if USERS_CSV.exists():
        with open(USERS_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                user_id = row['WhatsApp No']
                users[user_id] = {
                    'name': row['Party'],
                    'phone': row['WhatsApp No']
                }
    return users

# Save RSVP
def save_rsvp(user_id, data):
    RSVP_DIR.joinpath(f"{user_id}.json").write_text(json.dumps(data))

# Load RSVP
def load_rsvp(user_id):
    path = RSVP_DIR.joinpath(f"{user_id}.json")
    if path.exists():
        return json.loads(path.read_text())
    return None

def get_location_link():
    address = "123 Wedding Venue Road, Cityville"
    return f"https://www.google.com/maps/search/?{urlencode({'q': address})}"

# Entry point
query_params = st.experimental_get_query_params()
user_id = query_params.get("user", [None])[0]
users = load_users()

if not user_id or user_id not in users:
    st.error("Invalid or missing user ID.")
    st.stop()

user = users[user_id]
rsvp = load_rsvp(user_id)

now = datetime.datetime.now()
event_over = now > EVENT_DATE

if event_over:
    st.title("🎉 Wedding Gallery")
    st.markdown("Photos and videos coming soon!")
    st.stop()

if rsvp:
    st.title("💌 You're Invited!")
    st.markdown("Thank you for your RSVP.")

    st.download_button("📄 Download Invitation", INVITE_FILE.read_bytes(), file_name="wedding_invite.pdf")

    st.subheader("Your RSVP")
    st.write(rsvp)

    if st.button("✏️ Edit your RSVP"):
        RSVP_DIR.joinpath(f"{user_id}.json").unlink(missing_ok=True)
        st.rerun()

    st.subheader("Venue")
    st.markdown(f"**Address:** 123 Wedding Venue Road, Cityville")
    st.link_button("📍 Get Directions", get_location_link())
    st.stop()

# If not RSVP'd yet
st.title("🎊 Wedding RSVP")
st.markdown(f"Hi **{user['name']}**, please fill in the details below.")

with st.form("rsvp_form"):
    phone = st.text_input("Phone Number", user['phone'])
    guests = st.number_input("Additional Guests", min_value=0, step=1)
    food = st.selectbox("Food Preference", ["Veg", "Non-Veg", "Both"])
    speak = st.checkbox("Would you like to say a few words at the event?")
    group = st.checkbox("Would you like to participate in group activities?")
    submitted = st.form_submit_button("Submit RSVP")

    if submitted:
        save_rsvp(user_id, {
            "name": user['name'],
            "phone": phone,
            "additional_guests": guests,
            "food_preference": food,
            "wants_to_speak": speak,
            "group_activities": group
        })
        st.success("RSVP submitted!")
        st.rerun()