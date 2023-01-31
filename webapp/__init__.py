from flask import Flask
from flask import redirect
from flask import url_for

from webapp.views.tickets import tickets

app = Flask(__name__)

@app.get("/")
def index():
    return redirect(url_for("tickets.customers"))
    
def create_app(enviroment):
    app.config.from_object(enviroment)

    app.register_blueprint(tickets)

    return app