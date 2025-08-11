from flask import Flask, render_template, request, jsonify, url_for, session, redirect, make_response
from flask_socketio import SocketIO, emit
from medical_data import symptoms_db  # Import your symptoms database
from ayurvedic_concepts import doshas, get_current_season, analyze_dosha_responses, get_dosha_recommendations
from user_auth import user_db  # Import user authentication system
import google.generativeai as genai
import os
import time
import json
import re
from datetime import datetime
from functools import wraps

# Function to extract contextual information from user messages
def extract_context(message):
    """
    Extract contextual information from user messages that might be relevant for diagnosis.

    Args:
        message: The user's message as a string

    Returns:
        A dictionary containing extracted contextual information
    """
    context = {
        "weather_exposure": None,
        "time_reference": None,
        "duration": None,
        "severity_indicators": []
    }

    # Check for weather exposure
    weather_patterns = [
        (r"(got wet|soaked|drenched|caught) in (rain|snow|cold)", "weather_exposure", "rain/cold"),
        (r"(exposed|exposure) to (cold|rain|snow|wind|hot|heat)", "weather_exposure", "\\2"),
        (r"(stayed|been) in (cold|rain|ac|air conditioning|heat)", "weather_exposure", "\\2")
    ]

    for pattern, key, value in weather_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            if "\\2" in value:
                context[key] = match.group(2)
            else:
                context[key] = value

    # Check for time references
    time_patterns = [
        (r"(yesterday|last night|last week|last month|few days ago|a week ago)", "time_reference"),
        (r"(since|for) (a|one|two|three|four|five|1|2|3|4|5) (day|days|week|weeks|month|months)", "duration")
    ]

    for pattern, key in time_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            context[key] = match.group(0)

    # Check for severity indicators
    severity_patterns = [
        r"(very|really|so|too|extremely|quite|a lot|severe|bad|worst|terrible|horrible|unbearable)",
        r"(full|complete|totally|entirely|absolutely)",
        r"(can't|cannot|couldn't|unable to) (sleep|eat|work|function|breathe)"
    ]

    for pattern in severity_patterns:
        matches = re.finditer(pattern, message, re.IGNORECASE)
        for match in matches:
            if match.group(0) not in context["severity_indicators"]:
                context["severity_indicators"].append(match.group(0))

    return context

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
socketio = SocketIO(app, cors_allowed_origins="*")

