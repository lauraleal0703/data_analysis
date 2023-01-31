from flask import Flask
from flask import redirect
from flask import url_for

from webapp.views.tickets_customers import tickets_customers
from webapp.views.tickets_offenses import tickets_offenses
from webapp.views.tickets_admin import tickets_admin

app = Flask(__name__)

@app.get("/")
def index():
    return redirect(url_for("tickets_customers.index"))
    
def create_app(enviroment):
    app.config.from_object(enviroment)

    app.register_blueprint(tickets_customers)
    app.register_blueprint(tickets_offenses)
    app.register_blueprint(tickets_admin)

    return app