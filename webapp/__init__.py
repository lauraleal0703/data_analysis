from flask import Flask
from flask import redirect
from flask import url_for

from webapp.views.tickets import tickets
from webapp.views.api_v1 import api_v1

app = Flask(__name__)

@app.get("/")
def index():
    return redirect(url_for("tickets.customers"))
    
def create_app(enviroment):
    app.config.from_object(enviroment)

    app.register_blueprint(tickets)
    app.register_blueprint(api_v1)

    return app