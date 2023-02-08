from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

from webapp.analyzer import get_data_tickets
from webapp.analyzer.get_data_tickets import path_temp

import numpy  as np
from datetime import datetime
from pprint import pprint


tickets = Blueprint("tickets", __name__, url_prefix="/tickets")


@tickets.get("/")
def index():
    type_tickets = {"customers": "Requeridos por los Clientes",
                    "administrators": "Resueltos por los Administradores",
                    }
    update_date = get_data_tickets.get_update_date(path_temp)

    return render_template(
        "tickets/index/index.html",
        page={"title": "Data Adaptive Security"},
        type_tickets=type_tickets,
        update_date=update_date    
    )

    

@tickets.get("/customers")
def customers():
    def_name = "customers"
    type_tickets = {"customers": "Requeridos por los Clientes",
                    "administrators": "Resueltos por los administradores",
                    }
    list_year = get_data_tickets.get_list_year(path_temp, def_name)
    list_year = sorted([int(year_) for year_ in list_year])
    list_year.reverse()
    customers_actives = get_data_tickets.get_tools_json_temp(path_temp, "customers_actives")
    calendar_spanish = get_data_tickets.get_tools_json_temp(path_temp, "calendar_spanish")
    services_actives = get_data_tickets.get_tools_json_temp(path_temp, "services_actives")
    users_actives = get_data_tickets.get_tools_json_temp(path_temp, "users_actives")

    if request.method == "GET":
        year = request.args.get("year", type=str)
        month_year = request.args.get("month_year", type=str)
        customer = request.args.get("customer", type=str)
        month = request.args.get("month", type=str)
        service = request.args.get("service", type=str)
    
        if not year:
            year = str(list_year[0])

        data = get_data_tickets.get_tickets_json_temp(path_temp, def_name, year)

        total_tickets_customer = {}
        total_tickets = 0
        months_year = []
        months_year_total = {}
        for month_ in data:
            months_year.append(month_)
            total_month = 0
            for customer_ in data[month_]:
                total_month += len(data[month_][customer_].keys())
                total_month_customer = len(data[month_][customer_].keys())
                if customer_ not in total_tickets_customer:
                    total_tickets_customer[customer_] = total_month_customer
                    total_tickets += total_month_customer
                else:
                    total_tickets_customer[customer_] += total_month_customer
                    total_tickets += total_month_customer
            
            months_year_total[month_] = total_month
        
        months_year.reverse()
        months_year = {int(num): (calendar_spanish[num], months_year_total[num])  for num in months_year}
        total_tickets_customer = sorted(total_tickets_customer.items(), key=lambda x:x[1], reverse=True)
        customers = []
        data_grah_temp = []
        for customer_sum in total_tickets_customer:
            customers.append(customer_sum[0])
            data_grah_temp.append(customer_sum[1])
        data_grah = [{"name": "Tickets", "data": data_grah_temp}]

        if month_year and not customer:
            month_year_name = calendar_spanish[month_year]
            total_tickets_customer_month = {}
            total_tickets = 0
            for customer_month in data[month_year]:
                total_customer_month = len(data[month_year][customer_month].keys())
                if customer_ not in total_tickets_customer:
                    total_tickets_customer_month[customer_month] = total_customer_month
                    total_tickets += total_customer_month
            
            total_tickets_customer_month = sorted(total_tickets_customer_month.items(), key=lambda x:x[1], reverse=True)
            customers = []
            data_grah_temp = []
            for customer_sum in total_tickets_customer_month:
                customers.append(customer_sum[0])
                data_grah_temp.append(customer_sum[1])
            data_grah = [{"name": f"Tickets de {calendar_spanish[month_year]}", "data": data_grah_temp}]

            return render_template(
                "tickets/tickets_customers/index.html",
                page={"title": "Data Adaptive Security"},
                type_tickets=type_tickets,
                current_type_ticket=def_name,
                list_year=list_year,
                current_year=year,
                months_year=months_year,
                current_months_year=month_year,
                current_months_year_name=month_year_name,
                total_tickets=total_tickets,
                customers=customers,
                data_grah_x=customers,
                data_grah_y=data_grah      
            )


        if customer:
            months_customer_year_total = {}
            months_customer = []
            data_grah_temp = []
            total_tickets = 0
            for month_ in data:
                if customer in data[month_]:
                    total_month = len(data[month_][customer].keys())
                    months_customer.append(month_)
                    months_customer_year_total[month_] = total_month
                    data_grah_temp.append(total_month)
                    total_tickets += total_month
            
            customer_name = customers_actives[customer]
            data_grah = [{"name": f"Tickets de {customer_name}", "data": data_grah_temp}]
            months = [calendar_spanish[num] for num in months_customer]
            months_customer.reverse()
            months_customer = {int(num): (calendar_spanish[num], months_customer_year_total[num]) for num in months_customer}

            if not month and not service:
                return render_template(
                    "tickets/tickets_customers/index.html",
                    page={"title": "Data Adaptive Security"},
                    type_tickets=type_tickets,
                    current_type_ticket=def_name,
                    list_year=list_year,
                    current_year=year,
                    months_year=months_year,
                    customers=customers,
                    current_customer=customer,
                    customer_name=customer_name,
                    months_customer=months_customer,
                    total_tickets=total_tickets,
                    data_grah_x=months,
                    data_grah_y=data_grah      
                )
        
            services_customer = {}
            total_tickets = len(data[month][customer].keys())
            for ticket_ in data[month][customer]:
                service_id = data[month][customer][ticket_]["service_id"]
                if service_id not in services_customer:
                    services_customer[service_id] = 1
                else:
                    services_customer[service_id] += 1
            
            services_customer = sorted(services_customer.items(), key=lambda x:x[1], reverse=True)
            data_grah_temp = []
            services_customer_active = []
            services_customer_active_name = []
            services_table = {}
            for service_sum in services_customer:
                services_customer_active_name.append(services_actives[str(service_sum[0])])
                services_customer_active.append(str(service_sum[0]))
                data_grah_temp.append(service_sum[1])
                services_table[service_sum[0]] = (services_actives[str(service_sum[0])], service_sum[1])
    
            data_grah = [{"name": f"Tickets de {customer_name}", "data": data_grah_temp}]
            
            if month and not service:
                return render_template(
                    "tickets/tickets_customers/index.html",
                    page={"title": "Data Adaptive Security"},
                    type_tickets=type_tickets,
                    current_type_ticket=def_name,
                    list_year=list_year,
                    current_year=year,
                    months_year=months_year,
                    customers=customers,
                    current_customer=customer,
                    customer_name=customer_name,
                    months_customer=months_customer,
                    current_month_customer=month,
                    total_tickets=total_tickets,
                    data_grah_x=services_customer_active_name,
                    data_grah_y=data_grah,
                    services_table=services_table
                )
            
            ticket_service_table = {}
            for ticket_service in data[month][customer]:
                service_id = data[month][customer][ticket_service]["service_id"]
                if str(service_id) == service:
                    ticket_service_table[ticket_service] = data[month][customer][ticket_service]
            
            month_name = calendar_spanish[month]
            service_name = services_actives[service]

            if month and service:
                return render_template(
                    "tickets/tickets_customers/index_table.html",
                    page={"title": f'Tickets del Servicio "{service_name}" del Cliente "{customer_name}" en el Mes de "{month_name}"'},
                    type_tickets=type_tickets,
                    current_type_ticket=def_name,
                    list_year=list_year,
                    current_year=year,
                    months_year=months_year,
                    customers=customers,
                    current_customer=customer,
                    current_month_customer=month,
                    current_service=service,
                    services_table=services_table,
                    ticket_service_table=ticket_service_table,
                    users=users_actives
                )

        return render_template(
            "tickets/tickets_customers/index.html",
            page={"title": "Data Adaptive Security"},
            type_tickets=type_tickets,
            current_type_ticket=def_name,
            list_year=list_year,
            current_year=year,
            months_year=months_year,
            total_tickets=total_tickets,
            customers=customers,
            data_grah_x=customers,
            data_grah_y=data_grah
        )


