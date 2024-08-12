import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from streamlit_echarts import st_echarts
import plotly.graph_objects as go
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards
from datetime import datetime, timedelta
import random

# Custom CSS and page config
st.set_page_config(layout="wide", page_title="Study Progress Dashboard", page_icon="📚")
st.markdown("""
<style>
    .reportview-container {background-color: #0E1117;}
    .main {background-color: #0E1117;}
    body {color: #F0F2F6;}
    .stApp {background-color: #0E1117;}
    .stMetricLabel {font-size: 20px !important; color: #F0F2F6 !important;}
    .stMetricValue {font-size: 28px !important; color: #00CED1 !important;}
    .stMetricDelta {font-size: 16px !important; color: #F0F2F6 !important;}
    .stProgress > div > div > div > div {background-color: #00CED1 !important;}
    .stTextInput > div > div > input {color: #F0F2F6 !important; background-color: #262730 !important;}
    .stSelectbox > div > div > div {color: #F0F2F6 !important; background-color: #262730 !important;}
    .stDateInput > div > div > input {color: #F0F2F6 !important; background-color: #262730 !important;}
    .stTextInput > label {color: #F0F2F6 !important;}
    .stSelectbox > label {color: #F0F2F6 !important;}
    .stDateInput > label {color: #F0F2F6 !important;}
    .stSidebar {background-color: #262730;}
    .stSidebar [data-testid="stSidebarNav"] {background-color: #262730;}
    .stSidebar [data-testid="stMarkdownContainer"] {color: #F0F2F6;}
    .stRadio > label {color: #F0F2F6 !important;}
    .stCheckbox > label {color: #F0F2F6 !important;}
    .st-bw {color: #F0F2F6;}
    .st-er {color: #00CED1;}
    .st-en {color: #F0F2F6;}
    .badge {
        display: inline-block;
        padding: 0.4em 0.8em;
        font-size: 75%;
        font-weight: 700;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 0.25rem;
        color: #0E1117;
        background-color: #00CED1;
        margin: 0.2em;
        transition: all 0.2s ease;
    }
    .badge:hover {
        transform: scale(1.05);
        box-shadow: 0 0 10px rgba(0, 206, 209, 0.5);
    }
    .stAlert {background-color: #262730; color: #F0F2F6; border-color: #00CED1;}
    .stInfo {background-color: #262730; color: #F0F2F6; border-color: #3498DB;}
    .stSuccess {background-color: #262730; color: #F0F2F6; border-color: #00CED1;}
    .stWarning {background-color: #262730; color: #F0F2F6; border-color: #F1C40F;}
    .stError {background-color: #262730; color: #F0F2F6; border-color: #E74C3C;}
</style>
""", unsafe_allow_html=True)

# Generate sample data for demonstration
@st.cache_data
def generate_sample_data(num_users=5, days=30):
    categories = ['Category 1', 'Category 2', 'Category 3', 'Category 4', 'Category 5']
    users = [f'user{i}@example.com' for i in range(1, num_users+1)]
    
    data = []
    badges = []
    
    for user in users:
        start_date = datetime.now() - timedelta(days=days)
        user_skill = random.uniform(0.5, 1.0)
        for day in range(days):
            date = start_date + timedelta(days=day)
            num_questions = random.randint(5, 20)
            daily_focus = random.choice(categories)
            for _ in range(num_questions):
                question_category = daily_focus if random.random() < 0.6 else random.choice(categories)
                difficulty = random.choice(['easy', 'medium', 'hard'])
                time_spent = random.randint(30, 300)
                
                skill_factor = user_skill * (1.2 if question_category == daily_focus else 1.0)
                difficulty_factor = {'easy': 0.9, 'medium': 0.7, 'hard': 0.5}[difficulty]
                correctness_prob = skill_factor * difficulty_factor
                result = 'correct' if random.random() < correctness_prob else 'incorrect'
                
                data.append({
                    'email': user,
                    'event_date': date + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59)),
                    'question_category': question_category,
                    'result': result,
                    'difficulty': difficulty,
                    'time_spent': time_spent,
                    'focus_category': daily_focus
                })
        
        user_data = [d for d in data if d['email'] == user]
        total_questions = len(user_data)
        correct_answers = sum(1 for d in user_data if d['result'] == 'correct')
        accuracy = correct_answers / total_questions if total_questions > 0 else 0
        
        badges.append({
            'email': user,
            'quick_learner': accuracy > 0.8,
            'consistent_studier': len(set(d['event_date'].date() for d in user_data)) > days * 0.8,
            'category_master': max(categories, key=lambda c: sum(1 for d in user_data if d['question_category'] == c and d['result'] == 'correct')),
            'perfect_score': any(sum(1 for d in user_data if d['event_date'].date() == date and d['result'] == 'correct') == sum(1 for d in user_data if d['event_date'].date() == date) for date in set(d['event_date'].date() for d in user_data)),
            'study_marathon': any(sum(d['time_spent'] for d in user_data if d['event_date'].date() == date) > 4 * 3600 for date in set(d['event_date'].date() for d in user_data)),
        })
    
    return pd.DataFrame(data), pd.DataFrame(badges)

