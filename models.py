from datetime import datetime, timedelta
import random
import json
from app import db

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
    profile_image = db.Column(db.String(255))  # Path to profile image
    
    # Fan profile data
    events_attended = db.Column(db.Text)  # JSON list of events
    purchases = db.Column(db.Text)  # JSON list of purchases
    fan_badge = db.Column(db.String(50))  # Super Fã, Fã Casual, etc.
    
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

class Match(db.Model):
    """Representa uma partida de FURIA para o Bolão"""
    id = db.Column(db.Integer, primary_key=True)
    opponent = db.Column(db.String(100), nullable=False)  # Time adversário
    game = db.Column(db.String(50), nullable=False)  # CS:GO, Valorant, etc.
    tournament = db.Column(db.String(100))  # Torneio/campeonato
    match_time = db.Column(db.DateTime, nullable=False)  # Data e hora da partida
    format = db.Column(db.String(50))  # BO1, BO3, BO5
    map_pool = db.Column(db.Text)  # JSON com os mapas possíveis
    status = db.Column(db.String(20), default='scheduled')  # scheduled, live, completed, cancelled
    
    # Resultado (preenchido após a partida)
    furia_score = db.Column(db.Integer)
    opponent_score = db.Column(db.Integer)
    mvp = db.Column(db.String(100))  # Melhor jogador da FURIA
    opponent_highlight = db.Column(db.String(100))  # Destaque do time adversário
    
    # Meta
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    predictions = db.relationship('MatchPrediction', backref='match', lazy=True)
    
    @property
    def is_predictable(self):
        """Verifica se a partida ainda pode receber palpites (mais de 5min para começar)"""
        if self.status != 'scheduled':
            return False
        return datetime.utcnow() < (self.match_time - timedelta(minutes=5))
    
    @property
    def time_until_match(self):
        """Retorna o tempo restante até a partida em formato legível"""
        if self.match_time < datetime.utcnow():
            return "Partida em andamento ou finalizada"
            
        delta = self.match_time - datetime.utcnow()
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {seconds}s"
    
    @property
    def formatted_date(self):
        """Retorna a data formatada em pt-BR"""
        months = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        weekdays = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        
        weekday = weekdays[self.match_time.weekday()]
        day = self.match_time.day
        month = months[self.match_time.month - 1]
        year = self.match_time.year
        time = self.match_time.strftime("%H:%M")
        
        return f"{weekday}, {day} de {month} • {time}"

class MatchPrediction(db.Model):
    """Representa um palpite de um usuário em uma partida"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    
    # Previsão do usuário
    furia_score = db.Column(db.Integer, nullable=False)
    opponent_score = db.Column(db.Integer, nullable=False)
    predicted_mvp = db.Column(db.String(100))  # Palpite de quem será o MVP da FURIA
    predicted_opponent_highlight = db.Column(db.String(100))  # Palpite do destaque adversário
    
    # Pontuação do palpite (calculada após a partida)
    score_prediction_points = db.Column(db.Integer, default=0)  # +3 para placar exato, +1 para vencedor certo
    mvp_prediction_points = db.Column(db.Integer, default=0)  # +2 para MVP correto
    highlight_prediction_points = db.Column(db.Integer, default=0)  # +1 para destaque adversário correto
    total_points = db.Column(db.Integer, default=0)  # Soma dos pontos
    
    # Meta
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Referência para a relação reversa do User
    user = db.relationship('User', backref=db.backref('match_predictions', lazy=True))
