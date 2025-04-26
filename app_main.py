import os
import logging
from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup
import trafilatura
from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create database base class
class Base(DeclarativeBase):
    pass

# Initialize Flask app and database
db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure PostgreSQL database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure file uploads
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB limit
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Initialize extensions
db.init_app(app)

# Import models after db is initialized
with app.app_context():
    from app_models import User, UserInterest, Document, SocialMedia, ContentLink, Tournament, Match, Team, Player
    from app_forms import (
        RegistrationForm, LoginForm, DocumentUploadForm, SocialMediaForm, 
        ContentValidationForm, QuizForm
    )
    
    db.create_all()

# Utility function to fetch HLTV tournament data
def fetch_hltv_results():
    try:
        url = "https://www.hltv.org/results"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Extract tournament results
            result_containers = soup.select('.result-con')
            
            for result in result_containers:
                match_data = {}
                
                # Get teams
                teams = result.select('.team')
                if len(teams) >= 2:
                    match_data['team1'] = teams[0].text.strip()
                    match_data['team2'] = teams[1].text.strip()
                
                # Get scores
                scores = result.select('.score-cell')
                if len(scores) >= 1:
                    score_text = scores[0].text.strip()
                    if '-' in score_text:
                        score_parts = score_text.split('-')
                        match_data['score1'] = score_parts[0].strip()
                        match_data['score2'] = score_parts[1].strip()
                
                # Get event name
                event = result.select('.event-name')
                if event:
                    match_data['event'] = event[0].text.strip()
                
                # Get match date
                date = result.select('.date')
                if date:
                    match_data['date'] = date[0].text.strip()
                
                if match_data:
                    results.append(match_data)
            
            return results
        else:
            app.logger.error(f"Failed to fetch HLTV results: {response.status_code}")
            return []
    
    except Exception as e:
        app.logger.error(f"Error fetching HLTV results: {str(e)}")
        return []

# Save tournaments to database
def update_tournament_data():
    results = fetch_hltv_results()
    
    with app.app_context():
        for result in results:
            if 'event' in result and 'date' in result:
                # Check if tournament exists
                tournament = Tournament.query.filter_by(name=result['event']).first()
                if not tournament:
                    tournament = Tournament(
                        name=result['event'],
                        date=result.get('date'),
                        source='hltv'
                    )
                    db.session.add(tournament)
                
                # Add teams if they don't exist
                if 'team1' in result:
                    team1 = Team.query.filter_by(name=result['team1']).first()
                    if not team1:
                        team1 = Team(name=result['team1'])
                        db.session.add(team1)
                
                if 'team2' in result:
                    team2 = Team.query.filter_by(name=result['team2']).first()
                    if not team2:
                        team2 = Team(name=result['team2'])
                        db.session.add(team2)
                
                db.session.commit()
                
                # Add match if it doesn't exist
                if 'team1' in result and 'team2' in result and 'score1' in result and 'score2' in result:
                    team1 = Team.query.filter_by(name=result['team1']).first()
                    team2 = Team.query.filter_by(name=result['team2']).first()
                    tournament = Tournament.query.filter_by(name=result['event']).first()
                    
                    match = Match.query.filter_by(
                        team1_id=team1.id,
                        team2_id=team2.id,
                        tournament_id=tournament.id,
                        match_date=result.get('date')
                    ).first()
                    
                    if not match:
                        match = Match(
                            team1_id=team1.id,
                            team2_id=team2.id, 
                            score1=result['score1'],
                            score2=result['score2'],
                            tournament_id=tournament.id,
                            match_date=result.get('date')
                        )
                        db.session.add(match)
                
                db.session.commit()

# API Routes
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        session['user_id'] = user.id
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'fan_badge': user.fan_badge if user.fan_badge else "New Fan"
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    required_fields = ['name', 'email', 'password', 'address', 'cpf', 'birth_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
    
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'success': False, 'message': 'Email already registered'}), 400
    
    try:
        # Create the user
        user = User(
            name=data['name'],
            email=data['email'],
            address=data['address'],
            cpf=data['cpf'],
            birth_date=datetime.strptime(data['birth_date'], '%Y-%m-%d').date(),
            password_hash=generate_password_hash(data['password'])
        )
        db.session.add(user)
        db.session.commit()
        
        # Add user interests
        if 'interests' in data and isinstance(data['interests'], list):
            for interest in data['interests']:
                user_interest = UserInterest(user_id=user.id, interest=interest)
                db.session.add(user_interest)
        
        # Add esports events attended
        if 'events_attended' in data and isinstance(data['events_attended'], list):
            user.events_attended = json.dumps(data['events_attended'])
        
        # Add purchases
        if 'purchases' in data and isinstance(data['purchases'], list):
            user.purchases = json.dumps(data['purchases'])
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Registration successful!', 'user_id': user.id})
    
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Registration error: {str(e)}")
        return jsonify({'success': False, 'message': f'Registration failed: {str(e)}'}), 500

