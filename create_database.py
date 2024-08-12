import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Create a connection to the SQLite database
conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()

# Create the table
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_events (
    email TEXT,
    event_date DATETIME,
    question_id INTEGER,
    difficulty REAL,
    event_name TEXT,
    result TEXT,
    app_id TEXT,
    question_category TEXT,
    subscribed BOOLEAN,
    location TEXT
)
''')

# Create a table for badges
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_badges (
    email TEXT,
    most_engaged_studier BOOLEAN,
    most_active_in_state BOOLEAN,
    thirty_day_streak BOOLEAN,
    night_owl BOOLEAN,
    early_bird BOOLEAN,
    weekend_warrior BOOLEAN,
    category_master TEXT,
    perfect_week BOOLEAN,
    rapid_improver BOOLEAN
)
''')

# Sample users
users = [
    "andreispfranck@gmail.com",
    "janedoe@example.com",
    "johnsmith@example.com",
    "sarahconnor@example.com",
    "tonystark@example.com"
]

# Generate sample data
data = []
start_date = datetime(2022, 1, 1)
end_date = datetime(2024, 12, 31)
categories = ["Cardiovascular", "Respiratory", "Gastrointestinal", "Musculoskeletal", "Neurological", "Endocrine", "Renal", "Reproductive", "Psychiatric", "Pediatric"]
locations = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]

for user in users:
    num_events = np.random.randint(500, 2000)
    for _ in range(num_events):
        event_date = start_date + timedelta(days=np.random.randint(0, (end_date - start_date).days))
        data.append((
            user,
            event_date.strftime("%Y-%m-%d %H:%M:%S"),
            np.random.randint(10000, 500000),
            round(np.random.random(), 2),
            "Answered Practice Question",
            np.random.choice(["correct", "incorrect"], p=[0.7, 0.3]),
            "FNP_TestPrep",
            np.random.choice(categories),
            True,
            np.random.choice(locations)
        ))

# Insert the data into the table
cursor.executemany('''
INSERT INTO user_events (email, event_date, question_id, difficulty, event_name, result, app_id, question_category, subscribed, location)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', data)

# Generate and insert badge data
for user in users:
    cursor.execute('''
    INSERT INTO user_badges (email, most_engaged_studier, most_active_in_state, thirty_day_streak, night_owl, early_bird, weekend_warrior, category_master, perfect_week, rapid_improver)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user,
        np.random.choice([True, False]),
        np.random.choice([True, False]),
        np.random.choice([True, False]),
        np.random.choice([True, False]),
        np.random.choice([True, False]),
        np.random.choice([True, False]),
        np.random.choice(categories) if np.random.random() > 0.5 else None,
        np.random.choice([True, False]),
        np.random.choice([True, False])
    ))

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database created and sample data inserted successfully.")