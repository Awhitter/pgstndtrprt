# Study Progress Dashboard

This interactive dashboard provides a comprehensive view of your study progress for various exams. It visualizes your study habits, performance across different categories, and offers AI-powered insights to help you optimize your study strategy.

## Features

- Personal study progress tracking
- Performance analysis by question category
- Study intensity calendar
- Daily performance trends
- AI-powered insights
- Interactive study session analysis
- Achievement badges

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/study-progress-dashboard.git
   cd study-progress-dashboard
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run dashboard.py
   ```

2. Open your web browser and go to `http://localhost:8501` to view the dashboard.

3. Select your email from the dropdown to view your personalized dashboard.

## Data

The dashboard currently uses sample data for demonstration purposes. To use real data, you'll need to create a SQLite database named `user_data.db` with the following tables:

- `user_events`: Contains individual question attempts and results
- `user_badges`: Contains achievement data for each user

## Customization

You can modify the `dashboard.py` file to add new features, change the layout, or integrate with a different data source. The dashboard is designed to be flexible and can be adapted for various types of exams and study materials.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

## Contact

If you have any questions or feedback, please open an issue on this repository.