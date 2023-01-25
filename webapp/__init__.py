from flask import Flask
from flask import redirect
from flask import url_for

from webapp.views.tickets import tickets
from webapp.views.tickets_offenses import tickets_offenses

app = Flask(__name__)

@app.get("/")
def index():
    return redirect(url_for("tickets.index"))
    
    
def create_app(enviroment):
    app.config.from_object(enviroment)

    app.register_blueprint(tickets)
    app.register_blueprint(tickets_offenses)

    return app