# Python standard libraries
from functools import wraps
import os
import json
import time
import timeit
import sys
import traceback
import uuid

# Flask-y things
from flask import Flask, request, jsonify, current_app, url_for, render_template, make_response, session
from flask_sqlalchemy import SQLAlchemy

# Other libraries
import requests

app = Flask(__name__)
app.secret_key = os.urandom(32)

# Flask-SQLAlchemy setup
# ----------------------
if os.path.exists('test.db'):
    os.remove('test.db')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # See this: https://gehrcke.de/2015/05/in-memory-sqlite-database-and-flask-a-threading-trap/
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class RepoData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String)
    contents = db.Column(db.String)
db.create_all()

##########################################################
##################     ROUTES     ########################
##########################################################

the_repos = ['usnistgov/REFPROP-issues','usnistgov/REFPROP-wrappers','usnistgov/REFPROP-manager','usnistgov/REFPROP-cmake']
if sys.platform.startswith('win'):
    HOME = 'Q:/Public/IHB/issues_notes'
else:
    HOME = '/media/Q/IHB/issues_notes'

def api_calls(session):
    repoze = {}
    with requests.Session() as rs:
        pat = open('gh_pat','r').read()
        for repo in the_repos:
            if repo not in session:
                repoze[repo] = rs.get('https://api.github.com/repos/'+repo+'/issues?state=open', auth=('ianhbell', pat)).json()
    db.session.add(RepoData(session_id=session['Id'], contents=json.dumps(repoze)))
    db.commit()

def get_assignees(issue):
    return [a['login'] for a in issue['assignees']]

def attach_notes(items):
    if not os.path.exists(HOME):
        raise ValueError("HOME doesn't exist: " + HOME)
    notes = {}
    for repo in the_repos:
        path = os.path.join(HOME, repo.replace('/','_'))
        if os.path.exists(path):
            with open(path) as fp:
                notes[repo] = json.load(fp)

    def get_note(item):
        repo = item['repo']
        num = str(item['issue_num'])
        if repo in notes and num in notes[repo]:
            return notes[repo][num]
        else:
            return ''

    for iitem in range(len(items)):
        item = items[iitem]
        item['note'] = get_note(item)
    return items

def get_items(session):
    items = []
    repoze = json.loads(RepoData.query.filter_by(session_id=session['Id']).first().contents)
    for repo in the_repos:
        for issue in repoze[repo]:
            items.append({
                'repo': repo,
                'repo_short': repo.split('/')[1].split('-')[1],
                'issue_num': issue['number'],
                'title': issue['title'],
                'assignees': ','.join(get_assignees(issue))
            })
    return items

@app.route('/')
def get_open_issues():
    session['Id'] = str(uuid.uuid1())
    api_calls(session)
    log_message = ''
    items = get_items(session)
    try:
        items = attach_notes(items)
    except BaseException as BE:
        log_message = traceback.format_exc()
        print(BE)
    print(log_message)
    return render_template('frontend.html', items=items, log_message=log_message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)#, ssl_context=('cert.pem', 'key.pem'))