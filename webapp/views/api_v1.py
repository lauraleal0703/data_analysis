from flask import Blueprint

from webapp.analyzer.data_tickets import path_temp
from webapp.analyzer import data_tickets


api_v1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")


@api_v1.get("/customers")
def customers():
    return data_tickets.get_list_year(path_temp)