@tickets.get("/administrators")
def administrators():
    def_name = "administrators"
    type_tickets = {"customers": "Requeridos por los Clientes",
                    "administrators": "Resueltos por los administradores",
                    }
    list_year = get_data_tickets.get_list_year(path_temp, def_name)
    list_year = sorted([int(year_) for year_ in list_year])
    list_year.reverse()
    customers_actives = get_data_tickets.get_tools_json_temp(path_temp, "customers_actives")
    calendar_spanish = get_data_tickets.get_tools_json_temp(path_temp, "calendar_spanish")
    services_actives = get_data_tickets.get_tools_json_temp(path_temp, "services_actives")
    users_actives = get_data_tickets.get_tools_json_temp(path_temp, "users_actives")

    if request.method == "GET":
        year = request.args.get("year", type=str)
        month_year = request.args.get("month_year", type=str)
        administrator = request.args.get("administrator", type=str)
        month = request.args.get("month", type=str)
        service = request.args.get("service", type=str)
        customer = request.args.get("customer", type=str)
    
        if not year:
            year = str(list_year[0])

        data = get_data_tickets.get_tickets_json_temp(path_temp, def_name, year)
        
        total_tickets_administrator = {}
        total_tickets = 0
        months_year = []
        months_year_total = {}
        for month_ in data:
            months_year.append(month_)
            total_month = 0
            for administrator_ in data[month_]:
                total_month += len(data[month_][administrator_].keys())
                total_month_administrator = len(data[month_][administrator_].keys())
                if administrator_ not in total_tickets_administrator:
                    total_tickets_administrator[administrator_] = total_month_administrator
                    total_tickets += total_month_administrator
                else:
                    total_tickets_administrator[administrator_] += total_month_administrator
                    total_tickets += total_month_administrator
            
            months_year_total[month_] = total_month
        
        months_year.reverse()
        months_year = {int(num): (calendar_spanish[num], months_year_total[num])  for num in months_year}
        total_tickets_administrator = sorted(total_tickets_administrator.items(), key=lambda x:x[1], reverse=True)
        administrators_name = []
        administrators_id_name = {}
        data_grah_temp = []
        for administrator_sum in total_tickets_administrator:
            administrators_name.append(users_actives[str(administrator_sum[0])])
            administrators_id_name[int(administrator_sum[0])] = users_actives[str(administrator_sum[0])]
            data_grah_temp.append(administrator_sum[1])
        data_grah = [{"name": "Tickets", "data": data_grah_temp}]

        if month_year and not administrator:
            month_year_name = calendar_spanish[month_year]
            total_tickets_administrator_month = {}
            total_tickets = 0
            for administrator_month in data[month_year]:
                total_administrator_month = len(data[month_year][administrator_month].keys())
                if administrator_ not in total_tickets_administrator:
                    total_tickets_administrator_month[administrator_month] = total_administrator_month
                    total_tickets += total_administrator_month
            
            total_tickets_administrator_month = sorted(total_tickets_administrator_month.items(), key=lambda x:x[1], reverse=True)
            administrators_name = []
            administrators_id_name = {}
            data_grah_temp = []
            for administrator_sum in total_tickets_administrator_month:
                administrators_name.append(users_actives[str(administrator_sum[0])])
                administrators_id_name[int(administrator_sum[0])] = users_actives[str(administrator_sum[0])]
                data_grah_temp.append(administrator_sum[1])
            data_grah = [{"name": f"Tickets de {calendar_spanish[month_year]}", "data": data_grah_temp}]

            return render_template(
                "tickets/tickets_administrators/index.html",
                page={"title": "Data Adaptive Security"},
                type_tickets=type_tickets,
                current_type_ticket=def_name,
                list_year=list_year,
                current_year=year,
                months_year=months_year,
                current_months_year=month_year,
                current_months_year_name=month_year_name,
                total_tickets=total_tickets,
                administrators=administrators_id_name,
                data_grah_x=administrators_name,
                data_grah_y=data_grah       
            )


        if administrator:
            months_administrator_year_total = {}
            months_administrator = []
            data_grah_temp = []
            total_tickets = 0
            for month_ in data:
                if administrator in data[month_]:
                    total_month = len(data[month_][administrator].keys())
                    months_administrator.append(month_)
                    months_administrator_year_total[month_] = total_month
                    data_grah_temp.append(total_month)
                    total_tickets += total_month
            
            administrator_name = users_actives[administrator]
            data_grah = [{"name": f"Tickets de {administrator_name}", "data": data_grah_temp}]
            months = [calendar_spanish[num] for num in months_administrator]
            months_administrator.reverse()
            months_administrator = {int(num): (calendar_spanish[num], months_administrator_year_total[num]) for num in months_administrator}

            if not month and not service and not customer:
                return render_template(
                    "tickets/tickets_administrators/index.html",
                    page={"title": "Data Adaptive Security"},
                    type_tickets=type_tickets,
                    current_type_ticket=def_name,
                    list_year=list_year,
                    current_year=year,
                    months_year=months_year,
                    administrators=administrators_id_name,
                    current_administrator=administrator,
                    administrator_name=administrator_name,
                    months_administrator=months_administrator,
                    total_tickets=total_tickets,
                    data_grah_x=months,
                    data_grah_y=data_grah   
                )
        
            services_administrator = {}
            customers_administrator = {}
            total_tickets = len(data[month][administrator].keys())
            for ticket_ in data[month][administrator]:
                service_id = data[month][administrator][ticket_]["service_id"]
                customer_id = data[month][administrator][ticket_]["customer_id"]
                if service_id not in services_administrator:
                    services_administrator[service_id] = 1
                else:
                    services_administrator[service_id] += 1
                if customer_id not in customers_administrator:
                    customers_administrator[customer_id] = 1
                else:
                    customers_administrator[customer_id] += 1
            
            customers_administrator = sorted(customers_administrator.items(), key=lambda x:x[1], reverse=True)
            data_grah_temp = []
            customers_administrator_active_name = []
            customers_administrator_administrator_active = []
            customers_administrator_table = {}
            for customer_sum in customers_administrator:
                customers_administrator_active_name.append(customers_actives[customer_sum[0]])
                customers_administrator_administrator_active.append(str(customer_sum[0]))
                data_grah_temp.append(customer_sum[1])
                customers_administrator_table[str(customer_sum[0])] = (customers_actives[str(customer_sum[0])], customer_sum[1])

            data_grah_customer = [{"name": f"Tickets de {administrator_name}", "data": data_grah_temp}]

            services_administrator = sorted(services_administrator.items(), key=lambda x:x[1], reverse=True)
            data_grah_temp = []
            services_administrator_active = []
            services_administrator_active_name = []
            services_table = {}
            for service_sum in services_administrator:
                services_administrator_active_name.append(services_actives[str(service_sum[0])])
                services_administrator_active.append(str(service_sum[0]))
                data_grah_temp.append(service_sum[1])
                services_table[str(service_sum[0])] = (services_actives[str(service_sum[0])], service_sum[1])
            
            data_grah = [{"name": f"Tickets de {administrator_name}", "data": data_grah_temp}]
            
            if month and not service and not customer:
                return render_template(
                    "tickets/tickets_administrators/index.html",
                    page={"title": "Data Adaptive Security"},
                    type_tickets=type_tickets,
                    current_type_ticket=def_name,
                    list_year=list_year,
                    current_year=year,
                    months_year=months_year,
                    administrators=administrators_id_name,
                    current_administrator=administrator,
                    administrator_name=administrator_name,
                    months_administrator=months_administrator,
                    current_month_administrator=month,
                    total_tickets=total_tickets,
                    data_grah_x=services_administrator_active_name,
                    data_grah_y=data_grah,
                    services_table=services_table,
                    customers_administrator=customers_administrator,
                    customers_administrator_active_name=customers_administrator_active_name,
                    customers_administrator_table=customers_administrator_table,
                    data_grah_customer=data_grah_customer
                )
            
            if month and service and not customer:
                ticket_service_table = {}
                for ticket_service in data[month][administrator]:
                    service_id = data[month][administrator][ticket_service]["service_id"]
                    if str(service_id) == service:
                        ticket_service_table[ticket_service] = data[month][administrator][ticket_service]
                
                month_name = calendar_spanish[month]
                service_name = services_actives[service]
          
                return render_template(
                    "tickets/tickets_administrators/index_table.html",
                    page={"title": f'Tickets del Servicio "{service_name}" del Administrador "{administrator_name}" en el Mes de "{month_name}"'},
                    type_tickets=type_tickets,
                    current_type_ticket=def_name,
                    list_year=list_year,
                    current_year=year,
                    months_year=months_year,
                    administrators=administrators_id_name,
                    current_administrator=administrator,
                    current_month_administrator=month,
                    current_service=service,
                    services_table=services_table,
                    ticket_service_table=ticket_service_table
                )
            
            if month and not service and customer:
                customer_name = customers_actives[customer]
                ticket_customer_table = {}
                for ticket_customer in data[month][administrator]:
                    customer_id = data[month][administrator][ticket_customer]["customer_id"]
                    if customer_id == customer:
                        ticket_customer_table[ticket_customer] = data[month][administrator][ticket_customer]

                month_name = calendar_spanish[month]

                return render_template(
                    "tickets/tickets_administrators/index_table.html",
                    page={"title": f'Tickets del Cliente "{customer_name}" en el Mes de "{month_name}"'},
                    type_tickets=type_tickets,
                    current_type_ticket=def_name,
                    list_year=list_year,
                    current_year=year,
                    months_year=months_year,
                    administrators=administrators_id_name,
                    current_administrator=administrator,
                    current_month_administrator=month,
                    current_customer=customer,
                    customers_administrator=customers_administrator,
                    customers_administrator_active_name=customers_administrator_active_name,
                    customers_administrator_table=customers_administrator_table,
                    ticket_customer_table=ticket_customer_table,
                    services_actives=services_actives,
                )

        return render_template(
            "tickets/tickets_administrators/index.html",
            page={"title": "Data Adaptive Security"},
            type_tickets=type_tickets,
            current_type_ticket=def_name,
            list_year=list_year,
            current_year=year,
            months_year=months_year,
            total_tickets=total_tickets,
            administrators=administrators_id_name,
            data_grah_x=administrators_name,
            data_grah_y=data_grah      
        )


