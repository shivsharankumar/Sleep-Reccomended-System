import streamlit as st
import re
import datetime
from typing import List, Dict
import streamlit.components.v1 as components  # <-- Add this import
# Import the LLM-based recommendation function
from llm_sleep_recommend import generate_sleep_recommendation_llm

st.set_page_config(page_title="Sleep Coach Check-in", page_icon="😴", layout="centered")
st.title("😴 Sleep Coach Check-in")
st.markdown("""
<style>
.big-font { font-size: 1.3em; }
.result-box { background: #f6f6fa; border-radius: 10px; padding: 1.5em; margin-top: 1em; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
Enter your sleep data below (copy-paste from your tracker or use the example):
""")

example = (
    "Here is my sleep data from the past 7 days: "
    "Jul 09: Slept at 8:14 PM, woke at 7:12 AM (10.9 hours) "
    "Jul 08: Slept at 12:18 AM, woke at 7:45 AM (7.4 hours) "
    "Jul 07: Slept at 11:54 PM, woke at 5:31 AM (5.6 hours) "
    "Jul 06: Slept at 1:00 AM, woke at 6:49 AM (5.8 hours) "
    "Jul 05: Slept at 1:01 AM, woke at 9:58 AM (8.9 hours) "
    "Jul 04: Slept at 10:28 PM, woke at 6:46 AM (8.3 hours) "
    "Last night: Slept at 12:14 AM, woke at 7:55 AM (7.7 hours) "
    "Please return the sleep coach check-in formatted as clean HTML (with paragraphs, bold durations, and one italic closing line)."
)

user_input = st.text_area("Paste your sleep data here:", value=example, height=180)

# llm_mode = st.checkbox("Use LLM-based recommendation (Groq)")

# --- Parsing logic ---
def parse_sleep_data(text: str) -> List[Dict]:
    # Regex to match: Jul 09: Slept at 8:14 PM, woke at 7:12 AM (10.9 hours)
    pattern = r"(Jul|Jun|May|Apr|Mar|Feb|Jan|Aug|Sep|Oct|Nov|Dec|Last night)[^:]*: Slept at ([0-9: ]+[APM]+), woke at ([0-9: ]+[APM]+) \(([0-9.]+) hours\)"
    matches = re.findall(pattern, text)
    data = []
    for m in matches:
        date = m[0]
        if date == "Last night":
            # Try to infer the date as yesterday
            dt = datetime.datetime.now() - datetime.timedelta(days=1)
            date = dt.strftime("%b %d")
        else:
            date = m[0]  # e.g. Jul 09
        data.append({
            "date": date,
            "sleep": m[1].strip(),
            "wake": m[2].strip(),
            "duration": float(m[3])
        })
    return data

def analyze_sleep(data):
    durations = [d["duration"] for d in data]
    avg_sleep = sum(durations) / len(durations) if durations else 0
    min_sleep = min(durations) if durations else 0
    max_sleep = max(durations) if durations else 0
    below_7 = sum(1 for d in durations if d < 7)
    diagnosis = []
    recommendations = []
    if avg_sleep < 7:
        diagnosis.append("You are not getting enough average sleep. Chronic sleep deprivation can impact health.")
        recommendations.append("Aim for at least 7-9 hours of sleep per night.")
    elif avg_sleep > 9:
        diagnosis.append("You are sleeping more than the recommended amount. Excessive sleep can also be a sign of underlying issues.")
        recommendations.append("Try to keep your sleep within the 7-9 hour range.")
    else:
        diagnosis.append("Your average sleep duration is within the healthy range.")
    if below_7 > 2:
        diagnosis.append(f"You had {below_7} nights with less than 7 hours of sleep.")
        recommendations.append("Try to maintain a more consistent sleep schedule.")
    return avg_sleep, min_sleep, max_sleep, diagnosis, recommendations

