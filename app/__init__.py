from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
#app.config.from_object('config')

from app import views