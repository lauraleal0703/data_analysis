from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for


from webapp.analyzer import get_qradar

from pprint import pprint


analysis_qradar = Blueprint("analysis_qradar", __name__, url_prefix="/analysis_qradar")


@analysis_qradar.get("/")
def index():
    services = {"arbor": "Arbor"}

    if request.method == "GET":
        service = request.args.get("service", type=str)
        customer = request.args.get("customer", type=str)
        pos = request.args.get("pos", type=int)
        date = request.args.get("date", type=str)

        if service == "arbor":
            customers_actives = get_qradar.customers_arbor()
            dates_actives = get_qradar.dates_actives()
            total_blocked_events = get_qradar.total_blocked_events()

            if customer == "AAN":
                current_customer_name = customers_actives[customer]

                if date:
                    data_grah_events = get_qradar.blocked_events(
                        customer = customer,
                        date = date
                    )

                    data_grah_events_paises = get_qradar.events_paises(
                        customer = customer,
                        date = date
                    )

                    return render_template(
                        "analysis_qradar/arbor/index.html",
                        page={"title": ""},
                        services = services,
                        current_service = service,
                        customers_actives = customers_actives,
                        current_customer = customer,
                        current_customer_name = current_customer_name,
                        dates_actives = dates_actives,
                        current_date = date,
                        current_pos = pos,
                        data_grah_events = data_grah_events,
                        data_grah_events_paises = data_grah_events_paises
                    )
                
                return render_template(
                    "analysis_qradar/arbor/index.html",
                    page={"title": ""},
                    services = services,
                    current_service = service,
                    customers_actives = customers_actives,
                    current_customer = customer,
                    current_customer_name = current_customer_name,
                    dates_actives = dates_actives,
                    total_blocked_events = total_blocked_events
                )

            return render_template(
                "analysis_qradar/arbor/index.html",
                page={"title": "Análisis de Arbor - QRadar"},
                services = services,
                current_service = service,
                customers_actives = customers_actives
            )

    return render_template(
        "analysis_qradar/index/index.html",
        page={"title": "Análisis de QRadar"},
        services = services
    )

