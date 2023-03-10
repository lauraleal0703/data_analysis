from flask import Blueprint
from flask import render_template
from flask import request
from flask import current_app

from webapp.analyzer import get_otrs

from pprint import pprint


analysis_otrs = Blueprint("analysis_otrs", __name__, url_prefix="/analysis_otrs")


@analysis_otrs.get("/")
def index():
    queues = {
        "administrators": "De Administración",
        "analysts": "De Análisis",
        "conflictMonth": "Tickets en Conflicto de la última semana"
    }

    if request.method == "GET":
        refresh_queue = request.args.get("refresh_queue", type=int)
        refresh_customer = request.args.get("refresh_customer", type=int)
        refresh_year = request.args.get("refresh_year", type=int)
        refresh_month = request.args.get("refresh_month", type=int)
        queue = request.args.get("queue", type=str)
        customer = request.args.get("customer", type=str)
        year = request.args.get("year", type=str)
        table_month = request.args.get("table_month", type=str)
        table_year = request.args.get("table_year", type=str)
        month = request.args.get("month", type=str)
        table_day = request.args.get("table_day", type=str)
        

        if queue:
            if queue == "administrators":
                queue_id = 6
            
            if queue == "analysts":
                queue_id = 9
            
            if queue == "conflictMonth":
                time = "month"
                try:
                    data_tickets_conflic = get_otrs.get_tickets_conflic(
                        time = time,
                        refresh = refresh_queue
                    )
                except Exception as e:
                    current_app.logger.error(f"{str(request.url)}: {e}")
                current_date = data_tickets_conflic["current_date"]

                return render_template(
                    "analysis_otrs/customers/index_table.html",
                    page = {"title": """Se muestran los tickets que durante la última semana
                        no tienen servicio asociado o el usuario es de otra cola."""
                    },
                    queues = queues,
                    current_queue = queue,
                    data_tickets_conflic = data_tickets_conflic,
                    current_date = current_date
                )
            
            try:
                data_grah_general = get_otrs.get_count_tickets_years(
                    queue_id = queue_id,
                    customers = True,
                    refresh = refresh_queue
                )

            except Exception as e:
                current_app.logger.error(f"{str(request.url)}: {e}")
            
            customers_actives = data_grah_general["list_total_tickets"]
            current_date = data_grah_general["current_date"]
            
            if customer:
                try:
                    data = get_otrs.get_tickets_filtred(
                        customer_id = customer,
                        queue_id = queue_id,
                        customers = True,
                        refresh = refresh_customer
                    )
                except Exception as e:
                    current_app.logger.error(f"{str(request.url)}: {e}")
                
                current_date = data["current_date"]
                data_grah_general = data["data_grah_general"]
                data_total_table_year = data["data_total_table"]
                data_grah_services = data["data_grah_services"]
                data_grah_date_services = data["data_grah_date_services"]
                data_grah_users = data["data_grah_users"]
                data_grah_date_users = data["data_grah_date_users"]
                
                if year:
                    try:
                        data = get_otrs.get_tickets_filtred(
                            customer_id = customer,
                            queue_id = queue_id,
                            year = year,
                            customers = True,
                            refresh = refresh_year
                        )
                    except Exception as e:
                        current_app.logger.error(f"{str(request.url)}: {e}")
                    
                    current_date = data["current_date"]
                    data_grah_general = data["data_grah_general"]
                    data_total_table_month = data["data_total_table"]
                    data_grah_services = data["data_grah_services"]
                    data_grah_date_services = data["data_grah_date_services"]
                    data_grah_users = data["data_grah_users"]
                    data_grah_date_users = data["data_grah_date_users"]

                    if month:
                        try:
                            data = get_otrs.get_tickets_filtred(
                                customer_id = customer,
                                queue_id = queue_id,
                                year = year,
                                month = month,
                                customers = True,
                                refresh = refresh_month
                            )
                        except Exception as e:
                            current_app.logger.error(f"{str(request.url)}: {e}")
                        
                        current_date = data["current_date"]
                        data_grah_general = data["data_grah_general"]
                        data_total_table_day = data["data_total_table"]
                        data_grah_services = data["data_grah_services"]
                        data_grah_date_services = data["data_grah_date_services"]
                        data_grah_users = data["data_grah_users"]
                        data_grah_date_users = data["data_grah_date_users"]
                        
                        if table_day:
                            data_tickets = data["dict_tickets"][table_day]["total"]["tickets"]
            
                            return render_template(
                                "analysis_otrs/customers/index_table.html",
                                page={"title": ""},
                                queues = queues,
                                current_queue = queue,
                                customers_actives=customers_actives,
                                current_date = current_date,
                                current_customer=customer,
                                current_year = year,
                                current_month = month,
                                current_table_day = table_day,
                                data_total_year = data_total_table_year,
                                data_total_month = data_total_table_month,
                                data_total_table_day = data_total_table_day,
                                data_tickets = data_tickets
                            )

                        return render_template(
                            "analysis_otrs/customers/index.html",
                            page={"title": ""},
                            queues = queues,
                            current_queue = queue,
                            customers_actives = customers_actives,
                            current_date = current_date,
                            current_customer = customer,
                            current_year = year,
                            current_month = month,
                            data_total_year = data_total_table_year,
                            data_total_month = data_total_table_month,
                            data_total_day = data_total_table_day,
                            data_total_table_day = data_total_table_day,
                            data_grah_general = data_grah_general,
                            data_grah_services = data_grah_services,
                            data_grah_date_services = data_grah_date_services,
                            data_grah_users = data_grah_users,
                            data_grah_date_users = data_grah_date_users
                        )

                    if table_month:
                        data_tickets = data["dict_tickets"][table_month]["total"]["tickets"]
        
                        return render_template(
                            "analysis_otrs/customers/index_table.html",
                            page={"title": ""},
                            queues = queues,
                            current_queue = queue,
                            customers_actives = customers_actives,
                            current_date = current_date,
                            current_customer = customer,
                            current_year = year,
                            current_table_month = table_month,
                            data_total_year = data_total_table_year,
                            data_total_month = data_total_table_month,
                            data_total_table_month = data_total_table_month,
                            data_tickets = data_tickets
                        )
                    
                    return render_template(
                        "analysis_otrs/customers/index.html",
                        page={"title": ""},
                        queues = queues,
                        current_queue = queue,
                        customers_actives = customers_actives,
                        current_date = current_date,
                        current_customer = customer,
                        current_year = year,
                        data_total_year = data_total_table_year,
                        data_total_month = data_total_table_month,
                        data_total_table_month = data_total_table_month,
                        data_grah_general = data_grah_general,
                        data_grah_services = data_grah_services,
                        data_grah_date_services = data_grah_date_services,
                        data_grah_users = data_grah_users,
                        data_grah_date_users = data_grah_date_users
                    )

                if table_year:
                    data_tickets = data["dict_tickets"][table_year]["total"]["tickets"]
                    
                    return render_template(
                        "analysis_otrs/customers/index_table.html",
                        page={"title": ""},
                        queues = queues,
                        current_queue = queue,
                        customers_actives = customers_actives,
                        current_date = current_date,
                        current_customer = customer,
                        current_table_year = table_year,
                        data_total_year = data_total_table_year,
                        data_total_table_year = data_total_table_year,
                        data_tickets = data_tickets
                    )
                
                return render_template(
                    "analysis_otrs/customers/index.html",
                    page={"title": ""},
                    queues = queues,
                    current_queue = queue,
                    customers_actives = customers_actives,
                    current_date = current_date,
                    current_customer = customer,
                    data_total_year = data_total_table_year,
                    data_total_table_year = data_total_table_year,
                    data_grah_general = data_grah_general,
                    data_grah_services = data_grah_services,
                    data_grah_date_services = data_grah_date_services,
                    data_grah_users = data_grah_users,
                    data_grah_date_users = data_grah_date_users
                )

            return render_template(
                "analysis_otrs/customers/index.html",
                page={"title": ""},
                queues = queues,
                current_queue = queue,
                customers_actives = customers_actives,
                current_date = current_date,
                data_grah_general = data_grah_general
            )
        
    return render_template(
        "analysis_otrs/customers/index.html",
        page={"title": """En la pestaña superior puede seleccionar la vista de
            los tickets generados por los clientes de Adaptive Security
            para ser atendidos por los Administradores o los Analistas."""
        },
        queues = queues
    )


