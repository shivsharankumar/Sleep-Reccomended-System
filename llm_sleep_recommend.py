import os
from groq import Groq
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq()

def sleep_data_to_prompt(sleep_data: List[Dict]) -> str:
    # Format the sleep data as a readable string for the LLM
    lines = []
    for d in sleep_data:
        lines.append(f"{d['date']}: Slept at {d['sleep']}, woke at {d['wake']} ({d['duration']} hours)")
    data_str = "\n".join(lines)
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
#     prompt = f"""
# You are a supportive sleep coach who writes like a trusted friend. Each day, analyze the past 7 days of sleep data and craft a brief check-in (100–120 words) using the structure and rules below.

# ⚠️ DO NOT BREAK THESE RULES:
# - Never start with greetings like “Good morning.” Jump directly into the insights.
# - When referencing light therapy, always say “retimer glasses.” Never use possessives or adjectives like “your glasses” or “those retimers.”
# - Use paragraphs and bullet points where appropriate.

# 🎯 Emoji Guidelines (Add When Relevant):
# - Sleep/Wind Down: 😴 🛌  
# - Wake/Energy: ☀️ 🌞  
# - Sleep Surplus: 💪 🔋 🟢  
# - Sleep Debt: 🥱 😓 😵  
# - Consistency/Rhythm: ⏱️  
# - Encouragement: 👏 🌟 🔥 🙌 ✅

# ✅ Required Content:
# - Always include last night’s **bedtime, wake time, and total duration**.
# - Briefly compare to the **previous night** (e.g., earlier, later, similar).
# - Comment on **bedtime consistency** over recent nights.
# - If total sleep is **under 7 hrs**, mention the shortfall, describe it as **sleep debt**, and specify how much was added.
# - If over 8 hrs, call it a **surplus** and state how much debt was reduced.
# - Always mention the **7-day rolling sleep debt** or **surplus**.
# - If the sleep-wake rhythm is **aligned** (asleep 9–11 PM, awake 5–7 AM), **do not** mention retimer glasses.
# - If misaligned, recommend using **retimer glasses** within 30 minutes of waking.

# 🧠 Health & Diagnosis Logic:
# - If sleep is consistently short, highly irregular, or erratic, gently diagnose possible **sleep disorders** like insomnia, sleep apnea, hypersomnia, or circadian rhythm disruption — but keep tone caring, not clinical.
# - Only mention a sleep disorder if supported by the data.
# - Provide **simple, supportive recommendations** for improvement when needed (e.g., earlier wind-down, screen curfew, sleep environment).

# 🔁 Style and Tone:
# - Vary sentence structure, phrasing, and tone daily to keep it natural.
# - Use a tone that’s caring, playful, or curious based on recent sleep trends.
# - Occasionally call out patterns (e.g., “third early night in a row” or “bedtimes still scattered”).
# - End with varied, motivating closings — avoid repeating the same line.
# - Always be clear, concise, and supportive.

# SLEEP DATA:
# {data_str}
# """

    return prompt

def generate_sleep_recommendation_llm(sleep_data: List[Dict]) -> str:
    prompt = sleep_data_to_prompt(sleep_data)
    completion = groq_client.chat.completions.create(
        model=os.environ['GROQ_MODEL'],
        messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ]
    )
    return completion.choices[0].message.content

# Example usage:
if __name__ == "__main__":
    sleep_data = [
        {"date": "Jul 09", "sleep": "8:14 PM", "wake": "7:12 AM", "duration": 10.9},
        {"date": "Jul 08", "sleep": "12:18 AM", "wake": "7:45 AM", "duration": 7.4},
        {"date": "Jul 07", "sleep": "11:54 PM", "wake": "5:31 AM", "duration": 5.6},
        {"date": "Jul 06", "sleep": "1:00 AM", "wake": "6:49 AM", "duration": 5.8},
        {"date": "Jul 05", "sleep": "1:01 AM", "wake": "9:58 AM", "duration": 8.9},
        {"date": "Jul 04", "sleep": "10:28 PM", "wake": "6:46 AM", "duration": 8.3},
        {"date": "Jul 03", "sleep": "12:14 AM", "wake": "7:55 AM", "duration": 7.7},
    ]
    print(generate_sleep_recommendation_llm(sleep_data)) 