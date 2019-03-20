# Python standard libraries
from functools import wraps
import os
import json
from threading import Thread
import time
import timeit

# Flask-y things
from flask import Flask, request, jsonify, current_app, url_for, render_template, make_response, session
# Other libraries
import requests
app = Flask(__name__)

app.secret_key = os.urandom(32)

##########################################################
##################     ROUTES     ########################
##########################################################

the_repos = ['usnistgov/REFPROP-issues','usnistgov/REFPROP-wrappers']
def api_calls(session):
    for repo in the_repos:
        if repo not in session:
            session[repo] = requests.get('https://api.github.com/repos/'+repo+'/issues?state=open').json()

def get_assignees(issue):
    return [a['login'] for a in issue['assignees']]

def get_items(session):
    items = []
    for repo in the_repos:
        for issue in session[repo]:
            items.append({
                'repo': repo,
                'issue_num': issue['number'],
                'title': issue['title'],
                'assignees': ','.join(get_assignees(issue))
            })
    return items

@app.route('/')
def get_open_issues():
    api_calls(session)
    return render_template('frontend.html', items=get_items(session))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, ssl_context=('cert.pem', 'key.pem'))