@analysis_otrs.get("/attend")
def attend():
    queues = {
        "administrators": "Administradores",
        "analysts": "Analistas"
    }

    if request.method == "GET":
        refresh_queue = request.args.get("refresh_queue", type=int)
        refresh_user = request.args.get("refresh_user", type=int)
        refresh_year = request.args.get("refresh_year", type=int)
        refresh_month = request.args.get("refresh_month", type=int)
        queue = request.args.get("queue", type=str)
        user = request.args.get("user", type=str)
        year = request.args.get("year", type=str)
        table_month = request.args.get("table_month", type=str)
        table_year = request.args.get("table_year", type=str)
        month = request.args.get("month", type=str)
        table_day = request.args.get("table_day", type=str)

        if queue:
            if queue == "administrators":
                queue_id = 6
            
            if queue == "analysts":
                queue_id = 9
            
            try:
                data_grah_general = get_otrs.get_count_tickets_years(
                    queue_id = queue_id,
                    users = True,
                    refresh = refresh_queue
                )

            except Exception as e:
                current_app.logger.error(f"{str(request.url)}: {e}")
            
            users_actives = data_grah_general["list_total_tickets"]
            current_date = data_grah_general["current_date"]

            if user:
                try:
                    data = get_otrs.get_tickets_filtred(
                        user_id = user,
                        queue_id = queue_id,
                        users = True,
                        refresh = refresh_user
                    )
                except Exception as e:
                    current_app.logger.error(f"{str(request.url)}: {e}")

                current_date = data["current_date"]
                data_grah_general = data["data_grah_general"]
                data_total_table_year = data["data_total_table"]
                data_grah_services = data["data_grah_services"]
                data_grah_customers = data["data_grah_customers"]
                data_grah_date_services = data["data_grah_date_services"]
                data_grah_date_customers = data["data_grah_date_customers"]

                if year:
                    try:
                        data = get_otrs.get_tickets_filtred(
                            user_id = user,
                            queue_id = queue_id,
                            year = year,
                            users = True,
                            refresh = refresh_year
                        )
                    except Exception as e:
                        current_app.logger.error(f"{str(request.url)}: {e}")
                    
                    current_date = data["current_date"]
                    data_grah_general = data["data_grah_general"]
                    data_total_table_month = data["data_total_table"]
                    data_grah_services = data["data_grah_services"]
                    data_grah_customers = data["data_grah_customers"]
                    data_grah_date_services = data["data_grah_date_services"]
                    data_grah_date_customers = data["data_grah_date_customers"]

                    if month:
                        try:
                            data = get_otrs.get_tickets_filtred(
                                user_id = user,
                                queue_id = queue_id,
                                year = year,
                                month = month,
                                users = True,
                                refresh = refresh_month
                            )
                        except Exception as e:
                            current_app.logger.error(f"{str(request.url)}: {e}")
                        
                        current_date = data["current_date"]
                        data_grah_general = data["data_grah_general"]
                        data_total_table_day = data["data_total_table"]
                        data_grah_services = data["data_grah_services"]
                        data_grah_customers = data["data_grah_customers"]
                        data_grah_date_services = data["data_grah_date_services"]
                        data_grah_date_customers = data["data_grah_date_customers"]
                        
                        if table_day:
                            data_tickets = data["dict_tickets"][table_day]["total"]["tickets"]
            
                            return render_template(
                                "analysis_otrs/users/index_table.html",
                                page={"title": ""},
                                queues = queues,
                                current_queue = queue,
                                users_actives = users_actives,
                                current_date = current_date,
                                current_user = user,
                                current_year = year,
                                current_month = month,
                                current_table_day = table_day,
                                data_total_year = data_total_table_year,
                                data_total_month = data_total_table_month,
                                data_total_table_day = data_total_table_day,
                                data_tickets = data_tickets
                            )

                        return render_template(
                            "analysis_otrs/users/index.html",
                            page={"title": ""},
                            queues=queues,
                            current_queue = queue,
                            users_actives = users_actives,
                            current_date = current_date,
                            current_user = user,
                            current_year = year,
                            current_month = month,
                            data_total_year = data_total_table_year,
                            data_total_month = data_total_table_month,
                            data_total_day = data_total_table_day,
                            data_total_table_day = data_total_table_day,
                            data_grah_general = data_grah_general,
                            data_grah_services = data_grah_services,
                            data_grah_customers = data_grah_customers,
                            data_grah_date_services = data_grah_date_services,
                            data_grah_date_customers = data_grah_date_customers
                        )

                    if table_month:
                        data_tickets = data["dict_tickets"][table_month]["total"]["tickets"]
        
                        return render_template(
                            "analysis_otrs/users/index_table.html",
                            page={"title": ""},
                            queues = queues,
                            current_queue = queue,
                            users_actives = users_actives,
                            current_date = current_date,
                            current_user = user,
                            current_year = year,
                            current_table_month = table_month,
                            data_total_year = data_total_table_year,
                            data_total_month = data_total_table_month,
                            data_total_table_month = data_total_table_month,
                            data_tickets = data_tickets
                        )
                    
                    return render_template(
                        "analysis_otrs/users/index.html",
                        page={"title": ""},
                        queues = queues,
                        current_queue = queue,
                        users_actives = users_actives,
                        current_date = current_date,
                        current_user = user,
                        current_year = year,
                        data_total_year = data_total_table_year,
                        data_total_month = data_total_table_month,
                        data_total_table_month = data_total_table_month,
                        data_grah_general = data_grah_general,
                        data_grah_services = data_grah_services,
                        data_grah_customers = data_grah_customers,
                        data_grah_date_services = data_grah_date_services,
                        data_grah_date_customers = data_grah_date_customers
                    )

                if table_year:
                    data_tickets = data["dict_tickets"][table_year]["total"]["tickets"]
                    
                    return render_template(
                        "analysis_otrs/users/index_table.html",
                        page={"title": ""},
                        queues = queues,
                        current_queue = queue,
                        users_actives = users_actives,
                        current_date = current_date,
                        current_user = user,
                        current_table_year = table_year,
                        data_total_year = data_total_table_year,
                        data_total_table_year = data_total_table_year,
                        data_tickets = data_tickets
                    )
                
                return render_template(
                    "analysis_otrs/users/index.html",
                    page={"title": ""},
                    queues = queues,
                    current_queue = queue,
                    users_actives = users_actives,
                    current_date = current_date,
                    current_user = user,
                    data_total_year = data_total_table_year,
                    data_total_table_year = data_total_table_year,
                    data_grah_general = data_grah_general,
                    data_grah_services = data_grah_services,
                    data_grah_customers = data_grah_customers,
                    data_grah_date_services = data_grah_date_services,
                    data_grah_date_customers = data_grah_date_customers
                )

            return render_template(
                "analysis_otrs/users/index.html",
                page={"title": ""},
                queues = queues,
                current_queue = queue,
                users_actives = users_actives,
                current_date = current_date,
                data_grah_general = data_grah_general
            )
        
    return render_template(
        "analysis_otrs/users/index.html",
        page = {"title": """En la pestaña superior puede seleccionar la vista de
            los tickets atendidos por los Administradores o los Analistas de
            Adaptive Security."""
        },
        queues = queues
    )