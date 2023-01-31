from flask import Blueprint
from flask import render_template
from flask import request
from flask import current_app
from flask import redirect
from flask import url_for

from webapp.analyzer import data_tickets_customers

import os
import json
import statistics
import numpy  as np
import calendar
from datetime import datetime
from pprint import pprint


tickets_customers = Blueprint("tickets_customers", __name__, url_prefix="/tickets_customers")


@tickets_customers.get("/")
def index():
    list_year = list(range(2019, datetime.today().year+1))
    list_year.reverse()
    data = data_tickets_customers.tickets_customers_queue()
    
    if request.method == "GET":
        year = request.args.get("year", type=str)
        customer = request.args.get("customer", type=str)
        month =  request.args.get("month", type=str)
    
        if not year:
            year = "2023"
        
        customers = list(data[year].keys())
        if year == str(datetime.today().year):
            months_grah = [str(month_g) for month_g in range(1,datetime.today().month+1)]
        else:
            months_grah = [str(month_g) for month_g in range(1,13)]
        len_months_grah = len(months_grah)
        
        total_requeriments = 0
        data_grah = []
        for _customer in data[year]:
            data_grah_temp = []
            for _month in months_grah:
                if _month in data[year][_customer]:
                    y_temp = 0
                    for _day in data[year][_customer][_month]:
                        y_temp += int(data[year][_customer][_month][_day])
                    data_grah_temp.append(y_temp)
                else:
                    data_grah_temp.append(0)
            
            data_grah.append({"name": _customer, "data": data_grah_temp})
            total_requeriments += sum(data_grah_temp)
        
        if customer and not month:
            monts_customer = list(data[year][customer].keys())
            monts_customer.reverse()
            len_months_grah = len(monts_customer)
            calendar_spanish = data_tickets_customers.calendar_spanish()
            months = {int(num): calendar_spanish[int(num)] for num in monts_customer}
            
            total_requeriments = 0
            data_grah_temp = []
            for _month in months_grah:
                if _month in data[year][customer]:
                    y_temp = 0
                    for _day in data[year][customer][_month]:
                        y_temp += int(data[year][customer][_month][_day])
                    data_grah_temp.append(y_temp)
                else:
                    data_grah_temp.append(0)
            
            total_requeriments += sum(data_grah_temp)
            data_grah = [{"name": customer, "data": data_grah_temp}]
        
            return render_template(
                "tickets_customers/index.html",
                page={"title": "Data Adaptive Security"},
                list_year=list_year,
                current_year=year,
                customers=customers,
                current_customer=customer,
                months=months,
                data_grah=data_grah,
                len_months_grah=len_months_grah, 
                total_requeriments=total_requeriments

            )
        
        if customer and month:
            monts_customer = list(data[year][customer].keys())
            monts_customer.reverse()
            calendar_spanish = data_tickets_customers.calendar_spanish()
            months = {int(num): calendar_spanish[int(num)] for num in monts_customer}

            data_grah_temp = []
            if month in data[year][customer]:
                for day in data[year][customer][month]:
                    data_grah_temp.append(int(data[year][customer][month][day]))
            
            data_grah = [{"name": customer, "data": data_grah_temp}]
            len_months_grah = len(data_grah_temp)
            total_requeriments=sum(data_grah_temp)
            month_grah=months[int(month)]

            return render_template(
                "tickets_customers/index.html",
                page={"title": "Data Adaptive Security"},
                list_year=list_year,
                current_year=year,
                customers=customers,
                current_customer=customer,
                months=months,
                current_month=month,
                data_grah=data_grah,
                len_months_grah=len_months_grah,
                total_requeriments=total_requeriments,
                month_grah=month_grah
            )


    return render_template(
        "tickets_customers/index.html",
        page={"title": "Data Adaptive Security"},
        list_year=list_year,
        current_year=year,
        customers=customers,
        data_grah=data_grah,
        len_months_grah=len_months_grah,
        total_requeriments=total_requeriments
    )


@tickets_customers.get("/service")
def service():
    list_year = list(range(2019, datetime.today().year+1))
    list_year.reverse()
    data = data_tickets_customers.tickets_customers_queue_service()
    services = data_tickets_customers.services_actives()
    
    if request.method == "GET":
        year = request.args.get("year", type=str)
        customer = request.args.get("customer", type=str)
        month =  request.args.get("month", type=str)
    
        if not year:
            year = "2023"
        
        customers = list(data[year].keys())
        if year == str(datetime.today().year):
            months_grah = [str(month_g) for month_g in range(1,datetime.today().month+1)]
        else:
            months_grah = [str(month_g) for month_g in range(1,13)]
        len_months_grah = len(months_grah)

        if customer and not month:
            monts_customer = list(data[year][customer].keys())
            monts_customer.reverse()
            len_months_grah = len(monts_customer)
            calendar_spanish = data_tickets_customers.calendar_spanish()
            months = {int(num): calendar_spanish[int(num)] for num in monts_customer}
            
            total_requeriments = 0
            data_grah_temp = []
            for _month in months_grah:
                if _month in data[year][customer]:
                    print(f"_month {_month}")
                    y_temp = 0
                    for service_id in data[year][customer][_month]:
                        y_temp += int(data[year][customer][_month][service_id])
                    data_grah_temp.append(y_temp)
                else:
                    data_grah_temp.append(0)
            
            total_requeriments += sum(data_grah_temp)
            data_grah = [{"name": customer, "data": data_grah_temp}]

            return render_template(
                "tickets_customers_services/index.html",
                page={"title": "Data Adaptive Security"},
                list_year=list_year,
                current_year=year,
                customers=customers,
                current_customer=customer,
                months=months,
                data_grah=data_grah,
                len_months_grah=len_months_grah, 
                total_requeriments=total_requeriments
            )
        
        if customer and month:
            monts_customer = list(data[year][customer].keys())
            monts_customer.reverse()
            calendar_spanish = data_tickets_customers.calendar_spanish()
            months = {int(num): calendar_spanish[int(num)] for num in monts_customer}


            data_grah = []
            total_requeriments = 0
            services_active = {}
            if month in data[year][customer]:
                for service_id in data[year][customer][month]:
                    data_grah.append({"name": services[int(service_id)],
                        "data": [int(data[year][customer][month][service_id])]
                    })
                    services_active[int(service_id)] = services[int(service_id)]
                    total_requeriments += int(data[year][customer][month][service_id])
            
            month_grah=int(month)

            return render_template(
                "tickets_customers_services/index.html",
                page={"title": "Data Adaptive Security"},
                list_year=list_year,
                current_year=year,
                customers=customers,
                current_customer=customer,
                months=months,
                current_month=month,
                data_grah=data_grah,
                total_requeriments=total_requeriments,
                month_grah=month_grah,
                services_active=services_active
            )
    
    return render_template(
        "tickets_customers_services/index.html",
        page={"title": "Data Adaptive Security"},
        list_year=list_year,
        current_year=year,
        customers=customers
    )