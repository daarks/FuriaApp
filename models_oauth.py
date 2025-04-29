"""
Modelos de banco de dados para integração OAuth com redes sociais.
Estes modelos complementam os modelos existentes em models.py.
"""
from datetime import datetime
from app import db

class OAuthConnection(db.Model):
    """
    Armazena as informações de conexão OAuth para cada usuário e plataforma.
    """
    __tablename__ = 'oauth_connection'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # facebook, twitter, instagram, discord
    
    # Dados da conta OAuth
    provider_user_id = db.Column(db.String(255))  # ID do usuário na plataforma
    username = db.Column(db.String(255))  # Nome de usuário na plataforma
    display_name = db.Column(db.String(255))  # Nome de exibição
    profile_url = db.Column(db.String(512))  # URL do perfil na plataforma
    
    # Tokens de acesso
    access_token = db.Column(db.String(512), nullable=False)
    token_type = db.Column(db.String(50))  # Bearer, OAuth, etc.
    refresh_token = db.Column(db.String(512))
    expires_at = db.Column(db.DateTime)
    scopes = db.Column(db.String(512))  # Escopos de permissão separados por vírgula
    
    # Status da conexão
    is_active = db.Column(db.Boolean, default=True)
    last_synced = db.Column(db.DateTime)
    
    # Meta
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento
    user = db.relationship('User', backref=db.backref('oauth_connections', lazy=True))

    # Dados de análise específicos para cada rede social
    raw_data = db.Column(db.Text)  # JSON com os dados brutos da API
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'platform', name='uix_user_platform'),
    )

class OAuthInteraction(db.Model):
    """
    Armazena interações (likes, follows, etc.) detectadas nas plataformas conectadas
    relacionadas a esports e, especialmente, à FURIA.
    """
    __tablename__ = 'oauth_interaction'
    id = db.Column(db.Integer, primary_key=True)
    oauth_connection_id = db.Column(db.Integer, db.ForeignKey('oauth_connection.id'), nullable=False)
    
    # Dados da interação
    interaction_type = db.Column(db.String(50), nullable=False)  # follow, like, comment, member, etc.
    target_type = db.Column(db.String(50), nullable=False)  # page, post, group, guild, etc.
    target_id = db.Column(db.String(255))  # ID do alvo na plataforma
    target_name = db.Column(db.String(255))  # Nome do alvo (ex: "FURIA Esports")
    
    # Relevância para esports
    is_esports_related = db.Column(db.Boolean, default=False)
    is_furia_related = db.Column(db.Boolean, default=False)
    relevance_score = db.Column(db.Float, default=0.0)  # 0.0 a 1.0
    
    # Detalhes da interação
    interaction_data = db.Column(db.Text)  # JSON com metadados da interação
    
    # Meta
    last_checked = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento
    oauth_connection = db.relationship('OAuthConnection', backref=db.backref('interactions', lazy=True))
    
    __table_args__ = (
        db.UniqueConstraint('oauth_connection_id', 'interaction_type', 'target_id', name='uix_connection_interaction_target'),
    )

class OAuthContentAnalysis(db.Model):
    """
    Armazena análises de conteúdo postado ou interagido pelo usuário nas plataformas
    conectadas que sejam relevantes para esports.
    """
    __tablename__ = 'oauth_content_analysis'
    id = db.Column(db.Integer, primary_key=True)
    oauth_connection_id = db.Column(db.Integer, db.ForeignKey('oauth_connection.id'), nullable=False)
    
    # Dados do conteúdo
    content_type = db.Column(db.String(50), nullable=False)  # post, tweet, story, etc.
    content_id = db.Column(db.String(255))  # ID do conteúdo na plataforma
    content_text = db.Column(db.Text)  # Texto do conteúdo
    content_url = db.Column(db.String(512))  # URL do conteúdo, se disponível
    
    # Dados de análise
    esports_keywords = db.Column(db.Text)  # JSON com palavras-chave detectadas
    esports_relevance = db.Column(db.Float, default=0.0)  # 0.0 a 1.0
    sentiment_score = db.Column(db.Float)  # -1.0 (negativo) a 1.0 (positivo)
    
    # Meta
    content_created_at = db.Column(db.DateTime)  # Data de criação do conteúdo
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento
    oauth_connection = db.relationship('OAuthConnection', backref=db.backref('content_analyses', lazy=True))
    
    __table_args__ = (
        db.UniqueConstraint('oauth_connection_id', 'content_type', 'content_id', name='uix_connection_content'),
    )