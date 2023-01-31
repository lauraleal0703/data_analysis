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


tickets_admin = Blueprint("tickets_admin", __name__, url_prefix="/tickets_admin")


@tickets_admin.get("/")
def index():
    list_year = list(range(2019, datetime.today().year+1))
    list_year.reverse()
    data = data_tickets_customers.tickets_admin()
    users = data_tickets_customers.users_actives()
    
    if request.method == "GET":
        year = request.args.get("year", type=str)
        user = request.args.get("user", type=str)
        month =  request.args.get("month", type=str)
    
        if not year:
            year = "2023"
        
        users_active = {int(user): users[int(user)] for user in list(data[year].keys())}
        if year == str(datetime.today().year):
            months_grah = [str(month_g) for month_g in range(1,datetime.today().month+1)]
        else:
            months_grah = [str(month_g) for month_g in range(1,13)]
        len_months_grah = len(months_grah)

        if user and not month:
            current_user_name = users[int(user)]
            monts_user = list(data[year][user].keys())
            monts_user.reverse()
            len_months_grah = len(monts_user)
            calendar_spanish = data_tickets_customers.calendar_spanish()
            months = {int(num): calendar_spanish[int(num)] for num in monts_user}
            
            total_requeriments = 0
            data_grah_temp = []
            for _month in months_grah:
                if _month in data[year][user]:
                    y_temp = 0
                    for day in data[year][user][_month]:
                        y_temp += int(data[year][user][_month][day])
                    data_grah_temp.append(y_temp)
                else:
                    data_grah_temp.append(0)
            
            total_requeriments += sum(data_grah_temp)
            data_grah = [{"name": users[int(user)], "data": data_grah_temp}]

            return render_template(
                "tickets_admin/index.html",
                page={"title": "Data Adaptive Security"},
                list_year=list_year,
                current_year=year,
                users_active=users_active,
                current_user=user,
                current_user_name=current_user_name,
                months=months,
                data_grah=data_grah,
                len_months_grah=len_months_grah, 
                total_requeriments=total_requeriments
            )
        
        if user and month:
            current_user_name = users[int(user)]
            monts_user = list(data[year][user].keys())
            monts_user.reverse()
            calendar_spanish = data_tickets_customers.calendar_spanish()
            months = {int(num): calendar_spanish[int(num)] for num in monts_user}

            data_grah_temp = []
            total_requeriments = 0
            len_months_grah = []
            days = []
            if month in data[year][user]:
                for day in data[year][user][month]:
                    days.append(str(day))
                    data_grah_temp.append(int(data[year][user][month][day]))
                    total_requeriments += int(data[year][user][month][day])
            
            data_grah = [{"name": users[int(user)], "data": data_grah_temp}]
            month_grah=int(month)
            len_months_grah=len(len_months_grah)

            return render_template(
                "tickets_admin/index.html",
                page={"title": "Data Adaptive Security"},
                list_year=list_year,
                current_year=year,
                users_active=users_active,
                current_user_name=current_user_name,
                current_user=user,
                months=months,
                current_month=month,
                data_grah=data_grah,
                len_months_grah=len_months_grah, 
                total_requeriments=total_requeriments,
                month_grah=month_grah,
                days=days
            )

    return render_template(
        "tickets_admin/index.html",
        page={"title": "Data Adaptive Security"},
        list_year=list_year,
        current_year=year,
        users_active=users_active,
        current_user=user
    )


@tickets_admin.get("/service")
def service():
    list_year = list(range(2019, datetime.today().year+1))
    list_year.reverse()
    data = data_tickets_customers.tickets_admin_service_customer()
    users = data_tickets_customers.users_actives()
    services = data_tickets_customers.services_actives()

    if request.method == "GET":
        year = request.args.get("year", type=str)
        user = request.args.get("user", type=str)
        month =  request.args.get("month", type=str)
        customer =  request.args.get("customer", type=str)
        
        if not year:
            year = "2023"

        users_active = {int(user): users[int(user)] for user in list(data[year].keys())}
        if user and not month:
            month_temp = []
            for _month in data[year][user]:
                month_temp.append(_month)
            
            calendar_spanish = data_tickets_customers.calendar_spanish()
            months = {int(num): calendar_spanish[int(num)] for num in month_temp}
        
            return render_template(
                "tickets/tickets_admin_customer_service/index.html",
                page={"title": "Data Adaptive Security"},
                list_year=list_year,
                current_year=year,
                users_active=users_active,
                current_user=user,
                months=months
            )
        
        if user and month and not customer:
            month_temp = []
            for _month in data[year][user]:
                month_temp.append(_month)
            
            calendar_spanish = data_tickets_customers.calendar_spanish()
            months = {int(num): calendar_spanish[int(num)] for num in month_temp}

            customers_temp = []
            for customer in data[year][user][month]:
                customers_temp.append(customer)
        
            return render_template(
                "tickets/tickets_admin_customer_service/index.html",
                page={"title": "Data Adaptive Security"},
                list_year=list_year,
                current_year=year,
                users_active=users_active,
                current_user=user,
                months=months,
                current_month=month,
                current_customers=customers_temp
            )
        
        if user and month and customer:
            month_temp = []
            for _month in data[year][user]:
                month_temp.append(_month)
            
            calendar_spanish = data_tickets_customers.calendar_spanish()
            months = {int(num): calendar_spanish[int(num)] for num in month_temp}

            customers_temp = []
            for _customer in data[year][user][month]:
                customers_temp.append(_customer)
            
            services_temp=[]
            for service in data[year][user][month][customer]:
                services_temp.append([services[int(service)], data[year][user][month][customer][service]])
        
            return render_template(
                "tickets/tickets_admin_customer_service/index.html",
                page={"title": "Data Adaptive Security"},
                list_year=list_year,
                current_year=year,
                users_active=users_active,
                current_user=user,
                months=months,
                current_month=month,
                current_customers=customers_temp,
                current_customer=customer,
                services_temp=services_temp
            )


    return render_template(
        "tickets/tickets_admin_customer_service/index.html",
        page={"title": "Data Adaptive Security"},
        list_year=list_year,
        current_year=year,
        users_active=users_active
    )