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
INVITE_FILE = Path("static/Anjana x Sudarshan.pdf")
EVENT_DATE = datetime.datetime(2025, 8, 31, 12, 0, 0)
ADDRESS = "Farmhouse Collective, Nirmala Farm, Post, Virgonagar, Nimbekaipura, Bengaluru, Karnataka 560049"
MAPS_LINK = "https://maps.app.goo.gl/3ztqDExBFyaZ9Uer9"
TITLE = "Anjana x Sudarshan"

import base64
st.set_page_config(page_title=TITLE, layout="centered")

import base64
import streamlit as st

def set_bg_from_local(image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

        st.markdown(f"""
            <style>
            .stApp {{
                content: "";
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background-image: url("data:image/jpg;base64,{encoded}");
                background-size: contain;
                background-position: center top;
                background-repeat: repeat-y;
                background-attachment: fixed;
                z-index: -2;
            }}
    
            .stApp::after {{
                content: "";
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background-color: rgba(255, 248, 244, 0.90);  /* white transparent overlay */
                z-index: -1;
            }}
    
            .block-container {{
                background-color: transparent;
            }}
            </style>
        """, unsafe_allow_html=True)

# Call the function with your image
set_bg_from_local("static/background.jpeg")

st.markdown('''
<style>
.stApp [data-testid="stHeader"]{
    display:none;
}
</style>
''', unsafe_allow_html=True)

# Ensure directories exist
RSVP_DIR.mkdir(parents=True, exist_ok=True)
USERS_CSV.parent.mkdir(parents=True, exist_ok=True)


# Load user data from CSV (User ID, Party, WhatsApp No)
def load_users():
    users = {}
    if USERS_CSV.exists():
        with open(USERS_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                user_id = str(row['User Id']).strip()
                users[user_id] = {
                    'name': row['Party'].strip(),
                    'whatsapp': row['WhatsApp No'].strip()
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


# Entry point
query_params = st.query_params.to_dict()
print(query_params)
user_id = query_params.get("user", None)
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

    st.download_button("📄 Download Invitation", INVITE_FILE.read_bytes(), file_name="Anjana x Sudarshan.pdf")

    st.subheader("Your RSVP")
    st.markdown("### Your RSVP Details")
    st.write(f"**Name:** {rsvp['name']}")
    st.write(f"**WhatsApp No:** {rsvp['whatsapp']}")
    st.write(f"**Additional Guests:** {rsvp['additional_guests']}")
    st.write(f"**Food Preference:** {rsvp['food_preference']}")
    st.write(f"**Wants to Speak?** {'Yes' if rsvp['wants_to_speak'] else 'No'}")
    st.write(f"**Participating in Group Activities?** {'Yes' if rsvp['group_activities'] else 'No'}")

    if st.button("✏️ Edit your RSVP"):
        RSVP_DIR.joinpath(f"{user_id}.json").unlink(missing_ok=True)
        st.rerun()

    st.subheader("Venue")
    st.markdown(f"**Address:** {ADDRESS}")
    st.link_button("📍 Get Directions", MAPS_LINK)
    st.stop()

# If not RSVP'd yet
st.title("🎊 Wedding RSVP")
st.markdown(f"Hi **{user['name']}**, please fill in the details below.")

with st.form("rsvp_form"):
    whatsapp = st.text_input("WhatsApp No", user['whatsapp'])
    guests = st.number_input("Additional Guests", min_value=0, step=1)
    food = st.selectbox("Food Preference", ["Vegetarian", "Non-Vegetarian"])
    speak = st.checkbox("Would you like to say a few words at the event?")
    group = st.checkbox("Would you like to participate in group activities?")
    group_details = st.markdown("Group activities may include dancing/singing/acting "
                                "but rest assured there will be ample guidance in the "
                                "form of choreography as well as practice")
    submitted = st.form_submit_button("Submit RSVP")

    if submitted:
        save_rsvp(user_id, {
            "name": user['name'],
            "whatsapp": whatsapp,
            "additional_guests": guests,
            "food_preference": food,
            "wants_to_speak": speak,
            "group_activities": group
        })
        st.success("RSVP submitted!")
        st.rerun()
