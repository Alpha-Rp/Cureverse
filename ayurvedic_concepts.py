"""
Ayurvedic Concepts Module

This module contains Ayurvedic concepts, dosha analysis, and seasonal recommendations
for the CureVerse application.
"""

from datetime import datetime

# Dosha characteristics and descriptions
doshas = {
    "vata": {
        "name": "Vata",
        "elements": ["Air", "Space"],
        "qualities": ["Dry", "Light", "Cold", "Rough", "Subtle", "Mobile", "Clear"],
        "description": "Vata governs all movement in the mind and body. It controls blood flow, elimination of wastes, breathing, and the movement of thoughts across the mind.",
        "physical_characteristics": [
            "Thin, light frame",
            "Dry skin and hair",
            "Cold hands and feet",
            "Irregular hunger and digestion",
            "Light and interrupted sleep",
            "Speaks quickly",
            "Energetic, creative, and quick to learn"
        ],
        "mental_characteristics": [
            "Quick to learn but also quick to forget",
            "Enthusiastic and vivacious",
            "Imaginative and creative",
            "Tendency towards anxiety and worry",
            "Adapts quickly to change"
        ],
        "balanced_state": "When in balance, Vata promotes creativity, flexibility, and joy.",
        "imbalanced_state": "When imbalanced, Vata can lead to anxiety, insomnia, dry skin, constipation, and irregular digestion.",
        "balancing_diet": [
            "Favor warm, cooked, moist foods",
            "Sweet, sour, and salty tastes",
            "Warm drinks and spices",
            "Regular meals at consistent times",
            "Avoid cold, raw foods and bitter tastes"
        ],
        "balancing_lifestyle": [
            "Establish regular routines",
            "Get adequate rest and sleep",
            "Stay warm and avoid cold, windy conditions",
            "Practice gentle, grounding exercises like yoga",
            "Meditation and calming practices",
            "Oil massage (Abhyanga) with sesame oil"
        ],
        "balancing_herbs": ["Ashwagandha", "Ginger", "Cinnamon", "Cumin", "Cardamom", "Licorice"]
    },
    "pitta": {
        "name": "Pitta",
        "elements": ["Fire", "Water"],
        "qualities": ["Hot", "Sharp", "Light", "Liquid", "Spreading", "Oily"],
        "description": "Pitta governs digestion, metabolism, and energy production. It controls how we digest food, how we metabolize sensory perceptions, and how we discriminate between right and wrong.",
        "physical_characteristics": [
            "Medium build with good muscle development",
            "Warm skin, often reddish or flushed",
            "Strong digestion and strong appetite",
            "Sharp hunger at regular times",
            "Moderate and sound sleep",
            "Tendency towards early gray hair or baldness",
            "Precise and articulate speech"
        ],
        "mental_characteristics": [
            "Sharp intellect and good concentration",
            "Good memory and comprehension",
            "Ambitious and driven",
            "Natural leaders with strong opinions",
            "Tendency towards irritability when stressed"
        ],
        "balanced_state": "When in balance, Pitta promotes intelligence, understanding, and courage.",
        "imbalanced_state": "When imbalanced, Pitta can lead to anger, inflammation, skin rashes, acidity, and ulcers.",
        "balancing_diet": [
            "Favor cooling, fresh foods",
            "Sweet, bitter, and astringent tastes",
            "Moderate intake of oils and fats",
            "Cool or room temperature drinks",
            "Avoid spicy, salty, and fermented foods"
        ],
        "balancing_lifestyle": [
            "Avoid excessive heat and sun exposure",
            "Moderate exercise, avoiding overheating",
            "Cooling activities like swimming",
            "Moonlight walks and time in nature",
            "Relaxation and stress management",
            "Oil massage with coconut or sunflower oil"
        ],
        "balancing_herbs": ["Aloe Vera", "Coriander", "Mint", "Fennel", "Rose", "Sandalwood"]
    },
    "kapha": {
        "name": "Kapha",
        "elements": ["Earth", "Water"],
        "qualities": ["Heavy", "Slow", "Cool", "Oily", "Smooth", "Dense", "Soft", "Static", "Cloudy", "Hard", "Gross"],
        "description": "Kapha governs structure, cohesion, and lubrication. It provides the body with physical form, stability, and the smooth functioning of all its parts.",
        "physical_characteristics": [
            "Solid, heavy build with well-developed physique",
            "Smooth, oily skin",
            "Thick hair",
            "Slow digestion but steady appetite",
            "Deep, prolonged sleep",
            "Speaks slowly and melodiously",
            "Strong stamina and endurance"
        ],
        "mental_characteristics": [
            "Calm and thoughtful",
            "Slow to learn but excellent long-term memory",
            "Loyal and steady in relationships",
            "Patient and supportive",
            "Tendency towards complacency or attachment"
        ],
        "balanced_state": "When in balance, Kapha promotes love, calmness, and forgiveness.",
        "imbalanced_state": "When imbalanced, Kapha can lead to weight gain, congestion, lethargy, and excessive sleep.",
        "balancing_diet": [
            "Favor light, dry, warm foods",
            "Pungent, bitter, and astringent tastes",
            "Honey is especially beneficial",
            "Warm drinks with spices",
            "Avoid heavy, oily, cold, and sweet foods"
        ],
        "balancing_lifestyle": [
            "Regular, stimulating exercise",
            "Create variety and stimulation in daily routine",
            "Rise early (before 6 am)",
            "Avoid daytime naps",
            "Dry brushing and invigorating massage",
            "New experiences and mental challenges"
        ],
        "balancing_herbs": ["Ginger", "Black Pepper", "Turmeric", "Cinnamon", "Cardamom", "Clove"]
    }
}

