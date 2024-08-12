import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from streamlit_echarts import st_echarts
import plotly.graph_objects as go
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_lottie import st_lottie
import requests
from datetime import datetime, timedelta

# Custom CSS and page config
st.set_page_config(layout="wide", page_title="FNP TestPrep Study Progress Dashboard")
st.markdown("""
<style>
    .reportview-container {background-color: #000000;}
    .main {background-color: #000000;}
    body {color: #ffffff;}
    .stApp {background-color: #000000;}
    .stMetricLabel {font-size: 20px !important;}
    .stMetricValue {font-size: 28px !important;}
    .stMetricDelta {font-size: 16px !important;}
    .stProgress > div > div > div > div {background-color: #4CAF50 !important;}
    .custom-lottie {display: flex; justify-content: center; align-items: center;}
    .stTextInput > div > div > input {color: #ffffff !important; background-color: #333333 !important;}
    .stSelectbox > div > div > div {color: #ffffff !important; background-color: #333333 !important;}
    .stDateInput > div > div > input {color: #ffffff !important; background-color: #333333 !important;}
    .stTextInput > label {color: #ffffff !important;}
    .stSelectbox > label {color: #ffffff !important;}
    .stDateInput > label {color: #ffffff !important;}
    .badge {
        display: inline-block;
        padding: 0.25em 0.4em;
        font-size: 75%;
        font-weight: 700;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 0.25rem;
        color: #fff;
        background-color: #28a745;
    }
</style>
""", unsafe_allow_html=True)

# Load Lottie animation
@st.cache_resource
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_study = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_xyadoh9h.json")

# Load data from SQLite database
@st.cache_data
def load_data():
    conn = sqlite3.connect('user_data.db')
    df = pd.read_sql_query("SELECT * FROM user_events", conn)
    df['event_date'] = pd.to_datetime(df['event_date'])
    badges_df = pd.read_sql_query("SELECT * FROM user_badges", conn)
    conn.close()
    return df, badges_df

df, badges_df = load_data()

# Main app
st.title("🚀 FNP TestPrep Study Progress Dashboard")
st.markdown("<div class='custom-lottie'>", unsafe_allow_html=True)
st_lottie(lottie_study, height=200, key="study_animation")
st.markdown("</div>", unsafe_allow_html=True)

# Get unique user emails from the dataset
unique_user_emails = df['email'].unique()
user_email_example = unique_user_emails[0] if len(unique_user_emails) > 0 else "example@email.com"

st.info(f"To view the dashboard, please select your email address. For example: {user_email_example}")

user_email = st.selectbox("👤 Select your email to view your personalized dashboard:", options=unique_user_emails, index=0)

