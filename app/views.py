from flask import render_template, flash, redirect, request, url_for, g, session
from app import app
import replication
import json


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    username = request.form['username']
    password = request.form['password']
    url = request.form['url']
    org = request.form['org']
    flash('getting replications')
    session['username'] = username
    session['password'] = password
    session['url'] = url
    session['org'] = org
    return redirect(url_for('result'))


@app.route('/result', methods=['GET', 'POST'])
def result():
    username = session.get('username', None)
    password = session.get('password', None)
    url = session.get('url', None)
    org = session.get('org', None)
    session['data'] = replication.replications(username, password, url, org)
    data = session.get('data', None)
    headers = [['vm_name', 'string'], ['replication_href', 'string'], ['replicationState', 'string'],
               ['RPO(Hours)', 'number'], ['RPO violation', 'string'], ['HTTP status_code', 'number'],
               ['TransferStartTime', 'string'], ['TransferSeconds', 'string'], ['TransferBytes', 'string']]
    return render_template("result.html", replications=data, headers=headers)