def llm_sleep_disorder_assessment(data):
    durations = [d["duration"] for d in data]
    sleep_times = []
    wake_times = []
    for d in data:
        try:
            sleep_dt = datetime.datetime.strptime(d["sleep"], "%I:%M %p")
            wake_dt = datetime.datetime.strptime(d["wake"], "%I:%M %p")
        except Exception:
            continue
        sleep_times.append(sleep_dt)
        wake_times.append(wake_dt)
    assessment = []
    insomnia_nights = sum(1 for dur in durations if dur < 6)
    late_sleeps = sum(1 for d in data if "PM" in d["sleep"] and int(d["sleep"].split(":")[0]) >= 12)
    if insomnia_nights >= 3 or late_sleeps >= 3:
        assessment.append("<b>Insomnia risk:</b> Detected multiple nights with short sleep or late sleep onset. Consider improving sleep hygiene and consulting a professional if you feel unrested.")
    apnea_nights = sum(1 for dur in durations if dur > 9)
    if apnea_nights >= 2:
        assessment.append("<b>Sleep Apnea risk:</b> Several nights with long sleep duration. If you still feel tired during the day, consider screening for sleep apnea.")
    if apnea_nights >= 2:
        assessment.append("<b>Hypersomnia risk:</b> Multiple nights with excessive sleep duration. Monitor for excessive daytime sleepiness.")
    if sleep_times and wake_times:
        sleep_hours = [dt.hour + dt.minute/60 for dt in sleep_times]
        wake_hours = [dt.hour + dt.minute/60 for dt in wake_times]
        if max(sleep_hours) - min(sleep_hours) > 2 or max(wake_hours) - min(wake_hours) > 2:
            assessment.append("<b>Irregular Sleep Pattern:</b> Your sleep or wake times vary significantly. Try to keep a consistent schedule.")
    if not assessment:
        assessment.append("No major sleep disorder risks detected based on your data. Continue healthy sleep habits!")
    return assessment

# def generate_html(data, avg, min_s, max_s, diagnosis, recommendations, llm_assessment):
#     html = "<div class='result-box'>"
#     html += "<h3>Sleep Coach Check-in</h3>"
#     for d in data:
#         html += f'<p><b>{d["date"]}</b>: Slept at {d["sleep"]}, woke at {d["wake"]} (<b>{d["duration"]} hours</b>)</p>'
#     html += f'<p><b>Average sleep duration:</b> {avg:.1f} hours</p>'
#     html += f'<p><b>Shortest night:</b> {min_s:.1f} hours</p>'
#     html += f'<p><b>Longest night:</b> {max_s:.1f} hours</p>'
#     html += "<h4>Diagnosis</h4>"
#     for d in diagnosis:
#         html += f'<p>{d}</p>'
#     html += "<h4>Recommendations</h4>"
#     for r in recommendations:
#         html += f'<p>{r}</p>'
#     html += '<h4>Possible Sleep Disorders (LLM-based assessment)</h4>'
#     for a in llm_assessment:
#         html += f'<p>{a}</p>'
#     html += '<p><i>Keep tracking your sleep for better health!</i></p>'
#     html += "</div>"
#     return html

# if st.button("Analyze My Sleep Data", type="primary"):
#     data = parse_sleep_data(user_input)
#     if not data:
#         st.error("Could not parse your sleep data. Please check the format.")
#     else:
#         if llm_mode:
#             with st.spinner("Generating LLM-based recommendation..."):
#                 try:
#                     llm_result = generate_sleep_recommendation_llm(data)
#                     if not llm_result.strip():
#                         st.error("LLM returned an empty response.")
#                     else:
#                         # Show LLM output in a styled box
#                         st.markdown(f"<div class='result-box'>{llm_result}</div>", unsafe_allow_html=True)
#                         st.markdown("""
#                         <div style='margin-top:2em; padding:1.5em 1.5em 1.2em 1.5em; background:#fff; border-radius:14px; border:2.5px solid; border-image:linear-gradient(90deg,#6366f1,#06b6d4) 1; box-shadow:0 4px 24px 0 rgba(80,80,180,0.10); position:relative;'>
#                             <div style='display:flex; align-items:center; margin-bottom:0.7em;'>
#                                 <span style="font-size:1.7em; margin-right:0.5em;">🧠</span>
#                                 <span style='font-size:1.25em; font-weight:700; color:#DA2027; letter-spacing:0.5px;'>Raw LLM Output</span>
#                             </div>
#                             <pre style='white-space:pre-wrap; font-size:1.08em; color:#DA2027;  border:none; margin:0; font-family: "Fira Mono", "Consolas", "Menlo", monospace;'>
# {}</pre>
#                         </div>
#                         """.format(llm_result), unsafe_allow_html=True)
#                 except Exception as e:
#                     st.error(f"LLM error: {e}")
#         else:
#             avg, min_s, max_s, diagnosis, recommendations = analyze_sleep(data)
#             llm_assessment = llm_sleep_disorder_assessment(data)
#             html = generate_html(data, avg, min_s, max_s, diagnosis, recommendations, llm_assessment)
#             st.markdown(html, unsafe_allow_html=True) 

