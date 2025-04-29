import random
import json
import logging
from datetime import datetime
import re
import string

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# FURIA player data
FURIA_PLAYERS = [
    {
        "name": "KSCERATO",
        "full_name": "Kaike Cerato",
        "game": "CS:GO",
        "bio": "KSCERATO is a Brazilian CS:GO player known for his incredible rifling skills and consistency. With FURIA since 2018, he's been a cornerstone of the team's success in international competitions.",
        "image": "https://liquipedia.net/commons/images/thumb/a/a6/FURIA_KSCERATO_2023_1.png/600px-FURIA_KSCERATO_2023_1.png",
        "interests": ["cs", "fps", "competitive"],
        "playstyle": "Calculated, Precise, Technical"
    },
    {
        "name": "arT",
        "full_name": "Andrei Piovezan",
        "game": "CS:GO",
        "bio": "arT is the in-game leader for FURIA's CS:GO team, known for his aggressive playstyle and unconventional strategies. His fearless leadership has defined FURIA's unique approach to the game.",
        "image": "https://liquipedia.net/commons/images/thumb/a/a1/FURIA_arT_2023_1.png/600px-FURIA_arT_2023_1.png",
        "interests": ["cs", "leadership", "strategy"],
        "playstyle": "Aggressive, Unpredictable, Bold"
    },
    {
        "name": "yuurih",
        "full_name": "Yuri Santos",
        "game": "CS:GO",
        "bio": "yuurih is one of Brazil's top CS:GO talents, known for his versatility and clutch performances. His ability to adapt to different roles makes him an invaluable asset to FURIA.",
        "image": "https://liquipedia.net/commons/images/thumb/5/50/FURIA_yuurih_2023_1.png/600px-FURIA_yuurih_2023_1.png",
        "interests": ["cs", "fps", "versatility"],
        "playstyle": "Versatile, Smart, Clutch"
    },
    {
        "name": "saffee",
        "full_name": "Rafael Costa",
        "game": "CS:GO",
        "bio": "saffee is FURIA's dedicated AWPer, bringing years of experience and precision to the team. His consistent performances with the sniper rifle have been crucial for FURIA's success.",
        "image": "https://liquipedia.net/commons/images/thumb/c/c6/FURIA_saffee_2023_1.png/600px-FURIA_saffee_2023_1.png",
        "interests": ["cs", "awping", "precision"],
        "playstyle": "Patient, Precise, Methodical"
    },
    {
        "name": "guerri",
        "full_name": "Nicholas Nogueira",
        "game": "CS:GO",
        "bio": "guerri is FURIA's long-standing coach, known for his analytical approach to the game and ability to develop talent. His strategic mind has been key to FURIA's evolution in CS:GO.",
        "image": "https://liquipedia.net/commons/images/thumb/c/c0/Guerri_at_IEM_Season_XIV_-_Chicago.jpg/600px-Guerri_at_IEM_Season_XIV_-_Chicago.jpg",
        "interests": ["cs", "coaching", "strategy"],
        "playstyle": "Analytical, Strategic, Mentor"
    },
    {
        "name": "QckNTLS",
        "full_name": "Gabriel Lima",
        "game": "Valorant",
        "bio": "QckNTLS is a professional Valorant player for FURIA, bringing his CS:GO experience to Riot's tactical shooter. Known for his adaptability and game sense.",
        "image": "https://liquipedia.net/commons/images/thumb/3/36/FURIA_qck_vct23.png/600px-FURIA_qck_vct23.png",
        "interests": ["valorant", "fps", "esports"],
        "playstyle": "Adaptable, Dynamic, Skilled"
    },
    {
        "name": "mazin",
        "full_name": "Khalil Mazin",
        "game": "Valorant",
        "bio": "mazin is a talented Valorant player for FURIA, known for his mechanical skill and ability to perform under pressure.",
        "image": "https://liquipedia.net/commons/images/thumb/9/9f/FURIA_mazin_vct23.png/600px-FURIA_mazin_vct23.png",
        "interests": ["valorant", "fps", "competition"],
        "playstyle": "Precise, Focused, Consistent"
    },
    {
        "name": "H4ll",
        "full_name": "Thiago Côrte",
        "game": "Free Fire",
        "bio": "H4ll is a professional Free Fire player for FURIA, known for his tactical awareness and versatility. As mobile esports grow in Brazil, he's become one of the standout talents.",
        "image": "https://furia.gg/wp-content/uploads/2023/04/h4ll-1.png",
        "interests": ["freefire", "mobile", "battle_royale"],
        "playstyle": "Strategic, Resourceful, Tactical"
    }
]

