# 😴 Sleep Coach App

A modern, production-ready sleep analysis tool that generates personalized coaching recommendations. The app allows users to upload their sleep log (CSV), analyzes the data for healthy patterns and risks, and provides AI-powered insights using Groq.

## ✨ Features

- **CSV Data Upload**: Easily upload your sleep diary for instant analysis.
- **AI Coach**: Integrated with Groq LLM (e.g., Mixtral 8x7b) to generate empathetic, personalized feedback.
- **Sleep Metrics**: Automatically calculates average sleep, debt/surplus, and consistency stats.
- **Risk Assessment**: Heuristic detection of potential issues like insomnia or irregular sleep patterns.
- **Mobile-Friendly Reports**: Generates downloadable, beautifully styled HTML reports.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- A Groq API Key (optional, for AI features)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/shivsharankumar/Sleep-Reccomended-System.git
   cd Sleep-Reccomended-System
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=mixtral-8x7b-32768
   ```

### Running the App

Run the Streamlit application:
```bash
streamlit run main.py
```

## 📊 Data Format

The app accepts a CSV file with the following columns (case-insensitive):

| Column | Description | Example |
| :--- | :--- | :--- |
| `Date` | Date of the entry | `Jul 09` |
| `Sleep` | Bedtime | `10:30 PM` |
| `Wake` | Wake up time | `7:00 AM` |
| `Duration` | Total hours slept | `8.5` |

**Sample CSV:**
```csv
Date,Sleep,Wake,Duration
Jul 09,10:30 PM,7:00 AM,8.5
Jul 10,11:00 PM,6:30 AM,7.5
```

## 📂 Project Structure

- `main.py`: Core application logic and UI.
- `llm_sleep_recommend.py`: Module for Groq LLM integration and error handling.
- `requirements.txt`: Project dependencies.
- `test_sleep_data.csv`: Sample data file for testing.

## 📄 License

MIT