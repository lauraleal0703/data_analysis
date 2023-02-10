from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

from webapp.analyzer.get_data_portal_clientes import path_temp
from webapp.analyzer import get_data_portal_clientes

portal_clientes = Blueprint("portal_clientes", __name__, url_prefix="/portal_clientes")


@portal_clientes.get("/otrs")
def otrs():
    update_date = get_data_portal_clientes.get_update_date(path_temp)
    customers_actives = get_data_portal_clientes.get_customers_period(path_temp)
    calendar = get_data_portal_clientes.get_calendar_spanish(path_temp)
    customers_name = get_data_portal_clientes.get_customers_actives(path_temp)
    
    if request.method == "GET":
        customer = request.args.get("customer", type=str)
        year = request.args.get("year", type=str)
        month = request.args.get("month", type=str)

        if customer:
            data = get_data_portal_clientes.get_tickets_customer_years(
                path_temp, 
                customer
            )
            year_actives = data["data_x"]
            data_grah_y = data["data_y"]
            total_tickets =  data["total_tickets"]
            customer_name = customers_name[customer]

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


            return render_template(
                "portal_clientes/otrs/customers/index.html",
                page={"title": "Data Adaptive Security"},
                customers_actives=customers_actives,
                current_customer=customer,
                customer_name=customer_name,
                year_actives=year_actives,
                data_grah_x=year_actives,
                data_grah_y=data_grah_y,
                total_tickets=total_tickets
            )
    
    return render_template(
        "portal_clientes/otrs/index/index.html",
        page={"title": "Data Adaptive Security"},
        customers_actives=customers_actives,
        update_date=update_date
    )