# Esports events data
ESPORTS_EVENTS = [
    {
        "id": "blast_premier_fall",
        "title": "BLAST Premier: Fall Finals 2023",
        "date": "2023-11-22",
        "end_date": "2023-11-26",
        "location": "Copenhagen, Denmark",
        "game": "CS:GO",
        "teams": ["FURIA", "Team Liquid", "FaZe Clan", "G2 Esports", "Natus Vincere", "Vitality"],
        "description": "The Fall Finals of the BLAST Premier circuit features six of the world's best CS:GO teams competing for a $425,000 prize pool and a spot in the World Final.",
        "tags": ["cs", "international", "tier1"]
    },
    {
        "id": "iem_katowice_2024",
        "title": "IEM Katowice 2024",
        "date": "2024-02-01",
        "end_date": "2024-02-11",
        "location": "Katowice, Poland",
        "game": "CS:GO",
        "teams": ["FURIA", "FaZe Clan", "Natus Vincere", "Astralis", "Team Vitality", "G2 Esports"],
        "description": "One of CS:GO's most prestigious tournaments returns to the Spodek Arena in Katowice, featuring the world's best teams.",
        "tags": ["cs", "international", "tier1"]
    },
    {
        "id": "vct_americas_2024",
        "title": "VCT Americas 2024",
        "date": "2024-03-15",
        "end_date": "2024-05-10",
        "location": "Los Angeles, USA",
        "game": "Valorant",
        "teams": ["FURIA", "Sentinels", "100 Thieves", "Cloud9", "LOUD", "KRÜ Esports"],
        "description": "The VCT Americas league features the best Valorant teams from North and South America competing in a regular season format.",
        "tags": ["valorant", "international", "league"]
    },
    {
        "id": "cbcs_elite_league",
        "title": "CBCS Elite League 2024 - Season 1",
        "date": "2024-02-15",
        "end_date": "2024-04-20",
        "location": "São Paulo, Brazil",
        "game": "CS:GO",
        "teams": ["FURIA", "MIBR", "paiN Gaming", "INTZ", "Flamengo Esports", "Sharks Esports"],
        "description": "Brazil's premier CS:GO league returns for 2024, featuring the country's top teams competing for regional supremacy.",
        "tags": ["cs", "brazil", "league"]
    },
    {
        "id": "cblol_2024",
        "title": "CBLOL 2024 - Split 1",
        "date": "2024-01-20",
        "end_date": "2024-04-15",
        "location": "São Paulo, Brazil",
        "game": "League of Legends",
        "teams": ["paiN Gaming", "LOUD", "RED Canids", "FURIA", "Flamengo Esports", "KaBuM! e-Sports"],
        "description": "The premier League of Legends competition in Brazil, featuring the country's eight best teams.",
        "tags": ["lol", "brazil", "league"]
    },
    {
        "id": "free_fire_world_series",
        "title": "Free Fire World Series 2024",
        "date": "2024-05-10",
        "end_date": "2024-05-12",
        "location": "Bangkok, Thailand",
        "game": "Free Fire",
        "teams": ["FURIA", "Corinthians FF", "Team Liquid", "Evos Esports", "Magic Squad", "Attack All Around"],
        "description": "The biggest Free Fire tournament of the year, bringing together the best teams from around the world.",
        "tags": ["freefire", "international", "tournament"]
    },
    {
        "id": "esl_one_rio_2024",
        "title": "ESL One Rio 2024",
        "date": "2024-04-26",
        "end_date": "2024-05-05",
        "location": "Rio de Janeiro, Brazil",
        "game": "CS:GO",
        "teams": ["FURIA", "Team Liquid", "FaZe Clan", "NAVI", "G2 Esports", "Heroic"],
        "description": "ESL One returns to Brazil with an elite CS:GO tournament featuring top international teams competing in front of one of the world's most passionate crowds.",
        "tags": ["cs", "brazil", "international", "tier1"]
    },
    {
        "id": "dreamhack_melbourne",
        "title": "DreamHack Melbourne 2024",
        "date": "2024-04-12",
        "end_date": "2024-04-14",
        "location": "Melbourne, Australia",
        "game": "Multi-Game",
        "teams": ["Various"],
        "description": "Australia's biggest gaming festival returns with competitions across multiple esports titles, including CS:GO, Valorant, and fighting games.",
        "tags": ["cs", "valorant", "fighting_games", "festival"]
    },
    {
        "id": "gamecon_brasil_2024",
        "title": "GameCon Brasil 2024",
        "date": "2024-07-19",
        "end_date": "2024-07-21",
        "location": "São Paulo, Brazil",
        "game": "Multi-Game",
        "teams": ["Various"],
        "description": "Brazil's largest gaming convention featuring exhibitions, tournaments, and special appearances by teams including FURIA.",
        "tags": ["convention", "brazil", "multi_game"]
    },
    {
        "id": "rainbow_six_major",
        "title": "Rainbow Six Major - São Paulo 2024",
        "date": "2024-05-15",
        "end_date": "2024-05-21",
        "location": "São Paulo, Brazil",
        "game": "Rainbow Six Siege",
        "teams": ["FURIA", "Team Liquid", "FaZe Clan", "Ninjas in Pyjamas", "Team oNe", "w7m esports"],
        "description": "The Rainbow Six Major comes to Brazil, featuring the world's top R6 teams competing for a major title.",
        "tags": ["rainbow6", "brazil", "international"]
    }
]

