try:
    from .otrs.models.ticket import Ticket
    from .otrs.models.customer_company import CustomerCompany
    from .otrs.models.user import User
except:
    from otrs.models.ticket import Ticket
    from otrs.models.customer_company import CustomerCompany
    from otrs.models.user import User

import os
import json
from datetime import datetime, timedelta
from pprint import pprint

path_analyzer = os.path.dirname(__file__)


##########################################
##########Funciones de apoyo#############
##########################################


def analysis_start_day(number_of_days=int):
    """Obtener el día a partir del cual se iniciará el analisis
    
    Return
    ------
    date
        Una data del tipo datetime
    """

    return datetime.today() - timedelta(days=number_of_days)

def list_date(start, end):
    """Obtener la lista de los días en los cuales se hará el analisis
    
    Return
    ------
    Lista[date]
        Una lista con los días
    """

    return [str(start + timedelta(days=d)).split(" ")[0] for d in range((end - start).days + 1)]


#####################################################################
###Reponde a la pregunta: 1. Cantidad de tickets generados por clientes
########################################################################

def tickests_for_clientes():
    """Obtener los tickets diarios requeridos por los clientes 
    
    Parameters
    ---------
    
    Return
    Dict[Customer][Day] = len(tickets)
        Diccionario con los clientes y sus tickets requeridos
    """
    path_temp = os.path.join(path_analyzer, "temp")
    path_customers_active = os.path.join(path_temp,"customers_active.json")

    if not os.path.exists(path_temp):
        os.mkdir(path_temp)

    if os.path.exists(path_customers_active):
        with open(path_customers_active, "r") as f:
            json_customers_active = json.load(f)
            start_date = json_customers_active["last_date"]
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            days_for_analyzed = list_date(start_date, datetime.today())
            customers_active_temp = json_customers_active["customers_active"]
    else:
        customers_active_temp = {}
        start_date = "2022-12-30"
        days_for_analyzed = list_date(datetime.strptime(start_date, "%Y-%m-%d"), datetime.today())

    customers = [customer.customer_id for customer in CustomerCompany.all()]

    for day_for_analyzed in days_for_analyzed:
        print(f"Recopilando datos del día {day_for_analyzed}")
        tickets_by_day = Ticket.tickets_by_date(day_for_analyzed)
        if tickets_by_day:
            for ticket_by_day in tickets_by_day:
                if ticket_by_day.customer_id in customers:
                    _day_for_analyzed = datetime.strptime(day_for_analyzed, "%Y-%m-%d")
                    year = _day_for_analyzed.year
                    month = _day_for_analyzed.month
                    day =  _day_for_analyzed.day
                    if ticket_by_day.customer_id in customers:
                        if year not in customers_active_temp:
                            customers_active_temp[year] = {}
                        if ticket_by_day.customer_id not in customers_active_temp[year]:
                            customers_active_temp[year][ticket_by_day.customer_id] = {}
                        if month not in customers_active_temp[year][ticket_by_day.customer_id] :
                            customers_active_temp[year][ticket_by_day.customer_id][month] = {}
                        
                        if day == start_date or day not in customers_active_temp[year][ticket_by_day.customer_id][month]:
                            customers_active_temp[year][ticket_by_day.customer_id][month][day] = len(Ticket.tickets_by_customer_date(ticket_by_day.customer_id, day_for_analyzed))

    _customers_active = {
        "customers_active": customers_active_temp,
        "last_date": days_for_analyzed[-1]
    }

    with open(path_customers_active, "w") as f:
        json_customers_active = json.dumps(_customers_active)
        f.write(json_customers_active)

    return customers_active_temp