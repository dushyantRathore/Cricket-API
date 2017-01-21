from flask import Flask,jsonify,render_template
from bs4 import BeautifulSoup
import requests
import urllib2
import pandas as pd

app = Flask(__name__)


# Main Page
@app.route('/', methods = ['GET', 'POST'])
def index():
    return render_template('index.html')

# Crawler
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

sequence = ["Match ID", "Team A", "Team B", "Status"]

df = pd.DataFrame()
df = df.reindex(columns=sequence)

df["Match ID"] = ID
df["Team A"] = teamA
df["Team B"] = teamB
df["Status"] = status

match = []

for i in range(0, len(ID)):
    dic = {}
    dic["ID"] = df["Match ID"][i]
    dic["Team A"] = df["Team A"][i]
    dic["Team B"] = df["Team B"][i]
    dic["Status"] = df["Status"][i]
    match.append(dic)


# Live Scores
@app.route('/score', methods = ['GET', 'POST'])
def getScore():
    j = jsonify({'Matches' : match})
    print "Dataframe"
    print df
    print "JSON Format" + str(j)
    return j


if __name__ == "__main__":
    app.run(debug=True)