# Load data from SQLite database or generate sample data
@st.cache_data
def load_data():
    try:
        conn = sqlite3.connect('user_data.db')
        df = pd.read_sql_query("SELECT * FROM user_events", conn)
        badges_df = pd.read_sql_query("SELECT * FROM user_badges", conn)
        conn.close()
        
        required_columns = ['email', 'event_date', 'question_category', 'result', 'difficulty', 'time_spent', 'focus_category']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"Missing columns in the database: {', '.join(missing_columns)}")
            st.error("Using sample data for demonstration.")
            return generate_sample_data()
        
        df['event_date'] = pd.to_datetime(df['event_date'])
        return df, badges_df
        
    except sqlite3.OperationalError as e:
        st.error(f"Error accessing the database: {str(e)}")
        st.warning("Using sample data for demonstration.")
        return generate_sample_data()
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        st.warning("Using sample data for demonstration.")
        return generate_sample_data()

@st.cache_data
def process_user_data(df, user_email, start_date, end_date):
    user_df = df[df['email'] == user_email]
    filtered_df = user_df[(user_df['event_date'].dt.date >= start_date) & (user_df['event_date'].dt.date <= end_date)]
    return filtered_df

def get_badge_description(badge):
    descriptions = {
        'quick_learner': "You're picking up new concepts rapidly!",
        'consistent_studier': "You've maintained a regular study schedule.",
        'perfect_score': "You've achieved a perfect score in at least one category!",
        'study_marathon': "You've completed an extended study session.",
    }
    return descriptions.get(badge, "You've earned this achievement!")

# Main app
st.title("📚 Study Progress Dashboard")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Detailed Analysis", "Study Recommendations"])

# Demo mode toggle
demo_mode = st.sidebar.checkbox("Enable Demo Mode")

if demo_mode:
    st.warning("Demo Mode: Using sample data for demonstration purposes.")
    df, badges_df = generate_sample_data()
else:
    df, badges_df = load_data()

# Get unique user emails from the dataset
unique_user_emails = df['email'].unique()
user_email = st.selectbox("Select your email:", options=unique_user_emails, index=0)