@app.route('/api/user_profile', methods=['GET'])
def api_profile():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    try:
        user = User.query.get(session['user_id'])
        if not user:
            session.pop('user_id', None)
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Get user interests
        interests = UserInterest.query.filter_by(user_id=user.id).all()
        interests_list = [interest.interest for interest in interests]
        
        # Get document verification status
        document = Document.query.filter_by(user_id=user.id).first()
        document_status = {
            'has_document': document is not None,
            'status': document.validation_status if document else None
        }
        
        # Get social media profiles
        social_media = SocialMedia.query.filter_by(user_id=user.id).first()
        social_media_data = None
        if social_media:
            social_media_data = {
                'twitter': social_media.twitter,
                'instagram': social_media.instagram,
                'twitch': social_media.twitch,
                'youtube': social_media.youtube,
                'facebook': social_media.facebook,
                'engagement_score': social_media.engagement_score
            }
        
        # Get fan badge
        fan_badge = user.fan_badge if user.fan_badge else "New Fan"
        
        # Prepare user data response
        user_data = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'address': user.address,
            'cpf': user.cpf,
            'birth_date': user.birth_date.strftime('%Y-%m-%d'),
            'registration_date': user.registration_date.strftime('%Y-%m-%d'),
            'last_login': user.last_login.strftime('%Y-%m-%d') if user.last_login else None,
            'events_attended': json.loads(user.events_attended) if user.events_attended else [],
            'purchases': json.loads(user.purchases) if user.purchases else [],
            'fan_badge': fan_badge,
            'player_match': user.player_match,
            'player_bio': user.player_bio,
            'player_image': user.player_image,
            'quiz_score': user.quiz_score,
            'quiz_level': user.quiz_level,
            'interests': interests_list,
            'document': document_status,
            'social_media': social_media_data,
        }
        
        return jsonify({'success': True, 'user': user_data})
    
    except Exception as e:
        app.logger.error(f"Error in profile route: {str(e)}")
        return jsonify({'success': False, 'message': 'Error retrieving profile'}), 500

@app.route('/api/tournaments', methods=['GET'])
def api_tournaments():
    try:
        tournaments = Tournament.query.all()
        tournament_list = []
        
        for tournament in tournaments:
            tournament_data = {
                'id': tournament.id,
                'name': tournament.name,
                'date': tournament.date,
                'location': tournament.location,
                'prize_pool': tournament.prize_pool
            }
            tournament_list.append(tournament_data)
        
        return jsonify({'success': True, 'tournaments': tournament_list})
    
    except Exception as e:
        app.logger.error(f"Error fetching tournaments: {str(e)}")
        return jsonify({'success': False, 'message': 'Error fetching tournaments'}), 500

@app.route('/api/matches', methods=['GET'])
def api_matches():
    try:
        matches = Match.query.all()
        match_list = []
        
        for match in matches:
            team1 = Team.query.get(match.team1_id)
            team2 = Team.query.get(match.team2_id)
            tournament = Tournament.query.get(match.tournament_id)
            
            match_data = {
                'id': match.id,
                'team1': team1.name if team1 else "Unknown",
                'team2': team2.name if team2 else "Unknown",
                'score1': match.score1,
                'score2': match.score2,
                'tournament': tournament.name if tournament else "Unknown",
                'date': match.match_date
            }
            match_list.append(match_data)
        
        return jsonify({'success': True, 'matches': match_list})
    
    except Exception as e:
        app.logger.error(f"Error fetching matches: {str(e)}")
        return jsonify({'success': False, 'message': 'Error fetching matches'}), 500

@app.route('/api/update_data', methods=['GET'])
def api_update_data():
    try:
        update_tournament_data()
        return jsonify({'success': True, 'message': 'Data updated successfully'})
    except Exception as e:
        app.logger.error(f"Error updating data: {str(e)}")
        return jsonify({'success': False, 'message': 'Error updating data'}), 500

