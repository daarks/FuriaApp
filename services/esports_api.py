"""
ESports API Service module
Responsible for fetching esports match and tournament data from external APIs
"""

import json
import logging
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
CACHE_DURATION = 3600  # 1 hour cache
CACHE_FILE_TOURNAMENTS = "cache/tournaments.json"
CACHE_FILE_MATCHES = "cache/matches.json"

# Ensure cache directory exists
os.makedirs("cache", exist_ok=True)


class ESportsAPI:
    """
    Service for fetching esports data from various APIs
    Supports different providers like PandaScore, HLTV, Rib.gg
    Falls back to local data if API calls fail
    """

    def __init__(self):
        """Initialize the ESports API service"""
        # API keys from environment variables
        self.pandascore_key = os.environ.get("PANDASCORE_API_KEY")
        self.ribgg_key = os.environ.get("RIBGG_API_KEY")

    def get_tournaments(self, game: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get tournaments data filtered by game if specified
        
        Args:
            game: Optional game to filter by (cs, valorant, lol, etc.)
        
        Returns:
            List of tournament objects
        """
        # Check cache first
        cached_data = self._read_cache(CACHE_FILE_TOURNAMENTS)
        if cached_data:
            logger.info("Using cached tournament data")
            tournaments = cached_data
        else:
            # Try to fetch from API
            tournaments = self._fetch_tournaments_from_api()
            
            # Cache the results
            if tournaments:
                self._write_cache(CACHE_FILE_TOURNAMENTS, tournaments)
        
        # Filter by game if specified
        if game and tournaments:
            tournaments = [t for t in tournaments if game.lower() in t.get('tags', [])]
            
        return tournaments

    def get_matches(self, team: Optional[str] = None, game: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get matches data filtered by team and/or game if specified
        
        Args:
            team: Optional team to filter by (e.g. 'FURIA')
            game: Optional game to filter by (cs, valorant, lol, etc.)
        
        Returns:
            List of match objects
        """
        # Check cache first
        cached_data = self._read_cache(CACHE_FILE_MATCHES)
        if cached_data:
            logger.info("Using cached match data")
            matches = cached_data
        else:
            # Try to fetch from API
            matches = self._fetch_matches_from_api()
            
            # Cache the results
            if matches:
                self._write_cache(CACHE_FILE_MATCHES, matches)
        
        # Apply filters
        if matches:
            if team:
                team = team.upper()
                matches = [m for m in matches if team in m.get('team1', '') or team in m.get('team2', '')]
            
            if game:
                game = game.lower()
                matches = [m for m in matches if game == m.get('game', '').lower()]
            
        return matches

    def _fetch_tournaments_from_api(self) -> List[Dict[str, Any]]:
        """
        Fetch tournament data from the API
        
        Returns:
            List of tournament objects or empty list if failed
        """
        if self.pandascore_key:
            try:
                logger.info("Fetching tournaments from PandaScore API")
                response = requests.get(
                    "https://api.pandascore.co/tournaments/upcoming",
                    headers={"Authorization": f"Bearer {self.pandascore_key}"},
                    params={"per_page": 50}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Transform to our format
                    return self._transform_pandascore_tournaments(data)
            except Exception as e:
                logger.error(f"Error fetching from PandaScore API: {e}")
        
        # Fallback to local JSON file if API failed or no key available
        logger.info("Using local tournament data")
        try:
            with open("static/data/tournaments.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error reading local tournament data: {e}")
            return []

    def _fetch_matches_from_api(self) -> List[Dict[str, Any]]:
        """
        Fetch match data from the API
        
        Returns:
            List of match objects or empty list if failed
        """
        if self.pandascore_key:
            try:
                logger.info("Fetching matches from PandaScore API")
                response = requests.get(
                    "https://api.pandascore.co/matches/upcoming",
                    headers={"Authorization": f"Bearer {self.pandascore_key}"},
                    params={"per_page": 50}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Transform to our format
                    return self._transform_pandascore_matches(data)
            except Exception as e:
                logger.error(f"Error fetching from PandaScore API: {e}")
        
        # Fallback to local JSON file if API failed or no key available
        logger.info("Using local match data")
        try:
            with open("static/data/matches.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error reading local match data: {e}")
            return []

    def _transform_pandascore_tournaments(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform PandaScore tournament data to our app format
        
        Args:
            data: Raw data from PandaScore API
            
        Returns:
            Transformed tournament data
        """
        tournaments = []
        
        for item in data:
            # Skip non-relevant tournaments
            if not item.get('name') or not item.get('begin_at'):
                continue
                
            # Extract game type and create tags
            tags = []
            videogame = item.get('videogame', {})
            if isinstance(videogame, dict):
                game_name = videogame.get('name', '').lower()
                if 'cs' in game_name or 'counter' in game_name:
                    tags.append('cs')
                elif 'valorant' in game_name:
                    tags.append('valorant')
                elif 'league of legends' in game_name or 'lol' in game_name:
                    tags.append('lol')
                elif 'rainbow' in game_name:
                    tags.append('rainbow6')
                elif 'free fire' in game_name:
                    tags.append('freefire')
                elif 'dota' in game_name:
                    tags.append('dota')
            
            # Get teams if available
            teams = []
            for team in item.get('teams', []):
                if isinstance(team, dict):
                    team_name = team.get('name', '')
                    if team_name:
                        teams.append(team_name)
            
            # Format start and end dates
            try:
                begin_at = datetime.fromisoformat(item.get('begin_at').replace('Z', '+00:00'))
                end_at = datetime.fromisoformat(item.get('end_at', begin_at).replace('Z', '+00:00'))
                if not item.get('end_at'):
                    end_at = begin_at + timedelta(days=1)
            except (ValueError, AttributeError):
                # Skip if dates are invalid
                continue
            
            tournament = {
                'id': str(item.get('id')),
                'title': item.get('name', ''),
                'game': videogame.get('name') if isinstance(videogame, dict) else 'Unknown',
                'date': begin_at.isoformat(),
                'end_date': end_at.isoformat(),
                'location': item.get('league', {}).get('name', 'Online') if isinstance(item.get('league'), dict) else 'Online',
                'description': item.get('description') or f"Tournament: {item.get('name', '')}",
                'teams': teams,
                'tags': tags,
                'prize_pool': item.get('prize_pool'),
                'tier': item.get('tier')
            }
            
            tournaments.append(tournament)
        
        return tournaments

    def _transform_pandascore_matches(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform PandaScore match data to our app format
        
        Args:
            data: Raw data from PandaScore API
            
        Returns:
            Transformed match data
        """
        matches = []
        
        for item in data:
            # Skip non-relevant matches
            if not item.get('name') or not item.get('begin_at'):
                continue
            
            # Extract teams
            opponents = item.get('opponents', [])
            team1 = opponents[0].get('opponent', {}).get('name') if len(opponents) > 0 and isinstance(opponents[0], dict) else ''
            team2 = opponents[1].get('opponent', {}).get('name') if len(opponents) > 1 and isinstance(opponents[1], dict) else ''
            
            # Extract game type
            videogame = item.get('videogame', {})
            game = videogame.get('name') if isinstance(videogame, dict) else 'Unknown'
            
            # Format start date
            try:
                begin_at = datetime.fromisoformat(item.get('begin_at').replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                # Skip if date is invalid
                continue
            
            # Get tournament info
            tournament = item.get('tournament', {})
            tournament_name = tournament.get('name') if isinstance(tournament, dict) else ''
            
            match = {
                'id': str(item.get('id')),
                'team1': team1,
                'team2': team2,
                'date': begin_at.isoformat(),
                'tournament': tournament_name,
                'game': game,
                'status': item.get('status'),
                'match_type': item.get('match_type'),
                'has_furia': team1 == 'FURIA' or team2 == 'FURIA'
            }
            
            matches.append(match)
        
        return matches

    def _read_cache(self, cache_file: str) -> Optional[List[Dict[str, Any]]]:
        """
        Read data from cache if it exists and is not expired
        
        Args:
            cache_file: Path to the cache file
            
        Returns:
            Cached data or None if expired or not found
        """
        try:
            if not os.path.exists(cache_file):
                return None
                
            # Check if cache is expired
            modified_time = os.path.getmtime(cache_file)
            if datetime.now().timestamp() - modified_time > CACHE_DURATION:
                logger.info(f"Cache expired for {cache_file}")
                return None
                
            with open(cache_file, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error reading cache {cache_file}: {e}")
            return None

    def _write_cache(self, cache_file: str, data: List[Dict[str, Any]]) -> None:
        """
        Write data to cache file
        
        Args:
            cache_file: Path to the cache file
            data: Data to write to cache
        """
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            logger.error(f"Error writing to cache {cache_file}: {e}")