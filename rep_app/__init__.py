from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
from rep_app import views