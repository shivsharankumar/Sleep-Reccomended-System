# Sleep Coach Streamlit App

This project provides a modern, mobile-friendly sleep analysis and coaching app using Streamlit. It supports both rule-based and LLM (Groq) powered recommendations and generates beautiful, shareable HTML reports.

## Features
- Paste your 7-day sleep data in natural language format
- Get instant sleep analysis, diagnosis, and recommendations
- Optionally use Groq LLM for advanced, AI-powered insights
- Mobile-optimized, visually attractive HTML reports
- Download and share your sleep report

## Requirements
- Python 3.8+
- `streamlit`
- `groq` (for LLM mode)
- `python-dotenv` (for environment variables)

## Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Set up your Groq API key and model in a `.env` file:
   ```env
   GROQ_API_KEY=your_groq_api_key
   GROQ_MODEL=your_groq_model_name
   ```

## Running the App
```bash
streamlit run sleep_coach_app.py
```
- Paste your sleep data in the text area.
- Choose LLM mode for AI-powered recommendations (optional).
- Click "Analyze Sleep Data" to view your report.
- Download or share your report as needed.

## Customization
- You can adjust the UI, add more analysis rules, or change the LLM prompt in the code.
- The app is designed for easy extension and integration.

## File Structure
- `sleep_coach_app.py` - Main Streamlit app (now mobile-friendly and LLM-ready)
- `llm_sleep_recommend.py` - LLM integration for Groq
- `requirements.txt` - Python dependencies
- `.env` - (Optional) Your API keys and model names

## License
MIT 