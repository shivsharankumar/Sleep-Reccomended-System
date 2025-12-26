import datetime
import re
import logging
from typing import List, Dict, Tuple, Optional

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Import the LLM-based recommendation function
from llm_sleep_recommend import generate_sleep_recommendation_llm

# --- Configuration & Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Sleep Coach Check-in",
    page_icon="😴",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS Styling ---
def inject_custom_css():
    """Injects custom CSS to style the Streamlit app and mobile report."""
    st.markdown("""
    <style>
        .big-font { font-size: 1.3em; }
        .result-box { background: #f6f6fa; border-radius: 10px; padding: 1.5em; margin-top: 1em; }
        .stButton>button {
            width: 100%;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: #fff;
            border: none;
            border-radius: 12px;
            padding: 0.8rem;
            font-weight: 600;
            font-size: 1rem;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
            color: #fff;
        }
        .main .block-container { padding: 2rem; max-width: 800px; }
        .stSpinner > div { border-top-color: #667eea !important; }
        .success-box { border-radius: 8px; padding: 1rem; background-color: #d1fae5; color: #065f46; border: 1px solid #10b981; }
        .warning-box { border-radius: 8px; padding: 1rem; background-color: #fef3c7; color: #92400e; border: 1px solid #f59e0b; }
        .error-box { border-radius: 8px; padding: 1rem; background-color: #fee2e2; color: #b91c1c; border: 1px solid #ef4444; }
    </style>
    """, unsafe_allow_html=True)

# --- Data Parsing & Logic ---
def parse_csv_data(file) -> List[Dict]:
    """
    Parses an uploaded CSV file into a list of sleep data dictionaries.
    
    Expected CSV columns (case-insensitive):
    - Date
    - Sleep (Time)
    - Wake (Time)
    - Duration (Float)
    """
    try:
        df = pd.read_csv(file)
        df.columns = df.columns.str.lower().str.strip()
        
        required_cols = ['date', 'sleep', 'wake', 'duration']
        # Check if basic columns exist
        if not all(col in df.columns for col in required_cols):
             # Try to be flexible if exact names don't match but order or similar names might
             # For now, strict check is safer for production
             missing = [c for c in required_cols if c not in df.columns]
             logger.error(f"Missing columns in CSV: {missing}")
             st.error(f"CSV is missing required columns: {', '.join(missing)}")
             return []

        data = []
        for _, row in df.iterrows():
            try:
                entry = {
                    "date": str(row['date']).strip(),
                    "sleep": str(row['sleep']).strip(),
                    "wake": str(row['wake']).strip(),
                    "duration": float(row['duration'])
                }
                data.append(entry)
            except ValueError as ve:
                logger.warning(f"Skipping invalid row: {row} - {ve}")
                continue
        
        if not data:
            st.warning("No valid data rows found in CSV.")
            
        return data
    except Exception as e:
        logger.error(f"Error parsing CSV: {e}")
        st.error(f"Error parsing CSV file: {e}")
        return []

def analyze_sleep_stats(data: List[Dict]) -> Tuple[float, float, float, List[str], List[str]]:
    """Calculates basic sleep statistics and generates rule-based advice."""
    if not data:
        return 0, 0, 0, [], []

    durations = [d["duration"] for d in data]
    avg_sleep = sum(durations) / len(durations) if durations else 0
    min_sleep = min(durations) if durations else 0
    max_sleep = max(durations) if durations else 0
    below_7 = sum(1 for d in durations if d < 7)
    
    diagnosis = []
    recommendations = []
    
    # Average duration analysis
    if avg_sleep < 7:
        diagnosis.append("You are not getting enough average sleep. Chronic sleep deprivation can impact health.")
        recommendations.append("Aim for at least 7-9 hours of sleep per night.")
    elif avg_sleep > 9:
        diagnosis.append("You are sleeping more than the recommended amount. Excessive sleep can also be a sign of underlying issues.")
        recommendations.append("Try to keep your sleep within the 7-9 hour range.")
    else:
        diagnosis.append("Your average sleep duration is within the healthy range.")
        
    # Consistency analysis
    if below_7 > 2:
        diagnosis.append(f"You had {below_7} nights with less than 7 hours of sleep.")
        recommendations.append("Try to maintain a more consistent sleep schedule.")
        
    return avg_sleep, min_sleep, max_sleep, diagnosis, recommendations

