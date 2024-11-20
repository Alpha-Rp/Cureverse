from flask import Flask, render_template, request
from medical_data import symptoms_db  # Import your symptoms database
import google.generativeai as genai
import os

app = Flask(__name__)

# Configure the Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))  # Use your actual environment variable for the API key
model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat(history=[])

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')

    # Check if the user input relates to symptoms
    if "symptom" in userText.lower():
        return process_symptoms(userText)
    else:
        return get_gemini_response(userText)

def process_symptoms(symptoms):
    symptoms = symptoms.lower()  # Normalize input for matching
    response = {
        "message": "Here are the results:",
        "causes": [],
        "consultationAdvice": "Consult a doctor if symptoms persist.",
        "ayurvedicRemedies": [],
        "dietPlan": []
    }

    # Iterate through the symptoms_db to find a match
    for key, value in symptoms_db.items():
        if key in symptoms or any(keyword in symptoms for keyword in value["keywords"]):
            response["causes"] = value["possible_conditions"]
            response["consultationAdvice"] = value["seek_doctor"]
            response["ayurvedicRemedies"] = value["ayurvedic_remedies"]
            response["dietPlan"] = value["diet_tips"]
            break  # Stop searching after the first match

    if not response["causes"]:  # If no causes were found
        response["message"] = "Sorry, I couldn't find information for that symptom."

    return response

def get_gemini_response(question):
    try:
        # Generate content using the Gemini model
        response = chat.send_message(question)
        return {"message": response}  # Wrap the response in a dictionary
    except Exception as e:
        print(f"Error generating response from Gemini: {e}")
        return {"message": "Sorry, I couldn't retrieve a response from the AI."}

if __name__ == "__main__":
    app.run(debug=True)  # Enable debug mode for easier troubleshooting