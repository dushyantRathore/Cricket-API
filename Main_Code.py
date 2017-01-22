from flask import Flask,jsonify,render_template
from bs4 import BeautifulSoup
import requests
import urllib2
import pandas as pd

app = Flask(__name__)

# ---------------------  Crawler for Live Scores  ----------------------- #

def live_scores():
    url = "http://www.espncricinfo.com/ci/engine/match/index.html?view=live"
    score_file = urllib2.urlopen(url)
    score_html = score_file.read()
    score_file.close()

    soup = BeautifulSoup(score_html, 'html.parser')

    a = soup.find_all('div', attrs={'class': 'innings-info-1'})
    b = soup.find_all('div', attrs={'class': 'innings-info-2'})
    c = soup.find_all('div', attrs={'class': 'match-status'})

    teamA = []
    teamB = []
    status = []

    for results in a:
        teamA.append(results.text)

    for results in b:
        teamB.append(results.text)

    for results in c:
        status.append(results.text)

    # Strip Characters
    teamA = map(lambda s: s.strip(), teamA)
    teamB = map(lambda s: s.strip(), teamB)
    status = map(lambda s: s.strip(), status)

    ID = []
    for i in range(0, len(teamA)):
        ID.append(i+1)

    matches = []

    for i in range(0, len(ID)):
        dic = {}
        dic["ID"] = ID[i]
        dic["Team A"] = teamA[i]
        dic["Team B"] = teamB[i]
        dic["Status"] = status[i]
        matches.append(dic)

    return matches


# ---------------------  Crawler for Rankings  ----------------------- #

def get_rankings(u):
    rank_file = urllib2.urlopen(u)
    rank_html = rank_file.read()
    rank_file.close()

    soup = BeautifulSoup(rank_html, 'html.parser')

    data = []

    for table in soup.find_all('table'):
        for tr in table.find_all('tr'):
            row = []
            for td in tr.find_all('td'):
                row.append(td.get_text().encode("utf-8"))
            if len(row) == 4:
                data.append(row)
    Team = []
    for i in range(0,10):
        for j in range(0,1):
            Team.append(data[i][j])
    Team = map(lambda s: s.strip('\xc2\xa0'), Team)

    Matches = []
    for i in range(0,10):
        for j in range(1,2):
            Matches.append(data[i][j])

    Points = []
    for i in range(0,10):
        for j in range(2,3):
            Points.append(data[i][j])

    Rating = []
    for i in range(0,10):
        for j in range(3,4):
            Rating.append(data[i][j])

    Rank =[]
    for i in range(1,11):
        Rank.append(i)

    ranks =[]
    for i in range(0, len(Team)):
        dic = {}
        dic["Rank"] = Rank[i]
        dic["Team"] = Team[i]
        dic["Matches"] = Matches[i]
        dic["Points"] = Points[i]
        dic["Rating"] = Rating[i]
        ranks.append(dic)

    return ranks

# ---------------------  Flask Code  ----------------------- #


# Main Page
@app.route('/', methods = ['GET', 'POST'])
def index():
    return render_template('index.html')


# Live Scores
@app.route('/score', methods=['GET', 'POST'])
def get_score():
    matches = live_scores()
    j = jsonify({'Matches': matches})
    print "JSON Format" + str(j)
    return j


# Test Rankings
@app.route('/rankings/test', methods=['GET', 'POST'])
def test_rankings():
    url = "https://en.wikipedia.org/wiki/ICC_Test_Championship"
    ranks_test = get_rankings(url)
    j = jsonify({'Test Rankings': ranks_test})
    return j


# ODI Rankings
@app.route('/rankings/odi',methods=['GET', 'POST'])
def odi_rankings():
    url = "https://en.wikipedia.org/wiki/ICC_ODI_Championship"
    ranks_odi = get_rankings(url)
    j = jsonify({'ODI Rankings': ranks_odi})
    return j

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
