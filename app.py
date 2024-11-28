import streamlit as st
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import uuid
import os
import time
import subprocess
import smtplib
import requests as rq
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Apply Streamlit's dark theme via configuration
st.set_page_config(
    page_title="Hackathon Unified App",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)



# Sidebar for navigation
st.sidebar.title("Navigation")

# Hauptmenü
hauptmenue = st.sidebar.selectbox("Bereich auswählen",
                                 ["Home", "Bewerber", "Personalstelle", "Adminbereich"])

# Untermenüs
if hauptmenue == "Home":
    page = "Home"
elif hauptmenue == "Bewerber":
    page = st.sidebar.selectbox("Bewerber",
                                ["Bewerbung einreichen", "Bewerbungsfragen beantworten", "Feedback"])
elif hauptmenue == "Personalstelle":
    page = st.sidebar.selectbox("Personalstelle",
                                ["Personalstelle", "Personalleiter", "Feedback Analysis", "Personalrat"])
elif hauptmenue == "Adminbereich":
    page = st.sidebar.selectbox("Adminbereich",
                                ["Job Crew", "Eval Crew", "Scrape Site", "Watson AI"])




# Set the FastAPI URLs and Feedback file path
JOB_CREW_URL = "http://localhost:8000/job_crew"  # Update with your FastAPI endpoint
EVAL_CREW_URL = "http://localhost:8000/eval_crew"  # Update with your FastAPI endpoint
CV_CREW_URL = "http://localhost:8000/cv_crew"
SCRAPE_SITE_URL = "http://localhost:8000/scrape_site"  # Hypothetical endpoint for scrape_site
WATSON_AI_URL = "http://localhost:8000/watson_ai"  # Hypothetical endpoint for Watson AI
GET_QUESTION_URL = "http://localhost:8000/get_question"  # Hypothetical endpoint for fetching questions
SAVE_ANSWER_URL = "http://localhost:8000/save_answer"  # Hypothetical endpoint for saving answers
FEEDBACK_FILE = "feedback.json"
APPLICATIONS_DIR = "applications"
QUESTIONS_FILE = "questions.json"
ANSWERS_DIR = "answers"
RATINGS_FILE = "ratings.json"
ANONYMIZED_DIR = "anonymized_pdfs"


# Ensure directories exist
os.makedirs(APPLICATIONS_DIR, exist_ok=True)
os.makedirs(ANSWERS_DIR, exist_ok=True)

# Load ratings or initialize as empty
try:
    with open(RATINGS_FILE, "r") as f:
        ratings_data = json.load(f)
except FileNotFoundError:
    ratings_data = {}

# Simulated questions for evaluation
def fetch_questions():
    # Example questions for simulation
    return [
        "Warum interessieren Sie sich für diese Position?",
        "Welche Erfahrungen bringen Sie mit?",
        "Was sind Ihre größten Stärken und Schwächen?"
    ]

# Initialize session state variables
if "applicant_uuid" not in st.session_state:
    st.session_state.applicant_uuid = None
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 1
    print("reset")
if "answers_data" not in st.session_state:
    st.session_state.answers_data = {}


# Simulated email function
def send_email(to_email, subject, message):
    try:

        # Email configuration (adjust with actual credentials and server settings)
        sender_email = "your-email@example.com"
        sender_password = "your-password"
        smtp_server = "smtp.example.com"
        smtp_port = 587

        # Create email
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        # Send email via SMTP
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True, "E-Mail erfolgreich gesendet!"
    except Exception as e:
        return False, f"Fehler beim Senden der E-Mail: {e}"

