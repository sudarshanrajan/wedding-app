# app/web_app.py
import os
from reportlab.lib.utils import ImageReader
import streamlit as st
import datetime
import csv
from pathlib import Path
import base64
import qrcode
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from PIL import Image

# Config
USERS_CSV = Path("data/users.csv")
INVITE_FILE = Path("static/Anjana x Sudarshan.pdf")
EVENT_DATE = datetime.datetime(2025, 8, 30, 23, 59, 59)
ADDRESS = "Farmhouse Collective, Nirmala Farm, Post, Virgonagar, Nimbekaipura, Bengaluru, Karnataka 560049"
MAPS_LINK = "https://maps.app.goo.gl/3ztqDExBFyaZ9Uer9"
TITLE = "Anjana x Sudarshan"

INVITE_FILE_QR_X = int(os.getenv("INVITE_FILE_QR_X"))
INVITE_FILE_QR_Y = int(os.getenv("INVITE_FILE_QR_Y"))
INVITE_FILE_QR_SIZE = int(os.getenv("INVITE_FILE_QR_SIZE"))
INVITE_FILE_QR_PAGE = int(os.getenv("INVITE_FILE_QR_PAGE"))
RAILWAY_PUBLIC_DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN")

CSV_KEYS = {
    "name": "Party",
    "whatsapp": "WhatsApp No",
    "additional_guests": "Additional Guests",
    "food_preference": "Food Preference",
    "wants_to_speak": "Wants to Speak",
    "group_activities": "Group Activities"
}

