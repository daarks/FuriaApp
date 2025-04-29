"""
Serviços para integração com APIs OAuth de redes sociais.
"""
import json
import logging
import os
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests
from flask import current_app, url_for, request
from requests_oauthlib import OAuth2Session

from app import db
from models_oauth import OAuthConnection, OAuthInteraction, OAuthContentAnalysis
from oauth_config import (
    OAUTH_CREDENTIALS, OAUTH_REDIRECT_URI, SUPPORTED_PLATFORMS,
    USER_INFO_ENDPOINTS, CONNECTIONS_ENDPOINTS, ESPORTS_KEYWORDS,
    ESPORTS_ORGANIZATIONS
)

logger = logging.getLogger(__name__)

class OAuthService:
    """
    Serviço para gerenciar conexões OAuth com redes sociais.
    """
    
    @staticmethod
    def get_oauth_session(platform, token=None, redirect_uri=None):
        """
        Cria uma sessão OAuth2 para a plataforma especificada.
        
        Args:
            platform: Nome da plataforma (facebook, twitter, etc.)
            token: Token de acesso existente (opcional)
            redirect_uri: URI de redirecionamento (opcional)
            
        Returns:
            OAuth2Session configurada para a plataforma
        """
        if platform not in SUPPORTED_PLATFORMS:
            raise ValueError(f"Plataforma não suportada: {platform}")
        
        credentials = OAUTH_CREDENTIALS[platform]
        client_id = credentials['id']
        
        if not client_id:
            logger.error(f"Client ID não configurado para {platform}")
            raise ValueError(f"Client ID não configurado para {platform}")
        
        if token:
            return OAuth2Session(client_id, token=token)
        
        # URI de redirecionamento com domínio da aplicação
        if redirect_uri is None:
            domain = os.environ.get('REPLIT_DEV_DOMAIN')
            if not domain:
                domain = os.environ.get('REPLIT_DOMAIN', request.host)
            redirect_uri = OAUTH_REDIRECT_URI.format(domain=domain, provider=platform)
        
        # Escopos para a plataforma
        scope = credentials.get('scope', [])
        
        return OAuth2Session(
            client_id,
            redirect_uri=redirect_uri,
            scope=scope
        )
    
    @staticmethod
    def get_authorization_url(platform, redirect_uri=None):
        """
        Gera uma URL de autorização para a plataforma especificada.
        
        Args:
            platform: Nome da plataforma
            redirect_uri: URI de redirecionamento (opcional)
            
        Returns:
            URL de autorização e state para verificação CSRF
        """
        credentials = OAUTH_CREDENTIALS[platform]
        authorize_url = credentials['authorize_url']
        
        # Parâmetros específicos do token de solicitação (se houver)
        request_token_params = credentials.get('request_token_params', {})
        
        # Criar sessão OAuth
        oauth_session = OAuthService.get_oauth_session(platform, redirect_uri=redirect_uri)
        
        # Gerar URL de autorização
        authorization_url, state = oauth_session.authorization_url(
            authorize_url, **request_token_params
        )
        
        return authorization_url, state
    
    @staticmethod
    def get_token_from_callback(platform, callback_url, state=None, redirect_uri=None):
        """
        Obtém um token de acesso a partir da URL de callback.
        
        Args:
            platform: Nome da plataforma
            callback_url: URL de callback completa
            state: Estado CSRF para verificação
            redirect_uri: URI de redirecionamento (opcional)
            
        Returns:
            Token de acesso e informações relacionadas
        """
        credentials = OAUTH_CREDENTIALS[platform]
        client_secret = credentials['secret']
        token_url = credentials['access_token_url']
        
        if not client_secret:
            logger.error(f"Client Secret não configurado para {platform}")
            raise ValueError(f"Client Secret não configurado para {platform}")
        
        # Criar sessão OAuth
        oauth_session = OAuthService.get_oauth_session(platform, redirect_uri=redirect_uri)
        
        # Obter token de acesso
        token = oauth_session.fetch_token(
            token_url,
            authorization_response=callback_url,
            client_secret=client_secret,
            include_client_id=True
        )
        
        return token
    
    @staticmethod
    def fetch_user_info(platform, token):
        """
        Busca informações do usuário da plataforma.
        
        Args:
            platform: Nome da plataforma
            token: Token de acesso
            
        Returns:
            Informações do usuário
        """
        credentials = OAUTH_CREDENTIALS[platform]
        api_base_url = credentials['api_base_url']
        user_info_endpoint = USER_INFO_ENDPOINTS[platform]
        
        # Criar sessão OAuth com o token
        oauth_session = OAuthService.get_oauth_session(platform, token=token)
        
        # Buscar informações do usuário
        user_info_url = urljoin(api_base_url, user_info_endpoint)
        response = oauth_session.get(user_info_url)
        response.raise_for_status()
        
        return response.json()
    
    @staticmethod
    def store_oauth_connection(user_id, platform, token, user_info):
        """
        Armazena ou atualiza a conexão OAuth no banco de dados.
        
        Args:
            user_id: ID do usuário
            platform: Nome da plataforma
            token: Token de acesso
            user_info: Informações do usuário
            
        Returns:
            Instância de OAuthConnection
        """
        # Verificar se já existe uma conexão para esse usuário e plataforma
        connection = OAuthConnection.query.filter_by(
            user_id=user_id, platform=platform
        ).first()
        
        # Extrair IDs e informações específicos da plataforma
        provider_user_id, username, display_name, profile_url = OAuthService._extract_user_details(
            platform, user_info
        )
        
        # Definir data de expiração do token
        expires_at = None
        if token.get('expires_in'):
            expires_at = datetime.utcnow() + timedelta(seconds=token['expires_in'])
        
        # Converter escopos para string separada por vírgulas
        scopes = ",".join(token.get('scope', []))
        
        if connection:
            # Atualizar conexão existente
            connection.provider_user_id = provider_user_id
            connection.username = username
            connection.display_name = display_name
            connection.profile_url = profile_url
            connection.access_token = token['access_token']
            connection.token_type = token.get('token_type', 'Bearer')
            connection.refresh_token = token.get('refresh_token')
            connection.expires_at = expires_at
            connection.scopes = scopes
            connection.raw_data = json.dumps(user_info)
            connection.is_active = True
            connection.updated_at = datetime.utcnow()
        else:
            # Criar nova conexão
            connection = OAuthConnection(
                user_id=user_id,
                platform=platform,
                provider_user_id=provider_user_id,
                username=username,
                display_name=display_name,
                profile_url=profile_url,
                access_token=token['access_token'],
                token_type=token.get('token_type', 'Bearer'),
                refresh_token=token.get('refresh_token'),
                expires_at=expires_at,
                scopes=scopes,
                raw_data=json.dumps(user_info),
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(connection)
        
        # Salvar alterações
        db.session.commit()
        
        return connection
    
    @staticmethod
    def _extract_user_details(platform, user_info):
        """
        Extrai detalhes do usuário com base na plataforma.
        
        Args:
            platform: Nome da plataforma
            user_info: Informações do usuário
            
        Returns:
            Tupla com (provider_user_id, username, display_name, profile_url)
        """
        if platform == 'facebook':
            return (
                user_info.get('id'),
                user_info.get('name'),
                user_info.get('name'),
                f"https://facebook.com/{user_info.get('id')}"
            )
        elif platform == 'twitter':
            data = user_info.get('data', {})
            return (
                data.get('id'),
                data.get('username'),
                data.get('name'),
                f"https://twitter.com/{data.get('username')}"
            )
        elif platform == 'instagram':
            return (
                user_info.get('id'),
                user_info.get('username'),
                user_info.get('username'),
                f"https://instagram.com/{user_info.get('username')}"
            )
        elif platform == 'discord':
            return (
                user_info.get('id'),
                user_info.get('username'),
                f"{user_info.get('username')}",
                None  # Discord não tem URL de perfil público
            )
        
        # Fallback para plataformas desconhecidas
        return (
            user_info.get('id'),
            user_info.get('username') or user_info.get('name'),
            user_info.get('name') or user_info.get('username'),
            None
        )
    
    @staticmethod
    def fetch_esports_connections(connection_id):
        """
        Busca conexões relacionadas a esports de uma plataforma conectada.
        
        Args:
            connection_id: ID da conexão OAuth
            
        Returns:
            Lista de interações encontradas
        """
        connection = OAuthConnection.query.get(connection_id)
        if not connection or not connection.is_active:
            logger.error(f"Conexão não encontrada ou inativa: {connection_id}")
            return []
        
        platform = connection.platform
        token = {
            'access_token': connection.access_token,
            'token_type': connection.token_type
        }
        
        # Obter endpoints de conexões para a plataforma
        if platform not in CONNECTIONS_ENDPOINTS:
            logger.error(f"Endpoints de conexões não configurados para {platform}")
            return []
        
        # Buscar conexões da plataforma
        try:
            interactions = []
            
            # Criar sessão OAuth
            oauth_session = OAuthService.get_oauth_session(platform, token=token)
            api_base_url = OAUTH_CREDENTIALS[platform]['api_base_url']
            
            # Buscar com base na plataforma
            if platform == 'facebook':
                interactions.extend(
                    OAuthService._fetch_facebook_connections(connection, oauth_session, api_base_url)
                )
            elif platform == 'twitter':
                interactions.extend(
                    OAuthService._fetch_twitter_connections(connection, oauth_session, api_base_url)
                )
            elif platform == 'instagram':
                interactions.extend(
                    OAuthService._fetch_instagram_connections(connection, oauth_session, api_base_url)
                )
            elif platform == 'discord':
                interactions.extend(
                    OAuthService._fetch_discord_connections(connection, oauth_session, api_base_url)
                )
            
            # Atualizar timestamp de sincronização
            connection.last_synced = datetime.utcnow()
            db.session.commit()
            
            return interactions
            
        except Exception as e:
            logger.error(f"Erro ao buscar conexões para {platform}: {str(e)}")
            return []
    
    @staticmethod
    def _fetch_facebook_connections(connection, oauth_session, api_base_url):
        """Busca likes de páginas e posts relacionados a esports no Facebook."""
        interactions = []
        endpoints = CONNECTIONS_ENDPOINTS['facebook']
        esports_org_ids = set(ESPORTS_ORGANIZATIONS['facebook'])
        
        # Buscar páginas curtidas
        try:
            likes_url = urljoin(api_base_url, endpoints['likes'])
            response = oauth_session.get(likes_url)
            response.raise_for_status()
            
            likes_data = response.json()
            if 'data' in likes_data:
                for like in likes_data['data']:
                    page_id = like.get('id')
                    page_name = like.get('name')
                    
                    # Verificar se é uma organização de esports conhecida
                    is_esports_org = page_id in esports_org_ids
                    
                    # Verificar relevância para esports através do nome
                    is_esports_related = is_esports_org or OAuthService._is_esports_related(page_name)
                    is_furia_related = is_esports_org and 'furia' in page_name.lower()
                    
                    # Calcular pontuação de relevância
                    relevance_score = 0.0
                    if is_furia_related:
                        relevance_score = 1.0
                    elif is_esports_org:
                        relevance_score = 0.9
                    elif is_esports_related:
                        relevance_score = 0.7
                    
                    if is_esports_related or is_esports_org:
                        # Criar ou atualizar interação
                        interaction = OAuthService._store_interaction(
                            connection.id,
                            'like',
                            'page',
                            page_id,
                            page_name,
                            is_esports_related,
                            is_furia_related,
                            relevance_score,
                            like
                        )
                        interactions.append(interaction)
        except Exception as e:
            logger.error(f"Erro ao buscar likes do Facebook: {str(e)}")
        
        # Buscar posts recentes (opcional)
        try:
            posts_url = urljoin(api_base_url, endpoints['posts'])
            response = oauth_session.get(posts_url)
            response.raise_for_status()
            
            posts_data = response.json()
            if 'data' in posts_data:
                for post in posts_data['data']:
                    post_id = post.get('id')
                    post_message = post.get('message', '')
                    
                    # Verificar se o post está relacionado a esports
                    is_esports_related = OAuthService._is_esports_related(post_message)
                    is_furia_related = 'furia' in post_message.lower()
                    
                    # Calcular pontuação de relevância
                    relevance_score = 0.0
                    if is_furia_related:
                        relevance_score = 0.8
                    elif is_esports_related:
                        relevance_score = 0.6
                    
                    if is_esports_related or is_furia_related:
                        # Criar ou atualizar análise de conteúdo
                        content_analysis = OAuthService._store_content_analysis(
                            connection.id,
                            'post',
                            post_id,
                            post_message,
                            f"https://facebook.com/{post_id}",
                            post.get('created_time')
                        )
        except Exception as e:
            logger.error(f"Erro ao buscar posts do Facebook: {str(e)}")
        
        return interactions
    
    @staticmethod
    def _fetch_twitter_connections(connection, oauth_session, api_base_url):
        """Busca follows e tweets relacionados a esports no Twitter."""
        interactions = []
        endpoints = CONNECTIONS_ENDPOINTS['twitter']
        esports_org_ids = set(ESPORTS_ORGANIZATIONS['twitter'])
        
        # Buscar perfis seguidos
        try:
            # Substituir {user_id} pelo ID do usuário na plataforma
            following_url = urljoin(
                api_base_url, 
                endpoints['following'].format(user_id=connection.provider_user_id)
            )
            
            response = oauth_session.get(following_url)
            response.raise_for_status()
            
            following_data = response.json()
            if 'data' in following_data:
                for follow in following_data['data']:
                    follow_id = follow.get('id')
                    follow_name = follow.get('name')
                    follow_username = follow.get('username')
                    
                    # Verificar se é uma organização de esports conhecida
                    is_esports_org = follow_id in esports_org_ids
                    
                    # Verificar relevância para esports
                    is_esports_related = is_esports_org or OAuthService._is_esports_related(follow_name) or OAuthService._is_esports_related(follow_username)
                    is_furia_related = is_esports_org and ('furia' in follow_name.lower() or 'furia' in follow_username.lower())
                    
                    # Calcular pontuação de relevância
                    relevance_score = 0.0
                    if is_furia_related:
                        relevance_score = 1.0
                    elif is_esports_org:
                        relevance_score = 0.9
                    elif is_esports_related:
                        relevance_score = 0.7
                    
                    if is_esports_related or is_esports_org:
                        # Criar ou atualizar interação
                        interaction = OAuthService._store_interaction(
                            connection.id,
                            'follow',
                            'user',
                            follow_id,
                            f"{follow_name} (@{follow_username})",
                            is_esports_related,
                            is_furia_related,
                            relevance_score,
                            follow
                        )
                        interactions.append(interaction)
        except Exception as e:
            logger.error(f"Erro ao buscar follows do Twitter: {str(e)}")
        
        # Buscar tweets recentes (opcional)
        try:
            tweets_url = urljoin(
                api_base_url, 
                endpoints['tweets'].format(user_id=connection.provider_user_id)
            )
            
            response = oauth_session.get(tweets_url)
            response.raise_for_status()
            
            tweets_data = response.json()
            if 'data' in tweets_data:
                for tweet in tweets_data['data']:
                    tweet_id = tweet.get('id')
                    tweet_text = tweet.get('text', '')
                    
                    # Verificar se o tweet está relacionado a esports
                    is_esports_related = OAuthService._is_esports_related(tweet_text)
                    is_furia_related = 'furia' in tweet_text.lower()
                    
                    if is_esports_related or is_furia_related:
                        # Criar ou atualizar análise de conteúdo
                        content_analysis = OAuthService._store_content_analysis(
                            connection.id,
                            'tweet',
                            tweet_id,
                            tweet_text,
                            f"https://twitter.com/i/web/status/{tweet_id}",
                            tweet.get('created_at')
                        )
        except Exception as e:
            logger.error(f"Erro ao buscar tweets: {str(e)}")
        
        return interactions
    
    @staticmethod
    def _fetch_instagram_connections(connection, oauth_session, api_base_url):
        """Busca mídia relacionada a esports no Instagram."""
        interactions = []
        endpoints = CONNECTIONS_ENDPOINTS['instagram']
        esports_accounts = set(ESPORTS_ORGANIZATIONS['instagram'])
        
        # Buscar mídia recente
        try:
            media_url = urljoin(api_base_url, endpoints['media'])
            response = oauth_session.get(media_url)
            response.raise_for_status()
            
            media_data = response.json()
            if 'data' in media_data:
                for media in media_data['data']:
                    media_id = media.get('id')
                    media_caption = media.get('caption', '')
                    media_url = media.get('permalink')
                    
                    # Verificar se a mídia está relacionada a esports
                    is_esports_related = OAuthService._is_esports_related(media_caption)
                    is_furia_related = 'furia' in media_caption.lower()
                    
                    if is_esports_related or is_furia_related:
                        # Criar ou atualizar análise de conteúdo
                        content_analysis = OAuthService._store_content_analysis(
                            connection.id,
                            'media',
                            media_id,
                            media_caption,
                            media_url,
                            media.get('timestamp')
                        )
        except Exception as e:
            logger.error(f"Erro ao buscar mídia do Instagram: {str(e)}")
        
        # Instagram não fornece acesso direto aos perfis seguidos na API v2
        # Seria necessário solicitar permissões adicionais
        
        return interactions
    
    @staticmethod
    def _fetch_discord_connections(connection, oauth_session, api_base_url):
        """Busca servidores relacionados a esports no Discord."""
        interactions = []
        endpoints = CONNECTIONS_ENDPOINTS['discord']
        esports_guild_names = set(ESPORTS_ORGANIZATIONS['discord']['guild_names'])
        
        # Buscar servidores (guilds)
        try:
            guilds_url = urljoin(api_base_url, endpoints['guilds'])
            response = oauth_session.get(guilds_url)
            response.raise_for_status()
            
            guilds = response.json()
            for guild in guilds:
                guild_id = guild.get('id')
                guild_name = guild.get('name')
                
                # Verificar se é um servidor de esports conhecido
                is_esports_guild = guild_name in esports_guild_names
                
                # Verificar relevância para esports
                is_esports_related = is_esports_guild or OAuthService._is_esports_related(guild_name)
                is_furia_related = is_esports_guild and 'furia' in guild_name.lower()
                
                # Calcular pontuação de relevância
                relevance_score = 0.0
                if is_furia_related:
                    relevance_score = 1.0
                elif is_esports_guild:
                    relevance_score = 0.9
                elif is_esports_related:
                    relevance_score = 0.7
                
                if is_esports_related or is_esports_guild:
                    # Criar ou atualizar interação
                    interaction = OAuthService._store_interaction(
                        connection.id,
                        'member',
                        'guild',
                        guild_id,
                        guild_name,
                        is_esports_related,
                        is_furia_related,
                        relevance_score,
                        guild
                    )
                    interactions.append(interaction)
        except Exception as e:
            logger.error(f"Erro ao buscar servidores do Discord: {str(e)}")
        
        return interactions
    
    @staticmethod
    def _is_esports_related(text):
        """
        Verifica se um texto está relacionado a esports.
        
        Args:
            text: Texto a ser verificado
            
        Returns:
            True se estiver relacionado a esports, False caso contrário
        """
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Verificar palavras-chave de esports
        for keyword in ESPORTS_KEYWORDS:
            if keyword in text_lower:
                return True
        
        # Verificar padrões específicos (hashtags, menções, etc.)
        esports_hashtags = [
            r'#(esports?|gaming|gamer)',
            r'#(cs(go)?|valorant|lol|dota)',
            r'#(furia|mibr|liquid|cloud9|fazeclan|g2|navi)'
        ]
        
        for pattern in esports_hashtags:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    @staticmethod
    def _store_interaction(
        connection_id, interaction_type, target_type, target_id, target_name,
        is_esports_related, is_furia_related, relevance_score, interaction_data
    ):
        """
        Armazena ou atualiza uma interação no banco de dados.
        
        Returns:
            Instância de OAuthInteraction
        """
        # Verificar se já existe uma interação
        interaction = OAuthInteraction.query.filter_by(
            oauth_connection_id=connection_id,
            interaction_type=interaction_type,
            target_id=target_id
        ).first()
        
        if interaction:
            # Atualizar interação existente
            interaction.target_name = target_name
            interaction.is_esports_related = is_esports_related
            interaction.is_furia_related = is_furia_related
            interaction.relevance_score = relevance_score
            interaction.interaction_data = json.dumps(interaction_data)
            interaction.last_checked = datetime.utcnow()
            interaction.updated_at = datetime.utcnow()
        else:
            # Criar nova interação
            interaction = OAuthInteraction(
                oauth_connection_id=connection_id,
                interaction_type=interaction_type,
                target_type=target_type,
                target_id=target_id,
                target_name=target_name,
                is_esports_related=is_esports_related,
                is_furia_related=is_furia_related,
                relevance_score=relevance_score,
                interaction_data=json.dumps(interaction_data),
                last_checked=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(interaction)
        
        db.session.commit()
        return interaction
    
    @staticmethod
    def _store_content_analysis(
        connection_id, content_type, content_id, content_text, content_url, content_created_at=None
    ):
        """
        Armazena ou atualiza uma análise de conteúdo no banco de dados.
        
        Returns:
            Instância de OAuthContentAnalysis
        """
        # Verificar se já existe uma análise
        content_analysis = OAuthContentAnalysis.query.filter_by(
            oauth_connection_id=connection_id,
            content_type=content_type,
            content_id=content_id
        ).first()
        
        # Extrair palavras-chave de esports
        esports_keywords_found = []
        for keyword in ESPORTS_KEYWORDS:
            if keyword in content_text.lower():
                esports_keywords_found.append(keyword)
        
        # Calcular relevância para esports (simples)
        esports_relevance = min(1.0, len(esports_keywords_found) / 10)
        
        # Análise de sentimento simples
        positive_words = ['amo', 'adoro', 'gosto', 'top', 'melhor', 'bom', 'ótimo', 'incrível', 'love', 'great']
        negative_words = ['odeio', 'ruim', 'péssimo', 'horrível', 'pior', 'hate', 'bad', 'worst']
        
        sentiment_score = 0.0
        for word in positive_words:
            if word in content_text.lower():
                sentiment_score += 0.2
        
        for word in negative_words:
            if word in content_text.lower():
                sentiment_score -= 0.2
        
        # Limitar entre -1.0 e 1.0
        sentiment_score = max(-1.0, min(1.0, sentiment_score))
        
        # Converter data de criação do conteúdo
        if content_created_at:
            if isinstance(content_created_at, str):
                try:
                    content_created_at = datetime.fromisoformat(content_created_at.replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    content_created_at = datetime.utcnow()
        else:
            content_created_at = datetime.utcnow()
        
        if content_analysis:
            # Atualizar análise existente
            content_analysis.content_text = content_text
            content_analysis.content_url = content_url
            content_analysis.esports_keywords = json.dumps(esports_keywords_found)
            content_analysis.esports_relevance = esports_relevance
            content_analysis.sentiment_score = sentiment_score
            content_analysis.content_created_at = content_created_at
            content_analysis.updated_at = datetime.utcnow()
        else:
            # Criar nova análise
            content_analysis = OAuthContentAnalysis(
                oauth_connection_id=connection_id,
                content_type=content_type,
                content_id=content_id,
                content_text=content_text,
                content_url=content_url,
                esports_keywords=json.dumps(esports_keywords_found),
                esports_relevance=esports_relevance,
                sentiment_score=sentiment_score,
                content_created_at=content_created_at,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(content_analysis)
        
        db.session.commit()
        return content_analysis