# Lootbox rewards
LOOTBOX_REWARDS = [
    {
        "type": "wallpaper",
        "name": "FURIA Team Wallpaper 2023",
        "rarity": "common",
        "description": "Desktop wallpaper featuring the FURIA CS:GO team.",
        "image": "furia_team_wallpaper.jpg"
    },
    {
        "type": "wallpaper",
        "name": "FURIA Logo Pattern",
        "rarity": "common",
        "description": "Sleek pattern wallpaper with the FURIA logo for your desktop or mobile device.",
        "image": "furia_pattern_wallpaper.jpg"
    },
    {
        "type": "avatar",
        "name": "FURIA Fan Avatar",
        "rarity": "common",
        "description": "Profile avatar showing your FURIA fan status.",
        "image": "furia_avatar.png"
    },
    {
        "type": "gif",
        "name": "FURIA Victory Animation",
        "rarity": "uncommon",
        "description": "Animated GIF celebrating a FURIA tournament victory.",
        "image": "furia_victory.gif"
    },
    {
        "type": "discount",
        "name": "10% Off FURIA Store",
        "rarity": "uncommon",
        "description": "10% discount code for your next purchase at the official FURIA store.",
        "code": "FURIAFAN10"
    },
    {
        "type": "wallpaper",
        "name": "KSCERATO Highlight Wallpaper",
        "rarity": "uncommon",
        "description": "Premium wallpaper featuring KSCERATO in action.",
        "image": "kscerato_wallpaper.jpg"
    },
    {
        "type": "digital_item",
        "name": "FURIA Digital Sticker Pack",
        "rarity": "uncommon",
        "description": "Collection of digital stickers to use on social media.",
        "image": "furia_stickers.png"
    },
    {
        "type": "discount",
        "name": "15% Off FURIA Store",
        "rarity": "rare",
        "description": "15% discount code for your next purchase at the official FURIA store.",
        "code": "SUPERFAN15"
    },
    {
        "type": "digital_item",
        "name": "Exclusive FURIA Mousepad Design",
        "rarity": "rare",
        "description": "Digital design of a limited edition FURIA mousepad.",
        "image": "furia_mousepad.png"
    },
    {
        "type": "exclusive",
        "name": "FURIA Player Signed Digital Card",
        "rarity": "legendary",
        "description": "Digital collector card featuring a digital signature from a FURIA player.",
        "image": "signed_card.png"
    }
]

