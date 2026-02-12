CampusConnect

CampusConnect is a Flask-based web application that helps students find teammates and connect with peers based on shared interests and goals.

Features

User registration and login system

Profile creation with skills and interests

Teammate matching system

Profile viewing

Clean dashboard interface

Tech Stack

Python

Flask

Flask-Login

Flask-SQLAlchemy

SQLite

HTML / CSS

Project Structure
campus_connect/
│
├── app.py
├── models.py
├── requirements.txt
├── Procfile
│
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── profile.html
│
└── static/

Important Notes

The following files and folders are intentionally excluded from the repository:

venv/ or .venv/ (virtual environment)

instance/

database.db

static/uploads/

__pycache__/


These are either environment-specific or auto-generated files.

To run this project locally, create a virtual environment and install dependencies using:

pip install -r requirements.txt

Running the App Locally

Create a virtual environment

Install dependencies



Run:

python app.py




The application will start on:

http://127.0.0.1:5000



Deployment

This project is prepared for deployment using Gunicorn with the following start command:

gunicorn app:app
