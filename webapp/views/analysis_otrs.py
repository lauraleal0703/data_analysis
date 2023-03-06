from flask import Blueprint
from flask import render_template
from flask import request
from flask import current_app
from flask import redirect

from webapp.analyzer import get_otrs

from pprint import pprint


analysis_otrs = Blueprint("analysis_otrs", __name__, url_prefix="/analysis_otrs")


@analysis_otrs.get("/")
def index():
    queues = {
        "administrators": "De Administración",
        "analysts": "De Análisis",
        "conflictMonth": "Tickests en Conflicto del 2023",
        "conflictYear": "Tickests en Conflicto del 2022",
        "conflictTwoYear": "Tickests en Conflicto 2021"
    }

    if request.method == "GET":
        queue = request.args.get("queue", type=str)
        customer = request.args.get("customer", type=str)
        year_table = request.args.get("year_table", type=int)
        year_service = request.args.get("year_service", type=int)
        service = request.args.get("service", type=str)
        year_user = request.args.get("year_user", type=int)
        user = request.args.get("user", type=int)
        user_not = request.args.get("user_not", type=int)
        year = request.args.get("year", type=int)
        month_table = request.args.get("month_table", type=int)
        month_service = request.args.get("month_service", type=int)
        month_user = request.args.get("month_user", type=int)
        

        if queue:
            if queue == "administrators":
                queue_id = 6
            
            if queue == "analysts":
                queue_id = 9
            
            if queue == "conflictMonth":
                time = "month"
                
                try:
                    data_tickets_conflic = get_otrs.get_tickets_conflic(
                        time = time
                    )
                except Exception as e:
                    current_app.logger.error(f"{str(request.url)}: {e}")
                    return redirect(request.url)

                return render_template(
                    "analysis_otrs/customers/index_table.html",
                    page = {"title": """Se muestran los tickets que durante la última semana
                        no tienen servicio asociado o el usuario es de otra cola."""
                    },
                    queues = queues,
                    current_queue = queue,
                    data_tickets_conflic = data_tickets_conflic,
                    mensaje = "OK"
                )
            
            if queue == "conflictYear":
                time = "year"
                
                try:
                    data_tickets_conflic = get_otrs.get_tickets_conflic(
                        time = time
                    )
                except Exception as e:
                    current_app.logger.error(f"{str(request.url)}: {e}")
                    return redirect(request.url)

                return render_template(
                    "analysis_otrs/customers/index_table.html",
                    page = {"title": """Se muestran los tickets que en el
                        año 2022 no tienen servicio asociado o el usuario
                        es de otra cola."""
                    },
                    queues = queues,
                    current_queue = queue,
                    data_tickets_conflic = data_tickets_conflic,
                    mensaje = "OK"
                )
            
            if queue == "conflictTwoYear":
                time = "twoYear"
                
                try:
                    data_tickets_conflic = get_otrs.get_tickets_conflic(
                        time = time
                    )
                except Exception as e:
                    current_app.logger.error(f"{str(request.url)}: {e}")
                    return redirect(request.url)

                return render_template(
                    "analysis_otrs/customers/index_table.html",
                    page = {"title": """Se muestran los tickets que en el
                        año 2021 no tienen servicio asociado o el usuario
                        es de otra cola."""
                    },
                    queues = queues,
                    current_queue = queue,
                    data_tickets_conflic = data_tickets_conflic,
                    mensaje = "OK"
                )
            
            try:
                data_grah = get_otrs.get_count_tickets_customers_years(queue_id=queue_id)
                customers_actives = data_grah["total_tickets_customers"]
            except Exception as e:
                    current_app.logger.error(f"{str(request.url)}: {e}")
                    return redirect(request.url)
            
            if customer:

                try:
                    data = get_otrs.get_tickets_customer_years(
                        customer_id = customer,
                        queue_id = queue_id
                    )
                except Exception as e:
                    current_app.logger.error(f"{str(request.url)}: {e}")
                    return redirect(request.url)
                
                data_grah = data
                customer_name = data["customer_name"]
                data_total = data["data_total"]
                year_actives = data_total
                total_tickets = data["total_tickets"]
                data_service = data["data_service"]
                data_user = data["data_user"]
                data_grah_service = data["data_grah_service"]
                data_x_service = data["data_x_service"]
                
                if year_table:
                    data_tickets = data["data_tickets"][year_table]

                    return render_template(
                        "analysis_otrs/customers/index_table.html",
                        page={"title": ""},
                        queues=queues,
                        current_queue=queue,
                        year_actives_table=data_total,
                        customers_actives=customers_actives,
                        current_customer=customer,
                        customer_name=customer_name,
                        current_year_table=year_table,
                        data_tickets=data_tickets
                    )
                
                if year_service and service:
                    service = int(service) if service.isdigit() else service
                    data_tickets = data_service[year_service][service]["tickets"]
                    data_service_total = data["data_service_total"][year_service]
                    
                    return render_template(
                        "analysis_otrs/customers/index_table.html",
                        page={"title": ""},
                        queues=queues,
                        current_queue=queue,
                        customers_actives=customers_actives,
                        current_customer=customer,
                        current_year_service=year_service,
                        data_service_total=data_service_total,
                        data_tickets=data_tickets,
                        current_service=service 
                    )
                
                if year_user and user:
                    data_tickets = data_user[year_user][user]["tickets"]
                    data_user_total = data["data_user_total"][year_user]
                    
                    return render_template(
                        "analysis_otrs/customers/index_table.html",
                        page={"title": ""},
                        queues=queues,
                        current_queue=queue,
                        customers_actives=customers_actives,
                        current_customer=customer,
                        current_year_user=year_user,
                        current_user=user,
                        data_user_total=data_user_total,
                        data_tickets=data_tickets   
                    )
                
                if year_user and user_not:
                    data_tickets = data_user[year_user]["user_not"][user_not]["tickets"]
                    data_user_not_total = data["data_user_not_total"][year_user]
                    
                    return render_template(
                        "analysis_otrs/customers/index_table.html",
                        page={"title": ""},
                        queues=queues,
                        current_queue=queue,
                        customers_actives=customers_actives,
                        current_customer=customer,
                        current_year_user_not=year_user,
                        current_user_not=user_not,
                        data_user_not_total=data_user_not_total,
                        data_tickets=data_tickets  
                    )
                    
                if year:
                    try:
                        data = get_otrs.get_tickets_customer_months_year(
                            customer_id = customer,
                            queue_id = queue_id,
                            year=year
                        )
                    except Exception as e:
                        current_app.logger.error(f"{str(request.url)}: {e}")
                        return redirect(request.url)
                    
                    data_grah = data
                    customer_name = data["customer_name"]
                    data_total = data["data_total"]
                    data_total_sorted = data["data_total_sorted"]
                    total_tickets = data["total_tickets"]
                    data_service = data["data_service"]
                    data_user = data["data_user"]
                    data_grah_service = data["data_grah_service"]
                    data_x_service = data["data_x_service"]
                    data_x_service_total = data["data_x_service_total"]
                    data_grah_service_total = data["data_grah_service_total"]
                    
                    if month_table:
                        data_tickets = data["data_tickets"][month_table]["tickets"]

                        return render_template(
                            "analysis_otrs/customers/index_table.html",
                            page={"title": ""},
                            queues=queues,
                            current_queue=queue,
                            year_actives=year_actives,
                            current_year=year,
                            months_actives_table=data_total_sorted,
                            customers_actives=customers_actives,
                            current_customer=customer,
                            customer_name=customer_name,
                            current_month_table=month_table,
                            data_tickets=data_tickets
                        )
                    
                    if month_service and service:
                        service = int(service) if service.isdigit() else service
                        data_tickets = data_service[month_service][service]["tickets"]
                        data_service_total_month = data["data_service_total"][month_service]

                        return render_template(
                            "analysis_otrs/customers/index_table.html",
                            page={"title": ""},
                            queues=queues,
                            current_queue=queue,
                            year_actives=year_actives,
                            current_year=year,
                            customers_actives=customers_actives,
                            current_month_service=month_service,
                            month_service_name=data_total,
                            current_service_month=service,
                            current_customer=customer,
                            customer_name=customer_name,
                            current_month_table=month_table,
                            data_service_total_month=data_service_total_month,
                            data_tickets=data_tickets
                        )
                    
                    if month_user and user:
                        data_tickets = data_user[month_user][user]["tickets"]
                        data_user_total = data["data_user_total"][month_user]
                        
                        return render_template(
                            "analysis_otrs/customers/index_table.html",
                            page={"title": ""},
                            queues=queues,
                            current_queue=queue,
                            year_actives=year_actives,
                            current_year=year,
                            customers_actives=customers_actives,
                            current_customer=customer,
                            current_month_user=month_user,
                            current_user=user,
                            current_month_service=month_service,
                            month_user_name=data_total,
                            data_user_total_month=data_user_total,
                            data_tickets=data_tickets   
                        )
                    
                    if month_user and user_not:
                        
                        data_tickets = data_user[month_user]["user_not"][user_not]["tickets"]
                        data_user_not_total = data["data_user_not_total"][month_user]

                        return render_template(
                            "analysis_otrs/customers/index_table.html",
                            page={"title": ""},
                            queues=queues,
                            current_queue=queue,
                            year_actives=year_actives,
                            current_year=year,
                            customers_actives=customers_actives,
                            current_customer=customer,
                            current_month_user_not=month_user,
                            current_user_not=user_not,
                            month_user_name=data_total,
                            data_user_not_total_month=data_user_not_total,
                            data_tickets=data_tickets  
                        )
                    
                    return render_template(
                        "analysis_otrs/customers/index.html",
                        page={"title": ""},
                        queues=queues,
                        current_queue=queue,
                        customers_actives=customers_actives,
                        year_actives=year_actives,
                        current_year=year,
                        current_customer=customer,
                        customer_name=customer_name,
                        months_actives=data_total_sorted,
                        data_grah=data_grah,
                        total_tickets=total_tickets,
                        data_total=data_total,
                        data_service=data_service,
                        data_user=data_user,
                        data_grah_service=data_grah_service,
                        data_x_service=data_x_service,
                        data_x_service_total=data_x_service_total,
                        data_grah_service_total=data_grah_service_total
                    )
                
                return render_template(
                    "analysis_otrs/customers/index.html",
                    page={"title": ""},
                    queues=queues,
                    current_queue=queue,
                    customers_actives=customers_actives,
                    current_customer=customer,
                    customer_name=customer_name,
                    year_actives=year_actives,
                    data_grah=data_grah,
                    total_tickets=total_tickets,
                    data_total=data_total,
                    data_service=data_service,
                    data_user=data_user,
                    data_grah_service=data_grah_service,
                    data_x_service=data_x_service
                )

            return render_template(
                "analysis_otrs/customers/index.html",
                page={"title": ""},
                queues=queues,
                current_queue=queue,
                customers_actives=customers_actives,
                data_grah=data_grah
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
        queue = request.args.get("queue", type=str)
        user = request.args.get("user", type=int)
        year = request.args.get("year", type=int)
        table_month = request.args.get("table_month", type=str)
        table_year = request.args.get("table_year", type=int)
        month = request.args.get("month", type=str)
        table_day = request.args.get("table_day", type=int)

        if queue:
            if queue == "administrators":
                queue_id = 6
            
            if queue == "analysts":
                queue_id = 9
            
            try:
                data_grah_general = get_otrs.get_count_tickets_users(
                    queue_id = queue_id
                )
            except Exception as e:
                    current_app.logger.error(f"{str(request.url)}: {e}")
                    return redirect(request.url)
            
            users_actives = data_grah_general["total_tickets_users"]

            if user:
                
                try:
                    data = get_otrs.get_tickets_users(user_id=user)
                except Exception as e:
                    current_app.logger.error(f"{str(request.url)}: {e}")
                    return redirect(request.url)
                
                data_grah_general = data["data_grah_general"]
                data_total_table_year = data["data_total_table"]
                data_grah_services = data["data_grah_services"]
                data_grah_customers = data["data_grah_customers"]
                data_grah_services_year = data["dict_grah_year_services"]
                data_grah_customers_year = data["dict_grah_year_customers"]

                if year:

                    try:
                        data = get_otrs.get_tickets_users(
                            user_id = user,
                            year = year
                        )
                    except Exception as e:
                        current_app.logger.error(f"{str(request.url)}: {e}")
                        return redirect(request.url)
                    
                    data_grah_general = data["data_grah_general"]
                    data_total_table_month = data["data_total_table"]
                    data_grah_services = data["data_grah_services"]
                    data_grah_customers = data["data_grah_customers"]
                    data_grah_services_year = data["dict_grah_year_services"]
                    data_grah_customers_year = data["dict_grah_year_customers"]
                    dict_grah_year = data["dict_grah_year"]

                    if month:
                        
                        try:
                            data = get_otrs.get_tickets_users(
                                user_id = user,
                                year = year,
                                month = month
                            )
                        except Exception as e:
                            current_app.logger.error(f"{str(request.url)}: {e}")
                            return redirect(request.url)
                        
                        data_grah_general = data["data_grah_general"]
                        data_total_table_day = data["data_total_table"]
                        data_grah_services = data["data_grah_services"]
                        data_grah_customers = data["data_grah_customers"]
                        data_grah_services_year = data["dict_grah_year_services"]
                        data_grah_customers_year = data["dict_grah_year_customers"]
                        
                        if table_day:
                            data_tickets = data["dict_tickets"][table_day]["total"]["tickets"]
            
                            return render_template(
                                "analysis_otrs/users/index_table.html",
                                page={"title": ""},
                                queues = queues,
                                current_queue = queue,
                                users_actives = users_actives,
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
                            current_queue=queue,
                            users_actives=users_actives,
                            current_user=user,
                            current_year=year,
                            current_month=month,
                            data_total_year=data_total_table_year,
                            data_total_month=data_total_table_month,
                            data_total_table_day=data_total_table_day,
                            data_grah_general=data_grah_general,
                            data_grah_services=data_grah_services,
                            data_grah_customers=data_grah_customers,
                            data_grah_services_year=data_grah_services_year,
                            data_grah_customers_year=data_grah_customers_year
                        )

                    if table_month:
                        data_tickets = data["dict_tickets"][table_month]["total"]["tickets"]
        
                        return render_template(
                            "analysis_otrs/users/index_table.html",
                            page={"title": ""},
                            queues=queues,
                            current_queue=queue,
                            users_actives=users_actives,
                            current_user=user,
                            current_year=year,
                            current_table_month=table_month,
                            data_total_year=data_total_table_year,
                            data_total_table_month=data_total_table_month,
                            data_tickets=data_tickets
                        )
                    
                    return render_template(
                        "analysis_otrs/users/index.html",
                        page={"title": ""},
                        queues=queues,
                        current_queue=queue,
                        users_actives=users_actives,
                        current_user=user,
                        current_year=year,
                        data_total_year=data_total_table_year,
                        data_total_month=data_total_table_month,
                        data_total_table_month=data_total_table_month,
                        data_grah_general=data_grah_general,
                        data_grah_services=data_grah_services,
                        data_grah_customers=data_grah_customers,
                        data_grah_services_year=data_grah_services_year,
                        data_grah_customers_year=data_grah_customers_year,
                        dict_grah_year=dict_grah_year
                    )

                if table_year:
                    data_tickets = data["dict_tickets"][table_year]["total"]["tickets"]
                    
                    return render_template(
                        "analysis_otrs/users/index_table.html",
                        page={"title": ""},
                        queues=queues,
                        current_queue=queue,
                        users_actives=users_actives,
                        current_user=user,
                        current_table_year=table_year,
                        data_total_table=data_total_table_year,
                        data_tickets=data_tickets
                    )
                
                return render_template(
                    "analysis_otrs/users/index.html",
                    page={"title": ""},
                    queues=queues,
                    current_queue=queue,
                    users_actives=users_actives,
                    current_user=user,
                    data_total_year=data_total_table_year,
                    data_total_table_year=data_total_table_year,
                    data_grah_general=data_grah_general,
                    data_grah_services=data_grah_services,
                    data_grah_customers=data_grah_customers,
                    data_grah_services_year=data_grah_services_year,
                    data_grah_customers_year=data_grah_customers_year
                )

            return render_template(
                "analysis_otrs/users/index.html",
                page={"title": ""},
                queues=queues,
                current_queue=queue,
                users_actives=users_actives,
                data_grah_general=data_grah_general
            )
        
    return render_template(
        "analysis_otrs/index_users/index.html",
        page={"title": """En la pestaña superior puede seleccionar la vista de
            los tickets atendidos por los Administradores o los Analistas de
            Adaptive Security."""
        },
        queues=queues
    )