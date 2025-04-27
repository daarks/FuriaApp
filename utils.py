import random
import json
import logging
from datetime import datetime, timedelta
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
    Validação de documentos utilizando IA/OCR
    
    Args:
        file_path: Caminho para o arquivo do documento
        user_name: Nome registrado do usuário
        user_cpf: CPF registrado do usuário
    
    Returns:
        dict: Resultado da validação com status e mensagem
    """
    logger.debug(f"Validando documento: {file_path}")
    
    try:
        # Importar o serviço de IA para documentos
        from services.document_ai import document_ai
        
        # Preparar dados do usuário
        user_data = {
            "name": user_name,
            "cpf": user_cpf
        }
        
        # Usar IA para validar o documento
        result = document_ai.validate_document(file_path, user_data)
        
        # Traduzir mensagens de status para português
        if result["status"] == "verified":
            result["message"] = "Documento validado com sucesso!"
        elif result["status"] == "pending":
            result["message"] = "Documento em análise. Alguns dados precisam de verificação adicional."
        elif result["status"] == "rejected":
            if "qualidade" in result["message"].lower() or "quality" in result["message"].lower():
                result["message"] = "A qualidade da imagem do documento é muito baixa para verificação."
            elif "correspondem" in result["message"].lower() or "match" in result["message"].lower():
                result["message"] = "Os dados no documento não correspondem às informações registradas."
            elif "incompleto" in result["message"].lower() or "incomplete" in result["message"].lower():
                result["message"] = "O documento parece estar incompleto ou parcialmente visível."
            else:
                result["message"] = "Documento rejeitado. " + result["message"]
        
        return result
    
    except Exception as e:
        logger.error(f"Erro durante validação de documento: {str(e)}")
        
        # Retornar resposta de fallback em caso de falha no serviço de IA
        return {
            "status": "rejected",
            "message": "Erro ao processar documento. Por favor, tente novamente com uma imagem mais clara.",
            "extracted_data": {
                "confidence_score": 0.0,
                "error": str(e)
            }
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
    Simulates validation of content links
    
    Args:
        url: Content URL to validate
    
    Returns:
        dict: Validation results
    """
    logger.debug(f"Validating content link: {url}")
    
    # Determine content type based on URL
    if "youtube.com" in url or "youtu.be" in url:
        content_type = "video"
    elif "twitch.tv" in url:
        content_type = "stream"
    elif "twitter.com" in url or "x.com" in url:
        content_type = "social_post"
    elif "instagram.com" in url:
        content_type = "social_post"
    elif "liquipedia.net" in url or "hltv.org" in url:
        content_type = "esports_wiki"
    elif "reddit.com/r/" in url:
        content_type = "forum"
    else:
        content_type = "article"
    
    # Generate random relevance score
    relevance_score = random.randint(60, 100)
    
    # Generate simulated keywords found in content
    all_keywords = [
        "FURIA", "esports", "CS:GO", "Valorant", "Brazil", "tournament",
        "championship", "KSCERATO", "arT", "yuurih", "saffee", "guerri",
        "tactic", "strategy", "team", "player", "competition", "match",
        "win", "lose", "score", "clutch", "ace", "highlight"
    ]
    
    # Select random keywords
    keywords = random.sample(all_keywords, random.randint(5, 10))
    
    return {
        "content_type": content_type,
        "relevance_score": relevance_score,
        "keywords": keywords,
        "analyzed_at": datetime.now().isoformat()
    }

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
    logger.debug("Filtering events by user interests")
    
    # Convert string interests to list if needed
    if isinstance(interests, str):
        try:
            interests = json.loads(interests)
        except:
            interests = [interests]
    
    # Handle UserInterest objects from database
    if hasattr(interests[0], 'interest') if interests else False:
        interest_values = [interest.interest for interest in interests]
    else:
        interest_values = interests
    
    # Convert to lowercase for case-insensitive matching
    interest_values = [i.lower() for i in interest_values if i]
    
    # Match events with relevant tags
    matched_events = []
    for event in ESPORTS_EVENTS:
        # Case-insensitive tag matching
        event_tags = [tag.lower() for tag in event["tags"]]
        game_tag = event["game"].lower().replace(" ", "").replace("-", "").replace(":", "")
        
        # Add the game as an implicit tag
        event_tags.append(game_tag)
        
        # Check if any user interest matches event tags
        if any(interest in event_tags for interest in interest_values):
            matched_events.append(event)
        
        # Also match substrings (e.g. "cs" matches "csgo")
        elif any(any(interest in tag for interest in interest_values) for tag in event_tags):
            matched_events.append(event)
    
    # If no matches, return a few random events
    if not matched_events:
        matched_events = random.sample(ESPORTS_EVENTS, min(3, len(ESPORTS_EVENTS)))
    
    # Sort events by date
    matched_events.sort(key=lambda e: e["date"])
    
    return matched_events

