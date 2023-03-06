from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import current_app
from flask import redirect


from webapp.analyzer import get_qradar

from pprint import pprint


analysis_qradar = Blueprint("analysis_qradar", __name__, url_prefix="/analysis_qradar")


@analysis_qradar.get("/")
def index():
    services = {
        "arbor": "Arbor",
        "cloudflare": "Cloudflare",
        "firepower": "Firepower"
    }

    if request.method == "GET":
        service = request.args.get("service", type=str)
        customer = request.args.get("customer", type=str)
        pos = request.args.get("pos", type=int)
        date = request.args.get("date", type=str)

        if service == "arbor":
            
            try:
                customers_actives = get_qradar.customers_arbor()
                total_blocked_events = get_qradar.total_blocked_events()
            except Exception as e:
                current_app.logger.error(f"{str(request.url)}: {e}")
                return redirect(request.url)

            if customer:
                
                try:
                    dates_actives = get_qradar.dates_actives()
                except Exception as e:
                    current_app.logger.error(f"{str(request.url)}: {e}")
                    return redirect(request.url)
                
                current_customer_name = customers_actives[customer]

                if date:
                    
                    try: 
                        data_grah_events = get_qradar.blocked_events(
                            customer = customer,
                            date = date
                        )

                        data_grah_events_paises = get_qradar.events_paises(
                            customer = customer,
                            date = date
                        )
                    except Exception as e:
                        current_app.logger.error(f"{str(request.url)}: {e}")
                        return redirect(request.url)

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
                page={"title": "Análisis de Arbor - QRadar."},
                services = services,
                current_service = service,
                customers_actives = customers_actives
            )
        
        if service == "cloudflare":
            
            try:
                customers_actives = get_qradar.customers_cloudflare()
            except Exception as e:
                current_app.logger.error(f"{str(request.url)}: {e}")
                return redirect(request.url)

            if customer:
                
                try:
                    dates_actives = get_qradar.dates_actives()
                except Exception as e:
                    current_app.logger.error(f"{str(request.url)}: {e}")
                    return redirect(request.url)

                current_customer_name = customers_actives[customer]

                # if date:
                #     table_1 = get_qradar.tabla_reque_acep_boque_per_dominio(
                #         customer = customer,
                #         date = date
                #     )
                    
                #     return render_template(
                #         "analysis_qradar/cloudflare/index.html",
                #         page={"title": ""},
                #         services = services,
                #         current_service = service,
                #         customers_actives = customers_actives,
                #         current_customer = customer,
                #         current_customer_name = current_customer_name,
                #         dates_actives = dates_actives,
                #         current_date = date,
                #         current_pos = pos,
                #         table_1 = table_1 
                #     )

                return render_template(
                    "analysis_qradar/cloudflare/index.html",
                    page={"title": ""},
                    services = services,
                    current_service = service,
                    customers_actives = customers_actives,
                    current_customer = customer,
                    current_customer_name = current_customer_name,
                    dates_actives = dates_actives
                )
                
            return render_template(
                "analysis_qradar/cloudflare/index.html",
                page={"title": "Análisis de Cloudflare - QRadar."},
                services = services,
                current_service = service,
                customers_actives = customers_actives
            )
        
        if service == "firepower":
            
            try: 
                customers_actives = get_qradar.customers_firepower()
            except Exception as e:
                current_app.logger.error(f"{str(request.url)}: {e}")
                return redirect(request.url)
            
            if customer:
                dates_actives = get_qradar.dates_actives()
                current_customer_name = customers_actives[customer]

                if date:

                    try:
                        data = get_qradar.total_firepower(
                            customer = customer,
                            date = date
                        )
                    except Exception as e:
                        current_app.logger.error(f"{str(request.url)}: {e}")
                        return redirect(request.url)

                    if date != "2023-01-01":
                        data_grah = data["data_grah"]
                        data_table_top_1 = data["table_top"]["1"]
                        data_table_top_2 = data["table_top"]["2"]
                        data_table_top_3 = data["table_top"]["3"]
                        data_table_1 = data["table_all"]["1"]
                        data_table_2 = data["table_all"]["2"]
                        data_table_3 = data["table_all"]["3"]
                        data_table_4 = data["table_all"]["4"]
                        data_table_5 = data["table_all"]["5"]
                        data_table_6 = data["table_all"]["6"]
                        data_table_7 = data["table_all"]["7"]
                        data_table_8 = data["table_all"]["8"]
                        data_table_9 = data["table_all"]["9"]
                        data_table_10 = data["table_all"]["10"]
                        data_table_11 = data["table_all"]["11"]
                        name_date = data["name_date"]
                        year = data["year"]

                        return render_template(
                            "analysis_qradar/firepower/index.html",
                            page={"title": ""},
                            services = services,
                            current_service = service,
                            customers_actives = customers_actives,
                            current_customer = customer,
                            current_customer_name = current_customer_name,
                            dates_actives = dates_actives,
                            current_date = date,
                            current_pos = pos,
                            name_date = name_date,
                            year = year,
                            data_grah = data_grah,
                            data_table_top_1 = data_table_top_1,
                            data_table_top_2 = data_table_top_2,
                            data_table_top_3 = data_table_top_3,
                            data_table_1 = data_table_1,
                            data_table_2 = data_table_2,
                            data_table_3 = data_table_3,
                            data_table_4 = data_table_4,
                            data_table_5 = data_table_5,
                            data_table_6 = data_table_6,
                            data_table_7 = data_table_7,
                            data_table_8 = data_table_8,
                            data_table_9 = data_table_9,
                            data_table_10 = data_table_10,
                            data_table_11 = data_table_11
                        )
                    else:
                        data_grah = data["data_grah"]
                        data_table_top_1 = data["table_top"]["1"]
                        data_table_top_2 = data["table_top"]["2"]
                        data_table_top_3 = data["table_top"]["3"]
                        data_table_1 = data["table_all"]["1"]
                        data_table_2 = data["table_all"]["2"]
                        data_table_3 = data["table_all"]["3"]
                        data_table_4 = data["table_all"]["4"]
                        data_table_5 = data["table_all"]["5"]
                        data_table_6 = data["table_all"]["6"]
                        data_table_7 = data["table_all"]["7"]
                        data_table_8 = data["table_all"]["8"]
                        data_table_9 = data["table_all"]["9"]
                        name_date = data["name_date"]
                        year = data["year"]

                        return render_template(
                            "analysis_qradar/firepower/index.html",
                            page={"title": ""},
                            services = services,
                            current_service = service,
                            customers_actives = customers_actives,
                            current_customer = customer,
                            current_customer_name = current_customer_name,
                            dates_actives = dates_actives,
                            current_date = date,
                            current_pos = pos,
                            name_date = name_date,
                            year = year,
                            data_grah = data_grah,
                            data_table_top_1 = data_table_top_1,
                            data_table_top_2 = data_table_top_2,
                            data_table_top_3 = data_table_top_3,
                            data_table_1 = data_table_1,
                            data_table_2 = data_table_2,
                            data_table_3 = data_table_3,
                            data_table_4 = data_table_4,
                            data_table_5 = data_table_5,
                            data_table_6 = data_table_6,
                            data_table_7 = data_table_7,
                            data_table_8 = data_table_8,
                            data_table_9 = data_table_9
                        )
                
                return render_template(
                    "analysis_qradar/firepower/index.html",
                    page={"title": ""},
                    services = services,
                    current_service = service,
                    customers_actives = customers_actives,
                    current_customer = customer,
                    current_customer_name = current_customer_name,
                    dates_actives = dates_actives
                )
        
            return render_template(
                "analysis_qradar/firepower/index.html",
                page={"title": "Análisis de Firepower - QRadar."},
                services = services,
                current_service = service,
                customers_actives = customers_actives
            )
    
    return render_template(
        "analysis_qradar/index/index.html",
        page={"title": "Análisis de QRadar."},
        services = services
    )

