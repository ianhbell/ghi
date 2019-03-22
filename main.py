# Python standard libraries
from functools import wraps
import os
import json
import time
import timeit
import sys

# Flask-y things
from flask import Flask, request, jsonify, current_app, url_for, render_template, make_response, session
# Other libraries
import requests
app = Flask(__name__)

##########################################################
##################     ROUTES     ########################
##########################################################

the_repos = ['usnistgov/REFPROP-issues','usnistgov/REFPROP-wrappers','usnistgov/REFPROP-manager','usnistgov/REFPROP-cmake']
if sys.platform.startswith('win'):
    HOME = 'Q:/IHB/issues_notes'
else:
    HOME = '/media/Q/IHB/issues_notes'
def api_calls(session):
    for repo in the_repos:
        if repo not in session:
            session[repo] = requests.get('https://api.github.com/repos/'+repo+'/issues?state=open').json()

def get_assignees(issue):
    return [a['login'] for a in issue['assignees']]

def attach_notes(items):
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
    for repo in the_repos:
        for issue in session[repo]:
            items.append({
                'repo': repo,
                'repo_short': repo.split('/')[0],
                'issue_num': issue['number'],
                'title': issue['title'],
                'assignees': ','.join(get_assignees(issue))
            })
    items = attach_notes(items)
    return items

@app.route('/')
def get_open_issues():
    api_calls(session)
    return render_template('frontend.html', items=get_items(session))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)#, ssl_context=('cert.pem', 'key.pem'))