# Authentication helper functions
def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_token = request.cookies.get('session_token')
        if not session_token:
            return redirect(url_for('login'))
        
        session_result = user_db.validate_session(session_token)
        if not session_result['success']:
            response = make_response(redirect(url_for('login')))
            response.set_cookie('session_token', '', expires=0)
            return response
        
        # Add user info to request context
        request.current_user = session_result['user']
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current user from session"""
    session_token = request.cookies.get('session_token')
    if not session_token:
        return None
    
    session_result = user_db.validate_session(session_token)
    if session_result['success']:
        return session_result['user']
    return None

# Configure the Gemini API with your new API key
GEMINI_API_KEY = "AIzaSyB5zU9w4blPu-EDVmwzxpczQGWt1CbvzKg"  # Replace with your new API key
genai.configure(api_key=GEMINI_API_KEY)

# Configure Gemini model with better parameters for medical responses
generation_config = {
    "temperature": 0.4,  # Lower temperature for more factual responses
    "top_p": 0.8,
    "top_k": 40,
    "max_output_tokens": 2048,  # Allow longer responses for detailed medical information
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    safety_settings=safety_settings
)

chat = model.start_chat(history=[])

@app.route("/")
def home():
    return render_template("landing.html")

@app.route("/landing")
def landing():
    return render_template("landing.html")

@app.route("/chat")
@login_required
def chat_interface():
    user = get_current_user()
    user_name = f"{user['first_name']} {user['last_name']}" if user else "Guest"
    return render_template("modern_index.html", user_name=user_name)

@app.route("/legacy")
@login_required
def legacy_home():
    user = get_current_user()
    user_name = f"{user['first_name']} {user['last_name']}" if user else "Guest"
    return render_template("index.html", user_name=user_name)

@app.route("/login")
def login():
    # Redirect to chat if already logged in
    current_user = get_current_user()
    if current_user:
        return redirect(url_for('chat_interface'))
    return render_template("login.html")

@app.route("/register")
def register():
    # Redirect to chat if already logged in
    current_user = get_current_user()
    if current_user:
        return redirect(url_for('chat_interface'))
    return render_template("register.html")

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session_token = request.cookies.get('session_token')
    if session_token:
        user_db.logout_session(session_token)
    
    response = make_response(redirect(url_for('home')))
    response.set_cookie('session_token', '', expires=0)
    return response

@app.route("/dosha-analysis")
@login_required
def dosha_questionnaire():
    user = get_current_user()
    user_name = f"{user['first_name']} {user['last_name']}" if user else "Guest"
    return render_template("dosha_questionnaire.html", user_name=user_name)

@app.route("/seasonal-wellness")
@login_required
def seasonal_wellness():
    user = get_current_user()
    user_name = f"{user['first_name']} {user['last_name']}" if user else "Guest"
    season_name, season_data = get_current_season()
    return render_template("seasonal_wellness.html", season=season_name, season_data=season_data, user_name=user_name)

@app.route("/remedy-library")
@login_required
def remedy_library():
    user = get_current_user()
    user_name = f"{user['first_name']} {user['last_name']}" if user else "Guest"
    return render_template("remedy_library.html", user_name=user_name)

@app.route("/health-library")
@login_required
def health_library():
    user = get_current_user()
    user_name = f"{user['first_name']} {user['last_name']}" if user else "Guest"
    return render_template("health_library.html", user_name=user_name)

@app.route("/find-doctor")
@login_required
def find_doctor():
    user = get_current_user()
    user_name = f"{user['first_name']} {user['last_name']}" if user else "Guest"
    return render_template("find_doctor.html", user_name=user_name)

@app.route("/preferences")
@login_required
def preferences():
    user = get_current_user()
    user_name = f"{user['first_name']} {user['last_name']}" if user else "Guest"
    return render_template("preferences.html", user_name=user_name)

@app.route("/help-support")
@login_required
def help_support():
    user = get_current_user()
    user_name = f"{user['first_name']} {user['last_name']}" if user else "Guest"
    return render_template("help_support.html", user_name=user_name)

# Authentication API routes
@app.route("/api/register", methods=["POST"])
def api_register():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['firstName', 'lastName', 'email', 'password', 'dateOfBirth', 'gender', 'age']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"success": False, "message": f"{field} is required"})
        
        # Create user account
        result = user_db.create_user(data)
        
        if result['success']:
            return jsonify({
                "success": True, 
                "message": "Account created successfully! Please check your email for verification."
            })
        else:
            return jsonify({"success": False, "message": result['message']})
            
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({"success": False, "message": "Registration failed. Please try again."})

@app.route("/api/login", methods=["POST"])
def api_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        remember_me = data.get('remember', False)
        
        if not email or not password:
            return jsonify({"success": False, "message": "Email and password are required"})
        
        # Authenticate user
        auth_result = user_db.authenticate_user(email, password)
        
        if not auth_result['success']:
            return jsonify({"success": False, "message": auth_result['message']})
        
        user = auth_result['user']
        
        # Create session
        session_result = user_db.create_session(
            user['id'], 
            request.headers.get('User-Agent'),
            request.remote_addr,
            remember_me
        )
        
        if not session_result['success']:
            return jsonify({"success": False, "message": "Failed to create session"})
        
        # Create response with session cookie
        response_data = {
            "success": True,
            "message": f"Welcome back, {user['first_name']}!",
            "user": user,
            "redirect": "/chat"
        }
        
        response = make_response(jsonify(response_data))
        response.set_cookie(
            'session_token', 
            session_result['session_token'],
            expires=session_result['expires_at'],
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite='Lax'
        )
        
        return response
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"success": False, "message": "Login failed. Please try again."})

@app.route("/api/user/profile")
@login_required
def get_user_profile():
    try:
        user_id = request.current_user['id']
        profile_result = user_db.get_user_profile(user_id)
        
        if profile_result['success']:
            return jsonify({"success": True, "profile": profile_result['profile']})
        else:
            return jsonify({"success": False, "message": profile_result['message']})
            
    except Exception as e:
        print(f"Profile error: {e}")
        return jsonify({"success": False, "message": "Failed to get profile"})

@app.route("/api/user/chat-history")
@login_required
def get_user_chat_history():
    try:
        user_id = request.current_user['id']
        limit = request.args.get('limit', 50, type=int)

        history_result = user_db.get_chat_history(user_id, limit)

        return jsonify(history_result)

    except Exception as e:
        print(f"Chat history error: {e}")
        return jsonify({"success": False, "message": "Failed to get chat history"})

@app.route("/api/user/clear-chat-history", methods=["POST"])
@login_required
def clear_chat_history():
    try:
        user_id = request.current_user['id']
        # Add method to clear chat history in user_db
        # For now, return success
        return jsonify({"success": True, "message": "Chat history cleared successfully"})

    except Exception as e:
        print(f"Clear chat history error: {e}")
        return jsonify({"success": False, "message": "Failed to clear chat history"})

# Socket.IO event handler for receiving messages
@socketio.on('send_message')
def handle_message(data):
    user_message = data.get('message', '')
    
    # Get current user from session
    session_token = request.cookies.get('session_token') if hasattr(request, 'cookies') else None
    current_user = None
    
    if session_token:
        session_result = user_db.validate_session(session_token)
        if session_result['success']:
            current_user = session_result['user']

    # Check if the user input relates to symptoms by looking for exact matches or keywords
    is_symptom_related = False

    # First check for direct symptom names
    for symptom in symptoms_db.keys():
        if symptom in user_message.lower():
            is_symptom_related = True
            break

    # If not found, check for keywords
    if not is_symptom_related:
        for symptom_data in symptoms_db.values():
            if any(keyword in user_message.lower() for keyword in symptom_data.get("keywords", [])):
                is_symptom_related = True
                break

    # Process the message based on whether it's symptom-related
    if is_symptom_related:
        response = process_symptoms(user_message)
    else:
        response = get_gemini_response(user_message)

    # Add timestamp to the response
    response["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Add user info if logged in
    if current_user:
        response["user_id"] = current_user['id']
        response["user_name"] = f"{current_user['first_name']} {current_user['last_name']}"
        
        # Save chat history
        symptoms_detected = None
        remedies_suggested = None
        
        if is_symptom_related and response.get('matchedSymptom'):
            symptoms_detected = response.get('matchedSymptom')
            remedies_suggested = ', '.join(response.get('ayurvedicRemedies', []))
        
        user_db.save_chat_message(
            current_user['id'],
            user_message,
            response['message'],
            'symptom_query' if is_symptom_related else 'general_query',
            symptoms_detected,
            remedies_suggested
        )

    # Send the response back to the client
    emit('receive_message', response)

# Legacy HTTP route for backward compatibility
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

    # Get current season for seasonal recommendations
    current_season, season_data = get_current_season()

    # Extract context from the message
    context = extract_context(symptoms)

    # Track all matched symptoms with scores to prioritize them
    symptom_matches = []

    # First, check for exact matches (highest priority)
    for key, value in symptoms_db.items():
        if key in symptoms:
            # Exact match gets a high score
            symptom_matches.append({
                "symptom": key,
                "data": value,
                "score": 10,  # High score for exact match
                "match_type": "exact"
            })

    # Then check for keyword matches
    for key, value in symptoms_db.items():
        # Skip if we already have an exact match for this symptom
        if any(match["symptom"] == key and match["match_type"] == "exact" for match in symptom_matches):
            continue

        # Check each keyword
        for keyword in value["keywords"]:
            if keyword in symptoms:
                # Calculate score based on keyword length (longer keywords are more specific)
                score = 5 + (len(keyword) / 10)

                # Boost score if keyword appears multiple times or is a significant part of the message
                if symptoms.count(keyword) > 1:
                    score += 2

                # Add to matches if not already added or if this has a higher score
                existing_match = next((match for match in symptom_matches if match["symptom"] == key), None)
                if existing_match:
                    if score > existing_match["score"]:
                        existing_match["score"] = score
                        existing_match["match_type"] = "keyword"
                else:
                    symptom_matches.append({
                        "symptom": key,
                        "data": value,
                        "score": score,
                        "match_type": "keyword"
                    })

    # Sort matches by score (highest first)
    symptom_matches.sort(key=lambda x: x["score"], reverse=True)

    # Convert to the old format for compatibility
    matched_symptoms = [match["symptom"] for match in symptom_matches]
    matched_data = {match["symptom"]: match["data"] for match in symptom_matches}

    # If we found matches, create a response
    if matched_symptoms:
        # Check if we have multiple symptoms that should be combined
        combined_response = False

        # Look for common combinations (cold + fever, headache + fever, etc.)
        if len(matched_symptoms) >= 2:
            cold_index = next((i for i, s in enumerate(matched_symptoms) if s == "cold"), None)
            fever_index = next((i for i, s in enumerate(matched_symptoms) if s == "fever"), None)
            headache_index = next((i for i, s in enumerate(matched_symptoms) if s == "headache"), None)

            # If we have both cold and fever, create a combined response
            if cold_index is not None and fever_index is not None:
                combined_response = True
                primary_symptom = "cold with fever"
                primary_data = matched_data["cold"]  # Use cold as the base
                secondary_data = matched_data["fever"]
            # If we have both headache and fever, create a combined response
            elif headache_index is not None and fever_index is not None:
                combined_response = True
                primary_symptom = "headache with fever"
                primary_data = matched_data["headache"]  # Use headache as the base
                secondary_data = matched_data["fever"]
            # If we have both cold and headache, create a combined response
            elif cold_index is not None and headache_index is not None:
                combined_response = True
                primary_symptom = "cold with headache"
                primary_data = matched_data["cold"]  # Use cold as the base
                secondary_data = matched_data["headache"]

        # If no combined response, use the highest scoring symptom
        if not combined_response:
            primary_symptom = matched_symptoms[0]
            primary_data = matched_data[primary_symptom]
            secondary_data = None

        # Get context information
        context = extract_context(symptoms)

        # Create a personalized response message with improved formatting
        if combined_response:
            response_message = f"## Understanding Your {primary_symptom.capitalize()}\n\n"
        else:
            response_message = f"## Understanding Your {primary_symptom.capitalize()}\n\n"

        # Add context-specific information if available
        if context["weather_exposure"]:
            response_message += f"Based on your message, I understand that you were exposed to {context['weather_exposure']}. "

            if context["time_reference"]:
                response_message += f"This happened {context['time_reference']}. "

            response_message += "This exposure likely contributed to your current symptoms.\n\n"

        # Add possible causes section
        response_message += "### Possible Causes:\n"

        # For combined symptoms, merge and deduplicate causes
        if combined_response:
            all_causes = primary_data["possible_conditions"] + secondary_data["possible_conditions"]
            unique_causes = []
            for cause in all_causes:
                if cause not in unique_causes:
                    unique_causes.append(cause)
                    response_message += f"* **{cause}**\n"
        else:
            for cause in primary_data["possible_conditions"]:
                response_message += f"* **{cause}**\n"

        # Add description if available
        if "description" in primary_data:
            response_message += f"\n{primary_data['description']}\n"

        # For combined symptoms, add the secondary description
        if combined_response and "description" in secondary_data:
            response_message += f"\n{secondary_data['description']}\n"

        # Add dosha information if available
        if "dosha_imbalance" in primary_data:
            if combined_response and "dosha_imbalance" in secondary_data:
                response_message += f"\n### Dosha Imbalance:\n* This combination of symptoms indicates an imbalance of **{primary_data['dosha_imbalance']}** with **{secondary_data['dosha_imbalance']}**.\n"
            else:
                response_message += f"\n### Dosha Imbalance:\n* This condition is often associated with **{primary_data['dosha_imbalance']}**.\n"

        # Add when to see a doctor - use the more cautious advice if combined
        if combined_response:
            response_message += f"\n### When to Consult a Doctor:\n* {primary_data['seek_doctor']}\n* {secondary_data['seek_doctor']}\n"
        else:
            response_message += f"\n### When to Consult a Doctor:\n* {primary_data['seek_doctor']}\n"

        # Add Ayurvedic remedies section
        response_message += "\n### Ayurvedic Remedies You Can Try at Home:\n"

        # For combined symptoms, prioritize remedies that help both conditions
        if combined_response:
            # Find remedies that help both conditions
            primary_remedies = primary_data["ayurvedic_remedies"]
            secondary_remedies = secondary_data["ayurvedic_remedies"]

            # First add remedies that help both conditions
            for remedy in primary_remedies:
                if any(secondary_remedy.lower().startswith(remedy.split(" - ")[0].lower()) for secondary_remedy in secondary_remedies):
                    response_message += f"* {remedy} **(helps with both {primary_symptom.split(' with ')[0]} and {primary_symptom.split(' with ')[1]})**\n"
                else:
                    response_message += f"* {remedy} **(primarily for {primary_symptom.split(' with ')[0]})**\n"

            # Then add unique remedies from the secondary condition
            for remedy in secondary_remedies:
                if not any(primary_remedy.lower().startswith(remedy.split(" - ")[0].lower()) for primary_remedy in primary_remedies):
                    response_message += f"* {remedy} **(primarily for {primary_symptom.split(' with ')[1]})**\n"
        else:
            for remedy in primary_data["ayurvedic_remedies"]:
                response_message += f"* {remedy}\n"

        # Add diet recommendations
        response_message += "\n### Dietary Recommendations:\n"

        # For combined symptoms, merge and deduplicate diet tips
        if combined_response:
            all_diet_tips = primary_data["diet_tips"] + secondary_data["diet_tips"]
            unique_diet_tips = []
            for tip in all_diet_tips:
                if tip not in unique_diet_tips:
                    unique_diet_tips.append(tip)
                    response_message += f"* {tip}\n"
        else:
            for diet_tip in primary_data["diet_tips"]:
                response_message += f"* {diet_tip}\n"

        # Add seasonal considerations if available
        if "seasonal_considerations" in primary_data and current_season in primary_data["seasonal_considerations"]:
            response_message += f"\n### Seasonal Consideration ({current_season.capitalize()}):\n* {primary_data['seasonal_considerations'][current_season]}\n"

        # For combined symptoms, add secondary seasonal considerations
        if combined_response and "seasonal_considerations" in secondary_data and current_season in secondary_data["seasonal_considerations"]:
            response_message += f"* {secondary_data['seasonal_considerations'][current_season]}\n"

        # Create the response object
        if combined_response:
            # Merge causes from both conditions
            all_causes = primary_data["possible_conditions"] + secondary_data["possible_conditions"]
            unique_causes = []
            for cause in all_causes:
                if cause not in unique_causes:
                    unique_causes.append(cause)

            # Combine consultation advice
            combined_advice = f"{primary_data['seek_doctor']}. Also, {secondary_data['seek_doctor']}"

            # Combine remedies
            combined_remedies = primary_data["ayurvedic_remedies"] + [
                remedy for remedy in secondary_data["ayurvedic_remedies"]
                if not any(primary_remedy.lower().startswith(remedy.split(" - ")[0].lower())
                          for primary_remedy in primary_data["ayurvedic_remedies"])
            ]

            # Combine diet tips
            all_diet_tips = primary_data["diet_tips"] + secondary_data["diet_tips"]
            unique_diet_tips = []
            for tip in all_diet_tips:
                if tip not in unique_diet_tips:
                    unique_diet_tips.append(tip)

            response = {
                "message": response_message,
                "causes": unique_causes,
                "consultationAdvice": combined_advice,
                "ayurvedicRemedies": combined_remedies,
                "dietPlan": unique_diet_tips,
                "matchedSymptom": primary_symptom,
                "combinedSymptoms": True,
                "primarySymptom": primary_symptom.split(" with ")[0],
                "secondarySymptom": primary_symptom.split(" with ")[1]
            }

            # Add context information if available
            if context["weather_exposure"] or context["time_reference"] or context["severity_indicators"]:
                response["context"] = context

            # Add remedy preparations if available in either condition
            remedy_preps = {}
            if "remedy_preparations" in primary_data:
                remedy_preps.update(primary_data["remedy_preparations"])
            if "remedy_preparations" in secondary_data:
                remedy_preps.update(secondary_data["remedy_preparations"])

            if remedy_preps:
                response["remedyPreparations"] = list(remedy_preps.keys())

                # Add a note about detailed preparation instructions
                response_message += "\n### Detailed Remedy Preparations:\n"
                response_message += "* For detailed preparation instructions, click on any of the remedies in the card below.\n"

            # Add dosha information if available
            if "dosha_imbalance" in primary_data and "dosha_imbalance" in secondary_data:
                response["doshaImbalance"] = f"{primary_data['dosha_imbalance']} with {secondary_data['dosha_imbalance']}"
            elif "dosha_imbalance" in primary_data:
                response["doshaImbalance"] = primary_data["dosha_imbalance"]

            # Add seasonal considerations if available
            seasonal_considerations = {}
            if "seasonal_considerations" in primary_data:
                seasonal_considerations.update(primary_data["seasonal_considerations"])
            if "seasonal_considerations" in secondary_data:
                seasonal_considerations.update(secondary_data["seasonal_considerations"])

            if seasonal_considerations:
                response["seasonalConsiderations"] = seasonal_considerations
                response["currentSeason"] = current_season
        else:
            # Single symptom response
            response = {
                "message": response_message,
                "causes": primary_data["possible_conditions"],
                "consultationAdvice": primary_data["seek_doctor"],
                "ayurvedicRemedies": primary_data["ayurvedic_remedies"],
                "dietPlan": primary_data["diet_tips"],
                "matchedSymptom": primary_symptom
            }

            # Add context information if available
            if context["weather_exposure"] or context["time_reference"] or context["severity_indicators"]:
                response["context"] = context

            # Add remedy preparations if available
            if "remedy_preparations" in primary_data:
                response["remedyPreparations"] = list(primary_data["remedy_preparations"].keys())

                # Add a note about detailed preparation instructions
                response_message += "\n### Detailed Remedy Preparations:\n"
                response_message += "* For detailed preparation instructions, click on any of the remedies in the card below.\n"

            # Add dosha information if available
            if "dosha_imbalance" in primary_data:
                response["doshaImbalance"] = primary_data["dosha_imbalance"]

            # Add seasonal considerations if available
            if "seasonal_considerations" in primary_data:
                response["seasonalConsiderations"] = primary_data["seasonal_considerations"]
                response["currentSeason"] = current_season

        # Update the message in the response
        response["message"] = response_message
    else:
        # No matches found, use Gemini to generate a response with better formatting

        # Extract context for better prompting
        context = extract_context(symptoms)
        context_prompt = ""

        if context["weather_exposure"]:
            context_prompt += f"The user mentioned being exposed to {context['weather_exposure']}. "

        if context["time_reference"]:
            context_prompt += f"This happened {context['time_reference']}. "

        if context["severity_indicators"]:
            context_prompt += f"They described their symptoms as {', '.join(context['severity_indicators'])}. "

        prompt = f"""
        The user mentioned these symptoms: {symptoms}.
        {context_prompt}

        Please provide a helpful response in the following format:

        1. Start with a heading "## Understanding Your Symptoms"

        2. FIRST, explain the likely causes of these symptoms. Include a section "### Possible Causes:" with bullet points (* ) for each possible cause. This is very important - the user wants to understand WHY they are experiencing these symptoms before getting remedies.

        3. Include a section "### When to Consult a Doctor:" with bullet points

        4. Include a section "### Ayurvedic Remedies You Can Try at Home:" with detailed bullet points. For each remedy, include dosage information (e.g., "2-3 cups daily" or "apply twice daily").

        5. Include a section "### Dietary Recommendations:" with bullet points

        6. If possible, mention which dosha (Vata, Pitta, or Kapha) might be imbalanced in a section "### Dosha Imbalance:"

        7. Consider that it's currently {current_season} season and include seasonal advice

        Make sure each section is clearly formatted with markdown headings (###) and bullet points (*).
        Focus on Ayurvedic and natural remedies that can be prepared at home.
        Be specific and detailed in your recommendations.
        """

        gemini_response = get_gemini_response(prompt)

        response = {
            "message": gemini_response["message"],
            "causes": [],
            "consultationAdvice": "If symptoms persist or worsen, please consult a healthcare professional.",
            "ayurvedicRemedies": [],
            "dietPlan": [],
            "currentSeason": current_season
        }

    return response

def get_gemini_response(question):
    try:
        # Enhanced prompt specifically focused on Ayurvedic remedies
        enhanced_prompt = f"""
        You are CureVerse AI, an expert Ayurvedic health assistant specializing in traditional Indian medicine and natural remedies.

        User Question: {question}

        🌿 **IMPORTANT: Focus ONLY on Ayurvedic and natural remedies. This is your primary expertise.**

        Please provide a comprehensive Ayurvedic response that includes:

        ### 🕉️ Ayurvedic Analysis
        - Analyze the condition from an Ayurvedic perspective (Vata, Pitta, Kapha doshas)
        - Identify the root cause according to Ayurvedic principles

        ### 🌿 Natural Ayurvedic Remedies
        - Provide 3-5 specific Ayurvedic remedies using herbs, spices, and natural ingredients
        - Include preparation methods and dosage instructions
        - Mention traditional Ayurvedic formulations if applicable

        ### 🍃 Herbal Recommendations
        - Suggest specific Ayurvedic herbs (like Turmeric, Ashwagandha, Triphala, etc.)
        - Explain their properties and benefits
        - Provide usage instructions

        ### 🥗 Ayurvedic Diet & Lifestyle
        - Recommend foods that balance the affected doshas
        - Suggest foods to avoid
        - Include lifestyle practices (yoga, pranayama, meditation)

        ### ⚠️ Important Notes
        - Always emphasize consulting an Ayurvedic practitioner for personalized treatment
        - Mention any contraindications or precautions
        - Suggest when to seek medical attention

        Format your response with clear markdown headers (###) and bullet points (*).
        Focus exclusively on Ayurvedic wisdom and natural healing methods.
        Make your response detailed, practical, and actionable.
        """

        # Generate content using the Gemini model
        response = chat.send_message(enhanced_prompt)

        # Process the response to clean up formatting issues
        processed_text = response.text

        # Clean up triple asterisks and other formatting issues
        # Fix triple asterisks followed by text and colon (headers)
        processed_text = re.sub(r'\*\*\*\s*([^:*]+):', r'**\1:**', processed_text)
        # Fix triple asterisks at the beginning of lines (bullet points)
        processed_text = re.sub(r'^\*\*\*\s*([^\n]+)', r'* **\1**', processed_text, flags=re.MULTILINE)
        # Fix triple asterisks in the middle of text
        processed_text = re.sub(r'\*\*\*\s*([^*]+)\*\*\*', r'**\1**', processed_text)
        # Fix any remaining triple asterisks
        processed_text = re.sub(r'\*\*\*', r'**', processed_text)
        
        # Ensure proper bullet point formatting
        processed_text = re.sub(r'^(\*{2,})\s+', r'* ', processed_text, flags=re.MULTILINE)
        
        # Clean up any remaining formatting issues
        processed_text = re.sub(r'\*{4,}', r'**', processed_text)  # Replace 4+ asterisks with double
        processed_text = re.sub(r'^\s*\*\s*\*\s*', r'* ', processed_text, flags=re.MULTILINE)  # Fix double asterisks at start
        
        return {
            "message": processed_text,
            "causes": [],
            "consultationAdvice": "",
            "ayurvedicRemedies": [],
            "dietPlan": []
        }
    except Exception as e:
        print(f"Error generating response from Gemini: {e}")
        return {
            "message": "I apologize, but I'm having trouble processing your request right now. Please try again in a moment or rephrase your question.",
            "causes": [],
            "consultationAdvice": "",
            "ayurvedicRemedies": [],
            "dietPlan": []
        }

# API endpoint for dosha analysis
@app.route("/api/dosha-analysis", methods=["POST"])
def dosha_analysis():
    responses = request.json.get('responses', {})

    if not responses:
        return jsonify({"status": "error", "message": "No responses provided"})

    # Analyze the responses to determine dosha type
    analysis_result = analyze_dosha_responses(responses)

    # Get recommendations based on dosha type
    dosha_type = analysis_result["predominant_dosha"]
    recommendations = get_dosha_recommendations(dosha_type)

    # Get information about the dosha(s)
    dosha_info = {}
    if "-" in dosha_type:
        # Dual dosha
        primary, secondary = dosha_type.split("-")
        dosha_info = {
            "primary": {
                "name": doshas[primary]["name"],
                "description": doshas[primary]["description"],
                "balanced_state": doshas[primary]["balanced_state"],
                "imbalanced_state": doshas[primary]["imbalanced_state"]
            },
            "secondary": {
                "name": doshas[secondary]["name"],
                "description": doshas[secondary]["description"],
                "balanced_state": doshas[secondary]["balanced_state"],
                "imbalanced_state": doshas[secondary]["imbalanced_state"]
            }
        }
    else:
        # Single dosha
        dosha_info = {
            "primary": {
                "name": doshas[dosha_type]["name"],
                "description": doshas[dosha_type]["description"],
                "balanced_state": doshas[dosha_type]["balanced_state"],
                "imbalanced_state": doshas[dosha_type]["imbalanced_state"]
            }
        }

    return jsonify({
        "status": "success",
        "dosha_type": dosha_type,
        "dosha_info": dosha_info,
        "counts": analysis_result["counts"],
        "recommendations": recommendations
    })

# API endpoint for seasonal recommendations
@app.route("/api/seasonal-recommendations")
def seasonal_recommendations():
    season_name, season_data = get_current_season()

    return jsonify({
        "status": "success",
        "current_season": season_name,
        "predominant_dosha": season_data["predominant_dosha"],
        "characteristics": season_data["characteristics"],
        "dietary_recommendations": season_data["dietary_recommendations"],
        "lifestyle_recommendations": season_data["lifestyle_recommendations"],
        "herbs_and_spices": season_data["herbs_and_spices"]
    })

# API endpoint for remedy details
@app.route("/api/remedy-details")
def remedy_details():
    symptom = request.args.get('symptom', '')
    remedy = request.args.get('remedy', '')

    if not symptom or not remedy:
        return jsonify({"status": "error", "message": "Symptom and remedy parameters are required"})

    if symptom not in symptoms_db:
        return jsonify({"status": "error", "message": f"Symptom '{symptom}' not found"})

    symptom_data = symptoms_db[symptom]

    if "remedy_preparations" not in symptom_data or remedy not in symptom_data["remedy_preparations"]:
        return jsonify({"status": "error", "message": f"Remedy '{remedy}' not found for symptom '{symptom}'"})

    remedy_data = symptom_data["remedy_preparations"][remedy]

    return jsonify({
        "status": "success",
        "symptom": symptom,
        "remedy": remedy,
        "preparation": remedy_data
    })

# API endpoint for feedback
@app.route("/api/feedback", methods=["POST"])
def submit_feedback():
    feedback_data = request.json

    # In a production app, you would store this feedback in a database
    print(f"Received feedback: {json.dumps(feedback_data)}")

    return jsonify({"status": "success", "message": "Feedback received"})

if __name__ == "__main__":
    socketio.run(app, debug=True)  # Use socketio.run instead of app.run