# Dosha questionnaire for self-assessment
dosha_questionnaire = {
    "physical": [
        {
            "question": "Body frame:",
            "options": {
                "a": {"text": "I am thin, lanky, and slender with prominent joints and thin muscles.", "dosha": "vata"},
                "b": {"text": "I have a medium, symmetrical build with good muscle development.", "dosha": "pitta"},
                "c": {"text": "I have a large, sturdy build. My frame is broad with well-developed bodies and muscles.", "dosha": "kapha"}
            }
        },
        {
            "question": "Weight:",
            "options": {
                "a": {"text": "I am underweight and find it difficult to gain weight.", "dosha": "vata"},
                "b": {"text": "I maintain my weight easily, fluctuating little.", "dosha": "pitta"},
                "c": {"text": "I gain weight easily and have difficulty losing it.", "dosha": "kapha"}
            }
        },
        {
            "question": "Skin:",
            "options": {
                "a": {"text": "My skin is dry, thin, or rough.", "dosha": "vata"},
                "b": {"text": "My skin is warm, reddish, and prone to irritation.", "dosha": "pitta"},
                "c": {"text": "My skin is thick, moist, and smooth.", "dosha": "kapha"}
            }
        },
        {
            "question": "Hair:",
            "options": {
                "a": {"text": "My hair is dry, brittle, or frizzy.", "dosha": "vata"},
                "b": {"text": "My hair is fine with a tendency towards early thinning or graying.", "dosha": "pitta"},
                "c": {"text": "My hair is thick, full, wavy, and oily.", "dosha": "kapha"}
            }
        },
        {
            "question": "Appetite:",
            "options": {
                "a": {"text": "Irregular and variable.", "dosha": "vata"},
                "b": {"text": "Strong and predictable.", "dosha": "pitta"},
                "c": {"text": "Moderate but constant, can skip meals easily.", "dosha": "kapha"}
            }
        }
    ],
    "mental": [
        {
            "question": "Under stress, I tend to:",
            "options": {
                "a": {"text": "Feel anxious, worried, or overwhelmed.", "dosha": "vata"},
                "b": {"text": "Become irritable, frustrated, or angry.", "dosha": "pitta"},
                "c": {"text": "Withdraw, become stubborn, or complacent.", "dosha": "kapha"}
            }
        },
        {
            "question": "My mind is usually:",
            "options": {
                "a": {"text": "Active, creative, and sometimes restless.", "dosha": "vata"},
                "b": {"text": "Focused, determined, and ambitious.", "dosha": "pitta"},
                "c": {"text": "Calm, steady, and sometimes slow to engage.", "dosha": "kapha"}
            }
        },
        {
            "question": "When learning something new:",
            "options": {
                "a": {"text": "I learn quickly but may forget quickly too.", "dosha": "vata"},
                "b": {"text": "I learn at a moderate pace and retain information well.", "dosha": "pitta"},
                "c": {"text": "I learn slowly but have excellent long-term memory.", "dosha": "kapha"}
            }
        }
    ]
}

