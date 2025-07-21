# Execution Form Full Stack App

## Overview
This project digitizes and manages NYC Transit Exception Claim Forms. It includes a Flask backend and a React frontend.

## Project Structure
```
Execution-Form-Backend/
  app.py           # Flask backend
  db.py            # Database logic
  model.py         # ML model for field classification
  exception_codes.py
  add_users.py     # Script to add users
  users.db, forms.db # SQLite databases
  uploads/         # Uploaded files
  frontend/        # React frontend (after renaming)
```

## Setup Instructions

### 1. Backend (Flask)
- Create and activate a virtual environment:
  ```sh
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- Install dependencies:
  ```sh
  pip install flask flask-cors scikit-learn pytesseract opencv-python pillow
  ```
- Run the backend:
  ```sh
  python app.py
  ```
- The backend will run at `http://localhost:5000`

### 2. Frontend (React)
- Rename your frontend folder:
  ```sh
  mv "Exception-Form-App-main copy" frontend
  ```
- Install dependencies:
  ```sh
  cd frontend
  npm install
  ```
- Run the frontend:
  ```sh
  npm start
  ```
- The frontend will run at `http://localhost:3000`

### 3. Adding Users
- Use `add_users.py` to add users to the database:
  ```sh
  python add_users.py
  ```
- Edit the `users` list in `add_users.py` to add more users.

### 4. Notes
- Registration is disabled; only pre-created users can log in.
- All API calls in the frontend should use `http://localhost:5000` as the base URL.
- For production, use a WSGI server for Flask and build the React app.

---

For any issues, please check the backend and frontend logs, and ensure both servers are running. 