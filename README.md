# IDEH

# Flask Application with PostgreSQL, LangChain, and Social Login

## Overview
This is a Flask web application that integrates PostgreSQL with Flask-SQLAlchemy, provides social login using Google OAuth, implements LangChain for prompt-based interactions, and includes a web scraping feature. Key features include PostgreSQL integration for data storage, Google OAuth authentication via Flask-Dance, web scraping, LangChain for prompt-based responses, and CRUD APIs for scraped data and prompts. The app is also containerized using Docker.

## Prerequisites
Before running the application, ensure you have the following:
- Python 3.x
- PostgreSQL
- Docker (optional, for containerization)

## Installation
To set up the project:

```bash
1. Clone the Repository  
   Clone this repository to your local machine:  
   git clone https://github.com/yourusername/your-repository.git  
   cd your-repository  

2. Set Up Virtual Environment  
   Create and activate a virtual environment:  
   python3 -m venv venv  
   source venv/bin/activate  # On Windows, use venv\Scripts\activate  

3. Install Dependencies  
   Install the required Python packages:  
   pip install -r requirements.txt  

4. Configure Environment Variables  
   Create a `.env` file in the root of the project and add the following configuration:  
   DATABASE_URL=postgresql://username:password@localhost/dbname  
   SECRET_KEY=your_secret_key  
   GOOGLE_CLIENT_ID=your_google_client_id  
   GOOGLE_CLIENT_SECRET=your_google_client_secret  

5. Set Up PostgreSQL Database  
   Make sure you have PostgreSQL installed and create a database named `yourdb` or configure it as per your `.env` settings.

6. Run the Application  
   Run the Flask development server:  
   python app.py  
   The app should now be accessible at http://localhost:5000.


