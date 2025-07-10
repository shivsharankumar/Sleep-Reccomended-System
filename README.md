# Sleep Coach Check-in

This project analyzes your last 7 days of sleep data and generates a sleep coach check-in as a clean HTML report, including recommendations and a diagnosis.

## How to Use

1. Make sure you have Python 3 installed.
2. Run the script:
   ```bash
   python3 sleep_coach.py
   ```
3. The script will generate a file called `sleep_coach_checkin.html` in the same directory.
4. Open `sleep_coach_checkin.html` in your browser to view your sleep report.

## Customizing Data

To analyze your own sleep data, edit the `sleep_data` list in `sleep_coach.py` with your own dates, sleep/wake times, and durations. 