@tickets.get("/offenses")
def offenses():
    offenses_active = {
        "automatic": "Auto Ofensa",
        "automatic_intervention_manual_customer": "Auto Ofensa con Intervención Manual por Cliente",
        "automatic_intervention_manual_user": "Auto Ofensa con Intervención Manual por Análista",  
        "handwork_customers": 'Ofensas "Manuales" por Cliente',
        "handwork_user": 'Ofensas "Manuales" por Análista'
    }
    customers_actives = get_data_tickets.get_tools_json_temp(path_temp, "customers_actives")
    calendar_spanish = get_data_tickets.get_tools_json_temp(path_temp, "calendar_spanish")
    services_actives = get_data_tickets.get_tools_json_temp(path_temp, "services_actives")
    users_actives = get_data_tickets.get_tools_json_temp(path_temp, "users_actives")
    
    if request.method == "GET":
        type_ = request.args.get("type", type=str)
        year = request.args.get("year", type=str)
        month_year = request.args.get("month_year", type=str)
        customer = request.args.get("customer", type=str)
        month = request.args.get("month", type=str)
        service = request.args.get("service", type=str)
    
        if not type_:
            type_ = list(offenses_active.keys())[0]
        
        list_year_offense = get_data_tickets.get_list_offenses_year(path_temp, type_)
        list_year_offense = sorted([int(year_) for year_ in list_year_offense])
        list_year_offense.reverse()

        # if not year:
        #     if len(list_year_offense)>0:
        #         year = list_year_offense[0]

        if type_ == "handwork_user" or type_ == "automatic_intervention_manual_user":
            return redirect(url_for("tickets.offenses_user", type_=type_))
        
        if not year:
            return render_template(
                "tickets/tickets_offenses/index.html",
                page={"title": "Data Adaptive Security"},
                offenses_active=offenses_active,
                current_offense=type_,
                list_year_offense=list_year_offense
            )

        data = get_data_tickets.get_offenses_json_temp(path_temp, type_, year)

        total_tickets_customer = {}
        total_tickets = 0
        months_year = []
        months_year_total = {}
        for month_ in data:
            months_year.append(month_)
            total_month = 0
            for customer_ in data[month_]:
                total_month += len(data[month_][customer_].keys())
                total_month_customer = len(data[month_][customer_].keys())
                if customer_ not in total_tickets_customer:
                    total_tickets_customer[customer_] = total_month_customer
                    total_tickets += total_month_customer
                else:
                    total_tickets_customer[customer_] += total_month_customer
                    total_tickets += total_month_customer
            
            months_year_total[month_] = total_month
        
        months_year.reverse()
        months_year = {int(num): (calendar_spanish[num], months_year_total[num])  for num in months_year}
        total_tickets_customer = sorted(total_tickets_customer.items(), key=lambda x:x[1], reverse=True)
        customers = []
        data_grah_temp = []
        for customer_sum in total_tickets_customer:
            customers.append(customer_sum[0])
            data_grah_temp.append(customer_sum[1])
        data_grah = [{"name": "Tickets", "data": data_grah_temp}]

        if month_year:
            month_year_name = calendar_spanish[month_year]
            total_tickets_customer_month = {}
            total_tickets = 0
            for customer_month in data[month_year]:
                total_customer_month = len(data[month_year][customer_month].keys())
                if customer_ not in total_tickets_customer:
                    total_tickets_customer_month[customer_month] = total_customer_month
                    total_tickets += total_customer_month
            
            total_tickets_customer_month = sorted(total_tickets_customer_month.items(), key=lambda x:x[1], reverse=True)
            customers = []
            data_grah_temp = []
            for customer_sum in total_tickets_customer_month:
                customers.append(customer_sum[0])
                data_grah_temp.append(customer_sum[1])
            data_grah = [{"name": f"Tickets de {calendar_spanish[month_year]}", "data": data_grah_temp}]

            if not customer:
                return render_template(
                    "tickets/tickets_offenses/index.html",
                    page={"title": "Data Adaptive Security"},
                    offenses_active=offenses_active,
                    current_offense=type_,
                    list_year_offense=list_year_offense,
                    current_year=year,
                    months_year=months_year,
                    current_month_year=month_year,
                    current_month_year_name=month_year_name,
                    total_tickets=total_tickets,
                    customers=customers,
                    data_grah_x=customers,
                    data_grah_y=data_grah      
                )

        if customer:
            months_customer_year_total = {}
            months_customer = []
            data_grah_temp = []
            total_tickets = 0
            for month_ in data:
                if customer in data[month_]:
                    total_month = len(data[month_][customer].keys())
                    months_customer.append(month_)
                    months_customer_year_total[month_] = total_month
                    data_grah_temp.append(total_month)
                    total_tickets += total_month
            
            customer_name = customers_actives[customer]
            data_grah = [{"name": f"Tickets de {customer_name}", "data": data_grah_temp}]
            months = [calendar_spanish[num] for num in months_customer]
            months_customer.reverse()
            months_customer = {int(num): (calendar_spanish[num], months_customer_year_total[num]) for num in months_customer}

            if not month and not service:
                return render_template(
                    "tickets/tickets_offenses/index.html",
                    page={"title": "Data Adaptive Security"},
                    offenses_active=offenses_active,
                    current_offense=type_,
                    list_year_offense=list_year_offense,
                    current_year=year,
                    months_year=months_year,
                    customers=customers,
                    current_customer=customer,
                    customer_name=customer_name,
                    months_customer=months_customer,
                    total_tickets=total_tickets,
                    data_grah_x=months,
                    data_grah_y=data_grah      
                )

            month_name = calendar_spanish[month]
            services_customer = {}
            total_tickets = len(data[month][customer].keys())
            for ticket_ in data[month][customer]:
                service_id = data[month][customer][ticket_]["service_id"]
                if service_id not in services_customer:
                    services_customer[service_id] = 1
                else:
                    services_customer[service_id] += 1
            
            services_customer = sorted(services_customer.items(), key=lambda x:x[1], reverse=True)

            data_grah_temp = []
            services_customer_active = []
            services_customer_active_name = []
            services_table = {}
            for service_sum in services_customer:
                services_customer_active_name.append(services_actives[str(service_sum[0])])
                services_customer_active.append(str(service_sum[0]))
                data_grah_temp.append(service_sum[1])
                services_table[service_sum[0]] = (services_actives[str(service_sum[0])], service_sum[1])
               
            data_grah = [{"name": f"Tickets de {customer_name}", "data": data_grah_temp}]
            
            if month and not service:
                return render_template(
                    "tickets/tickets_offenses/index.html",
                    page={"title": "Data Adaptive Security"},
                    offenses_active=offenses_active,
                    current_offense=type_,
                    list_year_offense=list_year_offense,
                    current_year=year,
                    months_year=months_year,
                    customers=customers,
                    current_customer=customer,
                    customer_name=customer_name,
                    months_customer=months_customer,
                    current_month_customer=month,
                    current_month_customer_name=month_name,
                    total_tickets=total_tickets,
                    data_grah_x=services_customer_active_name,
                    data_grah_y=data_grah,
                    services_table=services_table
                )
            
            ticket_service_table = {}
            for ticket_service in data[month][customer]:
                service_id = data[month][customer][ticket_service]["service_id"]
                if str(service_id) == service:
                    ticket_service_table[ticket_service] = data[month][customer][ticket_service]
            
            month_name = calendar_spanish[month]
            service_name = services_actives[service]

            if month and service:
                return render_template(
                    "tickets/tickets_offenses/index_table.html",
                    page={"title": f'Tickets del Servicio "{service_name}" del Cliente "{customer_name}" en el Mes de "{month_name}"'},
                    offenses_active=offenses_active,
                    current_offense=type_,
                    list_year_offense=list_year_offense,
                    current_year=year,
                    months_year=months_year,
                    customers=customers,
                    current_customer=customer,
                    current_month_customer=month,
                    current_service=service,
                    services_table=services_table,
                    ticket_service_table=ticket_service_table,
                    users=users_actives
                )
        return render_template(
            "tickets/tickets_offenses/index.html",
            page={"title": "Data Adaptive Security"},
            offenses_active=offenses_active,
            current_offense=type_,
            list_year_offense=list_year_offense,
            current_year=year,
            months_year=months_year,
            total_tickets=total_tickets,
            customers=customers,
            data_grah_x=customers,
            data_grah_y=data_grah
        )
    

