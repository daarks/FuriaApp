import os
import logging
import random
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create database base class
class Base(DeclarativeBase):
    pass

# Initialize Flask app and database
db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///kyf.db")
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
csrf = CSRFProtect(app)

# Import models and forms
with app.app_context():
    from models import User, UserInterest, Document, SocialMedia, ContentLink, Quiz, Calendar, Match, MatchPrediction
    from forms import (
        RegistrationForm, LoginForm, DocumentUploadForm, SocialMediaForm, 
        ContentValidationForm, QuizForm, MatchPredictionForm
    )
    from utils import (
        validate_document, analyze_social_media, validate_content_links,
        match_player, get_fan_power, get_lootbox_reward, get_events_by_interests,
        generate_demo_matches, calculate_prediction_points, get_furia_players_by_game
    )
    
    db.create_all()

# Routes
@app.route('/')
def home():
    # Route principal diretamente para a página de login
    return render_template('app_login.html', form=LoginForm())

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered. Please login.', 'danger')
            return redirect(url_for('login'))
        
        try:
            # Check if user with this CPF already exists
            existing_cpf = User.query.filter_by(cpf=form.cpf.data).first()
            if existing_cpf:
                flash('CPF já cadastrado. Por favor, use outro CPF.', 'danger')
                return redirect(url_for('register'))
                
            # Create the user
            user = User(
                name=form.name.data,
                email=form.email.data,
                address=form.address.data,
                cpf=form.cpf.data,
                birth_date=form.birth_date.data,
                password_hash=generate_password_hash(form.password.data)
            )
            db.session.add(user)
            db.session.commit()
            
            # Add user interests
            interests = request.form.getlist('interests')
            for interest in interests:
                user_interest = UserInterest(user_id=user.id, interest=interest)
                db.session.add(user_interest)
            
            # Add esports events attended
            events = request.form.getlist('events')
            user.events_attended = json.dumps(events)
            
            # Add purchases
            purchases = request.form.getlist('purchases')
            user.purchases = json.dumps(purchases)
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error during registration: {str(e)}")
            flash('Erro durante o cadastro. Por favor, tente novamente.', 'danger')
            return redirect(url_for('register'))
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('app_register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            session['user_id'] = user.id
            user.last_login = datetime.now()
            db.session.commit()
            flash('Login successful!', 'success')
            return redirect(url_for('home_dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('app_login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/home')
def home_dashboard():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro.', 'warning')
        return redirect(url_for('login'))
    
    try:
        user = User.query.get(session['user_id'])
        if not user:
            session.pop('user_id', None)
            flash('Usuário não encontrado. Faça login novamente.', 'danger')
            return redirect(url_for('login'))
            
        # Buscar partidas futuras para o Bolão
        upcoming_matches = []
        try:
            # Verificar se temos partidas na base de dados
            matches = Match.query.order_by(Match.match_time).all()
            
            # Se não tiver, criar partidas de demonstração
            if not matches:
                # Gerar partidas de demonstração
                demo_matches = generate_demo_matches(8)  # Gerar 8 partidas
                for match_data in demo_matches:
                    match = Match(**match_data)
                    db.session.add(match)
                
                db.session.commit()
                matches = Match.query.order_by(Match.match_time).all()
            
            # Filtrar apenas partidas futuras
            now = datetime.now()
            upcoming_matches = [m for m in matches if m.match_time > now]
            
            # Ordenar por data/hora
            upcoming_matches.sort(key=lambda x: x.match_time)
        except Exception as e:
            app.logger.error(f"Erro ao buscar partidas para o dashboard: {str(e)}")
            # Não interromper o carregamento da página principal por causa deste erro
            
    except Exception as e:
        app.logger.error(f"Erro na página inicial: {str(e)}")
        flash('Ocorreu um erro ao acessar sua página inicial. Tente novamente.', 'danger')
        return redirect(url_for('login'))
    
    return render_template('app_home.html', 
                           user=user, 
                           now=lambda: datetime.now(),
                           upcoming_matches=upcoming_matches)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Por favor, faça login para acessar seu perfil.', 'warning')
        return redirect(url_for('login'))
    
    try:
        user = User.query.get(session['user_id'])
        if not user:
            session.pop('user_id', None)
            flash('Usuário não encontrado. Por favor, faça login novamente.', 'danger')
            return redirect(url_for('login'))
        
        # Get user interests
        interests = UserInterest.query.filter_by(user_id=user.id).all()
    except Exception as e:
        app.logger.error(f"Error in profile route: {str(e)}")
        flash('Ocorreu um erro ao acessar seu perfil. Por favor, tente novamente.', 'danger')
        return redirect(url_for('login'))
    
    # Get document verification status
    document = Document.query.filter_by(user_id=user.id).first()
    
    # Get social media profiles
    social_media = SocialMedia.query.filter_by(user_id=user.id).first()
    
    # Get fan badge
    fan_badge = user.fan_badge if user.fan_badge else "Fã Casual"
    
    # Get player match
    player_match = user.player_match
    
    # Current date for lootbox check
    today = datetime.now().date()
    
    return render_template(
        'app_profile.html', 
        user=user, 
        interests=interests,
        document=document,
        social_media=social_media,
        fan_badge=fan_badge,
        player_match=player_match,
        now=lambda: datetime.now()
    )

@app.route('/upload_profile_photo', methods=['POST'])
def upload_profile_photo():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro.', 'warning')
        return redirect(url_for('login'))
    
    try:
        user = User.query.get(session['user_id'])
        
        if 'profile_photo' not in request.files:
            flash('Nenhuma foto selecionada.', 'warning')
            return redirect(url_for('profile'))
        
        file = request.files['profile_photo']
        
        if file.filename == '':
            flash('Nenhuma foto selecionada.', 'warning')
            return redirect(url_for('profile'))
        
        if file:
            # Create uploads directory if it doesn't exist
            uploads_dir = os.path.join('static', 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            
            # Generate a secure filename with user ID to prevent duplication
            filename = secure_filename(f"user_{user.id}_{file.filename}")
            file_path = os.path.join(uploads_dir, filename)
            
            # Delete old profile image if exists
            if user.profile_image:
                old_file_path = os.path.join('static', 'uploads', user.profile_image)
                if os.path.exists(old_file_path):
                    try:
                        os.remove(old_file_path)
                    except Exception as e:
                        app.logger.error(f"Error deleting old profile image: {str(e)}")
            
            # Save new file
            file.save(file_path)
            
            # Update user record
            user.profile_image = filename
            db.session.commit()
            
            flash('Foto de perfil atualizada com sucesso!', 'success')
            return redirect(url_for('profile'))
    
    except Exception as e:
        app.logger.error(f"Error uploading profile photo: {str(e)}")
        flash('Ocorreu um erro ao atualizar sua foto de perfil. Tente novamente.', 'danger')
        return redirect(url_for('profile'))

@app.route('/document_validation', methods=['GET', 'POST'])
def document_validation():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro.', 'warning')
        return redirect(url_for('login'))
    
    form = DocumentUploadForm()
    user = User.query.get(session['user_id'])
    
    if form.validate_on_submit():
        try:
            # Obter o arquivo enviado
            document_file = form.document.data
            filename = secure_filename(document_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"user_{user.id}_{filename}")
            document_file.save(file_path)
            
            # Validar o documento usando IA
            validation_result = validate_document(file_path, user.name, user.cpf)
            
            # Log do resultado para debug
            app.logger.debug(f"Resultado da validação: {validation_result}")
            
            # Salvar registro do documento
            document = Document.query.filter_by(user_id=user.id).first()
            if document:
                document.file_path = file_path
                document.document_type = form.document_type.data
                document.validation_status = validation_result['status']
                document.validation_data = json.dumps(validation_result)
            else:
                document = Document(
                    user_id=user.id,
                    file_path=file_path,
                    document_type=form.document_type.data,
                    validation_status=validation_result['status'],
                    validation_data=json.dumps(validation_result)
                )
                db.session.add(document)
            
            db.session.commit()
            
            # Feedback para o usuário baseado no status
            if validation_result['status'] == 'verified':
                flash('Documento validado com sucesso!', 'success')
            elif validation_result['status'] == 'pending':
                flash('Documento em análise. Alguns dados precisam de verificação adicional.', 'warning')
            else:
                flash(f'Falha na validação do documento: {validation_result["message"]}', 'danger')
            
            return redirect(url_for('profile'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erro na validação de documento: {str(e)}")
            flash('Erro ao processar o documento. Por favor, tente novamente.', 'danger')
            return redirect(url_for('document_validation'))
    
    document = Document.query.filter_by(user_id=user.id).first()
    return render_template('app_document_validation.html', form=form, document=document)

@app.route('/social_media_remove/<platform>')
def social_media_remove(platform):
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro.', 'warning')
        return redirect(url_for('login'))
    
    try:
        user = User.query.get(session['user_id'])
        if not user:
            session.pop('user_id', None)
            flash('Usuário não encontrado. Por favor, faça login novamente.', 'danger')
            return redirect(url_for('login'))
        
        # Get existing social media data
        social_media = SocialMedia.query.filter_by(user_id=user.id).first()
        
        if social_media:
            if platform == 'twitter':
                social_media.twitter = ''
            elif platform == 'instagram':
                social_media.instagram = ''
            elif platform == 'twitch':
                social_media.twitch = ''
            elif platform == 'youtube':
                social_media.youtube = ''
            elif platform == 'facebook':
                social_media.facebook = ''
            
            # Recalculate engagement score if needed
            social_platforms = [
                social_media.twitter, 
                social_media.instagram, 
                social_media.twitch, 
                social_media.youtube, 
                social_media.facebook
            ]
            connected_platforms = sum(1 for p in social_platforms if p)
            
            # If no platforms left, reset hashtags and interactions
            if connected_platforms == 0:
                social_media.hashtags = '[]'
                social_media.interactions = '{}'
                social_media.engagement_score = 0
            
            db.session.commit()
            flash(f'Perfil de {platform} removido com sucesso!', 'success')
        
        return redirect(url_for('fan_power'))
        
    except Exception as e:
        app.logger.error(f"Error in social_media_remove route: {str(e)}")
        flash('Ocorreu um erro ao remover a rede social. Por favor, tente novamente.', 'danger')
        return redirect(url_for('fan_power'))

@app.route('/social_media', methods=['GET', 'POST'])
def social_media():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro.', 'warning')
        return redirect(url_for('login'))
    
    try:
        user = User.query.get(session['user_id'])
        if not user:
            session.pop('user_id', None)
            flash('Usuário não encontrado. Por favor, faça login novamente.', 'danger')
            return redirect(url_for('login'))
        
        # Get existing social media data
        social_media = SocialMedia.query.filter_by(user_id=user.id).first()
        
        if request.method == 'POST':
            # Get social media links from form
            twitter = request.form.get('twitter', '')
            instagram = request.form.get('instagram', '')
            twitch = request.form.get('twitch', '')
            youtube = request.form.get('youtube', '')
            facebook = request.form.get('facebook', '')
            
            # Validate URLs (basic validation)
            social_media_data = {
                'twitter': twitter if twitter and twitter.startswith('http') else '',
                'instagram': instagram if instagram and instagram.startswith('http') else '',
                'twitch': twitch if twitch and twitch.startswith('http') else '',
                'youtube': youtube if youtube and youtube.startswith('http') else '',
                'facebook': facebook if facebook and facebook.startswith('http') else ''
            }
            
            # Simulate social media analysis
            analysis_result = analyze_social_media(social_media_data)
            
            # Save social media data
            if social_media:
                social_media.twitter = social_media_data['twitter']
                social_media.instagram = social_media_data['instagram']
                social_media.twitch = social_media_data['twitch']
                social_media.youtube = social_media_data['youtube']
                social_media.facebook = social_media_data['facebook']
                social_media.engagement_score = analysis_result['engagement_score']
                social_media.hashtags = json.dumps(analysis_result['hashtags'])
                social_media.interactions = json.dumps(analysis_result['interactions'])
            else:
                social_media = SocialMedia(
                    user_id=user.id,
                    twitter=social_media_data['twitter'],
                    instagram=social_media_data['instagram'],
                    twitch=social_media_data['twitch'],
                    youtube=social_media_data['youtube'],
                    facebook=social_media_data['facebook'],
                    engagement_score=analysis_result['engagement_score'],
                    hashtags=json.dumps(analysis_result['hashtags']),
                    interactions=json.dumps(analysis_result['interactions'])
                )
                db.session.add(social_media)
            
            # Update user fan badge
            user.fan_badge = analysis_result['fan_badge']
            
            db.session.commit()
            
            flash(f'Perfis de redes sociais analisados! Você agora está categorizado como: {user.fan_badge}', 'success')
            return redirect(url_for('profile'))
        
        return render_template('app_social_media.html', social_media=social_media)
    
    except Exception as e:
        app.logger.error(f"Error in social_media route: {str(e)}")
        flash('Ocorreu um erro ao processar as redes sociais. Por favor, tente novamente.', 'danger')
        return redirect(url_for('profile'))

@app.route('/content_validation', methods=['GET', 'POST'])
def content_validation():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro.', 'warning')
        return redirect(url_for('login'))
    
    try:
        user = User.query.get(session['user_id'])
        if not user:
            session.pop('user_id', None)
            flash('Usuário não encontrado. Faça login novamente.', 'danger')
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            content_url = request.form.get('content_url')
            if not content_url:
                flash('A URL do conteúdo é obrigatória.', 'danger')
                content_links = ContentLink.query.filter_by(user_id=user.id).order_by(ContentLink.created_at.desc()).all()
                return render_template('app_content_validation.html', content_links=content_links)
            
            # Validate the content link
            try:
                validation_result = validate_content_links(content_url)
                
                # Save content link
                content_link = ContentLink(
                    user_id=user.id,
                    url=content_url,
                    content_type=validation_result['content_type'],
                    relevance_score=validation_result['relevance_score'],
                    keywords=json.dumps(validation_result['keywords'])
                )
                db.session.add(content_link)
                db.session.commit()
                
                flash(f'Conteúdo analisado com {validation_result["relevance_score"]}% de relevância para seu perfil!', 'success')
            except Exception as e:
                app.logger.error(f"Error validating content: {str(e)}")
                flash('Ocorreu um erro ao analisar o conteúdo. Verifique se o URL é válido.', 'danger')
        
        # Get user's content links
        content_links = ContentLink.query.filter_by(user_id=user.id).order_by(ContentLink.created_at.desc()).all()
        
        return render_template('app_content_validation.html', content_links=content_links)
    
    except Exception as e:
        app.logger.error(f"Error in content_validation route: {str(e)}")
        flash('Ocorreu um erro ao carregar a página de validação de conteúdo.', 'danger')
        return redirect(url_for('home_dashboard'))

@app.route('/player_match')
def player_match():
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Get all user data for matching
    interests = UserInterest.query.filter_by(user_id=user.id).all()
    social_media = SocialMedia.query.filter_by(user_id=user.id).first()
    
    # Only proceed if we have enough data
    if not interests or not social_media:
        flash('Complete your profile and social media information to get a player match.', 'warning')
        return redirect(url_for('profile'))
    
    # Get player match if not already assigned
    if not user.player_match or not user.player_bio:
        player_data = match_player(interests, social_media)
        user.player_match = player_data['player']
        user.player_bio = player_data['bio']
        user.player_image = player_data['image']
        db.session.commit()
    
    # Calculate match percentage (for display purposes)
    match_percentage = {
        'overall': random.randint(85, 99),
        'playstyle': random.randint(75, 98),
        'interests': random.randint(80, 95),
        'personality': random.randint(70, 99)
    }
    
    return render_template('app_player_match.html', 
                          user=user, 
                          match_percentage=match_percentage)

@app.route('/calendar')
def calendar():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro.', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Get user interests for filtering events
    interests = UserInterest.query.filter_by(user_id=user.id).all()
    interest_list = [interest.interest for interest in interests]
    
    # Get favorite events
    favorites = Calendar.query.filter_by(user_id=user.id, is_favorite=True).all()
    favorite_ids = [favorite.event_id for favorite in favorites]
    
    return render_template('app_calendar.html', 
                           user=user, 
                           interests=interest_list,
                           favorite_ids=json.dumps(favorite_ids))
                           
@app.route('/bolao')
def bolao():
    """Rota principal do Bolão da FURIA com lista de partidas"""
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro.', 'warning')
        return redirect(url_for('login'))
    
    try:
        user = User.query.get(session['user_id'])
        if not user:
            session.pop('user_id', None)
            flash('Usuário não encontrado. Por favor, faça login novamente.', 'danger')
            return redirect(url_for('login'))
        
        # Buscar partidas existentes ou criar novas se não houver
        matches = Match.query.order_by(Match.match_time).all()
        
        if not matches:
            # Gerar partidas de demonstração se não existir nenhuma
            demo_matches = generate_demo_matches(8)  # Gerar 8 partidas
            for match_data in demo_matches:
                match = Match(**match_data)
                db.session.add(match)
            
            db.session.commit()
            matches = Match.query.order_by(Match.match_time).all()
        
        # Buscar previsões do usuário
        user_predictions = {}
        predictions = MatchPrediction.query.filter_by(user_id=user.id).all()
        for pred in predictions:
            user_predictions[pred.match_id] = pred
        
        # Separar partidas futuras e passadas
        now = datetime.now()
        upcoming_matches = [m for m in matches if m.match_time > now]
        past_matches = [m for m in matches if m.match_time <= now]
        
        # Ordenar as partidas: futuras em ordem cronológica, passadas em ordem cronológica reversa
        upcoming_matches.sort(key=lambda x: x.match_time)
        past_matches.sort(key=lambda x: x.match_time, reverse=True)
        
        # Calcular pontuação total do usuário
        total_points = 0
        for match_id, prediction in user_predictions.items():
            total_points += prediction.total_points
        
        return render_template(
            'app_bolao.html',
            upcoming_matches=upcoming_matches,
            past_matches=past_matches,
            user_predictions=user_predictions,
            total_points=total_points,
            now=now
        )
    
    except Exception as e:
        app.logger.error(f"Erro na página do Bolão: {str(e)}")
        flash('Ocorreu um erro ao acessar o Bolão. Por favor, tente novamente.', 'danger')
        return redirect(url_for('home_dashboard'))

@app.route('/bolao/predict/<int:match_id>', methods=['GET', 'POST'])
def bolao_predict(match_id):
    """Rota para fazer uma previsão para uma partida"""
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro.', 'warning')
        return redirect(url_for('login'))
    
    try:
        user = User.query.get(session['user_id'])
        match = Match.query.get_or_404(match_id)
        
        # Verificar se a partida ainda permite palpites
        if not match.is_predictable:
            flash('Esta partida não está mais disponível para palpites.', 'warning')
            return redirect(url_for('bolao'))
        
        # Verificar se o usuário já fez uma previsão para esta partida
        existing_prediction = MatchPrediction.query.filter_by(
            user_id=user.id, match_id=match.id
        ).first()
        
        form = MatchPredictionForm()
        
        # Configurar as opções de jogadores para MVP
        players = get_furia_players_by_game(match.game)
        form.set_player_choices(players)
        
        if request.method == 'GET' and existing_prediction:
            # Preencher o formulário com os dados existentes
            form.furia_score.data = existing_prediction.furia_score
            form.opponent_score.data = existing_prediction.opponent_score
            form.predicted_mvp.data = existing_prediction.predicted_mvp
            form.predicted_opponent_highlight.data = existing_prediction.predicted_opponent_highlight
        
        if form.validate_on_submit():
            # Salvar ou atualizar a previsão
            if existing_prediction:
                existing_prediction.furia_score = form.furia_score.data
                existing_prediction.opponent_score = form.opponent_score.data
                existing_prediction.predicted_mvp = form.predicted_mvp.data
                existing_prediction.predicted_opponent_highlight = form.predicted_opponent_highlight.data
            else:
                prediction = MatchPrediction(
                    user_id=user.id,
                    match_id=match.id,
                    furia_score=form.furia_score.data,
                    opponent_score=form.opponent_score.data,
                    predicted_mvp=form.predicted_mvp.data,
                    predicted_opponent_highlight=form.predicted_opponent_highlight.data
                )
                db.session.add(prediction)
            
            db.session.commit()
            flash('Seu palpite foi registrado com sucesso!', 'success')
            return redirect(url_for('bolao'))
        
        return render_template(
            'app_bolao_predict.html',
            match=match,
            form=form,
            existing_prediction=existing_prediction
        )
    
    except Exception as e:
        app.logger.error(f"Erro ao fazer previsão: {str(e)}")
        flash('Ocorreu um erro ao processar seu palpite. Por favor, tente novamente.', 'danger')
        return redirect(url_for('bolao'))

@app.route('/bolao/detail/<int:match_id>')
def bolao_match_detail(match_id):
    """Rota para ver detalhes de uma partida e seu resultado"""
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro.', 'warning')
        return redirect(url_for('login'))
    
    try:
        user = User.query.get(session['user_id'])
        match = Match.query.get_or_404(match_id)
        
        # Buscar previsão do usuário
        prediction = MatchPrediction.query.filter_by(
            user_id=user.id, match_id=match.id
        ).first()
        
        # Calcular pontos se a partida já ocorreu
        points = None
        if match.status == 'completed' and prediction:
            points = calculate_prediction_points(prediction, match)
            
            # Atualizar os pontos na previsão se necessário
            if prediction.total_points == 0 and points['total_points'] > 0:
                prediction.score_prediction_points = points['score_prediction_points']
                prediction.mvp_prediction_points = points['mvp_prediction_points']
                prediction.highlight_prediction_points = points['highlight_prediction_points']
                prediction.total_points = points['total_points']
                db.session.commit()
        
        # Buscar outras previsões para esta partida (ranking)
        other_predictions = None
        if match.status == 'completed':
            other_predictions = MatchPrediction.query.filter_by(match_id=match.id).order_by(
                MatchPrediction.total_points.desc()
            ).limit(10).all()
        
        return render_template(
            'app_bolao_detail.html',
            match=match,
            prediction=prediction,
            points=points,
            other_predictions=other_predictions,
            user_id=user.id
        )
    
    except Exception as e:
        app.logger.error(f"Erro ao exibir detalhes da partida: {str(e)}")
        flash('Ocorreu um erro ao acessar os detalhes da partida. Por favor, tente novamente.', 'danger')
        return redirect(url_for('bolao'))

@app.route('/bolao/leaderboard')
def bolao_leaderboard():
    """Rota para ver o ranking geral do Bolão"""
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro.', 'warning')
        return redirect(url_for('login'))
    
    try:
        # Selecionar todos os usuários com previsões e calcular a pontuação total
        users = db.session.query(User).join(MatchPrediction).group_by(User.id).all()
        
        leaderboard = []
        for user in users:
            total_points = sum([p.total_points for p in user.match_predictions])
            predictions_count = len(user.match_predictions)
            exact_scores = sum([1 for p in user.match_predictions if p.score_prediction_points == 3])
            
            leaderboard.append({
                'user': user,
                'total_points': total_points,
                'predictions_count': predictions_count,
                'exact_scores': exact_scores
            })
        
        # Ordenar por pontuação total
        leaderboard.sort(key=lambda x: x['total_points'], reverse=True)
        
        # Adicionar posição no ranking
        for i, entry in enumerate(leaderboard):
            entry['position'] = i + 1
        
        # Encontrar a posição do usuário atual
        user_position = None
        for entry in leaderboard:
            if entry['user'].id == session['user_id']:
                user_position = entry
                break
        
        return render_template(
            'app_bolao_leaderboard.html',
            leaderboard=leaderboard[:20],  # Top 20
            user_position=user_position
        )
    
    except Exception as e:
        app.logger.error(f"Erro ao exibir ranking: {str(e)}")
        flash('Ocorreu um erro ao acessar o ranking. Por favor, tente novamente.', 'danger')
        return redirect(url_for('bolao'))

@app.route('/toggle_favorite', methods=['POST'])
def toggle_favorite():
    if 'user_id' not in session:
        return {"success": False, "message": "Not logged in"}, 401
    
    data = request.json
    event_id = data.get('event_id')
    
    if not event_id:
        return {"success": False, "message": "No event specified"}, 400
    
    # Check if the event is already favorited
    favorite = Calendar.query.filter_by(user_id=session['user_id'], event_id=event_id).first()
    
    if favorite:
        # Toggle favorite status
        favorite.is_favorite = not favorite.is_favorite
    else:
        # Create new favorite entry
        favorite = Calendar(
            user_id=session['user_id'],
            event_id=event_id,
            is_favorite=True
        )
        db.session.add(favorite)
    
    db.session.commit()
    
    return {"success": True, "is_favorite": favorite.is_favorite}

@app.route('/fan_power')
def fan_power():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro.', 'warning')
        return redirect(url_for('login'))
    
    try:
        user = User.query.get(session['user_id'])
        if not user:
            session.pop('user_id', None)
            flash('Usuário não encontrado. Por favor, faça login novamente.', 'danger')
            return redirect(url_for('login'))
        
        # Get all user data for fan power analysis
        social_media = SocialMedia.query.filter_by(user_id=user.id).first()
        content_links = ContentLink.query.filter_by(user_id=user.id).order_by(ContentLink.created_at.desc()).limit(5).all()
        document = Document.query.filter_by(user_id=user.id).first()
        
        # Calculate fan power metrics (with error handling)
        try:
            fan_power_data = get_fan_power(user, social_media, content_links)
        except Exception as e:
            app.logger.error(f"Error calculating fan power: {str(e)}")
            # Provide default values if calculation fails
            fan_power_data = {
                'fan_score': 10,
                'social_score': 0,
                'content_score': 0,
                'engagement_score': 0 if not social_media else social_media.engagement_score
            }
        
        # Convert social_media.hashtags to Python list if it exists as JSON string
        if social_media and social_media.hashtags:
            try:
                hashtags = json.loads(social_media.hashtags)
                social_media.hashtags = hashtags
            except Exception as e:
                app.logger.error(f"Error parsing hashtags: {str(e)}")
                social_media.hashtags = []
        
        return render_template('app_fan_power.html', 
                              user=user, 
                              fan_power=fan_power_data, 
                              social_media=social_media,
                              content_links=content_links,
                              document=document)
                              
    except Exception as e:
        app.logger.error(f"Error in fan_power route: {str(e)}")
        flash('Ocorreu um erro ao acessar o Fan Power. Por favor, tente novamente.', 'danger')
        return redirect(url_for('home_dashboard'))

@app.route('/edit_interests', methods=['GET', 'POST'])
def edit_interests():
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro.', 'warning')
        return redirect(url_for('login'))
    
    try:
        user = User.query.get(session['user_id'])
        if not user:
            session.pop('user_id', None)
            flash('Usuário não encontrado. Por favor, faça login novamente.', 'danger')
            return redirect(url_for('login'))
        
        # Get user's current interests
        interests = UserInterest.query.filter_by(user_id=user.id).all()
        current_interests = [interest.interest for interest in interests]
        
        if request.method == 'POST':
            # Clear existing interests
            UserInterest.query.filter_by(user_id=user.id).delete()
            
            # Get new interests from form
            new_interests = request.form.getlist('interests[]')
            
            # Add new interests
            for interest in new_interests:
                user_interest = UserInterest(
                    user_id=user.id,
                    interest=interest
                )
                db.session.add(user_interest)
            
            db.session.commit()
            flash('Seus interesses foram atualizados com sucesso!', 'success')
            return redirect(url_for('profile'))
        
        return render_template('app_edit_interests.html', user=user, current_interests=current_interests)
        
    except Exception as e:
        app.logger.error(f"Error in edit_interests route: {str(e)}")
        flash('Ocorreu um erro ao editar seus interesses. Por favor, tente novamente.', 'danger')
        return redirect(url_for('profile'))

@app.route('/lootbox')
def lootbox():
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Check if user already opened a lootbox today
    last_lootbox = user.last_lootbox_date
    today = datetime.now().date()
    can_open = True
    
    if last_lootbox and last_lootbox == today:
        can_open = False
    
    return render_template('app_lootbox.html', user=user, can_open=can_open)

@app.route('/open_lootbox', methods=['POST'])
def open_lootbox():
    if 'user_id' not in session:
        return {"success": False, "message": "Não está logado"}, 401
    
    try:
        user = User.query.get(session['user_id'])
        
        # Check if user already opened a lootbox today
        last_lootbox = user.last_lootbox_date
        today = datetime.now().date()
        
        if last_lootbox and last_lootbox == today:
            return {"success": False, "message": "Você já abriu sua lootbox hoje"}, 400
        
        # Get a random reward
        reward = get_lootbox_reward()
        
        # Update user's last lootbox date
        user.last_lootbox_date = today
        
        # Add reward to user's lootbox rewards
        # Make sure we handle both None values and existing JSON strings
        if not user.lootbox_rewards:
            user.lootbox_rewards = json.dumps([reward])
        else:
            try:
                current_rewards = json.loads(user.lootbox_rewards)
                if isinstance(current_rewards, list):
                    current_rewards.append(reward)
                else:
                    # If current_rewards is not a list, initialize a new list
                    current_rewards = [reward]
                user.lootbox_rewards = json.dumps(current_rewards)
            except json.JSONDecodeError:
                # Handle case where lootbox_rewards exists but isn't valid JSON
                user.lootbox_rewards = json.dumps([reward])
        
        # Commit changes to database
        db.session.commit()
        
        app.logger.debug(f"Lootbox reward generated: {reward}")
        
        # Return success response with reward data
        return {"success": True, "reward": reward}
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error opening lootbox: {str(e)}")
        return {"success": False, "message": "Erro ao abrir lootbox: " + str(e)}, 500

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    form = QuizForm()
    
    if form.validate_on_submit():
        # Calculate score
        score = 0
        for i in range(1, 6):
            question_field = getattr(form, f'question_{i}')
            correct_answer = getattr(form, f'correct_{i}').data
            
            if question_field.data == correct_answer:
                score += 1
        
        # Determine fan level based on score
        if score >= 4:
            fan_level = 'Expert'
        elif score >= 2:
            fan_level = 'Intermediate'
        else:
            fan_level = 'Casual'
        
        # Save quiz result
        quiz_result = Quiz(
            user_id=user.id,
            score=score,
            fan_level=fan_level
        )
        db.session.add(quiz_result)
        
        # Update user's quiz score if it's their highest
        if not user.quiz_score or score > user.quiz_score:
            user.quiz_score = score
            user.quiz_level = fan_level
        
        db.session.commit()
        
        flash(f'Quiz completed! Your score: {score}/5 - Fan Level: {fan_level}', 'success')
        return redirect(url_for('profile'))
    
    # Get user's previous quiz results
    quiz_results = Quiz.query.filter_by(user_id=user.id).order_by(Quiz.created_at.desc()).all()
    
    return render_template('app_quiz.html', form=form, user=user, quiz_results=quiz_results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