# Dados para gerar matches do Bolão
MATCH_OPPONENTS = [
    "MIBR", "paiN Gaming", "Liquid", "Cloud9", "FaZe", "G2", 
    "Astralis", "Natus Vincere", "Vitality", "NIP", "Complexity",
    "Imperial", "00Nation", "NAVI", "Evil Geniuses", "LOUD", 
    "Sentinels", "DRX", "KRÜ Esports", "Fnatic", "TSM"
]

TOURNAMENTS = [
    "ESL Pro League", "BLAST Premier", "IEM Cologne", "IEM Katowice", 
    "Major Championship", "ESL One", "Flashpoint", "CBCS", "PGL Major", 
    "VCT Americas", "VCT Champions", "VCT Masters", "CBLOL"
]

CS_MAPS = ["Inferno", "Mirage", "Nuke", "Ancient", "Overpass", "Vertigo", "Anubis"]
VALORANT_MAPS = ["Ascent", "Bind", "Haven", "Split", "Icebox", "Breeze", "Fracture", "Pearl", "Lotus"]
LOL_MAPS = ["Summoner's Rift"]

def generate_demo_matches(num_matches=5):
    """
    Gera partidas de demonstração para o Bolão da FURIA
    
    Args:
        num_matches: Número de partidas a serem geradas
        
    Returns:
        list: Lista de dicionários contendo dados das partidas
    """
    matches = []
    now = datetime.now()
    
    for i in range(num_matches):
        # Determinar o jogo (game) da partida
        game = random.choice(["CS:GO", "Valorant", "League of Legends"])
        
        # Selecionar o adversário
        opponent = random.choice(MATCH_OPPONENTS)
        
        # Selecionar o formato da partida
        if game == "CS:GO":
            match_format = random.choice(["BO1", "BO3", "BO5"])
            map_pool = random.sample(CS_MAPS, min(5, len(CS_MAPS)))
        elif game == "Valorant":
            match_format = random.choice(["BO3", "BO5"])
            map_pool = random.sample(VALORANT_MAPS, min(5, len(VALORANT_MAPS)))
        else:  # League of Legends
            match_format = random.choice(["BO1", "BO3", "BO5"])
            map_pool = LOL_MAPS
            
        # Determinar data e hora (algumas no passado, atual e futuro)
        days_offset = random.randint(-3, 15)  # -3 a -1 = passado, 0 = hoje, 1 a 15 = futuro
        hours_offset = random.randint(0, 23)
        minutes_offset = random.choice([0, 15, 30, 45])
        
        match_time = now + timedelta(days=days_offset, hours=hours_offset, minutes=minutes_offset)
        match_time = match_time.replace(second=0, microsecond=0)  # Arredondar para minutos
        
        # Construir o objeto de partida
        match = {
            "opponent": opponent,
            "game": game,
            "tournament": random.choice(TOURNAMENTS),
            "match_time": match_time,
            "format": match_format,
            "map_pool": json.dumps(map_pool) if isinstance(map_pool, list) else json.dumps([map_pool]),
            "status": "completed" if days_offset < 0 else "scheduled",
        }
        
        # Adicionar resultados para partidas já realizadas
        if match["status"] == "completed":
            # Determinar o resultado aleatoriamente (com viés para FURIA vencer)
            if random.random() < 0.6:  # 60% chance de FURIA vencer
                if match_format == "BO1":
                    match["furia_score"] = 1
                    match["opponent_score"] = 0
                elif match_format == "BO3":
                    match["furia_score"] = 2
                    match["opponent_score"] = random.choice([0, 1])
                else:  # BO5
                    match["furia_score"] = 3
                    match["opponent_score"] = random.randint(0, 2)
            else:  # 40% chance de FURIA perder
                if match_format == "BO1":
                    match["furia_score"] = 0
                    match["opponent_score"] = 1
                elif match_format == "BO3":
                    match["furia_score"] = random.choice([0, 1])
                    match["opponent_score"] = 2
                else:  # BO5
                    match["furia_score"] = random.randint(0, 2)
                    match["opponent_score"] = 3
                    
            # Adicionar MVP da FURIA e destaque do adversário
            cs_players = [p["name"] for p in FURIA_PLAYERS if p["game"] == "CS:GO"]
            valorant_players = [p["name"] for p in FURIA_PLAYERS if p["game"] == "Valorant"]
            lol_players = [p["name"] for p in FURIA_PLAYERS if p["game"] == "League of Legends"]
            
            if game == "CS:GO":
                match["mvp"] = random.choice(cs_players) if cs_players else "KSCERATO"
            elif game == "Valorant":
                match["mvp"] = random.choice(valorant_players) if valorant_players else "QA7"
            else:  # League of Legends
                match["mvp"] = random.choice(lol_players) if lol_players else "RedBert"
                
            # Gerar nomes fictícios para destaque do adversário
            common_nicknames = ["steel", "fallen", "cold", "tarik", "s1mple", "device", "niko", 
                             "tenz", "sinatraa", "shahzam", "scream", "hiko", "faker", "bjergsen"]
            match["opponent_highlight"] = random.choice(common_nicknames)
            
        matches.append(match)
        
    return matches

