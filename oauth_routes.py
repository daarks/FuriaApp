"""
Rotas para OAuth e integração com redes sociais.
"""
import json
import os
from datetime import datetime
from urllib.parse import urlencode

from flask import (
    Blueprint, current_app, flash, redirect, render_template, request, 
    session, url_for
)

from app import db
from models import User, SocialMedia
from models_oauth import OAuthConnection, OAuthInteraction, OAuthContentAnalysis
from oauth_config import OAUTH_CREDENTIALS, SUPPORTED_PLATFORMS, PLATFORM_NAMES
from oauth_services import OAuthService

# Criar Blueprint
oauth_blueprint = Blueprint('oauth', __name__)

@oauth_blueprint.route('/connect/<platform>')
def connect(platform):
    """
    Inicia o fluxo de conexão OAuth para a plataforma especificada.
    """
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro.', 'warning')
        return redirect(url_for('login'))
    
    # Verificar se a plataforma é suportada
    if platform not in SUPPORTED_PLATFORMS:
        flash(f'Plataforma {platform} não suportada.', 'danger')
        return redirect(url_for('fan_power'))
    
    # Verificar se já existe uma conexão ativa
    user_id = session['user_id']
    connection = OAuthConnection.query.filter_by(
        user_id=user_id, platform=platform, is_active=True
    ).first()
    
    if connection:
        flash(f'Você já está conectado ao {PLATFORM_NAMES[platform]}.', 'info')
        return redirect(url_for('social_oauth'))
    
    try:
        # Criar URI de redirecionamento
        domain = os.environ.get('REPLIT_DEV_DOMAIN')
        if not domain:
            domain = os.environ.get('REPLIT_DOMAIN', request.host)
        redirect_uri = f"https://{domain}/oauth/callback/{platform}"
        
        # Gerar URL de autorização
        authorization_url, state = OAuthService.get_authorization_url(
            platform, redirect_uri=redirect_uri
        )
        
        # Armazenar estado para verificação CSRF
        session[f'oauth_state_{platform}'] = state
        
        # Redirecionar para página de autorização
        return redirect(authorization_url)
    
    except Exception as e:
        current_app.logger.error(f"Erro ao iniciar conexão OAuth para {platform}: {str(e)}")
        flash(f'Ocorreu um erro ao conectar com {PLATFORM_NAMES[platform]}. Por favor, tente novamente.', 'danger')
        return redirect(url_for('social_oauth'))

@oauth_blueprint.route('/callback/<platform>')
def callback(platform):
    """
    Callback para o fluxo OAuth.
    """
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro.', 'warning')
        return redirect(url_for('login'))
    
    # Verificar se a plataforma é suportada
    if platform not in SUPPORTED_PLATFORMS:
        flash(f'Plataforma {platform} não suportada.', 'danger')
        return redirect(url_for('fan_power'))
    
    # Verificar estado para proteção CSRF
    state = session.pop(f'oauth_state_{platform}', None)
    if not state:
        flash('Sessão expirada ou inválida. Por favor, tente novamente.', 'danger')
        return redirect(url_for('social_oauth'))
    
    # Obter ID do usuário
    user_id = session['user_id']
    
    try:
        # Criar URI de redirecionamento
        domain = os.environ.get('REPLIT_DEV_DOMAIN')
        if not domain:
            domain = os.environ.get('REPLIT_DOMAIN', request.host)
        redirect_uri = f"https://{domain}/oauth/callback/{platform}"
        
        # Obter token de acesso
        token = OAuthService.get_token_from_callback(
            platform, request.url, state=state, redirect_uri=redirect_uri
        )
        
        # Buscar informações do usuário
        user_info = OAuthService.fetch_user_info(platform, token)
        
        # Armazenar conexão
        connection = OAuthService.store_oauth_connection(user_id, platform, token, user_info)
        
        # Buscar conexões relacionadas a esports
        OAuthService.fetch_esports_connections(connection.id)
        
        # Atualizar dados de redes sociais (para compatibilidade com o sistema existente)
        update_social_media_from_oauth(user_id, platform, connection)
        
        flash(f'Conexão com {PLATFORM_NAMES[platform]} realizada com sucesso!', 'success')
        return redirect(url_for('social_oauth'))
    
    except Exception as e:
        current_app.logger.error(f"Erro no callback OAuth para {platform}: {str(e)}")
        flash(f'Ocorreu um erro ao processar a conexão com {PLATFORM_NAMES[platform]}. Por favor, tente novamente.', 'danger')
        return redirect(url_for('social_oauth'))

@oauth_blueprint.route('/disconnect/<platform>', methods=['POST'])
def disconnect(platform):
    """
    Desconecta uma plataforma OAuth.
    """
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro.', 'warning')
        return redirect(url_for('login'))
    
    # Verificar se a plataforma é suportada
    if platform not in SUPPORTED_PLATFORMS:
        flash(f'Plataforma {platform} não suportada.', 'danger')
        return redirect(url_for('fan_power'))
    
    # Obter ID do usuário
    user_id = session['user_id']
    
    try:
        # Buscar conexão
        connection = OAuthConnection.query.filter_by(
            user_id=user_id, platform=platform
        ).first()
        
        if connection:
            # Desativar conexão
            connection.is_active = False
            connection.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Atualizar dados de redes sociais (para compatibilidade com o sistema existente)
            remove_social_media_from_oauth(user_id, platform)
            
            flash(f'Conexão com {PLATFORM_NAMES[platform]} removida com sucesso.', 'success')
        else:
            flash(f'Nenhuma conexão encontrada com {PLATFORM_NAMES[platform]}.', 'warning')
        
        return redirect(url_for('social_oauth'))
    
    except Exception as e:
        current_app.logger.error(f"Erro ao desconectar OAuth para {platform}: {str(e)}")
        flash(f'Ocorreu um erro ao remover a conexão com {PLATFORM_NAMES[platform]}. Por favor, tente novamente.', 'danger')
        return redirect(url_for('social_oauth'))