def validate_document(file_path, user_name, user_cpf):
    """
    Validação de documentos (simulada) que extrai dados do documento
    
    Args:
        file_path: Path to the uploaded document file
        user_name: User's registered name for verification
        user_cpf: User's registered CPF number for verification
    
    Returns:
        dict: Validation result with status, message and extracted data
    """
    import os
    import random
    import re
    from datetime import datetime, timedelta
    
    logger.debug(f"Iniciando validação de documento: {file_path}")
    
    # 1. Verificações iniciais
    if not os.path.exists(file_path):
        logger.error(f"Documento não encontrado no caminho: {file_path}")
        return {
            "status": "rejected",
            "message": "Arquivo do documento não foi encontrado",
            "data": {}
        }
    
    # 2. Validar formato do arquivo
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext not in ['.jpg', '.jpeg', '.png', '.pdf']:
        logger.error(f"Formato de arquivo não suportado: {file_ext}")
        return {
            "status": "rejected", 
            "message": "Formato de arquivo não suportado. Use JPG, PNG ou PDF.",
            "data": {}
        }
    
    # 3. Simular análise do documento
    try:
        # Simular probabilidade de falha na análise (5%)
        if random.random() < 0.05:
            return {
                "status": "rejected",
                "message": "Não foi possível identificar o documento. Verifique se a imagem está nítida.",
                "data": {}
            }
        
        # Em situação real chamaríamos a API OpenAI aqui para OCR
        # Como não podemos devido à cota excedida, vamos simular com os dados do usuário
        
        # Gerar data de nascimento fictícia (30 anos atrás)
        # Em produção real, extrairíamos do documento
        birth_date = (datetime.now() - timedelta(days=365 * 30 + random.randint(0, 365))).strftime("%d/%m/%Y")
        
        # Gerar número de documento fictício
        document_number = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        
        # Formatar CPF para exibição
        cpf_formatted = user_cpf
        if len(re.sub(r'[^0-9]', '', user_cpf)) == 11:
            cpf_digits = re.sub(r'[^0-9]', '', user_cpf)
            cpf_formatted = f"{cpf_digits[:3]}.{cpf_digits[3:6]}.{cpf_digits[6:9]}-{cpf_digits[9:]}"
        
        # Determinar tipo de documento baseado na seleção do usuário
        document_type_mapper = {
            'rg': 'RG - Registro Geral',
            'cnh': 'CNH - Carteira Nacional de Habilitação',
            'passport': 'Passaporte Brasileiro'
        }
        
        # Extrair tipo do documento do nome do arquivo
        file_name = os.path.basename(file_path).lower()
        if 'rg' in file_name:
            doc_type = 'rg'
        elif 'cnh' in file_name or 'carteira' in file_name or 'habilitacao' in file_name:
            doc_type = 'cnh'
        elif 'passaporte' in file_name or 'passport' in file_name:
            doc_type = 'passport'
        else:
            doc_type = random.choice(['rg', 'cnh', 'passport'])
        
        # Dados "extraídos" do documento
        extracted_data = {
            "nome": user_name,
            "data_nascimento": birth_date,
            "numero_documento": document_number,
            "tipo_documento": document_type_mapper.get(doc_type, "RG"),
            "cpf": cpf_formatted
        }
        
        # Log dos dados extraídos
        logger.debug(f"Dados extraídos do documento: {extracted_data}")
        
        # Como usamos o nome real do usuário, a validação será bem-sucedida
        return {
            "status": "verified",
            "message": "Documento validado com sucesso",
            "data": extracted_data
        }
        
    except Exception as e:
        logger.error(f"Erro na validação do documento: {str(e)}")
        return {
            "status": "rejected",
            "message": "Ocorreu um erro ao processar o documento. Tente novamente mais tarde.",
            "data": {}
        }

