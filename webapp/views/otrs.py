from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for


from webapp.analyzer.otrs.models.customer_company import CustomerCompany
from webapp.analyzer.otrs.models.service import Service
from webapp.analyzer import get_otrs


otrs = Blueprint("otrs", __name__, url_prefix="/otrs")


@otrs.get("/")
def index():
    queues = {
        "administrators": "Tickets queue_id=6",
        "analysts": "Tickets queue_id=9"
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
        month = request.args.get("month", type=int)

        if queue:
            if queue == "administrators":
                queue_id = 6
            
            if queue == "analysts":
                queue_id = 9

            customers_actives = get_otrs.customers_by_period(queue_id=queue_id)
            
            if customer:
                data = get_otrs.get_tickets_customer_years(
                    customer_id = customer,
                    queue_id = queue_id
                )
                year_actives = data["data_x"]
                customer_name = data["customer_name"]
                data_grah_y = data["data_y"]
                total_tickets =  data["total_tickets"]
                data_total = data["data_total"]
                data_service = data["data_service"]
                data_user = data["data_user"]
                
                if year_table:
                    data_tickets = data["data_tickets"][year_table]

                    return render_template(
                        "otrs/customers/index_table.html",
                        page={"title": "Data Adaptive Security"},
                        queues=queues,
                        current_queue=queue,
                        customers_actives=customers_actives,
                        current_customer=customer,
                        customer_name=customer_name,
                        current_year_table=year_table,
                        data_total=data_total,
                        data_tickets=data_tickets
                    )
                
                if year_service and service:
                    service = int(service) if service.isdigit() else service
                    data_tickets = data_service[year_service][service]["tickets"]
                    
                    return render_template(
                        "otrs/customers/index_table.html",
                        page={"title": "Data Adaptive Security"},
                        queues=queues,
                        current_queue=queue,
                        customers_actives=customers_actives,
                        current_customer=customer,
                        customer_name=customer_name,
                        current_year_service=year_service,
                        data_tickets=data_tickets,
                        current_service=service 
                    )
                
                if year_user and user:
                    data_tickets = data_user[year_user][user]["tickets"]
                    
                    return render_template(
                        "otrs/customers/index_table.html",
                        page={"title": "Data Adaptive Security"},
                        queues=queues,
                        current_queue=queue,
                        customers_actives=customers_actives,
                        current_customer=customer,
                        data_tickets=data_tickets   
                    )
                
                if year_user and user_not:
                    data_tickets = data_user[year_user]["user_not"][user_not]["tickets"]
                    
                    return render_template(
                        "otrs/customers/index_table.html",
                        page={"title": "Data Adaptive Security"},
                        queues=queues,
                        current_queue=queue,
                        customers_actives=customers_actives,
                        current_customer=customer,
                        data_tickets=data_tickets   
                    )

                

                '''
                if year:
                    data = get_data_portal_clientes.get_tickets_customer_months_year(
                        path_temp,
                        customer,
                        year
                    )
                    months_actives = data["months_actives"]
                    data_grah_x= data["data_x"]
                    data_grah_y = data["data_y"]
                    total_tickets = data["total_tickets"]

                    if month:
                        data = get_data_portal_clientes.get_tickets_customer_days_month_year(
                            path_temp,
                            customer,
                            year,
                            month
                        )
                        data_grah_x= data["data_x"]
                        data_grah_y = data["data_y"]
                        total_tickets = data["total_tickets"]
                        month_name = calendar[month]
                        

                        return render_template(
                            "portal_clientes/otrs/customers/index.html",
                            page={"title": "Data Adaptive Security"},
                            customers_actives=customers_actives,
                            current_customer=customer,
                            customer_name=customer_name,
                            year_actives=year_actives,
                            current_year=year,
                            months_actives=months_actives,
                            current_month=month,
                            month_name=month_name,
                            data_grah_x=data_grah_x,
                            data_grah_y=data_grah_y,
                            total_tickets=total_tickets
                        )

                    return render_template(
                        "portal_clientes/otrs/customers/index.html",
                        page={"title": "Data Adaptive Security"},
                        customers_actives=customers_actives,
                        current_customer=customer,
                        customer_name=customer_name,
                        year_actives=year_actives,
                        current_year=year,
                        months_actives=months_actives,
                        data_grah_x=data_grah_x,
                        data_grah_y=data_grah_y,
                        total_tickets=total_tickets
                    )
                '''

                return render_template(
                    "otrs/customers/index.html",
                    page={"title": "Data Adaptive Security"},
                    queues=queues,
                    current_queue=queue,
                    customers_actives=customers_actives,
                    current_customer=customer,
                    customer_name=customer_name,
                    year_actives=year_actives,
                    data_grah_x=year_actives,
                    data_grah_y=data_grah_y,
                    total_tickets=total_tickets,
                    data_total=data_total,
                    data_service=data_service,
                    data_user=data_user
                )
    
            return render_template(
                "otrs/customers/index.html",
                page={"title": "Data Adaptive Security"},
                queues=queues,
                current_queue=queue,
                customers_actives=customers_actives
            )
        
        return render_template(
            "otrs/index/index.html",
            page={"title": "Data Adaptive Security"},
            queues = queues
        )