def generate_mobile_sleep_report(data, avg, min_s, max_s, diagnosis, recommendations, llm_assessment):
    """Generate a concise, beautiful mobile sleep report."""
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sleep Coach</title>
    <style>
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;color:#fff;padding:1rem}}
        .app{{max-width:400px;margin:0 auto}}
        .header{{background:rgba(255,255,255,0.1);backdrop-filter:blur(10px);border-radius:20px;padding:1rem;margin-bottom:1rem;display:flex;justify-content:space-between;align-items:center}}
        .title{{font-size:1.2rem;font-weight:700}}
        .badge{{background:rgba(16,185,129,0.2);color:#10b981;padding:0.3rem 0.8rem;border-radius:15px;font-size:0.7rem;font-weight:600;border:1px solid rgba(16,185,129,0.3)}}
        .stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:0.5rem;margin-bottom:1rem}}
        .stat{{background:rgba(255,255,255,0.15);backdrop-filter:blur(5px);border-radius:15px;padding:1rem;text-align:center;border:1px solid rgba(255,255,255,0.2)}}
        .stat-value{{font-size:1.5rem;font-weight:800;display:block}}
        .stat-label{{font-size:0.7rem;opacity:0.8;margin-top:0.2rem}}
        .entries{{margin-bottom:1rem}}
        .entry{{background:rgba(255,255,255,0.1);backdrop-filter:blur(5px);border-radius:15px;padding:1rem;margin-bottom:0.5rem;border:1px solid rgba(255,255,255,0.15)}}
        .entry-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem}}
        .entry-date{{font-weight:600;font-size:0.9rem}}
        .entry-duration{{background:rgba(16,185,129,0.2);color:#10b981;padding:0.2rem 0.6rem;border-radius:10px;font-size:0.8rem;font-weight:600}}
        .entry-times{{display:flex;justify-content:space-between;font-size:0.8rem;opacity:0.9}}
        .section{{background:rgba(255,255,255,0.95);backdrop-filter:blur(10px);border-radius:15px;padding:1rem;margin-bottom:1rem;color:#1a1a2e}}
        .section-header{{display:flex;align-items:center;gap:0.5rem;margin-bottom:0.8rem;padding-bottom:0.5rem;border-bottom:1px solid #e5e7eb}}
        .section-icon{{width:30px;height:30px;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:0.9rem;font-weight:700}}
        .analysis-icon{{background:linear-gradient(135deg,#f59e0b,#d97706)}}
        .rec-icon{{background:linear-gradient(135deg,#10b981,#059669)}}
        .ai-icon{{background:linear-gradient(135deg,#8b5cf6,#7c3aed)}}
        .section-title{{font-size:1rem;font-weight:700;color:#1a1a2e}}
        .item{{background:#f8fafc;border-radius:8px;padding:0.8rem;margin-bottom:0.5rem;border-left:3px solid;font-size:0.85rem;line-height:1.4;color:#374151}}
        .diagnosis{{border-left-color:#f59e0b;background:linear-gradient(135deg,#fef3c7,#fde68a)}}
        .recommendation{{border-left-color:#10b981;background:linear-gradient(135deg,#d1fae5,#a7f3d0)}}
        .assessment{{border-left-color:#8b5cf6;background:linear-gradient(135deg,#e9d5ff,#ddd6fe)}}
        .footer{{background:rgba(255,255,255,0.1);backdrop-filter:blur(10px);border-radius:15px;padding:1rem;text-align:center;margin-top:1rem}}
        .footer-text{{font-size:0.9rem;margin-bottom:0.8rem;opacity:0.9}}
        .btn{{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;border-radius:12px;padding:0.8rem 1.5rem;font-weight:600;width:100%;cursor:pointer;transition:all 0.3s ease}}
        .btn:active{{transform:scale(0.98)}}
    </style>
</head>
<body>
    <div class="app">
        <div class="header">
            <div class="title">🌙 Sleep Coach</div>
            <div class="badge">✓ Complete</div>
        </div>
        
        <div class="stats">
            <div class="stat">
                <span class="stat-value">{avg:.1f}h</span>
                <span class="stat-label">Average</span>
            </div>
            <div class="stat">
                <span class="stat-value">{min_s:.1f}h</span>
                <span class="stat-label">Shortest</span>
            </div>
            <div class="stat">
                <span class="stat-value">{max_s:.1f}h</span>
                <span class="stat-label">Longest</span>
            </div>
        </div>
        
        <div class="entries">
            {''.join(f'''
            <div class="entry">
                <div class="entry-header">
                    <span class="entry-date">📅 {entry["date"]}</span>
                    <span class="entry-duration">{entry["duration"]}h</span>
                </div>
                <div class="entry-times">
                    <span>🌙 {entry["sleep"]}</span>
                    <span>☀️ {entry["wake"]}</span>
                </div>
            </div>
            ''' for entry in data)}
        </div>
        
        {f'''
        <div class="section">
            <div class="section-header">
                <div class="section-icon analysis-icon">🔍</div>
                <div class="section-title">Analysis</div>
            </div>
            {''.join(f'<div class="item diagnosis">{item}</div>' for item in diagnosis)}
        </div>
        ''' if diagnosis else ''}
        
        {f'''
        <div class="section">
            <div class="section-header">
                <div class="section-icon rec-icon">💡</div>
                <div class="section-title">Tips</div>
            </div>
            {''.join(f'<div class="item recommendation">{item}</div>' for item in recommendations)}
        </div>
        ''' if recommendations else ''}
        
        {f'''
        <div class="section">
            <div class="section-header">
                <div class="section-icon ai-icon">🤖</div>
                <div class="section-title">AI Insights</div>
            </div>
            {''.join(f'<div class="item assessment">{item}</div>' for item in llm_assessment)}
        </div>
        ''' if llm_assessment else ''}
        
        <div class="footer">
            <div class="footer-text">✨ Keep tracking for better sleep!</div>
            <button class="btn">📱 Share Report</button>
        </div>
    </div>
</body>
</html>"""


def handle_sleep_analysis():
    """Concise sleep analysis handler."""
    
    # Mobile-optimized styling
    st.markdown("""
    <style>
        .stButton>button{width:100%;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;border-radius:12px;padding:0.8rem;font-weight:600;font-size:1rem;box-shadow:0 4px 15px rgba(102,126,234,0.3);transition:all 0.3s ease}
        .stButton>button:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(102,126,234,0.4)}
        .main .block-container{padding:1rem;max-width:100%}
        .stSpinner>div{border-top-color:#667eea!important}
        .stError,.stSuccess,.stInfo{border-radius:8px;padding:0.8rem;margin:0.5rem 0}
    </style>
    """, unsafe_allow_html=True)
    
    if st.button("🔍 Analyze Sleep Data", type="primary"):
        with st.spinner("🔄 Analyzing..."):
            try:
                data = parse_sleep_data(user_input)
                
                if not data:
                    st.error("❌ Could not parse sleep data. Check format.")
                    return
                
                # if llm_mode:
                    # LLM Analysis
                try:
                    llm_result = generate_sleep_recommendation_llm(data)
                    if not llm_result.strip():
                        st.error("🚫 AI returned empty response.")
                        return
                    
                    st.markdown(f"""
                    <div style='background:linear-gradient(135deg,#667eea,#764ba2);padding:2px;border-radius:15px;margin:1rem 0'>
                        <div style='background:#fff;border-radius:13px;padding:1.5rem;color:#1a1a2e'>
                            <h3 style='display:flex;align-items:center;gap:0.5rem;margin-bottom:1rem;color:#1a1a2e'>
                                Sleep Coach
                            </h3>
                            <div style='line-height:1.6;color:#374151;font-size:0.9rem'>
                                {llm_result}
                    
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"🚨 AI Error: {e}")
                    # Fallback to standard analysis
                    avg, min_s, max_s, diagnosis, recommendations = analyze_sleep(data)
                    html_report = generate_mobile_sleep_report(data, avg, min_s, max_s, diagnosis, recommendations, [])
                    components.html(html_report, height=900, scrolling=True)
                
                # else:
                #     # Standard Analysis
                #     avg, min_s, max_s, diagnosis, recommendations = analyze_sleep(data)
                #     llm_assessment = llm_sleep_disorder_assessment(data)
                    
                #     html_report = generate_mobile_sleep_report(data, avg, min_s, max_s, diagnosis, recommendations, llm_assessment)
                #     components.html(html_report, height=900, scrolling=True)
                    
                #     # Download option
                #     st.download_button(
                #         label="📱 Download Report",
                #         data=html_report,
                #         file_name=f"sleep_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                #         mime="text/html",
                #         use_container_width=True
                #     )
                
            except Exception as e:
                st.error(f"🚨 Error: {e}")


# Initialize
if __name__ == "__main__":
    handle_sleep_analysis()
