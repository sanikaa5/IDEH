from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import LoginManager, login_user, current_user, login_required
import os
import requests
from bs4 import BeautifulSoup
from langchain.chains import ConversationChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

# Initialize the Flask app and setup config
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/yourdb')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db = SQLAlchemy(app)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)

# Google OAuth Setup
google_bp = make_google_blueprint(client_id=os.getenv('GOOGLE_CLIENT_ID'),
                                   client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
                                   redirect_to='google_login')
app.register_blueprint(google_bp, url_prefix='/google_login')

# Models for database
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
    try:
        if not google.authorized:
            return redirect(url_for('google.login'))
        user_info = google.get('/plus/v1/people/me')
        
        if not user_info.ok:
            return jsonify({'error': 'Failed to fetch user information from Google.'}), 400
        
        user = User.query.filter_by(email=user_info.json['emails'][0]['value']).first()
        if user is None:
            user = User(name=user_info.json['displayName'],
                        email=user_info.json['emails'][0]['value'])
            db.session.add(user)
            db.session.commit()
        login_user(user)
        return redirect(url_for('dashboard'))
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/')
@login_required
def dashboard():
    scraped_data = ScrapedData.query.filter_by(created_by_user_id=current_user.id).all()
    prompt_logs = PromptLog.query.filter_by(created_by_user_id=current_user.id).all()
    return render_template('dashboard.html', scraped_data=scraped_data, prompt_logs=prompt_logs)

@app.route('/scrape', methods=['POST'])
@login_required
def scrape_url():
    try:
        url = request.form['url']
        if not url or not url.startswith("http"):
            return jsonify({'error': 'Please provide a valid URL.'}), 400
        
        scraped_data = scrape_content(url)
        
        if not scraped_data['content']:
            return jsonify({'error': 'Failed to scrape content from the provided URL.'}), 400
        
        new_scraped_data = ScrapedData(url=url, content=scraped_data['content'], metadata=scraped_data['metadata'], created_by_user_id=current_user.id)
        db.session.add(new_scraped_data)
        db.session.commit()
        return jsonify({'message': 'Data scraped successfully'}), 200
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Scraping failed due to a network error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

def scrape_content(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string if soup.title else 'No title'
        description = soup.find('meta', attrs={'name': 'description'})
        description = description['content'] if description else 'No description available'

        content = soup.get_text(strip=True)
        metadata = {
            'title': title,
            'description': description,
            'url': url
        }
        return {'content': content, 'metadata': metadata}
    except requests.exceptions.RequestException as e:
        return {'content': '', 'metadata': {'error': str(e)}}
    except Exception as e:
        return {'content': '', 'metadata': {'error': str(e)}}

@app.route('/scraped_data/edit/<int:scraped_data_id>', methods=['GET', 'POST'])
@login_required
def edit_scraped_data(scraped_data_id):
    scraped_data = ScrapedData.query.get_or_404(scraped_data_id)
    if request.method == 'POST':
        scraped_data.url = request.form['url']
        scraped_data.content = request.form['content']
        scraped_data.metadata = request.form['metadata']
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('edit_scraped_data.html', scraped_data=scraped_data)

@app.route('/scraped_data/delete/<int:scraped_data_id>', methods=['GET'])
@login_required
def delete_scraped_data(scraped_data_id):
    scraped_data = ScrapedData.query.get_or_404(scraped_data_id)
    db.session.delete(scraped_data)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/prompt_log/edit/<int:prompt_log_id>', methods=['GET', 'POST'])
@login_required
def edit_prompt_log(prompt_log_id):
    prompt_log = PromptLog.query.get_or_404(prompt_log_id)
    if request.method == 'POST':
        prompt_log.prompt_text = request.form['prompt_text']
        prompt_log.generated_output = request.form['generated_output']
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('edit_prompt_log.html', prompt_log=prompt_log)

@app.route('/prompt_log/delete/<int:prompt_log_id>', methods=['GET'])
@login_required
def delete_prompt_log(prompt_log_id):
    prompt_log = PromptLog.query.get_or_404(prompt_log_id)
    db.session.delete(prompt_log)
    db.session.commit()
    return redirect(url_for('dashboard'))

# LangChain Example Endpoint (for generating prompt responses)
@app.route('/generate_prompt_response', methods=['POST'])
@login_required
def generate_prompt_response():
    try:
        prompt_text = request.form['prompt_text']
        
        if not prompt_text:
            return jsonify({'error': 'Prompt text is required.'}), 400

        # Initialize LangChain's OpenAI model (requires OpenAI API key in .env file)
        llm = OpenAI(model="text-davinci-003")
        conversation = ConversationChain(llm=llm)
        
        response = conversation.run(input=prompt_text)
        
        # Log the prompt and response
        new_prompt_log = PromptLog(prompt_text=prompt_text, generated_output=response, created_by_user_id=current_user.id)
        db.session.add(new_prompt_log)
        db.session.commit()

        return jsonify({'response': response}), 200
    except Exception as e:
        return jsonify({'error': f'Error generating prompt response: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