def evaluate_sleep_disorder_risks(data: List[Dict]) -> List[str]:
    """Evaluates potential sleep disorder risks based on data patterns."""
    if not data:
        return []

    durations = [d["duration"] for d in data]
    sleep_times = []
    wake_times = []
    
    for d in data:
        try:
            # Flexible time parsing could be added here if formats vary
            # Assuming standard "8:14 PM" format for now as per legacy input example
            # In a real app, dateutil.parser is more robust
            sleep_dt = datetime.datetime.strptime(d["sleep"], "%I:%M %p")
            wake_dt = datetime.datetime.strptime(d["wake"], "%I:%M %p")
            sleep_times.append(sleep_dt)
            wake_times.append(wake_dt)
        except Exception:
            # If time format is custom or fails, just skip time-based logic for that row
            continue

    assessment = []
    
    # Risk Detections
    insomnia_nights = sum(1 for dur in durations if dur < 6)
    # Simple check for very late sleep (after midnight often implies AM label but 'late' context)
    # This logic assumes "PM" is evening and 12+ PM isn't a thing (12 PM is noon).
    # "12:xx AM" is late night. "1:xx AM" is late.
    # Without full datetime objects with dates, this logic is heuristic
    late_sleeps = 0
    for d in data:
        s = d.get('sleep', '')
        if 'AM' in s:
            # Heuristic: 12 AM to 4 AM is 'late'
            try:
                hour = int(s.split(':')[0])
                if hour == 12 or 1 <= hour <= 4:
                    late_sleeps += 1
            except:
                pass

    if insomnia_nights >= 3 or late_sleeps >= 3:
        assessment.append("<b>Insomnia risk:</b> Detected multiple nights with short sleep or late sleep onset. Consider improving sleep hygiene.")
    
    apnea_nights = sum(1 for dur in durations if dur > 9)
    if apnea_nights >= 2:
        assessment.append("<b>Hypersomnia/Apnea risk:</b> Several nights with very long sleep duration. If you feel tired during daytime, consider screening.")
        
    if sleep_times and wake_times:
        # Calculate variability roughly by converting to fractional hours
        sleep_hours = [dt.hour + dt.minute/60.0 for dt in sleep_times]
        wake_hours = [dt.hour + dt.minute/60.0 for dt in wake_times]
        
        # Handle wraparound for sleep times (e.g., 10 PM vs 2 AM) requires more complex logic
        # For simple robustness, we'll check wake time consistency which is usually AM
        if len(wake_hours) > 1 and (max(wake_hours) - min(wake_hours) > 2):
            assessment.append("<b>Irregular Wake Patterns:</b> Your wake times vary by more than 2 hours. Consistency helps circadian rhythm.")

    if not assessment:
        assessment.append("No major sleep disorder risks detected based on heuristic analysis. Continue healthy habits!")
        
    return assessment

