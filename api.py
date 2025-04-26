from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)


@app.route('/matches', methods=['GET'])
def get_matches():
    url = 'https://www.hltv.org/matches'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    matches = []
    upcoming_matches = soup.find_all('div', class_='upcomingMatch')

    for match in upcoming_matches:
        teams = match.find_all('div', class_='matchTeamName')
        time = match.find('div', class_='matchTime')

        if len(teams) == 2 and time:
            matches.append({
                'team1': teams[0].text.strip(),
                'team2': teams[1].text.strip(),
                'time': time.text.strip()
            })

    return jsonify(matches)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