# Helper function to call the anonymization script
def anonymize_pdf(input_pdf_path, output_dir):
    script_path = "anonymer.py"
    command = [
        "python", script_path,
        input_pdf_path,
        output_dir
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        # Parse the output from the script (assumes it prints the result paths)
        output_lines = result.stdout.splitlines()
        md5_hash = output_lines[-3].split(": ")[-1]
        doc_uuid = output_lines[-2].split(": ")[-1]
        anonymized_pdf_path = output_lines[-1].split(": ")[-1]
        return md5_hash, doc_uuid, anonymized_pdf_path
    except subprocess.CalledProcessError as e:
        st.error(f"Fehler beim Anonymisieren der PDF: {e.stderr}")
        return None, None, None



if page == 'Home':

    # Create three columns
    col1, col2, col3 = st.columns(3)

    # Center the image in the middle column
    with col2:
        st.title("Willkommen bei")
        st.title("AI Trailblazers")
        st.image("logo.png", width=300)
        st.write(
            "Wir revolutionieren die Personalbeschaffung mit KI - vollautomatisiert und effizient."
    )


# Page content based on navigation
if page == "Job Crew":
    st.title("Job Crew Interaction")
    website_url = st.text_input("Website URL", placeholder="Enter the website URL")
    job_id = st.text_input("Job ID", placeholder="Enter the job ID")
    if st.button("Submit to Job Crew"):
        if website_url and job_id:
            payload = {"website_url": website_url, "job_id": job_id}
            try:
                response = requests.post(JOB_CREW_URL, json=payload)
                if response.status_code == 200:
                    st.success("Request was successful!")
                    st.json(response.json())
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please fill out all fields before submitting.")


elif page == "Eval Crew":
    st.title("Eval Crew Interaction")
    question = st.text_input("Question", placeholder="Enter your question")
    answer = st.text_input("Answer", placeholder="Enter your answer")
    if st.button("Submit to Eval Crew"):
        if question and answer:
            payload = {"question": question, "answer": answer}
            try:
                response = requests.post(EVAL_CREW_URL, json=payload)
                if response.status_code == 200:
                    st.success("Request was successful!")
                    st.json(response.json())
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please fill out all fields before submitting.")


elif page == "Scrape Site":
    st.title("Scrape Site Task")
    scrape_website_url = st.text_input("Website URL for Scraping", placeholder="Enter the website URL to scrape")
    if st.button("Scrape Website"):
        if scrape_website_url:
            payload = {"website_url": scrape_website_url}
            try:
                response = requests.post(SCRAPE_SITE_URL, json=payload)
                if response.status_code == 200:
                    st.success("Scraping was successful!")
                    st.json(response.json())
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please provide a URL to scrape.")


elif page == "Watson AI":
    st.title("Watson AI Prompt Interaction")
    prompt_text = st.text_area("Enter your prompt", placeholder="Describe what you want Watson AI to process")
    if st.button("Submit Prompt"):
        if prompt_text:
            payload = {"prompt": prompt_text}
            try:
                response = requests.post(WATSON_AI_URL, json=payload)
                if response.status_code == 200:
                    st.success("Watson AI Response:")
                    st.write(response.json().get("response", "No response provided"))
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a prompt before submitting.")


elif page == "Feedback":
    st.title("User Feedback")
    st.write("We value your feedback to improve the app!")
    user_feedback = st.text_area("Your Feedback", placeholder="Share your thoughts about the app")
    rating = st.slider("Rate the app", 1, 5, 3, help="1 = Poor, 5 = Excellent")
    if st.button("Submit Feedback"):
        if user_feedback:
            feedback_entry = {"feedback": user_feedback, "rating": rating}
            try:
                try:
                    with open(FEEDBACK_FILE, "r") as f:
                        feedback_data = json.load(f)
                except FileNotFoundError:
                    feedback_data = []
                feedback_data.append(feedback_entry)
                with open(FEEDBACK_FILE, "w") as f:
                    json.dump(feedback_data, f, indent=4)
                st.success("Thank you for your feedback!")
            except Exception as e:
                st.error(f"An error occurred while saving feedback: {e}")
        else:
            st.warning("Please provide your feedback before submitting.")


elif page == "Feedback Analysis":
    st.title("Feedback Analysis")
    try:
        with open(FEEDBACK_FILE, "r") as f:
            feedback_data = json.load(f)
        if feedback_data:
            df = pd.DataFrame(feedback_data)

            # Layout mit Spalten
            col1, col2 = st.columns([1, 2])

            # Feedback Data in der ersten Spalte
            with col1:
                st.subheader("Feedback Data")
                st.dataframe(df)

            # Rating Distribution in der zweiten Spalte
            with col2:
                st.subheader("Rating Distribution")
                fig, ax = plt.subplots()
                df['rating'].value_counts().sort_index().plot(kind='bar', ax=ax, color='r')
                ax.set_xlabel("Ratings")
                ax.set_ylabel("Frequency")
                ax.set_title("Distribution of Ratings")
                st.pyplot(fig)

            # Comments in voller Breite
            st.subheader("Comments")
            for i, row in df.iterrows():
                st.write(f"**Rating {row['rating']}**: {row['feedback']}")  # st.write für bessere Lesbarkeit

        else:
            st.warning("No feedback data available.")
    except FileNotFoundError:
        st.error("Feedback file not found. Please collect feedback first.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Page content based on navigation
if page == "Bewerbung einreichen":
    st.title("Bewerbung einreichen")

    # Input fields for applicant details
    name = st.text_input("Name", placeholder="Vor- und Nachname")
    email = st.text_input("Email", placeholder="Email")
    phone = st.text_input("Telefonnummer", placeholder="z. B. +49 123 4567890")
    birthdate = st.date_input("Geburtstag")
    job_id = st.text_input("Job-ID")

    # File uploader for the PDF application
    application_file = st.file_uploader("Bewerbung als PDF hochladen", type=["pdf"])

    # Submit button
    if st.button("Bewerbung einreichen"):
        if name and email and phone and application_file:
            try:
                # Generate a unique filename
                unique_id = str(uuid.uuid4())
                file_path = os.path.join(APPLICATIONS_DIR, f"{unique_id}.json")

                # Save application data as JSON
                application_data={
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "birthdate": birthdate.isoformat(),
                    "job_id": job_id,
                }

                files = {'cv': application_file.read()}
                response = rq.post(CV_CREW_URL, files=files, data=application_data)
                print(response.text)
                

                # Clear fields and display UUID
                st.success(f"Bewerbung erfolgreich eingereicht und anonymisiert! Ihre Referenz-ID: {unique_id}")
            except Exception as e:
                st.error(f"Ein Fehler ist aufgetreten: {e}")
        else:
            st.warning("Bitte alle Felder ausfüllen und ein PDF hochladen.")

# Initialize session state
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 1

if "answers_data" not in st.session_state:
    st.session_state.answers_data = {"answers": []}

if page == "Bewerbungsfragen beantworten":
    st.title("Bewerbungsfragen beantworten")

    # Input field for UUID
    applicant_uuid = st.text_input("Bewerbungs-UUID", placeholder="Geben Sie Ihre UUID ein")

    # Fetch and display questions
    if st.button("Fragen laden") or "loaded_questions" in st.session_state:
        # Load questions only once
        st.session_state.loaded_questions = True  # Ensure questions are only loaded once
        try:
            if st.session_state.current_question_index < 6:
                # Fetch the current question
                question_response = rq.get(GET_QUESTION_URL+f"?user_id={applicant_uuid}&n={st.session_state.current_question_index}")
                if question_response.status_code == 200:
                    question = question_response.text
                else:
                    question = "Fehler beim Laden der Frage. Bitte versuchen Sie es erneut."

                # Display the current question
                st.subheader(f"Frage: {question}")
                answer_text = st.text_area("Ihre Antwort", placeholder="Geben Sie Ihre Antwort ein")
                
                # Update the index for the next question
                st.session_state.current_question_index += 1

                # Start timer
                if "start_time" not in st.session_state:
                    st.session_state.start_time = time.time()

                # Submit answer
                if st.button("Antwort einreichen"):
                    # End timer
                    end_time = time.time()
                    time_taken = end_time - st.session_state.start_time
                    char_count = len(answer_text)
                    chars_per_minute = (char_count / time_taken) * 60 if time_taken > 0 else 0
                    response = rq.post(SAVE_ANSWER_URL, json={"user_id":applicant_uuid, "answer":answer_text, "n": st.session_state.current_question_index-1})

                    if response.status_code != 200:
                        st.error(f"Ein Fehler ist aufgetreten")
                    # Reset the timer
                    st.session_state.start_time = time.time()

            else:
                st.info("Sie haben alle Fragen beantwortet.")
        except Exception as e:
            st.error(f"Ein Fehler ist aufgetreten: {e}")
        

if page == "Personalstelle":
    st.title("Personalstelle")

    # Admin tabs
    admin_tab = st.tabs(["Eingegangene Bewerbungen", "Bewerbungsfragen und Auswertung", "Bewerberübersicht"])

    # Tab 1: Eingegangene Bewerbungen
    with admin_tab[0]:
        st.subheader("Eingegangene Bewerbungen")

        # List all UUIDs from the applications directory
        applications = [f.split(".")[0] for f in os.listdir(APPLICATIONS_DIR) if f.endswith(".json")]
        if applications:
            st.write("Liste der Bewerbungen (UUID):")
            for uuid in applications:
                st.write(f"- {uuid}")
        else:
            st.warning("Keine Bewerbungen vorhanden.")

    # Tab 2: Bewerbungsfragen und Auswertung
    with admin_tab[1]:
        st.subheader("Bewerbungsfragen und Auswertung")

        # List all UUIDs from the applications directory
        applications = [f.split(".")[0] for f in os.listdir(APPLICATIONS_DIR) if f.endswith(".json")]
        selected_uuid = st.selectbox("Wähle eine UUID",
                                     applications if applications else ["Keine Bewerbungen verfügbar"])

        if selected_uuid and selected_uuid != "Keine Bewerbungen verfügbar":
            # Check for answers file
            answers_file = os.path.join(ANSWERS_DIR, f"{selected_uuid}_answers.json")
            if os.path.exists(answers_file):
                with open(answers_file, "r") as f:
                    answers_data = json.load(f)

                st.write("Antworten des Bewerbers:")
                for answer_entry in answers_data.get("answers", []):
                    question = answer_entry.get("question", "Unbekannte Frage")
                    answer = answer_entry.get("answer", "Keine Antwort")
                    st.markdown(f"**{question}:** {answer}")

                # Example: Visualization (replace with real evaluation logic)
                st.subheader("Grafische Auswertung (Balkendiagramm)")
                fig, ax = plt.subplots()
                scores = [len(answer_entry.get("answer", "")) for answer_entry in answers_data.get("answers", [])]
                ax.bar(range(len(scores)), scores, tick_label=[f"Frage {i + 1}" for i in range(len(scores))])
                ax.set_ylabel("Zeichenanzahl")
                ax.set_title("Antwortlänge pro Frage")
                st.pyplot(fig)
            else:
                st.warning("Dieser Bewerber hat noch keine Fragen beantwortet.")
        else:
            st.warning("Keine gültige UUID ausgewählt.")

    # Tab 3: Bewerberübersicht
    with admin_tab[2]:
        st.subheader("Bewerberübersicht")
        if ratings_data:

            # Display UUIDs and points
            st.write("Liste der Bewerber mit Punkten:")
            for uuid, points in ratings_data.items():
                col1, col2, col3 = st.columns([2, 1, 2])
                col1.write(f"**UUID:** {uuid}")
                col2.write(f"Punkte: {points}")
                col3.button("EINLADEN", key=f"invite_{uuid}", help=f"Einladung für {uuid}")
                col3.button("NICHT EINLADEN", key=f"decline_{uuid}", help=f"Absage für {uuid}")
        else:
            st.warning("Keine Bewertungen vorhanden.")

if page == "Personalleiter":
    st.title("Personalleiter")

    # Load all applications
    applications = []
    for file in os.listdir(APPLICATIONS_DIR):
        if file.endswith(".json"):
            with open(os.path.join(APPLICATIONS_DIR, file), "r") as f:
                applications.append(json.load(f))
    if applications:
        for index, app in enumerate(applications):
            uuid = app.get("uuid", f"DummyUUID_{index}")
            name = app.get("name", "Unbekannt")
            email = app.get("email", "Unbekannt")
            points = app.get("points", "Keine Bewertung")

            # Display applicant details
            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
            col1.write(f"**UUID:** {uuid}")
            col2.write(f"**Name:** {name}")
            col3.write(f"**Punkte:** {points}")
            col4.button("Einladen", key=f"invite_{uuid}_{index}")
            col4.button("Nicht Einladen", key=f"decline_{uuid}_{index}")
    else:
        st.warning("Keine Bewerberdaten vorhanden.")

if page == 'Personalrat':
    st.title('Personalrat')
    st.title("Hinweis auf §78 BPersVG Mitbestimmung")
    st.write("""
            **§ 78 BPersVG** des Mitbestimmungsgesetzes regelt die Vertraulichkeit und den Umgang mit personenbezogenen Daten. 
            Informationen, die Sie im Rahmen des Bewerbungsverfahrens erhalten, unterliegen der Schweigepflicht.
            """)

    # Button zum Anzeigen einer Warnung
    if st.button("Alle eingeladenen Bewerbungen anzeigen"):
        st.warning("§11 BPerVG: Diese Daten unterliegen der Schweigepflicht! Sie sind nicht zur Einsicht berechtigt.")