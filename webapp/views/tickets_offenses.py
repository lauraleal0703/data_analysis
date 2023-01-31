from flask import Blueprint
from flask import render_template
from flask import request
from flask import current_app
from flask import redirect
from flask import url_for

import os
import json
import statistics
import numpy  as np


tickets_offenses = Blueprint("tickets_offenses", __name__, url_prefix="/tickets_offenses")


@tickets_offenses.get("/")
def index():
    list_year = list(range(2018, 2024))
    list_year.reverse()

    return render_template(
        "tickets_offenses/index.html",
        page={"title": "Data Adaptive Security"},
        list_year=list_year
    )