def generate_mobile_html_report(data, avg, min_s, max_s, diagnosis, recommendations, llm_assessment) -> str:
    """Generates a standalone HTML report string optimized for mobile view."""
    
    entries_html = ""
    for entry in data:
        entries_html += f'''
            <div class="entry">
                <div class="entry-header">
                    <span class="entry-date">📅 {entry.get("date", "N/A")}</span>
                    <span class="entry-duration">{entry.get("duration", 0)}h</span>
                </div>
                <div class="entry-times">
                    <span>🌙 {entry.get("sleep", "?")}</span>
                    <span>☀️ {entry.get("wake", "?")}</span>
                </div>
            </div>
        '''

    def make_section(title, icon, items, css_class):
        if not items:
            return ""
        items_html = ''.join(f'<div class="item {css_class}">{item}</div>' for item in items)
        return f'''
        <div class="section">
            <div class="section-header">
                <div class="section-icon {css_class}-icon">{icon}</div>
                <div class="section-title">{title}</div>
            </div>
            {items_html}
        </div>
        '''

    diagnosis_section = make_section("Analysis", "🔍", diagnosis, "diagnosis")
    rec_section = make_section("Tips", "💡", recommendations, "recommendation")
    ai_section = make_section("AI Insights", "🤖", llm_assessment, "assessment")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sleep Coach Report</title>
    <style>
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;color:#fff;padding:1rem}}
        .app{{max-width:480px;margin:0 auto;padding-bottom:2rem}}
        .header{{background:rgba(255,255,255,0.1);backdrop-filter:blur(10px);border-radius:20px;padding:1rem;margin-bottom:1rem;display:flex;justify-content:space-between;align-items:center}}
        .title{{font-size:1.2rem;font-weight:700}}
        .badge{{background:rgba(16,185,129,0.2);color:#10b981;padding:0.3rem 0.8rem;border-radius:15px;font-size:0.7rem;font-weight:600;border:1px solid rgba(16,185,129,0.3)}}
        .stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:0.5rem;margin-bottom:1rem}}
        .stat{{background:rgba(255,255,255,0.15);backdrop-filter:blur(5px);border-radius:15px;padding:1rem;text-align:center;border:1px solid rgba(255,255,255,0.2)}}
        .stat-value{{font-size:1.4rem;font-weight:800;display:block}}
        .stat-label{{font-size:0.7rem;opacity:0.8;margin-top:0.2rem;text-transform:uppercase;letter-spacing:0.5px}}
        .entries{{margin-bottom:1.5rem}}
        .entry{{background:rgba(255,255,255,0.1);backdrop-filter:blur(5px);border-radius:15px;padding:1rem;margin-bottom:0.5rem;border:1px solid rgba(255,255,255,0.15)}}
        .entry-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem}}
        .entry-date{{font-weight:600;font-size:0.95rem}}
        .entry-duration{{background:rgba(16,185,129,0.2);color:#10b981;padding:0.2rem 0.6rem;border-radius:10px;font-size:0.8rem;font-weight:600}}
        .entry-times{{display:flex;justify-content:space-between;font-size:0.85rem;opacity:0.9}}
        
        .section{{background:rgba(255,255,255,0.95);backdrop-filter:blur(10px);border-radius:15px;padding:1.2rem;margin-bottom:1rem;color:#1a1a2e;box-shadow:0 4px 6px rgba(0,0,0,0.05)}}
        .section-header{{display:flex;align-items:center;gap:0.7rem;margin-bottom:1rem;padding-bottom:0.8rem;border-bottom:1px solid #e5e7eb}}
        .section-icon{{width:32px;height:32px;border-radius:10px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:1rem;}}
        .diagnosis-icon{{background:linear-gradient(135deg,#f59e0b,#d97706)}}
        .recommendation-icon{{background:linear-gradient(135deg,#10b981,#059669)}}
        .assessment-icon{{background:linear-gradient(135deg,#8b5cf6,#7c3aed)}}
        .section-title{{font-size:1.1rem;font-weight:700;color:#1a1a2e}}
        
        .item{{background:#f8fafc;border-radius:10px;padding:0.9rem;margin-bottom:0.6rem;border-left:4px solid;font-size:0.9rem;line-height:1.5;color:#374151}}
        .diagnosis{{border-left-color:#f59e0b;background:#fffbeb}}
        .recommendation{{border-left-color:#10b981;background:#ecfdf5}}
        .assessment{{border-left-color:#8b5cf6;background:#f5f3ff}}
        
        .footer{{background:rgba(255,255,255,0.1);backdrop-filter:blur(10px);border-radius:15px;padding:1.5rem;text-align:center;margin-top:2rem}}
        .footer-text{{font-size:0.9rem;margin-bottom:1rem;opacity:0.9}}
        .btn{{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;border-radius:12px;padding:1rem 2rem;font-weight:600;width:100%;font-size:1rem;cursor:pointer;box-shadow:0 4px 15px rgba(0,0,0,0.2)}}
    </style>
</head>
<body>
    <div class="app">
        <div class="header">
            <div class="title">🌙 Sleep Coach Report</div>
            <div class="badge">Generated</div>
        </div>
        
        <div class="stats">
            <div class="stat">
                <span class="stat-value">{avg:.1f}h</span>
                <span class="stat-label">Avg Sleep</span>
            </div>
            <div class="stat">
                <span class="stat-value">{min_s:.1f}h</span>
                <span class="stat-label">Min</span>
            </div>
            <div class="stat">
                <span class="stat-value">{max_s:.1f}h</span>
                <span class="stat-label">Max</span>
            </div>
        </div>
        
        <h3 style="margin:1.5rem 0 1rem 0;font-size:1.1rem;opacity:0.9">Recent Sleep Log</h3>
        <div class="entries">
            {entries_html}
        </div>
        
        {diagnosis_section}
        {rec_section}
        {ai_section}
        
        <div class="footer">
            <div class="footer-text">✨ Consistency is key to better rest!</div>
        </div>
    </div>
</body>
</html>"""


# --- Main Application Logic ---
def main():
    inject_custom_css()
    
    st.title("😴 Sleep Coach Check-in")
    st.markdown("""
        <div style='background:rgba(255,255,255,0.7); padding:1rem; border-radius:10px; margin-bottom:2rem; border-left: 5px solid #667eea;'>
            Upload your sleep diary (CSV) to get an instant analysis and AI-powered recommendations.
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("1. Upload Data")
        uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'], help="Required columns: Date, Sleep, Wake, Duration")
        use_example = st.checkbox("Use example data")
        
        file_to_process = None
        
        if use_example:
            file_to_process = "test_sleep_data.csv"
            st.markdown(f"<div class='success-box'>✅ Using example file 'test_sleep_data.csv'.</div>", unsafe_allow_html=True)
        elif uploaded_file:
            file_to_process = uploaded_file
            st.markdown(f"<div class='success-box'>✅ File '{uploaded_file.name}' ready for analysis.</div>", unsafe_allow_html=True)
            
        if file_to_process:
            if st.button("🚀 Analyze Sleep Data", type="primary"):
                with st.spinner("Analyzing sleep patterns..."):
                    data = parse_csv_data(file_to_process)
                    
                    if not data:
                        st.error("Could not parse data.")
                        return # Error handled in parsing
                        
                    # 1. AI Analysis
                    try:
                        llm_result = generate_sleep_recommendation_llm(data)
                        
                        st.markdown("### 🧠 AI Sleep Coach")
                        st.markdown(f"""
                        <div style='background:linear-gradient(135deg,#667eea,#764ba2);padding:3px;border-radius:16px;margin:1rem 0;box-shadow:0 10px 25px rgba(102,126,234,0.2)'>
                            <div style='background:#fff;border-radius:14px;padding:2rem;color:#1a1a2e'>
                                <h3 style='display:flex;align-items:center;gap:0.5rem;margin-top:0;color:#1a1a2e;font-size:1.4rem'>
                                    <span>💭</span> Coach's Insights
                                </h3>
                                <div style='line-height:1.7;color:#374151;font-size:1.05rem'>
                                    {llm_result}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    except Exception as e:
                        logger.error(f"AI Module Error: {e}")
                        st.error("AI service is currently unavailable. Showing standard stats.")
                        llm_result = "AI Analysis Unavailable"

                    # 2. Statistical Analysis
                    avg, min_s, max_s, diagnosis, recommendations = analyze_sleep_stats(data)
                    heuristic_assessment = evaluate_sleep_disorder_risks(data)
                    
                    # 3. Generate Report
                    html_report = generate_mobile_html_report(
                        data, avg, min_s, max_s, 
                        diagnosis, recommendations, 
                        [llm_result] if "AI Analysis Unavailable" in llm_result else [] # Don't duplicate if AI worked
                    )
                    

                    
                    # Download Button
                    st.download_button(
                        label="📥 Download HTML Report",
                        data=html_report,
                        file_name=f"sleep_report_{datetime.datetime.now().strftime('%Y%m%d')}.html",
                        mime="text/html"
                    )
        else:
            st.info("👆 Please upload a CSV file or select example data to get started.")

    with col2:
        st.subheader("  ℹ️ Format Guide")
        st.markdown("""
        **CSV columns needed:**
        - `Date` (e.g., Jul 09)
        - `Sleep` (e.g., 10:00 PM)
        - `Wake` (e.g., 7:00 AM)
        - `Duration` (e.g., 9.0)
        """)
        st.caption("A sample file is available in the repo.")

if __name__ == "__main__":
    main()
