import os
import json
from openai_client import OpenAIClient
from health_assessment import HealthAssessment
from medication_parser import MedicationRegimen
from health_recommendation import main as hrm
import markdown
from bs4 import BeautifulSoup
from typing import Union

def convert_markdown_to_html(markdown_text: str) -> Union[str, None]:
    """
    Convert markdown text to HTML for Flask application.
    
    Args:
        markdown_text (str): Raw markdown text
        
    Returns:
        str: Formatted HTML string
        
    Raises:
        ValueError: If input is empty or invalid
    """
    try:
        # Validate input
        if not markdown_text:
            raise ValueError("Empty markdown text provided")
            
        # Remove any surrounding quotes and unescape newlines
        text = markdown_text.strip('"\'')
        text = text.replace('\\n', '\n')
        
        # Convert markdown to HTML
        html = markdown.markdown(text, extensions=['extra'])
        
        # Parse and clean HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Add styling
        style = """<style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            h3 {
                color: #2c3e50;
                margin-top: 1.5em;
                margin-bottom: 0.5em;
            }
            ul {
                margin-bottom: 1em;
            }
            li {
                margin-bottom: 0.5em;
            }
            strong {
                color: #e74c3c;
            }
        </style>"""
        
        # Create HTML document
        html_doc = f"<!DOCTYPE html><html><head><meta charset=\"UTF-8\"><title>Meal Plan</title>{style}</head><body>{str(soup)}</body></html>"
        
        return html_doc
        
    except ValueError as e:
        # Handle empty or invalid input
        return None
    except Exception as e:
        # Log the error (you can add proper logging here)
        print(f"Error converting markdown to HTML: {str(e)}")
        return None

json_file = '/Users/nealan/Documents/prototypes/health-hackathon/health_assessment.json'
assessment = HealthAssessment(json_file)

json_file = '/Users/nealan/Documents/prototypes/health-hackathon/medication.json'
medication = MedicationRegimen(json_file)

# Initialize the client
client = OpenAIClient(os.getenv('OPEN_AI_API_KEY'))

# Example 1: Simple prompt with system message
interactions = client.generate_response(
    system_prompt="You are a doctor tasked with identifying any side effects for each individual medication as well as the interaction of them together. ",
    prompt=f"""Below is the medication that will be taken today {medication.get_daily_summary_string()}.
        1. Start by first listing all medication
        2. For each list the side effects. 
        3. Afterwards, list the interactions between each medication.
        Please ensure that you do not make any mistakes.
        """,

)


chat_messages = [
    {
        "role": "user", 
        "content": f"""I am a dietician working with a client who is aiming to get stronger.
                They have provided for you their medication for the day.
                If there is any potential interaction for the medication, please provide a note against the meal so that they can be aware of the risk. "
                Provide a meal plan for today.
                
                Medication:
                {interactions}
                
                Format the meal plan to look like the following:


                MEAL_NAME (TIME):
                - MEAL ITEM 1
                - MEAL ITEM 2
                - MEAL ITEM 3

                - MEDICATION 1
                - MEDICATION 2
                
                """
    }
]

# Update the generate_chat_response method to use max_completion_tokens
o1_client = OpenAIClient(os.getenv('OPEN_AI_API_KEY'))

meal_plan = o1_client.generate_chat_response(chat_messages)

with open('sahha_scores.json', 'r') as file:
    sahha_scores = json.load(file)


def generate_health_recommendation(current_sahha_score):
    
    current_state = hrm(sahha_scores, current_sahha_score)

    refine_meal_plan_prompt = f"""
        Update the meal plan to ensure that it is in line with the client's current state.
        Provide your reasoning as to why you've made those changes as well. 

        Current state:
            {current_state}

        Meal Plan:
            {meal_plan}

        Return ONLY The updated meal plan and reasoning for the changes.
        """
    updated_meal_plan = client.generate_response(
        system_prompt="You are a dietician who has been given a meal plan and a client's current state.",
        prompt=refine_meal_plan_prompt,

    )

    return convert_markdown_to_html(updated_meal_plan)
