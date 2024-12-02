
# Web Scraping and Social Login Flask App

This project is a web scraping Flask application that allows users to log in via Google OAuth, scrape content from URLs, and manage their scraped data through a dashboard. It stores scraped data and user logs in a PostgreSQL database and provides an intuitive web interface for users to interact with their data.

## Features

- **Social Login**: Users can log in via Google OAuth.
- **Web Scraping**: Users can enter a URL to scrape content such as text, metadata (title, description), and more.
- **User Dashboard**: Users can view, edit, and delete their scraped data and prompts.
- **Database**: Scraped data, user profiles, and prompt logs are stored in a PostgreSQL database.
- **Frontend**: A responsive dashboard with Bootstrap for managing scraped content.

## Technologies Used

- **Flask**: A Python web framework for building the app.
- **Flask-SQLAlchemy**: ORM for managing PostgreSQL database interactions.
- **Flask-Dance**: Used for Google OAuth integration.
- **Flask-Login**: For managing user sessions and authentication.
- **BeautifulSoup**: For web scraping content from URLs.
- **PostgreSQL**: Database for storing user data and scraped content.
- **Bootstrap**: For styling the frontend.

### Key Libraries Used:
1. **Flask**: Web framework for building the application.
2. **Flask-SQLAlchemy**: ORM for database interaction, storing user and scraped data.
3. **Flask-Dance (Google OAuth)**: Handles user authentication via Google social login.
4. **Flask-Login**: Manages user sessions and authentication.
5. **Requests & BeautifulSoup**: Used for scraping web content.
6. **LangChain**: AI tool for processing natural language tasks.
   - **OpenAI (GPT-3)**: LLM (Large Language Model) used for generating content.
   - **ConversationChain**: For conversational agents.
   - **PromptTemplate**: Creates prompts for GPT-3 to generate AI responses.

## Prerequisites

Before running the app, make sure you have the following:

1. Python 3.x installed
2. Docker and Docker Compose (for easy deployment)
3. PostgreSQL database setup (handled through Docker Compose)

### Required Python Libraries

You can install the necessary Python libraries by running:

```bash
pip install -r requirements.txt
```

The `requirements.txt` file contains the following:

```
Flask==2.3.0
Flask-SQLAlchemy==3.0.0
Flask-Dance==5.0.0
Flask-Login==0.6.2
requests==2.28.1
beautifulsoup4==4.12.0
langchain==0.0.2
psycopg2==2.9.3
python-dotenv==0.19.2
```

## Environment Variables

Create a `.env` file in the root of the project and add the following variables:

```
DATABASE_URL=postgresql://username:password@db:5432/yourdb
SECRET_KEY=your_secret_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

Make sure to replace the placeholder values with your actual credentials and secrets.

## Running the App

### 1. **Set Up Docker**

You can use Docker to run the app and its PostgreSQL database. Ensure Docker and Docker Compose are installed, then run:

```bash
docker-compose up --build
```

This will build the Docker image and run both the web app and PostgreSQL database in separate containers.

### 2. **Accessing the Application**

Once the containers are up and running, access the application at:

```
http://localhost:5000
```

### 3. **Database Migration**

Before running the app, you need to initialize the database. You can do this by running the following in the Python shell after setting up the environment:

```python
from app import db
db.create_all()
```

This command will create the necessary database tables for the `User`, `ScrapedData`, and `PromptLog` models.

## Endpoints

- **`/google`**: Initiates Google OAuth login.
- **`/`**: Dashboard, accessible after login, shows scraped URLs, prompts, and logs.
- **`/scrape`**: Endpoint to post a URL and scrape its content.
- **`/scraped_data/edit/<id>`**: Edit a specific scraped data entry.
- **`/scraped_data/delete/<id>`**: Delete a specific scraped data entry.
- **`/prompt_log/edit/<id>`**: Edit a specific prompt log entry.
- **`/prompt_log/delete/<id>`**: Delete a specific prompt log entry.

## Frontend

The frontend uses **Bootstrap** for a simple, responsive design. The dashboard displays the user's scraped data and prompts with options to edit or delete entries.

### Dashboard Features

- View a list of scraped data with metadata.
- View a list of prompt logs and generated outputs.
- Edit or delete scraped data and prompts.

## Deployment

### Docker Deployment

The app is containerized using Docker. The following steps help in deploying the app in a production environment using Docker:

1. **Build the Docker Image**:
    ```bash
    docker build -t flask-scraper .
    ```

2. **Run the Containers** using Docker Compose:
    ```bash
    docker-compose up --build
    ```

3. **Access the App**: The app will be available on `http://localhost:5000`.

### Google OAuth Setup

You need to set up OAuth credentials for Google login. To do this, go to the [Google Developer Console](https://console.developers.google.com/), create a new project, and enable the Google+ API. After that, set up OAuth 2.0 credentials for your app.

- Use `http://localhost:5000/google` as the redirect URI.
- Copy the `client_id` and `client_secret` and update them in the `.env` file.

## Troubleshooting

- **If the app doesn't start**: Ensure your `.env` file is correctly configured and the database is set up.
- **Database errors**: Make sure the PostgreSQL container is running correctly. Check Docker logs for errors.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---


