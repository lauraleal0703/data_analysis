from flask import Flask
from flask import redirect
from flask import url_for

from webapp.views.analysis_otrs import analysis_otrs

app = Flask(__name__)

@app.get("/")
def index():
    return redirect(url_for("analysis_otrs.index"))
    
def create_app(enviroment):
    app.config.from_object(enviroment)
    app.register_blueprint(analysis_otrs)

    return app