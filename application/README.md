# Ekam Apps Assessment: QuickDocs

## Overview

QuickDocs is a Flask-powered document intelligence platform designed for streamlined workflow and smart data interaction. It allows quick user registration, efficient document handling, and Natural Language Processing (NLP) to extract insights from stored content. With a responsive interface and a scalable backend, QuickDocs is built to make document-driven processes faster, smarter, and easier to manage.

---

## Features

- User Registration & Assignment – Quickly add new users and link them to relevant processes.
- Document Upload & Management – Store, organize, and access files with minimal effort.
- Process Tracking Dashboard – Monitor workflow progress in a clear, structured view.
- NLP-Powered Queries – Search and analyze documents using natural language commands.
- Error-Resilient Query Handling – Smart handling of incomplete or unclear search requests.
- Responsive UI – HTML, CSS, and JavaScript interface optimized for seamless use across devices.

---
## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/jan257/Ekam_Apps_Submission-QuickDocs.git
   cd Ekam_Apps_assessment/application
   ```

2. **Create and Activate a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up the Database**
   - Create a database using your preferred SQL database engine.
   - Run the schema script:
     ```bash
     mysql -u <username> -p <database_name> < ../database/schema.sql
     ```
   - (Optional) Load sample data:
     ```bash
     mysql -u <username> -p <database_name> < ../database/sample_data.sql
     ```

5. **Configure Environment Variables**
   - Create a `.env` file in the `application` directory.
   - Add configuration values like:
     ```env
        SECRET_KEY=------------
        DB_HOST=------------
        DB_USER=-------------
        DB_PASSWORD=---------
        DB_NAME=-----------
     ```

---

## How to Run the Application

1. Activate your virtual environment:
   ```bash
   source venv/bin/activate  # On Windows use venv\Scripts\activate
   ```

2. Start the Flask application:
- (If in root dir)
   ```bash
   python -m application.app.py
   ```
- OR
```bash
   cd application
   python app.py
```

3. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## API Keys Needed
- **Secret Key**: Required for flash sessions.
- **Database Credentials**: Required to connect to your SQL database.

*(Do not commit actual keys to version control.)*

---

## Technologies Used
- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **Database**: MySQL (or compatible SQL database)
- **NLP**: Rule-based approach
- **Other Tools**: Jinja2 Templates

---

## Screenshots
Screenshots of the application are available in the `application/screenshots` directory.

---

## Author: 

**Jahnavi P**  
📍 Bangalore, India  
🔗 [LinkedIn](https://www.linkedin.com/in/jahnavi-p-a68788233) 

---