st.set_page_config(page_title=TITLE, layout="centered")


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
                background-color: rgba(255, 248, 244, 0.90);
                z-index: -1;
            }}

            .block-container {{
                background-color: transparent;
            }}
            </style>
        """, unsafe_allow_html=True)


set_bg_from_local("static/background.jpeg")

st.markdown('''
<style>
.stApp [data-testid="stHeader"]{
    display:none;
}
</style>
''', unsafe_allow_html=True)

USERS_CSV.parent.mkdir(parents=True, exist_ok=True)


# Load all users
def load_users():
    users = {}
    if USERS_CSV.exists():
        with open(USERS_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                user_id = str(row['User Id']).strip()
                users[user_id] = {
                    'name': row[CSV_KEYS['name']].strip(),
                    'whatsapp': row[CSV_KEYS['whatsapp']].strip()
                }
    return users


# Load RSVP from CSV
def load_rsvp_from_csv(user_id):
    if not USERS_CSV.exists():
        return None

    with open(USERS_CSV, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['User Id'].strip() == user_id:
                if any(row.get(CSV_KEYS[k], "").strip() != "" for k in
                       ['additional_guests', 'food_preference', 'wants_to_speak', 'group_activities']):
                    return {
                        "name": row.get(CSV_KEYS["name"], ""),
                        "whatsapp": row.get(CSV_KEYS["whatsapp"], ""),
                        "additional_guests": int(row.get(CSV_KEYS["additional_guests"], 0)),
                        "food_preference": row.get(CSV_KEYS["food_preference"], ""),
                        "wants_to_speak": row.get(CSV_KEYS["wants_to_speak"], "") == "True",
                        "group_activities": row.get(CSV_KEYS["group_activities"], "") == "True"
                    }
    return None


# Save RSVP to CSV
def save_rsvp_to_csv(user_id, rsvp_data):
    if not USERS_CSV.exists():
        return

    rows = []
    updated = False
    with open(USERS_CSV, newline='', encoding='utf-8') as csvfile:
        reader = list(csv.DictReader(csvfile))
        fieldnames = reader[0].keys() if reader else []

        for row in reader:
            if row['User Id'].strip() == user_id:
                for key, csv_key in CSV_KEYS.items():
                    if key in rsvp_data:
                        row[csv_key] = str(rsvp_data[key])
                updated = True
            rows.append(row)

    if not updated:
        return

    all_keys = list(fieldnames)
    for csv_key in CSV_KEYS.values():
        if csv_key not in all_keys:
            all_keys.append(csv_key)

    with open(USERS_CSV, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=all_keys)
        writer.writeheader()
        writer.writerows(rows)


# Generate QR image
def generate_qr_image(url: str) -> BytesIO:
    qr_img = qrcode.make(url)
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


# Create QR overlay
def create_qr_overlay(qr_image: BytesIO, coords) -> BytesIO:
    x, y, w, h = coords
    overlay = BytesIO()
    c = canvas.Canvas(overlay)

    qr_pil_image = Image.open(qr_image)
    qr_image_reader = ImageReader(qr_pil_image)
    c.drawImage(qr_image_reader, x, y, width=w, height=h)

    c.showPage()
    c.save()
    overlay.seek(0)
    return overlay


# Overlay QR on base PDF
def overlay_qr_on_pdf(base_pdf: bytes, overlay_pdf: BytesIO, page_num: int) -> BytesIO:
    base_pdf_stream = BytesIO(base_pdf)  # <-- wrap bytes in BytesIO
    reader = PdfReader(base_pdf_stream)
    overlay_reader = PdfReader(overlay_pdf)
    writer = PdfWriter()

    for i, page in enumerate(reader.pages):
        if i == page_num-1:
            page.merge_page(overlay_reader.pages[0])
        writer.add_page(page)

    result = BytesIO()
    writer.write(result)
    result.seek(0)
    return result


def prepare_invite(invite_for_user_id: str):
    url = "https://%s/app/?user=%s" % (RAILWAY_PUBLIC_DOMAIN, invite_for_user_id)
    qr = generate_qr_image(url)

    # Step 2: Create overlay for QR at specific position on A4 page
    coords = (INVITE_FILE_QR_X, INVITE_FILE_QR_Y, INVITE_FILE_QR_SIZE, INVITE_FILE_QR_SIZE)
    overlay = create_qr_overlay(qr, coords)

    # Step 3: Read base invitation from disk and overlay the QR
    base_pdf_bytes = INVITE_FILE.read_bytes()
    return overlay_qr_on_pdf(base_pdf_bytes, overlay, page_num=INVITE_FILE_QR_PAGE)


# App logic
query_params = st.query_params.to_dict()
user_id = query_params.get("user", None)
users = load_users()

if not user_id or user_id not in users:
    st.error("Invalid or missing user ID.")
    st.stop()

user = users[user_id]
rsvp = load_rsvp_from_csv(user_id)

now = datetime.datetime.now()
event_over = now > EVENT_DATE

if event_over:
    st.title("🎉 Wedding Gallery")
    st.markdown("Photos and videos coming soon!")
    st.stop()

if rsvp:
    st.title("💌 You're Invited!")
    st.markdown("Thank you for your RSVP.")

    prepared_invite = prepare_invite(invite_for_user_id=user_id)
    st.download_button("📄 Download Invitation", prepared_invite, file_name="Anjana x Sudarshan.pdf")

    st.subheader("Your RSVP")
    st.markdown("### Your RSVP Details")
    st.write(f"**Name:** {rsvp['name']}")
    st.write(f"**WhatsApp No:** {rsvp['whatsapp']}")
    st.write(f"**Additional Guests:** {rsvp['additional_guests']}")
    st.write(f"**Food Preference:** {rsvp['food_preference']}")
    st.write(f"**Wants to Speak?** {'Yes' if rsvp['wants_to_speak'] else 'No'}")
    st.write(f"**Participating in Group Activities?** {'Yes' if rsvp['group_activities'] else 'No'}")

    if st.button("✏️ Edit your RSVP"):
        save_rsvp_to_csv(user_id, {k: "" for k in
                                   ['additional_guests', 'food_preference', 'wants_to_speak', 'group_activities']})
        st.rerun()

    st.subheader("Venue")
    st.markdown(f"**Address:** {ADDRESS}")
    st.link_button("📍 Get Directions", MAPS_LINK)
    st.stop()

# Form
st.title("🎊 Wedding RSVP")
st.markdown(f"Hi **{user['name']}**, please fill in the details below.")

with st.form("rsvp_form"):
    whatsapp = st.text_input("WhatsApp No", user['whatsapp'], disabled=True)
    guests = st.number_input("Additional Guests", min_value=0, step=1)
    food = st.selectbox("Food Preference", ["Vegetarian", "Non-Vegetarian"])
    speak = st.checkbox("Would you like to say a few words at the event?")
    group = st.checkbox("Would you like to participate in group activities?")
    st.markdown("Group activities may include dancing/singing/acting "
                "but rest assured there will be ample guidance in the "
                "form of choreography as well as practice")
    submitted = st.form_submit_button("Submit RSVP")

    if submitted:
        save_rsvp_to_csv(user_id, {
            "name": user['name'],
            "whatsapp": whatsapp,
            "additional_guests": guests,
            "food_preference": food,
            "wants_to_speak": speak,
            "group_activities": group
        })
        st.success("RSVP submitted!")
        st.rerun()