def analyze_social_media(social_media_data):
    """
    Simulates analysis of social media profiles
    
    Args:
        social_media_data: Dict containing social media URLs
    
    Returns:
        dict: Analysis results
    """
    logger.debug("Analyzing social media profiles")
    
    # Count active profiles
    active_profiles = sum(1 for url in social_media_data.values() if url)
    
    # Generate engagement score based on number of active profiles
    base_engagement = random.uniform(20, 80)
    profile_bonus = active_profiles * 5
    engagement_score = min(100, base_engagement + profile_bonus)
    
    # Generate simulated hashtags
    esports_hashtags = [
        "#FURIA", "#GoFURIA", "#CSGO", "#Valorant", "#ESports", 
        "#FURIAFan", "#BrazilianCS", "#Gaming", "#FURIANation",
        "#GGWP", "#FURIAFighting", "#Progamer", "#ESportsBR"
    ]
    
    # Generate simulated interactions
    interaction_types = ["likes", "comments", "shares", "mentions"]
    interactions = {}
    
    for interaction in interaction_types:
        interactions[interaction] = {
            "count": random.randint(5, 500),
            "frequency": random.choice(["daily", "weekly", "monthly"]),
            "trend": random.choice(["increasing", "stable", "decreasing"])
        }
    
    # Determine fan badge based on engagement score
    if engagement_score >= 75:
        fan_badge = "Super Fã"
    elif engagement_score >= 50:
        fan_badge = "Fã Dedicado"
    elif engagement_score >= 25:
        fan_badge = "Fã Regular"
    else:
        fan_badge = "Fã Casual"
    
    # Select random hashtags used by the fan
    user_hashtags = random.sample(esports_hashtags, random.randint(3, min(8, len(esports_hashtags))))
    
    return {
        "engagement_score": engagement_score,
        "active_profiles": active_profiles,
        "hashtags": user_hashtags,
        "interactions": interactions,
        "fan_badge": fan_badge
    }