@tickets.get("/offenses/user")
def offenses_user():
    def_name = "offenses_user"
    offenses_active = {
        "automatic": "Auto Ofensa",
        "automatic_intervention_manual_customer": "Auto Ofensa con Intervención Manual por Cliente",
        "automatic_intervention_manual_user": "Auto Ofensa con Intervención Manual por Análista",  
        "handwork_customers": 'Ofensas "Manuales" por Cliente',
        "handwork_user": 'Ofensas "Manuales" por Análista'
    }
    customers_actives = get_data_tickets.get_tools_json_temp(path_temp, "customers_actives")
    calendar_spanish = get_data_tickets.get_tools_json_temp(path_temp, "calendar_spanish")
    services_actives = get_data_tickets.get_tools_json_temp(path_temp, "services_actives")
    users_actives = get_data_tickets.get_tools_json_temp(path_temp, "users_actives")
    
    if request.method == "GET":
        year = request.args.get("year", type=str)
        month_year = request.args.get("month_year", type=str)
        administrator = request.args.get("administrator", type=str)
        month = request.args.get("month", type=str)
        service = request.args.get("service", type=str)
        customer = request.args.get("customer", type=str)
        type_ = request.args.get("type_", type=str)

        list_year_offense = get_data_tickets.get_list_offenses_year(path_temp, type_)
        list_year_offense = sorted([int(year_) for year_ in list_year_offense])
        list_year_offense.reverse()
 

        # if not year:
        #     year = list_year_offense[0]
        
        if not year:
            return render_template(
                "tickets/tickets_offenses_user/index.html",
                page={"title": "Data Adaptive Security"},
                offenses_active=offenses_active,
                current_offense=type_,
                list_year_offense=list_year_offense,
                current_type=type_
            )
        
        data = get_data_tickets.get_offenses_json_temp(path_temp, type_, year)
        total_tickets_administrator = {}
        total_tickets = 0
        months_year = []
        months_year_total = {}
        for month_ in data:
            months_year.append(month_)
            total_month = 0
            for administrator_ in data[month_]:
                total_month += len(data[month_][administrator_].keys())
                total_month_administrator = len(data[month_][administrator_].keys())
                if administrator_ not in total_tickets_administrator:
                    total_tickets_administrator[administrator_] = total_month_administrator
                    total_tickets += total_month_administrator
                else:
                    total_tickets_administrator[administrator_] += total_month_administrator
                    total_tickets += total_month_administrator
            
            months_year_total[month_] = total_month
        
        months_year.reverse()
        months_year = {int(num): (calendar_spanish[num], months_year_total[num])  for num in months_year}
        total_tickets_administrator = sorted(total_tickets_administrator.items(), key=lambda x:x[1], reverse=True)
        administrators_name = []
        administrators_id_name = {}
        data_grah_temp = []
        for administrator_sum in total_tickets_administrator:
            administrators_name.append(users_actives[str(administrator_sum[0])])
            administrators_id_name[int(administrator_sum[0])] = users_actives[str(administrator_sum[0])]
            data_grah_temp.append(administrator_sum[1])
        data_grah = [{"name": "Tickets", "data": data_grah_temp}]

        if month_year and not administrator:
            month_year_name = calendar_spanish[month_year]
            total_tickets_administrator_month = {}
            total_tickets = 0
            for administrator_month in data[month_year]:
                total_administrator_month = len(data[month_year][administrator_month].keys())
                if administrator_ not in total_tickets_administrator:
                    total_tickets_administrator_month[administrator_month] = total_administrator_month
                    total_tickets += total_administrator_month
            
            total_tickets_administrator_month = sorted(total_tickets_administrator_month.items(), key=lambda x:x[1], reverse=True)
            administrators_name = []
            administrators_id_name = {}
            data_grah_temp = []
            for administrator_sum in total_tickets_administrator_month:
                administrators_name.append(users_actives[str(administrator_sum[0])])
                administrators_id_name[int(administrator_sum[0])] = users_actives[str(administrator_sum[0])]
                data_grah_temp.append(administrator_sum[1])
            data_grah = [{"name": f"Tickets de {calendar_spanish[month_year]}", "data": data_grah_temp}]

            return render_template(
                "tickets/tickets_offenses_user/index.html",
                page={"title": "Data Adaptive Security"},
                offenses_active=offenses_active,
                current_offense=type_,
                list_year_offense=list_year_offense,
                current_year=year,
                months_year=months_year,
                current_months_year=month_year,
                current_months_year_name=month_year_name,
                total_tickets=total_tickets,
                administrators=administrators_id_name,
                data_grah_x=administrators_name,
                data_grah_y=data_grah       
            )

        if administrator:
            months_administrator_year_total = {}
            months_administrator = []
            data_grah_temp = []
            total_tickets = 0
            for month_ in data:
                if administrator in data[month_]:
                    total_month = len(data[month_][administrator].keys())
                    months_administrator.append(month_)
                    months_administrator_year_total[month_] = total_month
                    data_grah_temp.append(total_month)
                    total_tickets += total_month
            
            administrator_name = users_actives[administrator]
            data_grah = [{"name": f"Tickets de {administrator_name}", "data": data_grah_temp}]
            months = [calendar_spanish[num] for num in months_administrator]
            months_administrator.reverse()
            months_administrator = {int(num): (calendar_spanish[num], months_administrator_year_total[num]) for num in months_administrator}

            if not month and not service and not customer:
                return render_template(
                    "tickets/tickets_offenses_user/index.html",
                    page={"title": "Data Adaptive Security"},
                    offenses_active=offenses_active,
                    current_offense=type_,
                    list_year_offense=list_year_offense,
                    current_year=year,
                    months_year=months_year,
                    administrators=administrators_id_name,
                    current_administrator=administrator,
                    administrator_name=administrator_name,
                    months_administrator=months_administrator,
                    total_tickets=total_tickets,
                    data_grah_x=months,
                    data_grah_y=data_grah   
                )
        
            services_administrator = {}
            customers_administrator = {}
            total_tickets = len(data[month][administrator].keys())
            for ticket_ in data[month][administrator]:
                service_id = data[month][administrator][ticket_]["service_id"]
                customer_id = data[month][administrator][ticket_]["customer_id"]
                if service_id not in services_administrator:
                    services_administrator[service_id] = 1
                else:
                    services_administrator[service_id] += 1
                if customer_id not in customers_administrator:
                    customers_administrator[customer_id] = 1
                else:
                    customers_administrator[customer_id] += 1

            customers_administrator = sorted(customers_administrator.items(), key=lambda x:x[1], reverse=True)
            data_grah_temp = []
            customers_administrator_active_name = []
            customers_administrator_administrator_active = []
            customers_administrator_table = {}
            for customer_sum in customers_administrator:
                customers_administrator_active_name.append(customers_actives[customer_sum[0]])
                customers_administrator_administrator_active.append(str(customer_sum[0]))
                data_grah_temp.append(customer_sum[1])
                customers_administrator_table[str(customer_sum[0])] = (customers_actives[str(customer_sum[0])], customer_sum[1])

            data_grah_customer = [{"name": f"Tickets de {administrator_name}", "data": data_grah_temp}]

            services_administrator = sorted(services_administrator.items(), key=lambda x:x[1], reverse=True)
            data_grah_temp = []
            services_administrator_active = []
            services_administrator_active_name = []
            services_table = {}
            for service_sum in services_administrator:
                if service_sum[0] != "Undefined":
                    services_administrator_active_name.append(services_actives[str(service_sum[0])])
                    services_administrator_active.append(str(service_sum[0]))
                    data_grah_temp.append(service_sum[1])
                    services_table[str(service_sum[0])] = (services_actives[str(service_sum[0])], service_sum[1])
                else:
                    services_administrator_active_name.append("Undefined")
                    services_administrator_active.append("Undefined")
                    data_grah_temp.append(service_sum[1])
                    services_table["Undefined"] = ("Undefined",service_sum[1])
            
            data_grah = [{"name": f"Tickets de {administrator_name}", "data": data_grah_temp}]
            
            if month and not service and not customer:
                return render_template(
                    "tickets/tickets_offenses_user/index.html",
                    page={"title": "Data Adaptive Security"},
                    offenses_active=offenses_active,
                    current_offense=type_,
                    list_year_offense=list_year_offense,
                    current_year=year,
                    months_year=months_year,
                    administrators=administrators_id_name,
                    current_administrator=administrator,
                    administrator_name=administrator_name,
                    months_administrator=months_administrator,
                    current_month_administrator=month,
                    total_tickets=total_tickets,
                    data_grah_x=services_administrator_active_name,
                    data_grah_y=data_grah,
                    services_table=services_table,
                    customers_administrator=customers_administrator,
                    customers_administrator_active_name=customers_administrator_active_name,
                    customers_administrator_table=customers_administrator_table,
                    data_grah_customer=data_grah_customer

                )
            
            if month and service and not customer:
                ticket_service_table = {}
                for ticket_service in data[month][administrator]:
                    service_id = data[month][administrator][ticket_service]["service_id"]
                    if str(service_id) == service:
                        ticket_service_table[ticket_service] = data[month][administrator][ticket_service]
                
                month_name = calendar_spanish[month]
                service_name = services_actives[service]
          
                return render_template(
                    "tickets/tickets_offenses_user/index_table.html",
                    page={"title": f'Tickets del Servicio "{service_name}" del Administrador "{administrator_name}" en el Mes de "{month_name}"'},
                    offenses_active=offenses_active,
                    current_offense=type_,
                    list_year_offense=list_year_offense,
                    current_year=year,
                    months_year=months_year,
                    administrators=administrators_id_name,
                    current_administrator=administrator,
                    current_month_administrator=month,
                    current_service=service,
                    services_table=services_table,
                    ticket_service_table=ticket_service_table
                )
            
            if month and not service and customer:
                customer_name = customers_actives[customer]
                ticket_customer_table = {}
                for ticket_customer in data[month][administrator]:
                    customer_id = data[month][administrator][ticket_customer]["customer_id"]
                    if customer_id == customer:
                        ticket_customer_table[ticket_customer] = data[month][administrator][ticket_customer]
            
                month_name = calendar_spanish[month]

                return render_template(
                    "tickets/tickets_offenses_user/index_table.html",
                    page={"title": f'Tickets del Cliente "{customer_name}" en el Mes de "{month_name}"'},
                    offenses_active=offenses_active,
                    current_offense=type_,
                    list_year_offense=list_year_offense,
                    current_year=year,
                    months_year=months_year,
                    administrators=administrators_id_name,
                    current_administrator=administrator,
                    current_month_administrator=month,
                    current_customer=customer,
                    customers_administrator=customers_administrator,
                    customers_administrator_active_name=customers_administrator_active_name,
                    customers_administrator_table=customers_administrator_table,
                    ticket_customer_table=ticket_customer_table,
                    services_actives=services_actives
                )

        return render_template(
            "tickets/tickets_offenses_user/index.html",
            page={"title": "Data Adaptive Security"},
            offenses_active=offenses_active,
            current_offense=type_,
            list_year_offense=list_year_offense,
            current_year=year,
            months_year=months_year,
            total_tickets=total_tickets,
            administrators=administrators_id_name,
            data_grah_x=administrators_name,
            data_grah_y=data_grah      
        )