if user_email:
    st.success(f"Analyzing data for user: {user_email}")
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date", min(df['event_date']).date())
    with col2:
        end_date = st.date_input("End date", max(df['event_date']).date())
    
    # Process user data
    filtered_df = process_user_data(df, user_email, start_date, end_date)
    
    if page == "Dashboard":
        # Display user badges
        user_badges = badges_df[badges_df['email'] == user_email].iloc[0]
        st.subheader("🏆 Your Achievements")
        badge_cols = st.columns(5)
        badge_index = 0
        for badge, value in user_badges.items():
            if badge != 'email' and value:
                if badge == 'category_master':
                    badge_cols[badge_index % 5].markdown(f"<span class='badge' title='You've mastered the {value} category!'>🎓 Category Master: {value}</span>", unsafe_allow_html=True)
                else:
                    badge_name = badge.replace('_', ' ').title()
                    badge_cols[badge_index % 5].markdown(f"<span class='badge' title='{get_badge_description(badge)}'>🌟 {badge_name}</span>", unsafe_allow_html=True)
                badge_index += 1
        
        # Basic Statistics
        total_questions = filtered_df.shape[0]
        correct_answers = filtered_df[filtered_df['result'] == 'correct'].shape[0]
        accuracy = correct_answers / total_questions * 100 if total_questions > 0 else 0
        study_hours = filtered_df['time_spent'].sum() / 3600  # Convert seconds to hours
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📚 Total Questions", total_questions)
        col2.metric("✅ Correct Answers", correct_answers)
        col3.metric("🎯 Accuracy", f"{accuracy:.2f}%")
        col4.metric("⏱️ Study Hours", f"{study_hours:.1f}")
        style_metric_cards()

        # Progress Bar
        st.subheader("📊 Overall Progress")
        progress = min(accuracy, 100)  # Cap at 100%
        st.progress(progress / 100)
        st.write(f"You have completed {progress:.1f}% of your study material based on your current performance.")

        # Performance by Category
        st.subheader("📊 Performance by Category")
        category_performance = filtered_df.groupby('question_category').apply(lambda x: (x['result'] == 'correct').mean() * 100).reset_index()
        category_performance.columns = ['category', 'accuracy']
        
        radar_option = {
            "title": {"text": "Performance by Question Category", "textStyle": {"color": "#F0F2F6"}},
            "radar": {
                "indicator": [{"name": c, "max": 100} for c in category_performance['category']],
                "splitArea": {"show": False},
                "axisLine": {"lineStyle": {"color": "rgba(240, 242, 246, 0.2)"}},
                "splitLine": {"lineStyle": {"color": "rgba(240, 242, 246, 0.2)"}}
            },
            "series": [{
                "name": "Category Accuracy",
                "type": "radar",
                "data": [{
                    "value": category_performance['accuracy'].tolist(),
                    "name": "Accuracy %",
                    "areaStyle": {"color": "rgba(0, 206, 209, 0.6)"},
                    "lineStyle": {"color": "rgba(0, 206, 209, 0.8)"},
                    "itemStyle": {"color": "rgba(0, 206, 209, 1)"}
                }]
            }]
        }
        st_echarts(options=radar_option, height="400px")

        # Daily Performance Time Series
        st.subheader("📈 Daily Performance Trend")
        daily_performance = filtered_df.groupby(filtered_df['event_date'].dt.date).agg({
            'result': lambda x: (x == 'correct').mean(),
            'time_spent': 'sum'
        }).reset_index()
        daily_performance.columns = ['date', 'accuracy', 'study_time']
        daily_performance['study_hours'] = daily_performance['study_time'] / 3600

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily_performance['date'], y=daily_performance['accuracy'], name="Accuracy", line=dict(color="#00CED1")))
        fig.add_trace(go.Scatter(x=daily_performance['date'], y=daily_performance['study_hours'], name="Study Hours", line=dict(color="#FF69B4"), yaxis="y2"))

        fig.update_layout(
            title_text="Daily Performance and Study Time Trend",
            xaxis_title="Date",
            yaxis_title="Accuracy",
            yaxis2=dict(title="Study Hours", overlaying="y", side="right"),
            height=400,
            paper_bgcolor='rgba(14,17,23,1)',
            plot_bgcolor='rgba(14,17,23,1)',
            font_color='#F0F2F6',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig, use_container_width=True)

        # AI-Powered Insights
        st.subheader("🤖 AI-Powered Insights")
        insights = [
            f"Your overall accuracy of {accuracy:.2f}% shows {('strong progress' if accuracy > 70 else 'room for improvement')}.",
            f"You've been most consistent in the question category: {filtered_df['question_category'].value_counts().index[0]}.",
            f"The question category '{category_performance.iloc[category_performance['accuracy'].idxmin()]['category']}' needs more attention.",
            f"Your daily performance trend shows {'improvement' if daily_performance['accuracy'].iloc[-1] > daily_performance['accuracy'].iloc[0] else 'a slight decline'}. Keep pushing!",
            f"You've studied on {len(daily_performance)} days in the selected period, with an average of {filtered_df.groupby('event_date').size().mean():.1f} questions per day.",
            f"Your total study time is {study_hours:.1f} hours, with an average of {daily_performance['study_hours'].mean():.2f} hours per day.",
            f"Your strongest performance is in the '{category_performance.iloc[category_performance['accuracy'].idxmax()]['category']}' category with an accuracy of {category_performance['accuracy'].max():.2f}%.",
        ]
        for insight in insights:
            st.info(insight)

    elif page == "Detailed Analysis":
        st.subheader("📊 Study Patterns")

        # Time of day analysis
        hourly_performance = filtered_df.groupby(filtered_df['event_date'].dt.hour).agg({
            'result': lambda x: (x == 'correct').mean(),
            'event_date': 'count'
        }).reset_index()
        hourly_performance.columns = ['hour', 'accuracy', 'questions']

        fig = px.line(hourly_performance, x='hour', y=['accuracy', 'questions'], 
                    title='Performance and Activity by Hour of Day')
        fig.update_layout(
            paper_bgcolor='rgba(14,17,23,1)',
            plot_bgcolor='rgba(14,17,23,1)',
            font_color='#F0F2F6'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Day of week analysis
        weekday_performance = filtered_df.groupby(filtered_df['event_date'].dt.dayofweek).agg({
            'result': lambda x: (x == 'correct').mean(),
            'event_date': 'count'
        }).reset_index()
        weekday_performance.columns = ['day', 'accuracy', 'questions']
        weekday_performance['day'] = weekday_performance['day'].map({0:'Mon', 1:'Tue', 2:'Wed', 3:'Thu', 4:'Fri', 5:'Sat', 6:'Sun'})

        fig = px.bar(weekday_performance, x='day', y=['accuracy', 'questions'], 
                    title='Performance and Activity by Day of Week')
        fig.update_layout(
            paper_bgcolor='rgba(14,17,23,1)',
            plot_bgcolor='rgba(14,17,23,1)',
            font_color='#F0F2F6'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Difficulty analysis
        difficulty_performance = filtered_df.groupby('difficulty').agg({
            'result': lambda x: (x == 'correct').mean(),
            'event_date': 'count'
        }).reset_index()
        difficulty_performance.columns = ['difficulty', 'accuracy', 'questions']

        fig = px.bar(difficulty_performance, x='difficulty', y=['accuracy', 'questions'],
                    title='Performance and Activity by Question Difficulty')
        fig.update_layout(
            paper_bgcolor='rgba(14,17,23,1)',
            plot_bgcolor='rgba(14,17,23,1)',
            font_color='#F0F2F6'
        )
        st.plotly_chart(fig, use_container_width=True)

    elif page == "Study Recommendations":
        st.subheader("📚 Study Recommendations")

        # Identify areas for improvement
        category_performance = filtered_df.groupby('question_category').apply(lambda x: (x['result'] == 'correct').mean() * 100).reset_index()
        category_performance.columns = ['category', 'accuracy']
        weak_categories = category_performance[category_performance['accuracy'] < 70].sort_values('accuracy')

        if not weak_categories.empty:
            st.write("Based on your performance, we recommend focusing on the following categories:")
            for _, category in weak_categories.iterrows():
                st.write(f"- {category['category']}: {category['accuracy']:.2f}% accuracy")
        else:
            st.write("Great job! You're performing well in all categories. Keep up the good work!")

        # Study schedule recommendation
        st.write("\n### Recommended Study Schedule")
        study_hours = filtered_df['time_spent'].sum() / 3600
        avg_daily_study = study_hours / (end_date - start_date).days

        if avg_daily_study < 2:
            st.write("We recommend increasing your daily study time. Aim for at least 2 hours per day.")
        elif avg_daily_study > 6:
            st.write("You're studying a lot! Make sure to take breaks and not overexert yourself.")
        else:
            st.write(f"Your current average of {avg_daily_study:.2f} hours per day is good. Try to maintain this consistency.")

        # Best study time recommendation
        hourly_performance = filtered_df.groupby(filtered_df['event_date'].dt.hour).apply(lambda x: (x['result'] == 'correct').mean() * 100).reset_index()
        hourly_performance.columns = ['hour', 'accuracy']
        best_hour = hourly_performance.loc[hourly_performance['accuracy'].idxmax(), 'hour']
        st.write(f"\nYour most productive study hour seems to be around {best_hour}:00. Try to schedule your most challenging study sessions during this time.")

        # Spaced repetition recommendation
        st.write("\n### Spaced Repetition Strategy")
        st.write("To improve long-term retention, try the following spaced repetition schedule:")
        st.write("1. Review new material after 1 day")
        st.write("2. Review again after 3 days")
        st.write("3. Then after 1 week")
        st.write("4. Finally, after 2 weeks")
        st.write("This strategy helps reinforce your learning and move information into long-term memory.")

else:
    st.write("Please select your email to view your personalized study progress dashboard.")

# Add a button to regenerate sample data
if st.sidebar.button("Regenerate Sample Data"):
    st.cache_data.clear()
    st.experimental_rerun()