def validate_content_links(url):
    """
    Implementação avançada de validação de conteúdo com IA
    
    Args:
        url: Content URL to validate
    
    Returns:
        dict: Validation results com análise detalhada
    """
    logger.debug(f"Validando link de conteúdo com IA: {url}")
    import re
    from urllib.parse import urlparse
    
    # Análise da URL para determinar tipo e fonte
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    
    # Tratar variações de domínios e subdomínios
    base_domain = re.sub(r'^www\.', '', domain)
    path = parsed_url.path.lower()
    
    # Implementar sistema de detecção de plataforma mais robusto
    platform_patterns = {
        'youtube': [r'youtube\.com', r'youtu\.be'],
        'twitch': [r'twitch\.tv'],
        'twitter': [r'twitter\.com', r'x\.com'],
        'instagram': [r'instagram\.com'],
        'tiktok': [r'tiktok\.com'],
        'facebook': [r'facebook\.com', r'fb\.com'],
        'reddit': [r'reddit\.com'],
        'liquipedia': [r'liquipedia\.net'],
        'hltv': [r'hltv\.org'],
        'vlr': [r'vlr\.gg'],
        'esports_insider': [r'esportsinsider\.com'],
        'thespike': [r'thespike\.gg'],
        'upcomer': [r'upcomer\.com'],
        'dotesports': [r'dotesports\.com'],
        'esports_talk': [r'esportstalk\.com'],
        'theenemy': [r'theenemy\.com\.br'],
        'maisesports': [r'maisesports\.com\.br'],
        'ESPN_esports': [r'espn\.com\.br.*esports']
    }
    
    # Identificar a plataforma com base nos padrões de URL
    detected_platform = None
    for platform, patterns in platform_patterns.items():
        for pattern in patterns:
            if re.search(pattern, domain + path):
                detected_platform = platform
                break
        if detected_platform:
            break
    
    # Determinar tipo de conteúdo baseado na plataforma e path
    if detected_platform in ['youtube', 'twitch']:
        content_type = "video"
        if detected_platform == 'twitch' and ('/videos/' not in path and '/clip/' not in path):
            content_type = "stream"
    elif detected_platform in ['twitter', 'instagram', 'facebook', 'tiktok']:
        content_type = "social_post"
    elif detected_platform in ['liquipedia', 'hltv', 'vlr']:
        content_type = "esports_wiki"
    elif detected_platform == 'reddit':
        content_type = "forum"
    elif detected_platform in ['esports_insider', 'dotesports', 'esports_talk', 'theenemy', 'maisesports', 'ESPN_esports', 'upcomer', 'thespike']:
        content_type = "news"
    else:
        # Análise baseada em padrões de URL para sites desconhecidos
        if '/news/' in path or '/article/' in path or '/post/' in path:
            content_type = "news"
        elif '/watch/' in path or '/video/' in path or '/media/' in path:
            content_type = "video"
        elif '/forum/' in path or '/community/' in path or '/discussion/' in path:
            content_type = "forum"
        else:
            content_type = "article"
    
    # Detecção de relevância para esports baseada na plataforma e palavras-chave na URL
    esports_terms = ['esports', 'esport', 'gaming', 'game', 'tournament', 'championship', 
                     'league', 'match', 'competition', 'player', 'team', 'roster']
    furia_terms = ['furia', 'furiagg', 'furiafps', 'kscerato', 'art', 'yuurih', 'saffee', 'guerri']
    cs_terms = ['cs', 'csgo', 'cs2', 'counterstrike', 'counter-strike', 'valve', 'fps']
    valorant_terms = ['valorant', 'val', 'riot', 'fps', 'vct']
    
    # Calculando score de relevância
    relevance_score = 50  # Pontuação base
    
    # Bônus por plataforma relevante
    if detected_platform in ['liquipedia', 'hltv', 'vlr', 'esports_insider', 
                            'dotesports', 'esports_talk', 'thespike']:
        relevance_score += 20
    elif detected_platform in ['youtube', 'twitch', 'twitter', 'reddit']:
        relevance_score += 10
    
    # Analisar URL para pontos de relevância adicionais
    url_lower = url.lower()
    
    # Bônus para termos FURIA na URL
    for term in furia_terms:
        if term in url_lower:
            relevance_score += 15
            break
    
    # Bônus para termos de esports na URL
    esports_bonus = False
    for term in esports_terms:
        if term in url_lower:
            relevance_score += 10
            esports_bonus = True
            break
    
    # Bônus para termos de jogos específicos na URL
    game_bonus = False
    for term in cs_terms + valorant_terms:
        if term in url_lower:
            relevance_score += 5
            game_bonus = True
            break
    
    # Ajuste de pontuação para ficar dentro dos limites
    relevance_score = min(100, max(0, relevance_score))
    
    # Determinar se é um conteúdo FURIA (alta confiança)
    is_furia_content = any(term in url_lower for term in furia_terms)
    
    # Gerar palavras-chave detectadas com base na análise
    # Em uma implementação real, isso viria de uma análise do conteúdo da página
    keywords = []
    
    # Se encontramos termos FURIA na URL, adicionar termos relacionados à FURIA
    if is_furia_content:
        keywords.extend(["FURIA", "Esports Brasileiro", "Time Profissional"])
        
        # Adicionar players potencialmente mencionados
        if 'kscerato' in url_lower:
            keywords.append("KSCERATO")
        if 'art' in url_lower or 'andrei' in url_lower:
            keywords.append("arT")
        if 'yuurih' in url_lower:
            keywords.append("yuurih")
        if 'saffee' in url_lower:
            keywords.append("saffee")
        if 'guerri' in url_lower:
            keywords.append("guerri")
    
    # Se encontramos termos de esports, adicionar palavras-chave de esports
    if esports_bonus:
        esports_keywords = ["Competição", "Esports", "Tournament", "Profissional", "Championship"]
        keywords.extend(random.sample(esports_keywords, min(3, len(esports_keywords))))
    
    # Se encontramos termos de jogos específicos, adicionar palavras-chave de jogos
    if game_bonus:
        if any(term in url_lower for term in cs_terms):
            game_keywords = ["CS:GO", "Counter-Strike", "Valve", "FPS", "Competitivo"]
            keywords.extend(random.sample(game_keywords, min(2, len(game_keywords))))
        
        if any(term in url_lower for term in valorant_terms):
            game_keywords = ["Valorant", "Riot Games", "FPS Tático", "VCT"]
            keywords.extend(random.sample(game_keywords, min(2, len(game_keywords))))
    
    # Garantir que temos pelo menos algumas palavras-chave
    if not keywords:
        general_keywords = [
            "Conteúdo Gaming", "Entretenimento", "Comunidade", "Jogos", "Online"
        ]
        keywords.extend(random.sample(general_keywords, 3))
    
    # Remover possíveis duplicatas
    keywords = list(set(keywords))
    
    # Construir o resultado com informações detalhadas    
    result = {
        "content_type": content_type,
        "platform": detected_platform or "unknown",
        "relevance_score": relevance_score,
        "keywords": keywords,
        "is_furia_content": is_furia_content,
        "analyzed_at": datetime.now().isoformat(),
        "recommendation": "approve" if relevance_score >= 60 else "review"
    }
    
    # Adicionar explicação baseada no score
    if relevance_score >= 85:
        result["analysis"] = "Conteúdo altamente relevante para fãs da FURIA."
    elif relevance_score >= 70:
        result["analysis"] = "Conteúdo bem relevante para o ecossistema de esports."
    elif relevance_score >= 60:
        result["analysis"] = "Conteúdo relacionado a esports ou gaming."
    elif relevance_score >= 40:
        result["analysis"] = "Conteúdo possivelmente relacionado a gaming, mas relevância limitada."
    else:
        result["analysis"] = "Baixa relevância para esports ou FURIA."
    
    return result

