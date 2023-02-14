from flask import Flask
from flask import redirect
from flask import url_for

from webapp.views.otrs import otrs

app = Flask(__name__)

@app.get("/")
def index():
    return redirect(url_for("otrs.index"))
    
def create_app(enviroment):
    app.config.from_object(enviroment)
    app.register_blueprint(otrs)

    return app