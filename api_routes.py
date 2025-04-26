"""
API routes for the FURIA fan app
Provides endpoints for tournaments, matches and player information
"""

import json
import os
from datetime import datetime
from flask import Blueprint, jsonify, request

api_blueprint = Blueprint('api', __name__, url_prefix='/api')

# Path to data files
STATIC_DATA_PATH = os.path.join('static', 'data')

def load_json_data(filename):
    """Helper function to load data from JSON files"""
    try:
        file_path = os.path.join(STATIC_DATA_PATH, filename)
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return []

@api_blueprint.route('/tournaments', methods=['GET'])
def get_tournaments():
    """
    Get upcoming tournaments
    
    Query params:
    - game: Filter by game (cs, valorant, lol, etc.)
    - limit: Limit the number of results
    
    Returns a list of tournament objects
    """
    tournaments = load_json_data('tournaments.json')
    
    # Apply filters
    game = request.args.get('game')
    if game:
        tournaments = [t for t in tournaments if game in t.get('tags', [])]
    
    # Sort by date
    tournaments.sort(key=lambda x: x.get('date', ''))
    
    # Apply limit
    limit = request.args.get('limit', type=int)
    if limit and limit > 0:
        tournaments = tournaments[:limit]
    
    return jsonify(tournaments)

@api_blueprint.route('/matches', methods=['GET'])
def get_matches():
    """
    Get upcoming matches
    
    Query params:
    - team: Filter by team name
    - game: Filter by game (cs, valorant, lol, etc.)
    - limit: Limit the number of results
    - has_furia: If true, only return matches involving FURIA
    
    Returns a list of match objects
    """
    matches = load_json_data('matches.json')
    
    # Apply filters
    team = request.args.get('team')
    if team:
        matches = [m for m in matches if team in m.get('team1', '') or team in m.get('team2', '')]
    
    game = request.args.get('game')
    if game:
        matches = [m for m in matches if game.lower() == m.get('game', '').lower()]
    
    has_furia = request.args.get('has_furia')
    if has_furia and has_furia.lower() == 'true':
        matches = [m for m in matches if m.get('has_furia', False)]
    
    # Sort by date
    matches.sort(key=lambda x: x.get('date', ''))
    
    # Apply limit
    limit = request.args.get('limit', type=int)
    if limit and limit > 0:
        matches = matches[:limit]
    
    return jsonify(matches)

@api_blueprint.route('/tournament/<tournament_id>', methods=['GET'])
def get_tournament_detail(tournament_id):
    """
    Get details for a specific tournament
    
    Returns a tournament object or 404 if not found
    """
    tournaments = load_json_data('tournaments.json')
    
    for tournament in tournaments:
        if tournament.get('id') == tournament_id:
            return jsonify(tournament)
    
    return jsonify({'error': 'Tournament not found'}), 404

@api_blueprint.route('/match/<match_id>', methods=['GET'])
def get_match_detail(match_id):
    """
    Get details for a specific match
    
    Returns a match object or 404 if not found
    """
    matches = load_json_data('matches.json')
    
    for match in matches:
        if match.get('id') == match_id:
            return jsonify(match)
    
    return jsonify({'error': 'Match not found'}), 404

@api_blueprint.route('/furia-matches', methods=['GET'])
def get_furia_matches():
    """
    Get only FURIA matches
    
    Query params:
    - game: Filter by game (cs, valorant, lol, etc.)
    - limit: Limit the number of results
    
    Returns a list of match objects
    """
    matches = load_json_data('matches.json')
    
    # Filter for FURIA matches
    furia_matches = [m for m in matches if m.get('has_furia', False)]
    
    # Apply game filter if provided
    game = request.args.get('game')
    if game:
        furia_matches = [m for m in furia_matches if game.lower() == m.get('game', '').lower()]
    
    # Sort by date
    furia_matches.sort(key=lambda x: x.get('date', ''))
    
    # Apply limit
    limit = request.args.get('limit', type=int)
    if limit and limit > 0:
        furia_matches = furia_matches[:limit]
    
    return jsonify(furia_matches)