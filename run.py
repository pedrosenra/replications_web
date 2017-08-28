#!flask/bin/python
from app import app
app.jinja_env.cache = {}
app.run(port=80, debug=True)
