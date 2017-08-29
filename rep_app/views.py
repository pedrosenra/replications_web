from flask import render_template, flash, redirect, request, url_for, g, session
from rep_app import app
import replication


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    flash('getting replications')
    session['username'] = request.form['username']
    session['password'] = request.form['password']
    session['url'] = request.form['url']
    session['org'] = request.form['org']
    return redirect(url_for('result'))


@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'GET':
        username = session.get('username', None)
        password = session.get('password', None)
        url = session.get('url', None)
        org = session.get('org', None)
    else:
        username = request.form['username']
        password = request.form['password']
        url = request.form['url']
        org = request.form['org']
    session['data'] = replication.replications(username, password, url, org)
    headers = [['vm_name', 'string'], ['replication_href', 'string'], ['replicationState', 'string'],
               ['RPO(Hours)', 'number'], ['RPO violation', 'string'], ['HTTP status_code', 'number'],
               ['TransferStartTime', 'string'], ['TransferSeconds', 'string'], ['TransferBytes', 'string']]
    if session['data'] == 401:
        return render_template("index.html", error=('autentications failed %s' % username))
    return render_template("result.html", replications=session['data'], headers=headers)
