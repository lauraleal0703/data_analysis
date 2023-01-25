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


data_as = Blueprint("data_as", __name__, url_prefix="/data_as")


@data_as.get("/")
def index():
    current_folder = os.path.join(current_app.root_path, "static", "data_storage", "data_as", "data_collected")
    if request.method == "GET":
        year = request.args.get("year", type=int)
        
        if not year:
            year = 2022
        elif year < 2018 or year > 2023:
            year = 2022

        month = request.args.get("month", type=int)

        if month and (month < 1 or month > 12):
            return redirect(url_for("data_as.index", year=year, month=1))

        if year and not month:
            file_path = os.path.join(current_folder, str(year), f"total_offenses_year_{year}.json")
            data = open(file_path)
            data = json.load(data)

        elif year and month:
            file_path = os.path.join(current_folder, str(year), f"total_offenses_month_{month}.json")
            data = open(file_path)
            data = json.load(data)

        cases_statistics = ["Promedio", "Máximo", "Mínimo"]
        variables = ["handwork_total",
            "handwork_success",
            "handwork_fails",
            "handwork_undefined",
            "handwork_low",
            "handwork_mean",
            "handwork_high",
            "automatic_total",
            "automatic_success",
            "automatic_fails",
            "automatic_undefined",
            "automatic_low",
            "automatic_mean",
            "automatic_high",
            "undefined",
            "total"
        ]

        cases_statistics_total = {}
        for variable in variables:
            cases_statistics_total[variable] = [ round(statistics.mean(data[variable]),1), 
                max(data[variable]), 
                min(data[variable])
            ]

        return render_template(
            "data_as/index.html",
            page={"title": "Data Adaptive Security"},
            data=data,
            current_year=year,
            current_month=month if month else None,
            cases_statistics=cases_statistics,
            cases_statistics_total = cases_statistics_total
        )

    return render_template(
        "data_as/index.html",
        page={"title": "Data Adaptive Security"}
    )


@data_as.get("/detail")
def index_detail():
    current_folder = os.path.join(current_app.root_path, "static", "data_storage", "data_as", "data_collected")
    if request.method == "GET":
        year = request.args.get("year", type=int)
        month = request.args.get("month", type=int)
        type = request.args.get("type")
        
        if not year:
            year = 2023
        elif year < 2018 or year > 2023:
            year = 2022

        month = request.args.get("month", type=int)

        if month and (month < 1 or month > 12):
            return redirect(url_for("data_as.index", year=year, month=1))

        if year and not month:
            file_path = os.path.join(current_folder, str(year), f"total_offenses_year_{year}.json")
            data = open(file_path)
            data = json.load(data)

        elif year and month:
            file_path = os.path.join(current_folder, str(year), f"total_offenses_month_{month}.json")
            data = open(file_path)
            data = json.load(data)

        if type == "handwork":
            data = {"total": data["handwork_total"],
                "success": data["handwork_success"],
                "fails": data["handwork_fails"],
                "undefined": data["handwork_undefined"],
                "low": data["handwork_low"],
                "mean": data["handwork_mean"],
                "high": data["handwork_high"],
                "total_sum": data["handwork_total_sum"],
                "success_sum": data["handwork_success_sum"],
                "fails_sum": data["handwork_fails_sum"],
                "undefined_sum": data["handwork_undefined_sum"],
                "low_sum": data["handwork_low_sum"],
                "mean_sum": data["handwork_mean_sum"],
                "high_sum": data["handwork_high_sum"]
            }
        else:
            data = {"total": data["automatic_total"],
                "success": data["automatic_success"],
                "fails": data["automatic_fails"],
                "undefined": data["automatic_undefined"],
                "low": data["automatic_low"],
                "mean": data["automatic_mean"],
                "high": data["automatic_high"],
                "total_sum": data["automatic_total_sum"],
                "success_sum": data["automatic_success_sum"],
                "fails_sum": data["automatic_fails_sum"],
                "undefined_sum": data["automatic_undefined_sum"],
                "low_sum": data["automatic_low_sum"],
                "mean_sum": data["automatic_mean_sum"],
                "high_sum": data["automatic_high_sum"]
            }

        return render_template(
            "data_as/index_detail.html",
            page={"title": "Data Adaptive Security"},
            data=data,
            current_year=year
        )

    return render_template(
        "data_as/index_detail.html",
        page={"title": "Data Adaptive Security"}
    )