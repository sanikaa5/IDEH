import os
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import LoginManager, login_user, current_user
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Initialize Flask app and set up config
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/yourdb')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Secret key for session management
db = SQLAlchemy(app)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)

# Google OAuth Setup (Social Login)
google_bp = make_google_blueprint(client_id=os.getenv('GOOGLE_CLIENT_ID'),
                                   client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
                                   redirect_to='google_login')
app.register_blueprint(google_bp, url_prefix='/google_login')

# LangChain Setup for OpenAI
llm = OpenAI(model="text-davinci-003", temperature=0.7)

# Create a Prompt Template for LangChain
prompt_template = """
Write a brief summary for the following content:

{content}
"""
prompt = PromptTemplate(input_variables=["content"], template=prompt_template)
chain = LLMChain(llm=llm, prompt=prompt)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    social_login_provider = db.Column(db.String(50))
    profile_picture = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class ScrapedData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255))
    content = db.Column(db.Text)
    metadata = db.Column(db.JSON)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class PromptLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt_text = db.Column(db.Text)
    generated_output = db.Column(db.Text)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Routes
@app.route('/google')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    
    # Fetch user information from Google API
    user_info = google.get('/plus/v1/people/me')
    user = User.query.filter_by(email=user_info.json['emails'][0]['value']).first()
    
    if user is None:
        # Create new user if not in the database
        user = User(
            name=user_info.json['displayName'],
            email=user_info.json['emails'][0]['value'],
            profile_picture=user_info.json['image']['url']
        )
        db.session.add(user)
        db.session.commit()

    # Log the user in
    login_user(user)
    return redirect(url_for('dashboard'))

@app.route('/')
def dashboard():
    if current_user.is_authenticated:
        # Fetch scraped data for the logged-in user
        scraped_data = ScrapedData.query.filter_by(created_by_user_id=current_user.id).all()
        return render_template('dashboard.html', scraped_data=scraped_data)
    return redirect(url_for('google.login'))

@app.route('/scrape', methods=['POST'])
def scrape_url():
    url = request.form['url']
    # Logic for web scraping (simplified)
    scraped_data = ScrapedData(url=url, content="Scraped Content", metadata={"title": "Title"})
    db.session.add(scraped_data)
    db.session.commit()

    # Use LangChain to summarize the scraped content
    generated_summary = chain.run(content=scraped_data.content)

    # Log the prompt and generated output
    prompt_log = PromptLog(
        prompt_text=f"Summary for: {scraped_data.content}",
        generated_output=generated_summary,
        created_by_user_id=current_user.id
    )
    db.session.add(prompt_log)
    db.session.commit()

    return jsonify({'message': 'Data scraped and summarized successfully', 'summary': generated_summary})

if __name__ == '__main__':
    app.run(debug=True)
