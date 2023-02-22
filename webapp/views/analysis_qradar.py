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
    services = {"arbor": "Arbor AAN"}

    if request.method == "GET":
        service = request.args.get("service", type=str)
        pos = request.args.get("pos", type=int)
        date = request.args.get("date", type=str)

        if service == "arbor":
            dates_actives = get_qradar.dates_actives()
            total_blocked_events = get_qradar.total_blocked_events()

            if date:
                data_grah = get_qradar.blocked_events(
                    date = date,
                    aql_name = "AAN_Informe_Arbor_1"
                )

                return render_template(
                    "analysis_qradar/arbor/index.html",
                    page={"title": "KPI 1: Eventos Bloqueados"},
                    services = services,
                    current_service = service,
                    dates_actives = dates_actives,
                    current_date = date,
                    current_pos = pos,
                    data_grah = data_grah
                )

            return render_template(
                "analysis_qradar/arbor/index.html",
                page={"title": "Análisis de Arbor - QRadar"},
                services = services,
                current_service = service,
                dates_actives = dates_actives,
                total_blocked_events = total_blocked_events
            )

    return render_template(
        "analysis_qradar/index/index.html",
        page={"title": "Análisis de QRadar"},
        services = services
    )