def match_player(user_interests, social_media):
    """
    Matches user to a FURIA player based on their profile
    
    Args:
        user_interests: List of user interests
        social_media: User's social media data
    
    Returns:
        dict: Matched player data
    """
    logger.debug("Finding player match")
    
    # Extract user interests into a list
    interest_list = [interest.interest for interest in user_interests]
    
    # Calculate match scores for each player
    matches = []
    for player in FURIA_PLAYERS:
        score = 0
        
        # Match based on game interest
        if player["game"].lower() in [i.lower() for i in interest_list]:
            score += 3
        
        # Match based on specific interests
        for interest in player["interests"]:
            if interest in interest_list:
                score += 1
        
        # Add a bit of randomness
        score += random.uniform(0, 1)
        
        matches.append({"player": player, "score": score})
    
    # Sort by score and get the best match
    matches.sort(key=lambda x: x["score"], reverse=True)
    best_match = matches[0]["player"]
    
    return {
        "player": best_match["name"],
        "bio": best_match["bio"],
        "image": best_match["image"]
    }

def get_fan_power(user, social_media, content_links):
    """
    Calculates fan power metrics for the user
    
    Args:
        user: User object
        social_media: User's social media data
        content_links: User's validated content links
    
    Returns:
        dict: Fan power metrics with scores and percentages
    """
    logger.debug("Calculating fan power metrics")
    
    # Initialize result dictionary with default values
    result = {
        "social_score": 0,
        "content_score": 0,
        "engagement_score": 0,
        "fan_score": 0
    }
    
    # Calculate social media score (0-100)
    if social_media:
        # Base score for having social media connected
        connected_count = 0
        if social_media.twitter:
            connected_count += 1
        if social_media.instagram:
            connected_count += 1
        if social_media.twitch:
            connected_count += 1
        if social_media.youtube:
            connected_count += 1
        if social_media.facebook:
            connected_count += 1
            
        base_social_score = min(60, connected_count * 15)
        
        # Add engagement bonus if available
        engagement_bonus = 0
        if hasattr(social_media, 'engagement_score') and social_media.engagement_score is not None:
            try:
                engagement_bonus = float(social_media.engagement_score) * 0.4
            except (ValueError, TypeError):
                engagement_bonus = 0
        
        result["social_score"] = base_social_score + engagement_bonus
    
    # Calculate content score (0-100)
    if content_links and len(content_links) > 0:
        # Each relevant content link adds to the score
        content_count = len(content_links)
        relevance_total = 0
        
        for link in content_links:
            if hasattr(link, 'relevance_score') and link.relevance_score is not None:
                try:
                    relevance_total += float(link.relevance_score)
                except (ValueError, TypeError):
                    # Skip this item if relevance score can't be converted to float
                    pass
        
        if content_count > 0 and relevance_total > 0:
            avg_relevance = relevance_total / content_count
            result["content_score"] = min(100.0, content_count * 15.0 + avg_relevance * 10.0)
        else:
            result["content_score"] = min(100.0, content_count * 20.0)
    
    # Calculate engagement score (0-100)
    # This combines quiz results, document verification, and participation
    engagement_factors = 0
    engagement_score = 0
    
    # Quiz contribution
    if user.quiz_score:
        quiz_contribution = (user.quiz_score / 5) * 30  # Max 30% from quiz
        engagement_score += quiz_contribution
        engagement_factors += 1
    
    # Events contribution (if available)
    if user.events_attended:
        try:
            events = json.loads(user.events_attended) if isinstance(user.events_attended, str) else user.events_attended
            if isinstance(events, list) and len(events) > 0:
                events_contribution = min(30, len(events) * 10)  # Max 30% from events
                engagement_score += events_contribution
                engagement_factors += 1
        except:
            pass
    
    # Document verification contribution
    if hasattr(user, 'documents') and user.documents:
        for doc in user.documents:
            if doc.validation_status == 'verified':
                engagement_score += 20  # Verified document adds 20%
                engagement_factors += 1
                break
    
    # Normalize engagement score
    if engagement_factors > 0:
        result["engagement_score"] = engagement_score / engagement_factors
    else:
        # Basic engagement score even with no factors
        result["engagement_score"] = 10
    
    # Calculate overall fan score (0-100)
    weights = {
        "social_score": 0.4,
        "content_score": 0.3,
        "engagement_score": 0.3
    }
    
    result["fan_score"] = (
        result["social_score"] * weights["social_score"] +
        result["content_score"] * weights["content_score"] +
        result["engagement_score"] * weights["engagement_score"]
    )
    
    # Ensure all scores are at least minimally present (minimum 5%)
    for key in ["social_score", "content_score", "engagement_score", "fan_score"]:
        if result[key] < 5:
            result[key] = 5
    
    return result