# Additional routes for document validation, social media linking, etc.
@app.route('/api/validate_document', methods=['POST'])
def api_validate_document():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    if 'document' not in request.files:
        return jsonify({'success': False, 'message': 'No document file provided'}), 400
    
    document_type = request.form.get('document_type')
    if not document_type:
        return jsonify({'success': False, 'message': 'No document type provided'}), 400
    
    user = User.query.get(session['user_id'])
    document_file = request.files['document']
    filename = secure_filename(document_file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"user_{user.id}_{filename}")
    document_file.save(file_path)
    
    # Simulate document validation with OCR/AI
    # In a real app, this would use a proper OCR service
    validation_status = "verified"
    validation_message = "Document verified successfully"
    validation_data = {
        "name_match": True,
        "cpf_match": True,
        "expiry_check": "valid",
        "authenticity": "valid"
    }
    
    # Save document record
    document = Document.query.filter_by(user_id=user.id).first()
    if document:
        document.file_path = file_path
        document.document_type = document_type
        document.validation_status = validation_status
        document.validation_data = json.dumps(validation_data)
    else:
        document = Document(
            user_id=user.id,
            file_path=file_path,
            document_type=document_type,
            validation_status=validation_status,
            validation_data=json.dumps(validation_data)
        )
        db.session.add(document)
    
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'status': validation_status, 
        'message': validation_message,
        'data': validation_data
    })

@app.route('/api/social_media', methods=['POST'])
def api_social_media():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    data = request.json
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    user = User.query.get(session['user_id'])
    
    # Extract social media links
    social_media_data = {
        'twitter': data.get('twitter', ''),
        'instagram': data.get('instagram', ''),
        'twitch': data.get('twitch', ''),
        'youtube': data.get('youtube', ''),
        'facebook': data.get('facebook', '')
    }
    
    # Simulate social media analysis
    # In a real app, this would use proper API integrations
    engagement_score = 75.5  # Percentage
    fan_badge = "Dedicated Fan"
    hashtags = ["FURIA", "CSGO", "esports", "gaming", "Brazil"]
    interactions = {
        "likes": 142,
        "comments": 34,
        "shares": 18,
        "followers_with_interests": 63,
        "esports_related_posts": 28
    }
    
    # Save social media data
    social_media = SocialMedia.query.filter_by(user_id=user.id).first()
    if social_media:
        social_media.twitter = social_media_data['twitter']
        social_media.instagram = social_media_data['instagram']
        social_media.twitch = social_media_data['twitch']
        social_media.youtube = social_media_data['youtube']
        social_media.facebook = social_media_data['facebook']
        social_media.engagement_score = engagement_score
        social_media.hashtags = json.dumps(hashtags)
        social_media.interactions = json.dumps(interactions)
    else:
        social_media = SocialMedia(
            user_id=user.id,
            twitter=social_media_data['twitter'],
            instagram=social_media_data['instagram'],
            twitch=social_media_data['twitch'],
            youtube=social_media_data['youtube'],
            facebook=social_media_data['facebook'],
            engagement_score=engagement_score,
            hashtags=json.dumps(hashtags),
            interactions=json.dumps(interactions)
        )
        db.session.add(social_media)
    
    # Update user fan badge
    user.fan_badge = fan_badge
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'fan_badge': fan_badge,
        'engagement_score': engagement_score,
        'hashtags': hashtags,
        'interactions': interactions
    })

@app.route('/api/content_validation', methods=['POST'])
def api_content_validation():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    data = request.json
    if not data or 'content_url' not in data:
        return jsonify({'success': False, 'message': 'No content URL provided'}), 400
    
    content_url = data['content_url']
    user = User.query.get(session['user_id'])
    
    # Simulate content validation with AI
    # In a real app, this would use proper content analysis
    try:
        # Attempt to fetch and analyze the content
        downloaded = trafilatura.fetch_url(content_url)
        content_text = trafilatura.extract(downloaded)
        
        # Simple keyword-based analysis
        esports_keywords = ["esports", "gaming", "tournament", "FURIA", "CS:GO", "fps", "competitive", "championship"]
        relevance_score = 0
        keyword_matches = []
        
        if content_text:
            content_lower = content_text.lower()
            for keyword in esports_keywords:
                if keyword.lower() in content_lower:
                    relevance_score += 12.5  # Each keyword adds 12.5%, max 100%
                    keyword_matches.append(keyword)
            
            relevance_score = min(relevance_score, 100)
        
        # Determine content type based on URL
        content_type = "article"
        if "youtube.com" in content_url or "youtu.be" in content_url:
            content_type = "video"
        elif "twitch.tv" in content_url:
            content_type = "stream"
        elif "twitter.com" in content_url or "x.com" in content_url:
            content_type = "tweet"
        
        # Save content link
        content_link = ContentLink(
            user_id=user.id,
            url=content_url,
            content_type=content_type,
            relevance_score=relevance_score,
            keywords=json.dumps(keyword_matches)
        )
        db.session.add(content_link)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'relevance_score': relevance_score,
            'content_type': content_type,
            'keywords': keyword_matches
        })
    
    except Exception as e:
        app.logger.error(f"Error validating content: {str(e)}")
        return jsonify({'success': False, 'message': f'Error validating content: {str(e)}'}), 500

# Serve the SPA
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_spa(path):
    return render_template('app.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)