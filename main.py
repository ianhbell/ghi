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

here = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = os.urandom(32)

# Flask-SQLAlchemy setup
# ----------------------
# if os.path.exists('test.db'):
#     os.remove('test.db')
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
    if 'Id' not in session:
        session['Id'] = str(uuid.uuid1())
    repoze = {}
    pat = open(here+'/gh_pat','r').read().strip()

    with requests.Session() as rs:
        for repo in the_repos:
            issues = []
            base_url = 'https://api.github.com/repos/'+repo+'/issues?state=all&filter=all'
            r = rs.get(base_url, auth=('ianhbell', pat))
            if not r.ok:
                print(r)
            issues += r.json()
            while 'next' in r.links:
                url = r.links['next']['url']
                r = rs.get(url, auth=('ianhbell', pat))
                issues += r.json()
            repoze[repo] = issues
    db.session.add(RepoData(session_id=session['Id'], contents=json.dumps(repoze)))
    db.session.commit()

def get_assignees(issue):
    return [a['login'].replace('EricLemmon','Eric').replace('ianhbell','Ian') for a in issue['assignees']]

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

def get_items(*, session, state):
    items = []
    print(session)
    repoze = json.loads(RepoData.query.filter_by(session_id=session['Id']).first().contents)
    for repo in the_repos:
        for issue in repoze[repo]:
            print(repo, issue['number'], issue['state'])
            if issue['state'] != state:
                continue
            items.append({
                'repo': repo,
                'repo_short': repo.split('/')[1].split('-')[1],
                'issue_num': issue['number'],
                'title': issue['title'],
                'state': issue['state'],
                'assignees': ','.join(get_assignees(issue))
            })
    return items

@app.route('/<state>_issues')
def get_issues(state):
    api_calls(session)
    log_message = ''
    items = get_items(session=session, state=state)
    try:
        items = attach_notes(items)
    except BaseException as BE:
        log_message = traceback.format_exc()
        print(BE)
    print(log_message)
    return render_template('frontend.html', items=items, log_message=log_message, state=state, repos = the_repos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)#, ssl_context=('cert.pem', 'key.pem'))