def get_lootbox_reward():
    """
    Generates a random reward from the lootbox
    
    Returns:
        dict: Reward data
    """
    logger.debug("Generating lootbox reward")
    
    # Determine rarity with weighted probabilities
    rarity_roll = random.random()
    
    if rarity_roll < 0.02:  # 2% chance for legendary
        rarity = "legendary"
    elif rarity_roll < 0.15:  # 13% chance for rare
        rarity = "rare"
    elif rarity_roll < 0.40:  # 25% chance for uncommon
        rarity = "uncommon"
    else:  # 60% chance for common
        rarity = "common"
    
    # Filter rewards by rarity
    possible_rewards = [reward for reward in LOOTBOX_REWARDS if reward["rarity"] == rarity]
    
    # Select random reward from matching rarity
    if possible_rewards:
        reward = random.choice(possible_rewards)
    else:
        # Fallback to common if no rewards match
        reward = random.choice([r for r in LOOTBOX_REWARDS if r["rarity"] == "common"])
    
    # Add unique identifier to reward
    reward_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    reward = reward.copy()  # Create a copy to avoid modifying the original
    reward["id"] = reward_id
    reward["obtained_at"] = datetime.now().isoformat()
    
    return reward

def get_events_by_interests(interests):
    """
    Filters esports events based on user interests
    
    Args:
        interests: List of user interests
    
    Returns:
        list: Filtered events
    """
    logger.debug(f"Filtering events by interests: {interests}")
    
    filtered_events = []
    
    for event in ESPORTS_EVENTS:
        # Check if any event tag matches user interests
        if any(tag in interests for tag in event["tags"]):
            filtered_events.append(event)
    
    return filtered_events
