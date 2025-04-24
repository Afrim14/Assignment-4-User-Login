# Golf Score Tracker with MongoDB

## Overview
Golf Score Tracker is a comprehensive web application that helps golfers record, analyze, and visualize their performance across multiple courses. This version includes MongoDB integration for user authentication and data persistence.

## Features
- **User Authentication**
  - Secure login and registration
  - Password encryption with bcrypt
  - User-specific scorecards

- **Score Management**
  - Record detailed scorecards with hole-by-hole scores
  - Track par values for each hole
  - Add weather conditions and personal notes
  - Calculate scores relative to par

- **Data Visualization**
  - Score trend line chart to track improvement over time
  - Course distribution pie chart 
  - Performance statistics dashboard
  - Color-coded score indicators (under par, even, over par)

- **Course Tracking**
  - Record scores from multiple golf courses
  - Filter scorecards by specific courses
  - Compare performance across different courses

## Installation

### Prerequisites
- Python 3.7+
- MongoDB 4.4+
- Web browser (Chrome, Firefox, Safari, etc.)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/golf-score-tracker.git
   cd golf-score-tracker
   ```

2. **Install required packages**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Start MongoDB**
   Make sure MongoDB is running on your system.
   ```bash
   # Check MongoDB status (on Linux)
   sudo systemctl status mongod
   
   # Start MongoDB if not running
   sudo systemctl start mongod
   ```

4. **Run the backend server**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```
   The API will be available at `http://localhost:8000`

5. **Open the frontend**
   Open `frontend/index.html` in your web browser, or serve it using a simple HTTP server:
   ```bash
   cd frontend
   python -m http.server
   ```
   Then open `http://localhost:8000` in your browser.

## Usage Guide

### Creating an Account
1. Open the application in your browser
2. Click "Sign Up" to create a new account
3. Fill in the registration form with username, email, and password
4. Click "Sign Up" to create your account
5. Log in with your new credentials

### Adding a New Round
1. After logging in, click the "New Round" button in the top right corner
2. Enter the course name, date played, and weather conditions
3. Input scores for each hole (front nine and back nine)
4. Add optional notes about your round
5. Click "Save Scorecard"

### Viewing Statistics
1. Navigate to "Statistics" in the sidebar
2. View your average score relative to par
3. See your best round performance
4. Analyze your score trends over time

### Filtering Scorecards
1. Use the course dropdown to filter by specific golf courses
2. Filter by date range (last month, last 3 months, last year)
3. Use the search bar to find specific notes or course names

## Project Structure
```
golf-score-tracker/
├── backend/
│   ├── main.py            # FastAPI application with MongoDB integration
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── index.html         # Main application dashboard
│   ├── login.html         # User login page
│   ├── signup.html        # User registration page
│   ├── styles.css         # CSS styling
│   └── script.js          # JavaScript functionality with auth
└── README.md              # Project documentation
```

## Technologies Used
- **Backend**: FastAPI, PyMongo, Pydantic, Passlib
- **Database**: MongoDB
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Chart.js
- **Date Picker**: Flatpickr
- **Icons**: Font Awesome

## Security Features
- Password hashing with bcrypt
- Session-based authentication
- Protected API endpoints
- User-specific data isolation

## License
This project is licensed under the MIT License - see the LICENSE file for details.



<img width="1800" alt="Screenshot 2025-04-23 at 9 21 07 PM" src="https://github.com/user-attachments/assets/7f2d0562-d4f3-49da-9bea-669741546e03" />

