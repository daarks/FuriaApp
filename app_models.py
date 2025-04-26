from datetime import datetime
from app_main import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Fan profile data
    events_attended = db.Column(db.Text)  # JSON list of events
    purchases = db.Column(db.Text)  # JSON list of purchases
    fan_badge = db.Column(db.String(50))  # Super Fã, Fã Intermediário, Novato, etc.
    
    # Player match data
    player_match = db.Column(db.String(100))  # Name of FURIA player match
    player_bio = db.Column(db.Text)  # Bio of matched player
    player_image = db.Column(db.String(255))  # URL/path to player image
    
    # Quiz data
    quiz_score = db.Column(db.Integer)
    quiz_level = db.Column(db.String(50))  # Expert, Intermediate, Casual
    
    # Lootbox data
    last_lootbox_date = db.Column(db.Date)
    lootbox_rewards = db.Column(db.Text)  # JSON list of rewards
    
    # Relationships
    interests = db.relationship('UserInterest', backref='user', lazy=True)
    documents = db.relationship('Document', backref='user', lazy=True)
    social_media = db.relationship('SocialMedia', backref='user', lazy=True)
    content_links = db.relationship('ContentLink', backref='user', lazy=True)
    quiz_results = db.relationship('Quiz', backref='user', lazy=True)
    calendar_favorites = db.relationship('Calendar', backref='user', lazy=True)

class UserInterest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    interest = db.Column(db.String(100), nullable=False)
    
    # Meta
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    document_type = db.Column(db.String(20), nullable=False)  # RG, CNH, etc.
    file_path = db.Column(db.String(255), nullable=False)
    validation_status = db.Column(db.String(20), nullable=False)  # pending, verified, rejected
    validation_data = db.Column(db.Text)  # JSON with OCR data
    
    # Meta
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SocialMedia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    twitter = db.Column(db.String(255))
    instagram = db.Column(db.String(255))
    twitch = db.Column(db.String(255))
    youtube = db.Column(db.String(255))
    facebook = db.Column(db.String(255))
    
    # Analysis data
    engagement_score = db.Column(db.Float)
    hashtags = db.Column(db.Text)  # JSON list of hashtags
    interactions = db.Column(db.Text)  # JSON data about interactions
    
    # Meta
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContentLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    content_type = db.Column(db.String(50))  # article, video, profile
    relevance_score = db.Column(db.Float)
    keywords = db.Column(db.Text)  # JSON list of keywords
    
    # Meta
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    fan_level = db.Column(db.String(50), nullable=False)  # Expert, Intermediate, Casual
    
    # Meta
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Calendar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.String(100), nullable=False)  # ID of the esports event
    is_favorite = db.Column(db.Boolean, default=False)
    
    # Meta
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# New models for tournament data

class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(50))
    location = db.Column(db.String(100))
    prize_pool = db.Column(db.String(50))
    source = db.Column(db.String(50), default='hltv')  # Source of data
    
    # Meta
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    matches = db.relationship('Match', backref='tournament', lazy=True)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    logo_url = db.Column(db.String(255))
    country = db.Column(db.String(50))
    
    # Meta
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    players = db.relationship('Player', backref='team', lazy=True)
    matches_team1 = db.relationship('Match', backref='team1', foreign_keys='Match.team1_id', lazy=True)
    matches_team2 = db.relationship('Match', backref='team2', foreign_keys='Match.team2_id', lazy=True)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(100), nullable=False)
    real_name = db.Column(db.String(100))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    country = db.Column(db.String(50))
    photo_url = db.Column(db.String(255))
    bio = db.Column(db.Text)
    
    # Meta
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team1_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    team2_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    score1 = db.Column(db.String(10))
    score2 = db.Column(db.String(10))
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    match_date = db.Column(db.String(50))
    map = db.Column(db.String(50))
    
    # Meta
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)