from flask import Flask,jsonify,render_template
from bs4 import BeautifulSoup
import requests
import urllib2
import pandas as pd
import json

app = Flask(__name__)

# ---------------------  Crawler for Live Scores  ----------------------- #


def live_scores():
    url = "http://www.espncricinfo.com/scores/"
    score_file = urllib2.urlopen(url)
    score_html = score_file.read()
    score_file.close()

    soup = BeautifulSoup(score_html, 'html.parser')

    soup = BeautifulSoup(score_html, 'html.parser')

    teamA = []
    teamB = []

    scoreA = []
    scoreB = []

    for ul in soup.find_all('li', attrs={'class': 'cscore_item cscore_item--home'}):
        for span in ul.find_all("span", attrs={"class": "cscore_name cscore_name--long"}):
            teamA.append(str(span.text))
        for div in ul.find_all("div", attrs={"class": "cscore_score"}):
            score = str(div.text)
            score = score.replace("(", "")
            score = score.replace(")", "")
            score = score.replace("/", " for ")
            score = score.replace("ov", "overs")
            scoreA.append(score)

    for ul in soup.find_all('li', attrs={'class': 'cscore_item cscore_item--away'}):
        for span in ul.find_all("span", attrs={"class": "cscore_name cscore_name--long"}):
            teamB.append(str(span.text))
        for div in ul.find_all("div", attrs={"class": "cscore_score"}):
            score = str(div.text)
            score = score.replace("(", "")
            score = score.replace(")", "")
            score = score.replace("/", " for ")
            score = score.replace("ov", "overs")
            scoreB.append(score)

    # print len(teamA)
    # print teamA

    # print len(teamB)
    # print teamB

    # print len(scoreA)
    # print scoreA

    # print len(scoreB)
    # print scoreB

    # Strip Characters
    teamA = map(lambda s: s.strip(), teamA)
    teamB = map(lambda s: s.strip(), teamB)
    scoreA = map(lambda s: s.strip(), scoreA)
    scoreB = map(lambda s: s.strip(), scoreB)


    ID = []
    for i in range(0, len(teamA)):
        ID.append(i+1)

    matches = []

    for i in range(0, len(ID)):
        dic = {}
        dic["ID"] = ID[i]
        dic["Team A"] = teamA[i]
        dic["Team B"] = teamB[i]
        dic["Score A"] = scoreA[i]
        dic["Score B"] = scoreB[i]
        matches.append(dic)

    return matches


# --------------------- Crawler for Latest News ------------------------- #


def getNews():
    url = "https://sports.ndtv.com/cricket/news"
    news_file = urllib2.urlopen(url)
    news_html = news_file.read()
    news_file.close()

    soup = BeautifulSoup(news_html, "html.parser")

    title = soup.find_all("div", attrs={"class": "post-title"})

    t = []
    for i in title:
        t.append(i.text)

    news = []
    for i in range(0,len(t)):
        dic = {}
        dic["ID"] = i
        dic["Title"] = t[i]
        news.append(dic)

    print news

    return news


# ---------------------  Crawler for Team Rankings  ----------------------- #


def team_rankings(u):
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

# --------------------- Crawler for Player Rankings -------------------- #


def player_rankings(u, start):
    rank_file = urllib2.urlopen(u)
    rank_html = rank_file.read()
    rank_file.close()

    soup = BeautifulSoup(rank_html, "html.parser")

    data = []

    for table in soup.find_all('table', attrs={'class': 'multicol'}):
        for td in table.find_all('td', attrs={'style': 'width: 33.33%;text-align:left;vertical-align:top;'}):
            for table in td.find_all('table', attrs={'class': 'wikitable'}):
                for tr in table.find_all('tr'):
                    row = []
                    for td in tr.find_all('td'):
                        row.append(td.get_text().encode("utf-8"))
                    if len(row) == 3:
                        data.append(row)

    rank = []
    for i in range(0, 10):
        rank.append(i + 1)

    # ---------------- Batsmen --------------------#
    batsmen_name = []
    batsmen_rating = []

    for i in range(start, start + 10):
        batsmen_name.append(data[i][1])
        batsmen_rating.append(data[i][2])

    sequence = ["Rank", "Player", "Rating"]
    df_bt = pd.DataFrame()
    df_bt = df_bt.reindex(columns=sequence)
    df_bt["Rank"] = rank
    df_bt["Player"] = batsmen_name
    df_bt["Rating"] = batsmen_rating

    # ---------------- Bowlers --------------------#
    bowler_name = []
    bowler_rating = []
    for i in range(start + 10, start + 20):
        bowler_name.append(data[i][1])
        bowler_rating.append(data[i][2])

    sequence = ["Rank", "Player", "Rating"]
    df_bo = pd.DataFrame()
    df_bo = df_bo.reindex(columns=sequence)
    df_bo["Rank"] = rank
    df_bo["Player"] = bowler_name
    df_bo["Rating"] = bowler_rating

    # ---------------- All-Rounders--------------------#
    all_name = []
    all_rating = []
    for i in range(start + 20, start + 30):
        all_name.append(data[i][1])
        all_rating.append(data[i][2])

    sequence = ["Rank", "Player", "Rating"]
    df_ar = pd.DataFrame()
    df_ar = df_ar.reindex(columns=sequence)
    df_ar["Rank"] = rank
    df_ar["Player"] = all_name
    df_ar["Rating"] = all_rating

    # Dictionary Formation
    ranks_batsmen =[]
    for i in range(0, len(rank)):
        dic = {}
        dic["Rank"] = rank[i]
        dic["Name"] = batsmen_name[i]
        dic["Rating"] = batsmen_rating[i]
        ranks_batsmen.append(dic)

    ranks_bowlers =[]
    for i in range(0, len(rank)):
        dic = {}
        dic["Rank"] = rank[i]
        dic["Name"] = bowler_name[i]
        dic["Rating"] = bowler_rating[i]
        ranks_bowlers.append(dic)

    ranks_allrounders = []
    for i in range(0, len(rank)):
        dic = {}
        dic["Rank"] = rank[i]
        dic["Name"] = all_name[i]
        dic["Rating"] = all_rating[i]
        ranks_allrounders.append(dic)

    final_ranks = []
    final_ranks.append(ranks_batsmen)
    final_ranks.append(ranks_bowlers)
    final_ranks.append(ranks_allrounders)

    print final_ranks

    return final_ranks