if user_email:
    st.success(f"Analyzing data for user: {user_email}")
    
    # Filter data for the selected user
    user_df = df[df['email'] == user_email]
    
    # Date range selector
    st.sidebar.title("Date Range")
    min_date = user_df['event_date'].min().date()
    max_date = user_df['event_date'].max().date()
    default_start = max(min_date, max_date - timedelta(days=365))
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(default_start, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Ensure date_range is a tuple of two dates
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = date_range
        end_date = max_date
    
    # Filter data based on date range
    filtered_df = user_df[(user_df['event_date'].dt.date >= start_date) & (user_df['event_date'].dt.date <= end_date)]
    
    # Display user badges
    user_badges = badges_df[badges_df['email'] == user_email].iloc[0]
    st.subheader("🏆 Your Achievements")
    badge_cols = st.columns(5)
    badge_index = 0
    for badge, value in user_badges.items():
        if badge != 'email' and value:
            if badge == 'category_master':
                badge_cols[badge_index % 5].markdown(f"<span class='badge'>🎓 Category Master: {value}</span>", unsafe_allow_html=True)
            else:
                badge_name = badge.replace('_', ' ').title()
                badge_cols[badge_index % 5].markdown(f"<span class='badge'>🌟 {badge_name}</span>", unsafe_allow_html=True)
            badge_index += 1
    
    # Basic Statistics
    total_questions = filtered_df.shape[0]
    correct_answers = filtered_df[filtered_df['result'] == 'correct'].shape[0]
    accuracy = correct_answers / total_questions * 100 if total_questions > 0 else 0
    study_hours = len(filtered_df['event_date'].dt.date.unique()) * 2  # Assuming 2 hours per day
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📚 Total Questions", total_questions)
    col2.metric("✅ Correct Answers", correct_answers)
    col3.metric("🎯 Accuracy", f"{accuracy:.2f}%")
    col4.metric("⏱️ Study Hours", f"{study_hours:.1f}")
    style_metric_cards()

    # Exam Readiness Progress Bar
    st.subheader("📊 Exam Readiness")
    readiness = min(accuracy, 100)  # Cap at 100%
    st.progress(readiness / 100)
    st.write(f"You are approximately {readiness:.1f}% ready for the FNP exam based on your current performance.")

    # Study Calendar Heatmap
    st.subheader("📅 Study Intensity Calendar")
    study_counts = filtered_df.groupby(filtered_df['event_date'].dt.date).size().reset_index(name='count')
    study_counts['event_date'] = pd.to_datetime(study_counts['event_date'])
    study_counts['date'] = study_counts['event_date'].dt.strftime('%Y-%m-%d')
    
    calendar_data = [[d, int(c)] for d, c in zip(study_counts['date'], study_counts['count'])]
    
    calendar_option = {
        "tooltip": {"position": "top"},
        "visualMap": {
            "min": 0,
            "max": int(study_counts['count'].max()),
            "calculable": True,
            "orient": "horizontal",
            "left": "center",
            "top": "top",
            "inRange": {"color": ["#1A5276", "#2E86C1", "#D6EAF8"]}  # Updated color scheme for dark background
        },
        "calendar": [{"range": str(start_date.year), "cellSize": ["auto", 20]}],
        "series": [{"type": "heatmap", "coordinateSystem": "calendar", "data": calendar_data}]
    }
    st_echarts(options=calendar_option, height="250px")

    # Performance by Category
    st.subheader("📊 Performance by Category")
    categories = filtered_df['question_category'].unique()
    category_performance = []
    
    for category in categories:
        cat_df = filtered_df[filtered_df['question_category'] == category]
        cat_accuracy = cat_df[cat_df['result'] == 'correct'].shape[0] / cat_df.shape[0] * 100 if cat_df.shape[0] > 0 else 0
        category_performance.append(cat_accuracy)
    
    radar_option = {
        "title": {"text": "Performance by Question Category", "textStyle": {"color": "#ffffff"}},
        "radar": {
            "indicator": [{"name": c, "max": 100} for c in categories],
            "splitArea": {"areaStyle": {"color": ["rgba(114, 172, 209, 0.2)","rgba(114, 172, 209, 0.4)","rgba(114, 172, 209, 0.6)","rgba(114, 172, 209, 0.8)","rgba(114, 172, 209, 1)"]}}
        },
        "series": [{
            "name": "Category Accuracy",
            "type": "radar",
            "data": [{"value": category_performance, "name": "Accuracy %", "areaStyle": {"color": "rgba(46, 134, 193, 0.6)"}}]
        }]
    }
    st_echarts(options=radar_option, height="400px")

    # Study Session Analysis
    st.subheader("📉 Study Session Analysis")
    session_data = filtered_df.sort_values('event_date')
    session_data['time_diff'] = session_data['event_date'].diff()
    session_data['new_session'] = session_data['time_diff'] > pd.Timedelta(hours=1)
    session_data['session'] = session_data['new_session'].cumsum()
    
    session_stats = session_data.groupby('session').agg({
        'event_date': ['count', 'min', 'max'],
        'result': lambda x: (x == 'correct').mean()
    }).reset_index()
    
    session_stats.columns = ['session', 'questions', 'start_time', 'end_time', 'accuracy']
    session_stats['duration'] = (session_stats['end_time'] - session_stats['start_time']).dt.total_seconds() / 60
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=session_stats['start_time'], 
        y=session_stats['questions'],
        mode='markers',
        marker=dict(
            size=session_stats['duration'],
            sizemode='area',
            sizeref=2.*max(session_stats['duration'])/(40.**2),
            sizemin=4,
            color=session_stats['accuracy'],
            colorscale='Viridis',
            showscale=True
        ),
        text=session_stats.apply(lambda row: f"Duration: {row['duration']:.1f} min<br>Accuracy: {row['accuracy']*100:.1f}%", axis=1),
        hoverinfo='text'
    ))
    
    fig.update_layout(
        title='Study Sessions: Duration, Questions, and Accuracy',
        xaxis_title='Session Start Time',
        yaxis_title='Number of Questions',
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#ffffff'
    )
    st.plotly_chart(fig, use_container_width=True)

    # Daily Performance Time Series
    st.subheader("📈 Daily Performance Trend")
    daily_performance = filtered_df.groupby(filtered_df['event_date'].dt.date).agg({
        'result': lambda x: (x == 'correct').mean(),
        'event_date': 'count'
    }).reset_index()
    daily_performance.columns = ['date', 'accuracy', 'questions']

    fig = px.line(daily_performance, x='date', y='accuracy', title='Daily Accuracy Trend')
    fig.update_traces(line_color='#2E86C1')
    fig.update_layout(height=400, xaxis_title='Date', yaxis_title='Accuracy', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#ffffff')
    st.plotly_chart(fig, use_container_width=True)

    # AI-Powered Insights
    st.subheader("🤖 AI-Powered Insights")
    insights = [
        f"Your overall accuracy of {accuracy:.2f}% shows {('strong progress' if accuracy > 70 else 'room for improvement')}.",
        f"You've been most consistent in the question category: {filtered_df['question_category'].value_counts().index[0]}.",
        f"Your average study session duration is {session_stats['duration'].mean():.0f} minutes.",
        f"You tend to perform better in {('morning' if session_stats.groupby(session_stats['start_time'].dt.hour)['accuracy'].mean().idxmax() < 12 else 'evening')} sessions.",
        f"The question category '{categories[np.argmin(category_performance)]}' needs more attention.",
        f"Your daily performance trend shows {'improvement' if daily_performance['accuracy'].iloc[-1] > daily_performance['accuracy'].iloc[0] else 'a slight decline'}. Keep pushing!",
        f"You've studied on {len(daily_performance)} days in the selected period, with an average of {daily_performance['questions'].mean():.1f} questions per day."
    ]
    for insight in insights:
        st.info(insight)

    # Natural Language Query
    st.subheader("🙋 Ask about your study progress")
    query = st.text_input("What would you like to know about your study progress?")
    if query:
        # Here you would integrate with an AI model to generate a response
        # For now, we'll use a placeholder response
        ai_response = f"Based on your study data, here's an answer to '{query}':\n\n[AI-generated response would go here, providing personalized insights based on the user's specific question and their study data.]"
        st.write(ai_response)

else:
    st.write("Please select your email to view your personalized study progress dashboard.")