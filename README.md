# CureVerse - AI Health Assistant

CureVerse is an advanced AI-powered health assistant that provides information about symptoms, medical conditions, and Ayurvedic remedies. It combines modern AI technology with traditional Ayurvedic knowledge to offer a comprehensive health information platform.

![CureVerse Logo](static/img/logo.svg)

## Features

- **AI-Powered Health Assistant**: Get intelligent responses to your health queries using Google's Gemini AI
- **Symptom Analysis**: Describe your symptoms and get information about possible conditions
- **Ayurvedic Remedies**: Access traditional Ayurvedic remedies for common health issues
- **Diet Recommendations**: Receive dietary advice tailored to specific health conditions
- **Modern UI**: Enjoy a clean, responsive interface that works on all devices
- **Real-time Chat**: Interact with the AI assistant in a natural, conversational way

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Internet connection (for API access)

### Installation

1. Clone this repository or download the source code
2. Run the setup script:

```
setup_and_run.bat
```

This script will:
- Create a virtual environment
- Install all required dependencies
- Start the application

Alternatively, you can manually set up the environment:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

3. Open your browser and navigate to: http://127.0.0.1:5000

## Usage

1. Type your health question or describe your symptoms in the chat input
2. Click the send button or press Enter to submit your query
3. The AI will analyze your input and provide relevant information
4. For symptom-related queries, you'll receive:
   - Possible conditions
   - When to consult a doctor
   - Ayurvedic remedies
   - Diet recommendations

## Technology Stack

- **Backend**: Flask, Flask-SocketIO, Python
- **Frontend**: HTML5, CSS3, JavaScript
- **AI**: Google Gemini API
- **Database**: In-memory symptom database with Ayurvedic knowledge

## Project Structure

```
CureVerse/
├── app.py                 # Main application file
├── medical_data.py        # Symptom database
├── requirements.txt       # Python dependencies
├── setup_and_run.bat      # Setup script
├── static/                # Static assets
│   ├── css/               # CSS stylesheets
│   ├── img/               # Images and icons
│   └── js/                # JavaScript files
└── templates/             # HTML templates
    └── modern_index.html  # Main application template
```

## Customization

### Adding New Symptoms

To add new symptoms to the database, edit the `medical_data.py` file and add new entries to the `symptoms_db` dictionary following the existing format.

### Changing the API Key

To use your own Gemini API key, modify the `GEMINI_API_KEY` variable in `app.py`.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini API for powering the AI responses
- Ayurvedic medical texts for traditional health knowledge
- Flask and SocketIO for the web framework
- The open-source community for various libraries and tools

## Disclaimer

This application is for informational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.