@oauth_blueprint.route('/sync/<platform>')
def sync(platform):
    """
    Sincroniza dados de uma plataforma OAuth.
    """
    if 'user_id' not in session:
        flash('Por favor, faça login primeiro.', 'warning')
        return redirect(url_for('login'))
    
    # Verificar se a plataforma é suportada
    if platform not in SUPPORTED_PLATFORMS:
        flash(f'Plataforma {platform} não suportada.', 'danger')
        return redirect(url_for('fan_power'))
    
    # Obter ID do usuário
    user_id = session['user_id']
    
    try:
        # Buscar conexão
        connection = OAuthConnection.query.filter_by(
            user_id=user_id, platform=platform, is_active=True
        ).first()
        
        if connection:
            # Buscar conexões relacionadas a esports
            interactions = OAuthService.fetch_esports_connections(connection.id)
            
            # Atualizar dados de redes sociais (para compatibilidade com o sistema existente)
            update_social_media_from_oauth(user_id, platform, connection)
            
            flash(f'Dados do {PLATFORM_NAMES[platform]} sincronizados com sucesso. {len(interactions)} conexões encontradas.', 'success')
        else:
            flash(f'Nenhuma conexão ativa encontrada com {PLATFORM_NAMES[platform]}.', 'warning')
        
        return redirect(url_for('social_oauth'))
    
    except Exception as e:
        current_app.logger.error(f"Erro ao sincronizar OAuth para {platform}: {str(e)}")
        flash(f'Ocorreu um erro ao sincronizar os dados com {PLATFORM_NAMES[platform]}. Por favor, tente novamente.', 'danger')
        return redirect(url_for('social_oauth'))

def update_social_media_from_oauth(user_id, platform, connection):
    """
    Atualiza os dados de redes sociais existentes a partir de uma conexão OAuth.
    """
    try:
        # Obter dados de redes sociais
        social_media = SocialMedia.query.filter_by(user_id=user_id).first()
        
        if not social_media:
            # Criar nova entrada
            social_media = SocialMedia(user_id=user_id)
            db.session.add(social_media)
        
        # Atualizar plataforma específica
        profile_url = connection.profile_url or ""
        
        if platform == 'facebook':
            social_media.facebook = profile_url
        elif platform == 'twitter':
            social_media.twitter = profile_url
        elif platform == 'instagram':
            social_media.instagram = profile_url
        
        # Contar conexões ativas
        active_connections = OAuthConnection.query.filter_by(
            user_id=user_id, is_active=True
        ).count()
        
        # Contar interações relacionadas a esports
        esports_interactions = OAuthInteraction.query.join(
            OAuthConnection, OAuthInteraction.oauth_connection_id == OAuthConnection.id
        ).filter(
            OAuthConnection.user_id == user_id,
            OAuthConnection.is_active == True,
            OAuthInteraction.is_esports_related == True
        ).count()
        
        # Contar interações relacionadas à FURIA
        furia_interactions = OAuthInteraction.query.join(
            OAuthConnection, OAuthInteraction.oauth_connection_id == OAuthConnection.id
        ).filter(
            OAuthConnection.user_id == user_id,
            OAuthConnection.is_active == True,
            OAuthInteraction.is_furia_related == True
        ).count()
        
        # Calcular nova pontuação de engajamento
        base_score = 40.0
        connection_bonus = active_connections * 10.0
        esports_bonus = min(30.0, esports_interactions * 2.0)
        furia_bonus = min(20.0, furia_interactions * 4.0)
        
        engagement_score = min(100.0, base_score + connection_bonus + esports_bonus + furia_bonus)
        social_media.engagement_score = engagement_score
        
        # Determinar Fan Badge com base na pontuação de engajamento
        user = User.query.get(user_id)
        if engagement_score >= 80:
            user.fan_badge = "Super Fã"
        elif engagement_score >= 60:
            user.fan_badge = "Fã Dedicado"
        elif engagement_score >= 40:
            user.fan_badge = "Fã Regular"
        else:
            user.fan_badge = "Fã Casual"
        
        # Salvar alterações
        db.session.commit()
        
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar dados de redes sociais a partir de OAuth: {str(e)}")
        db.session.rollback()

def remove_social_media_from_oauth(user_id, platform):
    """
    Remove uma plataforma dos dados de redes sociais existentes.
    """
    try:
        # Obter dados de redes sociais
        social_media = SocialMedia.query.filter_by(user_id=user_id).first()
        
        if social_media:
            # Remover plataforma específica
            if platform == 'facebook':
                social_media.facebook = ""
            elif platform == 'twitter':
                social_media.twitter = ""
            elif platform == 'instagram':
                social_media.instagram = ""
            
            # Contar conexões ativas restantes
            active_connections = OAuthConnection.query.filter_by(
                user_id=user_id, is_active=True
            ).count()
            
            # Se não houver mais conexões, resetar pontuação de engajamento
            if active_connections == 0:
                social_media.engagement_score = 0.0
                
                # Resetar Fan Badge
                user = User.query.get(user_id)
                user.fan_badge = "Fã Casual"
            
            # Salvar alterações
            db.session.commit()
        
    except Exception as e:
        current_app.logger.error(f"Erro ao remover dados de redes sociais a partir de OAuth: {str(e)}")
        db.session.rollback()