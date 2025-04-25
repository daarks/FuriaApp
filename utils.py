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
    Simulates document validation using OCR/AI
    
    Args:
        file_path: Path to the uploaded document
        user_name: User's registered name
        user_cpf: User's registered CPF
    
    Returns:
        dict: Validation result with status and message
    """
    logger.debug(f"Validating document: {file_path}")
    
    # Simulate OCR analysis
    # In a real implementation, this would use actual OCR libraries
    
    # Generate random validation data with 70% chance of success
    success = random.random() > 0.3
    
    if success:
        # Simulate extracting correct information
        extracted_name = user_name
        extracted_cpf = user_cpf
        confidence_score = random.uniform(0.85, 0.99)
        
        return {
            "status": "verified",
            "message": "Document successfully validated",
            "extracted_data": {
                "name": extracted_name,
                "cpf": extracted_cpf,
                "confidence_score": confidence_score
            }
        }
    else:
        # Simulate extraction failure or mismatch
        failure_type = random.choice(["poor_quality", "data_mismatch", "incomplete_document"])
        
        if failure_type == "poor_quality":
            return {
                "status": "rejected",
                "message": "Document image quality is too low for verification",
                "extracted_data": {
                    "confidence_score": random.uniform(0.3, 0.6)
                }
            }
        elif failure_type == "data_mismatch":
            # Simulate slight name variation
            name_parts = user_name.split()
            if len(name_parts) > 1:
                extracted_name = f"{name_parts[0]} {''.join([p[0] + '.' for p in name_parts[1:]])}"
            else:
                extracted_name = user_name
                
            # Generate slightly modified CPF
            cpf_digits = user_cpf.replace('.', '').replace('-', '')
            modified_cpf = list(cpf_digits)
            modified_cpf[random.randint(0, len(modified_cpf)-1)] = str(random.randint(0, 9))
            modified_cpf = ''.join(modified_cpf)
            
            return {
                "status": "rejected",
                "message": "Data in the document doesn't match registered information",
                "extracted_data": {
                    "name": extracted_name,
                    "cpf": modified_cpf,
                    "confidence_score": random.uniform(0.7, 0.85)
                }
            }
        else:  # incomplete_document
            return {
                "status": "rejected",
                "message": "Document appears to be incomplete or partially visible",
                "extracted_data": {
                    "name": user_name if random.random() > 0.5 else None,
                    "cpf": None,
                    "confidence_score": random.uniform(0.4, 0.7)
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
        dict: Fan power metrics
    """
    logger.debug("Calculating fan power metrics")
    
    # Base metrics
    metrics = {
        "social_engagement": 0,
        "content_consumption": 0,
        "event_participation": 0,
        "merchandise_support": 0,
        "overall_score": 0
    }
    
    # Calculate social engagement
    if social_media:
        metrics["social_engagement"] = social_media.engagement_score
    
    # Calculate content consumption
    if content_links:
        relevance_scores = [link.relevance_score for link in content_links]
        if relevance_scores:
            metrics["content_consumption"] = sum(relevance_scores) / len(relevance_scores)
    
    # Calculate event participation
    if user.events_attended:
        events = json.loads(user.events_attended)
        metrics["event_participation"] = min(100, len(events) * 20)
    
    # Calculate merchandise support
    if user.purchases:
        purchases = json.loads(user.purchases)
        metrics["merchandise_support"] = min(100, len(purchases) * 15)
    
    # Calculate overall score
    weights = {
        "social_engagement": 0.35,
        "content_consumption": 0.25,
        "event_participation": 0.25,
        "merchandise_support": 0.15
    }
    
    overall_score = sum(metrics[key] * weights[key] for key in weights.keys())
    metrics["overall_score"] = overall_score
    
    # Determine fan category
    if overall_score >= 70:
        metrics["fan_category"] = "Super Fã"
    elif overall_score >= 40:
        metrics["fan_category"] = "Intermediário"
    else:
        metrics["fan_category"] = "Novato"
    
    return metrics

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