def calculate_prediction_points(prediction, match):
    """
    Calcula os pontos de uma previsão com base no resultado real da partida
    
    Args:
        prediction: Objeto MatchPrediction
        match: Objeto Match
        
    Returns:
        dict: Pontuação detalhada
    """
    if match.status != 'completed':
        return {
            "score_prediction_points": 0,
            "mvp_prediction_points": 0,
            "highlight_prediction_points": 0,
            "total_points": 0,
            "message": "A partida ainda não foi realizada"
        }
    
    score_points = 0
    mvp_points = 0
    highlight_points = 0
    
    # Avalia previsão de pontuação
    if prediction.furia_score == match.furia_score and prediction.opponent_score == match.opponent_score:
        # Placar exato - 3 pontos
        score_points = 3
    elif (prediction.furia_score > prediction.opponent_score and match.furia_score > match.opponent_score) or \
         (prediction.furia_score < prediction.opponent_score and match.furia_score < match.opponent_score) or \
         (prediction.furia_score == prediction.opponent_score and match.furia_score == match.opponent_score):
        # Acertou o vencedor - 1 ponto
        score_points = 1
    
    # Avalia previsão de MVP
    if prediction.predicted_mvp and match.mvp and prediction.predicted_mvp.lower() == match.mvp.lower():
        # MVP correto - 2 pontos
        mvp_points = 2
    
    # Avalia previsão de destaque do adversário
    if prediction.predicted_opponent_highlight and match.opponent_highlight and \
       prediction.predicted_opponent_highlight.lower() == match.opponent_highlight.lower():
        # Destaque adversário correto - 1 ponto
        highlight_points = 1
    
    total_points = score_points + mvp_points + highlight_points
    
    return {
        "score_prediction_points": score_points,
        "mvp_prediction_points": mvp_points,
        "highlight_prediction_points": highlight_points,
        "total_points": total_points,
        "message": "Pontuação calculada com sucesso"
    }

def get_furia_players_by_game(game):
    """
    Retorna a lista de jogadores da FURIA para um determinado jogo
    
    Args:
        game: Nome do jogo (CS:GO, Valorant, etc.)
        
    Returns:
        list: Lista de nomes de jogadores
    """
    game = game.lower().replace(":", "").replace("-", "").strip()
    
    if game == "csgo" or game == "cs":
        game = "CS:GO"
    elif game == "lol":
        game = "League of Legends"
    
    return [p["name"] for p in FURIA_PLAYERS if p["game"] == game]
