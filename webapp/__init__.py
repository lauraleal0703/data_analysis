from flask import Flask
from flask import redirect
from flask import url_for

from webapp.views.tickets import tickets
from webapp.views.portal_clientes import portal_clientes

app = Flask(__name__)

@app.get("/")
def index():
    return redirect(url_for("tickets.index"))
    
def create_app(enviroment):
    app.config.from_object(enviroment)
    app.register_blueprint(tickets)
    app.register_blueprint(portal_clientes)

    return app