# ---------------------  Flask Code  ----------------------- #


# Main Page
@app.route('/', methods = ['GET', 'POST'])
def index():
    return render_template('index.html')


# Live Scores
@app.route('/live', methods=['GET', 'POST'])
def get_score():
    matches = live_scores()
    j = jsonify({'Matches': matches})
    j.headers.add('Access-Control-Allow-Origin', '*') # Support for CORS
    return j


# Latest News
@app.route("/news", methods=['GET', 'POST'])
def latest_news():
    news = getNews()
    j = jsonify({'Latest News' : news})
    return j


# Test Rankings - Teams
@app.route('/rankings/test/team', methods=['GET', 'POST'])
def test_rankings():
    url = "https://en.wikipedia.org/wiki/ICC_Test_Championship"
    ranks_test = team_rankings(url)
    j = jsonify({'Rankings': ranks_test})
    return j


# Test Rankings - Batsmen
@app.route('/rankings/test/batsmen', methods = ['GET', 'POST'])
def test_batsmen_rankings():
    url = "https://en.wikipedia.org/wiki/ICC_Player_Rankings"
    ranks = player_rankings(url, 0)
    j = jsonify({'Rankings': ranks[0]})
    return j


# Test Rankings - Bowlers
@app.route('/rankings/test/bowlers', methods = ['GET', 'POST'])
def test_bowler_rankings():
    url = "https://en.wikipedia.org/wiki/ICC_Player_Rankings"
    ranks = player_rankings(url, 0)
    j = jsonify({'Rankings': ranks[1]})
    return j


# Test Rankings - All-Rounders
@app.route('/rankings/test/allrounders', methods = ['GET', 'POST'])
def test_allrounders_rankings():
    url = "https://en.wikipedia.org/wiki/ICC_Player_Rankings"
    ranks = player_rankings(url, 0)
    j = jsonify({'Rankings': ranks[2]})
    return j


# ODI Rankings - Teams
@app.route('/rankings/odi/team',methods=['GET', 'POST'])
def odi_rankings():
    url = "https://en.wikipedia.org/wiki/ICC_ODI_Championship"
    ranks_odi = team_rankings(url)
    j = jsonify({"Rankings": ranks_odi})
    return j


# ODI Rankings - Batsmen
@app.route('/rankings/odi/batsmen', methods = ['GET', 'POST'])
def odi_batsmen_rankings():
    url = "https://en.wikipedia.org/wiki/ICC_Player_Rankings"
    ranks = player_rankings(url, 30)
    j = jsonify({'Rankings': ranks[0]})
    return j


# ODI Rankings - Bowlers --------------------  !!!! Error
@app.route('/rankings/odi/bowlers', methods = ['GET', 'POST'])
def odi_bowler_rankings():
    url = "https://en.wikipedia.org/wiki/ICC_Player_Rankings"
    ranks = player_rankings(url, 30)
    j = jsonify({'Rankings': ranks[1]})
    return j


# ODI Rankings - All-Rounders
@app.route('/rankings/odi/allrounders', methods = ['GET', 'POST'])
def odi_allrounders_rankings():
    url = "https://en.wikipedia.org/wiki/ICC_Player_Rankings"
    ranks = player_rankings(url, 30)
    j = jsonify({'Rankings': ranks[2]})
    return j


# T20 Rankings - Teams
@app.route('/rankings/t20/team', methods=['GET', 'POST'])
def t20_rankings():
    url = "https://en.wikipedia.org/wiki/ICC_T20I_Championship"
    ranks_t20 = team_rankings(url)
    j = jsonify({'Rankings': ranks_t20})
    return j


# T20 Rankings - Batsmen
@app.route('/rankings/t20/batsmen', methods = ['GET', 'POST'])
def t20_batsmen_rankings():
    url = "https://en.wikipedia.org/wiki/ICC_Player_Rankings"
    ranks = player_rankings(url, 60)
    j = jsonify({'Rankings': ranks[0]})
    return j


# T20 Rankings - Bowlers
@app.route('/rankings/t20/bowlers', methods = ['GET', 'POST'])
def t20_bowler_rankings():
    url = "https://en.wikipedia.org/wiki/ICC_Player_Rankings"
    ranks = player_rankings(url, 60)
    j = jsonify({'Rankings': ranks[1]})
    return j


# T20 Rankings - All-Rounders
@app.route('/rankings/t20/allrounders', methods = ['GET', 'POST'])
def t20_allrounders_rankings():
    url = "https://en.wikipedia.org/wiki/ICC_Player_Rankings"
    ranks = player_rankings(url, 60)
    j = jsonify({'Rankings': ranks[2]})
    return j


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
