"""
Configurações para integrações OAuth com redes sociais.
"""
import os

# Plataformas suportadas
SUPPORTED_PLATFORMS = ['facebook', 'twitter', 'instagram', 'discord']

# Nomes de exibição das plataformas
PLATFORM_NAMES = {
    'facebook': 'Facebook',
    'twitter': 'Twitter/X',
    'instagram': 'Instagram',
    'discord': 'Discord'
}

# URI de redirecionamento padrão
OAUTH_REDIRECT_URI = "https://{domain}/oauth/callback/{provider}"

# Credenciais para cada plataforma
# Nota: Valores reais virão de variáveis de ambiente
OAUTH_CREDENTIALS = {
    'facebook': {
        'id': os.environ.get('FACEBOOK_CLIENT_ID', ''),
        'secret': os.environ.get('FACEBOOK_CLIENT_SECRET', ''),
        'authorize_url': 'https://www.facebook.com/v18.0/dialog/oauth',
        'access_token_url': 'https://graph.facebook.com/v18.0/oauth/access_token',
        'api_base_url': 'https://graph.facebook.com/v18.0/',
        'scope': ['email', 'public_profile', 'user_likes', 'user_posts'],
        'request_token_params': {'display': 'popup'},
    },
    'twitter': {
        'id': os.environ.get('TWITTER_CLIENT_ID', ''),
        'secret': os.environ.get('TWITTER_CLIENT_SECRET', ''),
        'authorize_url': 'https://twitter.com/i/oauth2/authorize',
        'access_token_url': 'https://api.twitter.com/2/oauth2/token',
        'api_base_url': 'https://api.twitter.com/2/',
        'scope': ['tweet.read', 'users.read', 'follows.read'],
        'request_token_params': {'code_challenge_method': 'S256', 'response_type': 'code'},
    },
    'instagram': {
        'id': os.environ.get('INSTAGRAM_CLIENT_ID', ''),
        'secret': os.environ.get('INSTAGRAM_CLIENT_SECRET', ''),
        'authorize_url': 'https://api.instagram.com/oauth/authorize',
        'access_token_url': 'https://api.instagram.com/oauth/access_token',
        'api_base_url': 'https://graph.instagram.com/',
        'scope': ['user_profile', 'user_media'],
    },
    'discord': {
        'id': os.environ.get('DISCORD_CLIENT_ID', ''),
        'secret': os.environ.get('DISCORD_CLIENT_SECRET', ''),
        'authorize_url': 'https://discord.com/api/oauth2/authorize',
        'access_token_url': 'https://discord.com/api/oauth2/token',
        'api_base_url': 'https://discord.com/api/',
        'scope': ['identify', 'guilds'],
    }
}

# Endpoints para informações de usuário
USER_INFO_ENDPOINTS = {
    'facebook': 'me?fields=id,name,email',
    'twitter': 'users/me?user.fields=id,name,username,profile_image_url',
    'instagram': 'me?fields=id,username',
    'discord': 'users/@me'
}

# Endpoints para buscar conexões relacionadas a esports
CONNECTIONS_ENDPOINTS = {
    'facebook': {
        'likes': 'me/likes?fields=id,name,category',
        'posts': 'me/posts?fields=id,message,created_time'
    },
    'twitter': {
        'following': 'users/{user_id}/following?user.fields=id,name,username,description',
        'tweets': 'users/{user_id}/tweets?tweet.fields=id,text,created_at'
    },
    'instagram': {
        'media': 'me/media?fields=id,caption,permalink,timestamp'
    },
    'discord': {
        'guilds': 'users/@me/guilds'
    }
}

# Palavras-chave relacionadas a esports
ESPORTS_KEYWORDS = [
    'esports', 'esport', 'e-sports', 'e-sport',
    'cs', 'csgo', 'counter-strike', 'cs2', 
    'valorant', 'val',
    'lol', 'league of legends',
    'dota', 'dota2',
    'fortnite', 'fn',
    'apex', 'apex legends',
    'overwatch', 'ow',
    'rainbow6', 'r6', 'rainbow six',
    'freefire', 'free fire', 'ff',
    'rocket league', 'rl',
    'hearthstone', 'hs',
    'fifa', 'ea fc',
    'pubg', 'warzone',
    'halo', 'call of duty', 'cod',
    'pro player', 'streamer', 'gamer', 'gaming',
    'twitch', 'tournament', 'championship', 'major',
    'furia', 'furiaggg', 'furiagg', 'mibr', 'liquid', 'cloud9', 'cloud 9', 'c9',
    'navi', 'astralis', 'fnatic', 'g2', 'eg', 'evil geniuses',
    'paiN', 'loud', 'los grandes', 'fluxo'
]

# Organizações e times de esports para identificação direta
ESPORTS_ORGANIZATIONS = {
    'facebook': [
        # IDs de páginas oficiais no Facebook
        '300327796685506',  # FURIA
        '184454441592062',  # MIBR
        '162545097240191',  # Team Liquid
        '227582193957130',  # Cloud9
        '192518494112',     # FaZe Clan
        '126087571128',     # G2 Esports
        '481226615323908',  # NAVI
        '173442445999198',  # Astralis
        '184391128270870',  # Fnatic
        '251623901594654'   # Evil Geniuses
    ],
    'twitter': [
        # IDs de contas oficiais no Twitter
        '819741205',        # FURIA (@FURIA)
        '878660834400251905', # MIBR (@mibr)
        '18008575',         # Team Liquid (@TeamLiquid)
        '35803755',         # Cloud9 (@Cloud9)
        '15542160',         # FaZe Clan (@FaZeClan)
        '592485744',        # G2 Esports (@G2esports)
        '28118541',         # NAVI (@natusvincere)
        '1091349305267544064', # Astralis (@AstralisGG)
        '19238355',         # Fnatic (@FNATIC)
        '357313359'         # Evil Geniuses (@EvilGeniuses)
    ],
    'instagram': [
        # Nomes de usuário no Instagram 
        'furiagg',
        'mibrteam',
        'teamliquid',
        'cloud9gg',
        'fazeclan',
        'g2esports',
        'natusvincere',
        'astralisgg',
        'fnatic',
        'evilgeniuses'
    ],
    'discord': {
        # Nomes de servidores (guilds) de esports no Discord
        'guild_names': [
            'FURIA', 
            'MIBR', 
            'Team Liquid', 
            'Cloud9', 
            'FaZe Clan',
            'G2 Esports',
            'NAVI',
            'Astralis',
            'Fnatic',
            'Evil Geniuses',
            'ESL',
            'BLAST',
            'DreamHack',
            'FACEIT',
            'Valorant',
            'Counter-Strike',
            'League of Legends',
            'Dota 2',
            'Overwatch',
            'Rainbow Six Siege'
        ]
    }
}