# Seasonal recommendations (Ritucharya)
seasons = {
    "spring": {
        "months": [3, 4, 5],  # March, April, May
        "predominant_dosha": "kapha",
        "characteristics": "Wet, cool, heavy, and oily",
        "dietary_recommendations": [
            "Favor light, dry, and warm foods",
            "Reduce sweet, sour, and salty tastes",
            "Increase pungent, bitter, and astringent tastes",
            "Include barley, honey, and spices like ginger, black pepper, and turmeric",
            "Reduce heavy dairy products and cold foods"
        ],
        "lifestyle_recommendations": [
            "Rise early before 6 am",
            "Engage in regular, vigorous exercise",
            "Dry brushing (Garshana) before bathing",
            "Use warming, stimulating oils like mustard for massage",
            "Practice Neti (nasal cleansing) and Nasya (nasal oil application)"
        ],
        "herbs_and_spices": ["Ginger", "Turmeric", "Black Pepper", "Fenugreek", "Cinnamon"]
    },
    "summer": {
        "months": [6, 7, 8],  # June, July, August
        "predominant_dosha": "pitta",
        "characteristics": "Hot, sharp, and intense",
        "dietary_recommendations": [
            "Favor cooling, light foods",
            "Increase sweet, bitter, and astringent tastes",
            "Reduce pungent, sour, and salty tastes",
            "Include fresh fruits, vegetables, and grains like rice and barley",
            "Drink cooling beverages like coconut water and mint tea"
        ],
        "lifestyle_recommendations": [
            "Exercise during cooler parts of the day (early morning or evening)",
            "Moonlight walks and swimming",
            "Cooling oil massage with coconut or sunflower oil",
            "Wear light, breathable clothing",
            "Practice cooling pranayama like Sheetali (cooling breath)"
        ],
        "herbs_and_spices": ["Coriander", "Fennel", "Mint", "Rose", "Sandalwood"]
    },
    "autumn": {
        "months": [9, 10, 11],  # September, October, November
        "predominant_dosha": "vata",
        "characteristics": "Dry, rough, windy, erratic, cool, subtle, and clear",
        "dietary_recommendations": [
            "Favor warm, moist, and grounding foods",
            "Increase sweet, sour, and salty tastes",
            "Reduce pungent, bitter, and astringent tastes",
            "Include root vegetables, grains, and healthy oils",
            "Drink warm beverages and soups"
        ],
        "lifestyle_recommendations": [
            "Establish regular daily routines",
            "Oil massage (Abhyanga) with sesame oil",
            "Gentle, grounding exercise like yoga",
            "Keep warm and avoid cold, windy conditions",
            "Practice meditation and calming pranayama"
        ],
        "herbs_and_spices": ["Ashwagandha", "Ginger", "Cinnamon", "Cardamom", "Cumin"]
    },
    "winter": {
        "months": [12, 1, 2],  # December, January, February
        "predominant_dosha": "vata-kapha",
        "characteristics": "Cold, heavy, dull, and cloudy",
        "dietary_recommendations": [
            "Favor warm, nourishing foods",
            "Moderate use of healthy fats and oils",
            "Include warming spices in cooking",
            "Enjoy warm soups and stews",
            "Drink warm water throughout the day"
        ],
        "lifestyle_recommendations": [
            "Regular, moderate exercise",
            "Warming oil massage",
            "Keep warm and avoid cold exposure",
            "Practice sun salutations and warming pranayama",
            "Early to bed, slightly later to rise"
        ],
        "herbs_and_spices": ["Ginger", "Cinnamon", "Clove", "Black Pepper", "Cardamom"]
    }
}

def get_current_season():
    """Determine the current season based on the month."""
    current_month = datetime.now().month
    
    for season_name, season_data in seasons.items():
        if current_month in season_data["months"]:
            return season_name, season_data
    
    # Default to spring if something goes wrong
    return "spring", seasons["spring"]

def analyze_dosha_responses(responses):
    """
    Analyze dosha questionnaire responses and determine predominant dosha.
    
    Args:
        responses: Dictionary with question indices as keys and selected option letters as values
                  e.g., {"physical_0": "a", "physical_1": "b", ...}
    
    Returns:
        Dictionary with dosha counts and predominant dosha
    """
    dosha_counts = {"vata": 0, "pitta": 0, "kapha": 0}
    
    for question_key, answer in responses.items():
        category, index = question_key.split('_')
        index = int(index)
        
        if category in dosha_questionnaire and index < len(dosha_questionnaire[category]):
            question = dosha_questionnaire[category][index]
            if answer in question["options"]:
                dosha = question["options"][answer]["dosha"]
                dosha_counts[dosha] += 1
    
    # Determine predominant dosha
    predominant_dosha = max(dosha_counts, key=dosha_counts.get)
    
    # Check for dual dosha (if two doshas are tied or close)
    sorted_doshas = sorted(dosha_counts.items(), key=lambda x: x[1], reverse=True)
    if sorted_doshas[0][1] == sorted_doshas[1][1]:
        # Exact tie between top two
        predominant_dosha = f"{sorted_doshas[0][0]}-{sorted_doshas[1][0]}"
    elif sorted_doshas[0][1] - sorted_doshas[1][1] <= 2 and sorted_doshas[1][1] > 0:
        # Close scores (within 2 points) and second dosha has some points
        predominant_dosha = f"{sorted_doshas[0][0]}-{sorted_doshas[1][0]}"
    
    return {
        "counts": dosha_counts,
        "predominant_dosha": predominant_dosha
    }

def get_dosha_recommendations(dosha_type):
    """
    Get recommendations for balancing a specific dosha.
    
    Args:
        dosha_type: String representing dosha type (vata, pitta, kapha) or dual dosha (vata-pitta, etc.)
    
    Returns:
        Dictionary with recommendations
    """
    if "-" in dosha_type:
        # Handle dual dosha types
        primary, secondary = dosha_type.split("-")
        recommendations = {
            "diet": doshas[primary]["balancing_diet"][:3] + doshas[secondary]["balancing_diet"][:2],
            "lifestyle": doshas[primary]["balancing_lifestyle"][:3] + doshas[secondary]["balancing_lifestyle"][:2],
            "herbs": list(set(doshas[primary]["balancing_herbs"][:3] + doshas[secondary]["balancing_herbs"][:3]))
        }
    else:
        # Single dosha type
        recommendations = {
            "diet": doshas[dosha_type]["balancing_diet"],
            "lifestyle": doshas[dosha_type]["balancing_lifestyle"],
            "herbs": doshas[dosha_type]["balancing_herbs"]
        }
    
    return recommendations
