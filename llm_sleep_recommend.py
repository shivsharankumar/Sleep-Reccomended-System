import os
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv
from groq import Groq, GroqError

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Groq client with error handling
try:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
    groq_client = Groq(api_key=api_key)
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    groq_client = None

def get_groq_model() -> str:
    """Retrieve the Groq model from environment variables with a default fallback."""
    return os.environ.get("GROQ_MODEL", "mixtral-8x7b-32768")

def format_sleep_data_for_prompt(sleep_data: List[Dict]) -> str:
    """
    Format the list of sleep data dictionaries into a readable string for the LLM.
    
    Args:
        sleep_data: List of dictionaries containing date, sleep time, wake time, and duration.
        
    Returns:
        Formatted string representation of the sleep data.
    """
    lines = []
    for d in sleep_data:
        try:
            line = f"{d.get('date', 'Unknown')}: Slept at {d.get('sleep', '?')}, woke at {d.get('wake', '?')} ({d.get('duration', 0)} hours)"
            lines.append(line)
        except Exception as e:
            logger.warning(f"Skipping malformed data entry: {d} - {e}")
            continue
    return "\n".join(lines)

def generate_sleep_recommendation_llm(sleep_data: List[Dict]) -> str:
    """
    Generate a sleep recommendation using the LLM based on provided sleep data.
    
    Args:
        sleep_data: List of sleep data entries.
        
    Returns:
        String containing the LLM's recommendation or an error message.
    """
    if not groq_client:
        return "Error: LLM client is not initialized. Please check API configuration."

    if not sleep_data:
        return "No sleep data provided for analysis."

    data_str = format_sleep_data_for_prompt(sleep_data)
    
    prompt = f"""
You are a sleep coach AI. Write a message (100–120 words). Analyze the following 7 days of sleep data and:
- First, determine if the sleep is good or not (based on average duration, consistency, and healthy sleep guidelines).
- If sleep is good, generate a positive, encouraging message.
- If sleep is not good, diagnose possible issues (such as insomnia, sleep apnea, hypersomnia, or irregular sleep) and provide recommendations for improvement.
- Be concise, clear, and supportive. Use paragraphs and bullet points where appropriate.

SLEEP DATA:
{data_str}

Your response:
"""

    try:
        model = get_groq_model()
        completion = groq_client.chat.completions.create(
            model=model,
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            temperature=0.7,
            max_tokens=300
        )
        return completion.choices[0].message.content
    except GroqError as ge:
        logger.error(f"Groq API error: {ge}")
        return "I'm having trouble connecting to the sleep coach AI right now. Please try again later."
    except Exception as e:
        logger.error(f"Unexpected error during LLM generation: {e}")
        return "An unexpected error occurred while generating recommendations."

if __name__ == "__main__":
    # Test data for standalone execution
    test_data = [
        {"date": "Jul 09", "sleep": "8:14 PM", "wake": "7:12 AM", "duration": 10.9},
        {"date": "Jul 08", "sleep": "12:18 AM", "wake": "7:45 AM", "duration": 7.4},
        {"date": "Jul 07", "sleep": "11:54 PM", "wake": "5:31 AM", "duration": 5.6},
        {"date": "Jul 06", "sleep": "1:00 AM", "wake": "6:49 AM", "duration": 5.8},
        {"date": "Jul 05", "sleep": "1:01 AM", "wake": "9:58 AM", "duration": 8.9},
        {"date": "Jul 04", "sleep": "10:28 PM", "wake": "6:46 AM", "duration": 8.3},
        {"date": "Jul 03", "sleep": "12:14 AM", "wake": "7:55 AM", "duration": 7.7},
    ]
    print(generate_sleep_recommendation_llm(test_data))