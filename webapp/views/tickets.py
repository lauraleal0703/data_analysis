from flask import Blueprint
from flask import render_template
from flask import request
from flask import current_app
from flask import redirect
from flask import url_for

from webapp.analyzer import totalization_tickets

import os
import json
import statistics
import numpy  as np
import calendar
from datetime import datetime


tickets = Blueprint("tickets", __name__, url_prefix="/tickets")


@tickets.get("/")
def index():
    list_year = list(range(2018, 2024))
    
    if request.method == "GET":
        year = request.args.get("year", type=int)
        month =  request.args.get("month", type=str)

        if not year:
            return render_template(
                "tickets/index.html",
                page={"title": "Data Adaptive Security"},
                list_year=list_year
            )

        if year == datetime.today().year:
            months = {num : calendar.month_name[num] for num in list(range(1, datetime.today().month+1))}
        else:
            months = {num: calendar.month_name[num] for num in list(range(1, 13))}
        
        if year and month:
            print("jj")

        return render_template(
            "tickets/index.html",
            page={"title": "Data Adaptive Security"},
            list_year=list_year,
            current_year=year,
            months=months,
            current_month=month
        )
