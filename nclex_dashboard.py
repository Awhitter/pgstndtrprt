import streamlit as st
import pandas as pd
import numpy as np
from streamlit_echarts import st_echarts
from datetime import datetime, timedelta
import plotly.graph_objects as go
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_lottie import st_lottie
import json
import requests

# Custom CSS for a sleeker look
st.set_page_config(layout="wide")
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6
    }
    .main {
        background: #f0f2f6
    }
</style>
""", unsafe_allow_html=True)

# Load Lottie animation
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_study = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_xyadoh9h.json")

# Load and preprocess data
@st.cache_data
def load_data():
    # Simulated data loading - replace with actual data source
    data = {
        'name': ['Tagged Practice Question', 'Expanded Explanation', 'Expanded Answer Choice Rationale', 'Answered Practice Question'] * 100,
        'at': pd.date_range(start='2023-10-01', end='2023-10-22', freq='H').tolist()[:400],
        'user_class': ['fnp_testprep'] * 400,
        'subcription_during_event': ['Mo (1225)'] * 400,
        'custom_answer_was': np.random.choice(['correct', 'incorrect', ''], size=400, p=[0.7, 0.2, 0.1]),
        'custom_question_marked_as': np.random.choice(['correct', 'incorrect', ''], size=400, p=[0.6, 0.3, 0.1]),
        'category': np.random.choice(['Fundamentals', 'Med-Surg', 'Pediatrics', 'OB/GYN', 'Psychiatric', 'Pharmacology'], size=400)
    }
    df = pd.DataFrame(data)
    df['at'] = pd.to_datetime(df['at'])
    return df

df = load_data()

# Main app
st.title("🚀 NCLEX Study Progress Dashboard")
st_lottie(lottie_study, height=200, key="study_animation")

email = st.text_input("📧 Enter your email to view your personalized dashboard:")

if email:
    st.success(f"Analyzing data for: {email}")
    
    # 1. Enhanced Basic Statistics with Trend Indicators
    total_questions = df[df['name'] == 'Answered Practice Question'].shape[0]
    correct_answers = df[(df['name'] == 'Answered Practice Question') & (df['custom_answer_was'] == 'correct')].shape[0]
    accuracy = correct_answers / total_questions * 100 if total_questions > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📚 Total Questions", total_questions, "1.2% increase")
    col2.metric("✅ Correct Answers", correct_answers, "2.5% increase")
    col3.metric("🎯 Accuracy", f"{accuracy:.2f}%", "0.5% increase")
    col4.metric("⏱️ Study Hours", f"{len(df['at'].dt.date.unique()) * 2:.1f}", "1.5 hours increase")
    style_metric_cards()

    # 2. Interactive Study Calendar Heatmap
    st.subheader("📅 Study Intensity Calendar")
    
    study_counts = df.groupby(df['at'].dt.date).size().reset_index(name='count')
    study_counts['date'] = study_counts['at'].dt.strftime('%Y-%m-%d')
    
    calendar_data = [
        [d.strftime("%Y-%m-%d"), c] for d, c in zip(study_counts['at'], study_counts['count'])
    ]
    
    calendar_option = {
        "tooltip": {"position": "top"},
        "visualMap": {
            "min": 0,
            "max": 30,
            "calculable": True,
            "orient": "horizontal",
            "left": "center",
            "top": "top",
        },
        "calendar": [
            {
                "range": "2023",
                "cellSize": ["auto", 20],
            }
        ],
        "series": [
            {
                "type": "heatmap",
                "coordinateSystem": "calendar",
                "data": calendar_data,
            }
        ],
    }
    st_echarts(options=calendar_option, height="250px")

    # 3. Performance by Category Radar Chart
    st.subheader("📊 Performance by Category")
    
    categories = df['category'].unique()
    category_performance = []
    
    for category in categories:
        cat_df = df[(df['name'] == 'Answered Practice Question') & (df['category'] == category)]
        cat_accuracy = cat_df[cat_df['custom_answer_was'] == 'correct'].shape[0] / cat_df.shape[0] * 100 if cat_df.shape[0] > 0 else 0
        category_performance.append(cat_accuracy)
    
    radar_option = {
        "title": {"text": "Category Performance"},
        "radar": {
            "indicator": [{"name": c, "max": 100} for c in categories]
        },
        "series": [{
            "name": "Category Accuracy",
            "type": "radar",
            "data": [{
                "value": category_performance,
                "name": "Accuracy %"
            }]
        }]
    }
    st_echarts(options=radar_option, height="400px")

    # 4. Study Session Analysis
    st.subheader("📉 Study Session Analysis")
    
    session_data = df.sort_values('at')
    session_data['time_diff'] = session_data['at'].diff()
    session_data['new_session'] = session_data['time_diff'] > pd.Timedelta(hours=1)
    session_data['session'] = session_data['new_session'].cumsum()
    
    session_stats = session_data.groupby('session').agg({
        'at': ['count', 'min', 'max'],
        'custom_answer_was': lambda x: (x == 'correct').mean()
    }).reset_index()
    
    session_stats.columns = ['session', 'questions', 'start_time', 'end_time', 'accuracy']
    session_stats['duration'] = (session_stats['end_time'] - session_stats['start_time']).dt.total_seconds() / 60
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=session_stats['start_time'], y=session_stats['questions'],
                             mode='markers', name='Questions per Session',
                             marker=dict(size=session_stats['duration'], sizemode='area', sizeref=2.*max(session_stats['duration'])/(40.**2),
                                         sizemin=4, color=session_stats['accuracy'], colorscale='Viridis', showscale=True),
                             text=session_stats['accuracy'].apply(lambda x: f'{x*100:.1f}% accuracy')))
    
    fig.update_layout(title='Study Sessions: Duration, Questions, and Accuracy',
                      xaxis_title='Session Start Time', yaxis_title='Number of Questions')
    st.plotly_chart(fig, use_container_width=True)

    # 5. AI-Powered Insights and Recommendations
    st.subheader("🤖 AI-Powered Insights")
    
    insights = [
        f"Your overall accuracy of {accuracy:.2f}% shows strong progress. Keep it up!",
        f"You've been most consistent in studying {df['category'].value_counts().index[0]}. Consider balancing your focus across all categories.",
        f"Your longest study session was {session_stats['duration'].max():.0f} minutes. Try to maintain this level of focus regularly.",
        "You tend to perform better in morning sessions. Consider scheduling more study time in the AM if possible.",
        f"The category '{categories[np.argmin(category_performance)]}' needs more attention. We recommend focusing on this area.",
    ]
    
    for insight in insights:
        st.info(insight)

    # 6. Personalized Study Plan Generator
    st.subheader("📝 Personalized Study Plan Generator")
    days_to_exam = st.slider("Days until your NCLEX exam:", 1, 90, 30)
    
    if st.button("Generate Study Plan"):
        study_plan = f"""
        Based on your performance and {days_to_exam} days until your exam, here's a personalized study plan:
        
        1. Focus on {categories[np.argmin(category_performance)]} for the next week, aiming for 2 hours of study per day.
        2. Increase your daily question count to {max(50, total_questions // days_to_exam)} to ensure comprehensive coverage.
        3. Schedule 3 mock exams in the coming weeks to simulate test conditions.
        4. Dedicate 30 minutes daily to reviewing your weakest areas identified in the performance radar.
        5. Use the 'Expanded Explanation' feature more frequently to deepen your understanding of complex topics.
        """
        st.success(study_plan)

    # 7. Interactive Question Bank Explorer
    st.subheader("🔍 Question Bank Explorer")
    selected_category = st.selectbox("Select a category to explore:", categories)
    
    category_questions = df[(df['name'] == 'Answered Practice Question') & (df['category'] == selected_category)]
    correct_ratio = category_questions[category_questions['custom_answer_was'] == 'correct'].shape[0] / category_questions.shape[0]
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = correct_ratio * 100,
        title = {'text': f"{selected_category} Performance"},
        gauge = {'axis': {'range': [None, 100]},
                 'steps': [
                     {'range': [0, 60], 'color': "lightgray"},
                     {'range': [60, 80], 'color': "gray"}],
                 'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 80}}))
    
    st.plotly_chart(fig, use_container_width=True)

    # 8. Study Streak Tracker
    st.subheader("🔥 Study Streak Tracker")
    
    daily_activity = df.groupby(df['at'].dt.date).size().reset_index(name='count')
    daily_activity['streak'] = (daily_activity['at'] != daily_activity['at'].shift() + timedelta(days=1)).cumsum()
    current_streak = daily_activity.groupby('streak').size().iloc[-1]
    
    streak_option = {
        "title": {"text": f"Current Streak: {current_streak} days"},
        "xAxis": {"type": "category", "data": daily_activity['at'].dt.strftime('%Y-%m-%d').tolist()},
        "yAxis": {"type": "value"},
        "series": [{
            "data": daily_activity['count'].tolist(),
            "type": "line",
            "smooth": True,
            "markPoint": {
                "data": [{"type": "max", "name": "Max"}, {"type": "min", "name": "Min"}]
            },
            "markLine": {"data": [{"type": "average", "name": "Avg"}]}
        }]
    }
    st_echarts(options=streak_option, height="300px")

    # 9. Peer Comparison (simulated)
    st.subheader("👥 Peer Comparison")
    
    peer_data = {
        'Metric': ['Questions Answered', 'Accuracy', 'Study Hours', 'Categories Covered'],
        'You': [total_questions, accuracy, len(df['at'].dt.date.unique()) * 2, len(categories)],
        'Peer Average': [total_questions * 0.8, accuracy * 0.9, len(df['at'].dt.date.unique()) * 1.5, len(categories) * 0.8]
    }
    peer_df = pd.DataFrame(peer_data)
    
    fig = go.Figure(data=[
        go.Bar(name='You', x=peer_df['Metric'], y=peer_df['You']),
        go.Bar(name='Peer Average', x=peer_df['Metric'], y=peer_df['Peer Average'])
    ])
    fig.update_layout(barmode='group', title='Your Performance vs. Peer Average')
    st.plotly_chart(fig, use_container_width=True)

    # 10. AI Q&A Assistant
    st.subheader("🙋 Ask AI About Your Progress")
    user_question = st.text_input("What would you like to know about your study progress?")
    if user_question:
        ai_response = f"Based on your study data, here's an answer to '{user_question}':\n\n[AI-generated response would go here, providing personalized insights based on the user's specific question and their study data.]"
        st.write(ai_response)

else:
    st.write("Please enter your email to view your personalized study progress dashboard.")
