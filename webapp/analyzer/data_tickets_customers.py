try:
    from .otrs.models.ticket import Ticket
    from .otrs.models.customer_company import CustomerCompany
    from .otrs.models.service import Service
    from .otrs.models.user import User
except:
    from otrs.models.ticket import Ticket
    from otrs.models.customer_company import CustomerCompany
    from otrs.models.service import Service
    from otrs.models.user import User

import os
import json
from datetime import datetime, timedelta
from pprint import pprint
from dateutil.relativedelta import relativedelta


path_analyzer = os.path.dirname(__file__)


##########################################
##########Funciones de apoyo#############
##########################################


def list_months(date: str):
    """Obtener una lista con los meses a analizar

    Parameters
    ---------
    date:str
        El día desde el que se quiere iniciar el analisis
        en formato formato Y-M-D
    
    Return
    ------
    List(months)
        Una lista de meses
    """

    end_date=datetime.today()+relativedelta(months=1)
    month_temp=datetime.strptime(date, "%Y-%m-%d")
    list_months_active=[month_temp.strftime("%Y-%m-%d")]
    while True:
        month_temp=month_temp+relativedelta(months=1)
        list_months_active.append(month_temp.strftime("%Y-%m-%d"))
        if month_temp.year == end_date.year:
            if month_temp.month == end_date.month:
                break
        month_temp=month_temp
    
    return list_months_active


def calendar_spanish():
    """Obtener un diciconario con los meses del año en español
    
    Return
    ------
    calendar_spanish
        Una diccionario de calendar_spanish
    """

    months = ["Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre"
    ]

    return {pos+1: month for pos, month in enumerate(months)}

def services_actives():
    """Obtener un diciconario con los servicios
    
    Return
    ------
    {id: services_active.name}
        Una diccionario de services_active
    """
    services = Service.all()

    return {service.id: service.name for service in services}


def users_actives():
    """Obtener un diciconario con los usuarios
    
    Return
    ------
    {id: user_id_active.full_name}
        Una diccionario de user_id_active
    """
    users = User.all()

    return {user.id: user.full_name for user in users}

######################################################################
###Reponde a la pregunta: 1. Cantidad de tickets generados por clientes
########################################################################

def tickets_queue_customers():
    name = "tickets_queue_customers"
    """Obtener los tickets mensuales requeridos por los clientes 
        que esten con queue_id=6.
    
    Parameters
    ---------
    
    Return
    Dict[customer][moth] = {ticket_id: }
        Diccionario con los clientes y sus tickets requeridos
    """
    path_temp = os.path.join(path_analyzer, "temp")
    path_customers_active = os.path.join(path_temp,"tickets_queue_customers.json")

    if not os.path.exists(path_temp):
        os.mkdir(path_temp)

    if os.path.exists(path_customers_active):
        with open(path_customers_active, "r") as f:
            json_customers_active = json.load(f)
            last_ticket_id = json_customers_active["last_ticket_id"]
            start_date = json_customers_active["last_date"]
            list_months_temp = list_months(start_date)
            customers_active_temp = json_customers_active["customers_active"]
            print(last_ticket_id, list_months_temp)
    else:
        customers_active_temp = {}
        last_ticket_id = 100
        start_date = "2019-1-1" 
        list_months_temp = list_months(start_date)

    try:
        customers = ['AS']+[customer.customer_id for customer in CustomerCompany.all() if customer.customer_id != "Adaptive Security"]
        last_ticket = Ticket.last_ticket_queue(6)
        last_ticket_id_temp = last_ticket.id
    except:
        last_ticket_id_temp=last_ticket_id
        customers=[]
    
    if int(last_ticket_id) < last_ticket_id_temp:
        for pos, period in enumerate(list_months_temp):
            print(f"{period} Recopilando datos del periodo")
            if pos+1 < len(list_months_temp):
                start_period = period
                end_period =  list_months_temp[pos+1]
                try:
                    tickets_by_period = Ticket.tickets_by_queue_period(6, start_period, end_period)
                except:
                    tickets_by_period = []

                if not tickets_by_period:
                    continue
                period_temp = datetime.strptime(period, "%Y-%m-%d")
                year = period_temp.year
                month = period_temp.month
                print(f"{name} Recopilando datos del periodo {year, month} --> {len(tickets_by_period)}")
                for ticket in tickets_by_period:
                    last_ticket_id_temp = ticket.id
                    customer_temp = ticket.customer_id
                    if customer_temp == "Adaptive Security":
                        customer_temp = "AS"
                    if customer_temp in customers:
                        if year not in customers_active_temp:
                            customers_active_temp[year] = {}
                        if month not in customers_active_temp[year]:
                            customers_active_temp[year][month] = {}
                        if customer_temp not in customers_active_temp[year][month]:
                            customers_active_temp[year][month][customer_temp] = {}
                        if ticket.id not in customers_active_temp[year][month][customer_temp]:
                            if ticket.type_id == 68:
                                resolution_time = 0
                            else:
                                resolution_time = ticket.last_history.change_time - ticket.create_time
                            if ticket.service:
                                service = ticket.service_id
                            else:
                                service = "Undefined"
                            customers_active_temp[year][month][customer_temp][ticket.id] = {"service_id": service,
                                "admin": ticket.user_id,
                                "title": ticket.title,
                                "tn": ticket.tn,
                                "resolution_time": str(resolution_time)
                            }
            

    _customers_active = {
        "customers_active": customers_active_temp,
        "last_date": list_months_temp[-2],
        "last_ticket_id": last_ticket_id_temp
    }

    with open(path_customers_active, "w") as f:
        json_customers_active = json.dumps(_customers_active)
        f.write(json_customers_active)

    return customers_active_temp

print(tickets_queue_customers())

def tickets_queue_users():
    name = "tickets_queue_users"
    """Obtener los tickets mensuales requeridos por los clientes 
        que esten con queue_id=6.
    
    Parameters
    ---------
    
    Return
    Dict[customer][moth] = {ticket_id: }
        Diccionario con los clientes y sus tickets requeridos
    """
    path_temp = os.path.join(path_analyzer, "temp")
    path_customers_active = os.path.join(path_temp,"tickets_queue_users.json")

    if not os.path.exists(path_temp):
        os.mkdir(path_temp)

    if os.path.exists(path_customers_active):
        with open(path_customers_active, "r") as f:
            json_customers_active = json.load(f)
            last_ticket_id = json_customers_active["last_ticket_id"]
            start_date = json_customers_active["last_date"]
            list_months_temp = list_months(start_date)
            customers_active_temp = json_customers_active["customers_active"]
            print(last_ticket_id, list_months_temp)
    else:
        customers_active_temp = {}
        last_ticket_id = 100
        start_date = "2019-1-1" 
        list_months_temp = list_months(start_date)

    try:
        customers = ['AS']+[customer.customer_id for customer in CustomerCompany.all() if customer.customer_id != "Adaptive Security"]
        last_ticket = Ticket.last_ticket_queue(6)
        last_ticket_id_temp = last_ticket.id
    except:
        last_ticket_id_temp=last_ticket_id
        customers=[]
    
    if int(last_ticket_id) < last_ticket_id_temp:
        for pos, period in enumerate(list_months_temp):
            print(f"{period} Recopilando datos del periodo")
            if pos+1 < len(list_months_temp):
                start_period = period
                end_period =  list_months_temp[pos+1]
                try:
                    tickets_by_period = Ticket.tickets_by_queue_period(6, start_period, end_period)
                except:
                    tickets_by_period = []

                if not tickets_by_period:
                    continue
                period_temp = datetime.strptime(period, "%Y-%m-%d")
                year = period_temp.year
                month = period_temp.month
                print(f"{name} Recopilando datos del periodo {year, month} --> {len(tickets_by_period)}")
                for ticket in tickets_by_period:
                    last_ticket_id_temp = ticket.id
                    customer_temp = ticket.customer_id
                    if customer_temp == "Adaptive Security":
                        customer_temp = "AS"
                    if customer_temp in customers:
                        if year not in customers_active_temp:
                            customers_active_temp[year] = {}
                        if month not in customers_active_temp[year]:
                            customers_active_temp[year][month] = {}
                        if ticket.user_id not in customers_active_temp[year][month]:
                            customers_active_temp[year][month][ticket.user_id] = {}
                        if ticket.id not in customers_active_temp[year][month][ticket.user_id]:
                            if ticket.type_id == 68:
                                resolution_time = 0
                            else:
                                resolution_time = ticket.last_history.change_time - ticket.create_time
                            if ticket.service:
                                service = ticket.service_id
                            else:
                                service = "Undefined"
                            customers_active_temp[year][month][ticket.user_id][ticket.id] = {"customer_id": customer_temp,
                                "service_id": service,
                                "admin": ticket.user_id,
                                "title": ticket.title,
                                "tn": ticket.tn,
                                "resolution_time": str(resolution_time)
                            }
            

    _customers_active = {
        "customers_active": customers_active_temp,
        "last_date": list_months_temp[-2],
        "last_ticket_id": last_ticket_id_temp
    }

    with open(path_customers_active, "w") as f:
        json_customers_active = json.dumps(_customers_active)
        f.write(json_customers_active)

    return customers_active_temp

print(tickets_queue_users())

exit()

##########################################################################################
###Reponde a la pregunta: 2. Cantidad de tickets generados por plataformas en cada cliente
##########################################################################################

def tickets_customers_queue_service():
    name = "tickets_customers_queue_service"
    """Obtener los tickets diarios requeridos por los clientes 
        que esten con queue_id=6 y clasificados según la plataforma
    
    Parameters
    ---------
    
    Return
    Dict[Customer][service_id] = len(tickets)
        Diccionario con los clientes y sus tickets requeridos por servicio
    """
    path_temp = os.path.join(path_analyzer, "temp")
    path_customers_active = os.path.join(path_temp,"customers_active_service.json")

    if not os.path.exists(path_temp):
        os.mkdir(path_temp)

    if os.path.exists(path_customers_active):
        with open(path_customers_active, "r") as f:
            json_customers_active = json.load(f)
            last_ticket_id = json_customers_active["last_ticket_id"]
            start_date = json_customers_active["last_date"]
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            days_for_analyzed = list_date(start_date, datetime.today())
            customers_active_temp = json_customers_active["customers_active"]
    else:
        customers_active_temp = {}
        last_ticket_id = 1
        start_date = datetime.strptime("2019-1-1", "%Y-%m-%d") 
        days_for_analyzed = list_date(start_date, datetime.today())

    customers = [customer.customer_id for customer in CustomerCompany.all()]
    last_ticket = Ticket.last_ticket()
    last_ticket_id_temp = last_ticket.id
    
    if int(last_ticket_id) < last_ticket_id_temp:
        for day_for_analyzed in days_for_analyzed:
            print(f"{name} Recopilando datos de los CLientes del día {day_for_analyzed}")
            tickets_by_day = Ticket.tickets_by_date(day_for_analyzed)
            if not tickets_by_day:
                continue

            customers_temp = []
            service_temp = []
            for ticket_by_day in tickets_by_day:
                last_ticket_id_temp = ticket_by_day.id
                print(f"{name} Analizando Ticket ID = {ticket_by_day.id}")
                if not ticket_by_day.service_id:
                    continue
                if not ticket_by_day.queue_id == 6:
                    continue
                
                if ticket_by_day.customer_id in customers and ticket_by_day.customer_id not in customers_temp:
                    customers_temp.append(ticket_by_day.customer_id)
                    service_temp.append(ticket_by_day.service_id)
                    _day_for_analyzed = datetime.strptime(day_for_analyzed, "%Y-%m-%d")
                    year = str(_day_for_analyzed.year)
                    month = str(_day_for_analyzed.month)
                    print(ticket_by_day.service_id)

                    count_service = len(Ticket.tickets_by_customer_service_date_queue(6, ticket_by_day.customer_id, ticket_by_day.service_id, last_ticket_id, day_for_analyzed))
                    print(f"count_service {count_service}")
                    if not count_service:
                        continue
                    if ticket_by_day.customer_id in customers:
                        if year not in customers_active_temp:
                            customers_active_temp[year] = {}
                        if ticket_by_day.customer_id not in customers_active_temp[year]:
                            customers_active_temp[year][ticket_by_day.customer_id] = {}
                        if month not in customers_active_temp[year][ticket_by_day.customer_id] :
                            customers_active_temp[year][ticket_by_day.customer_id][month] = {}
                        if ticket_by_day.service_id not in customers_active_temp[year][ticket_by_day.customer_id][month]:
                            customers_active_temp[year][ticket_by_day.customer_id][month][ticket_by_day.service_id] = count_service
                        else:
                            customers_active_temp[year][ticket_by_day.customer_id][month][ticket_by_day.service_id] += count_service
    _customers_active = {
        "customers_active": customers_active_temp,
        "last_date": days_for_analyzed[-1],
        "last_ticket_id": last_ticket_id_temp
    }

    with open(path_customers_active, "w") as f:
        json_customers_active = json.dumps(_customers_active)
        f.write(json_customers_active)

    return customers_active_temp

# print(tickets_customers_queue_service())

##############################################################################
###Reponde a la pregunta: 2. Cantidad de tickets atendidos por administrador
##############################################################################


def tickets_admin():
    name = "tickets_admin"
    """Obtener los tickets diarios atendidos por administrador
    
    Parameters
    ---------
    
    Return
    Dict[year][admin][month][day] = len(tickets)
        Diccionario con adminitradores y sus requerimientos atendidos por año
    """
    path_temp = os.path.join(path_analyzer, "temp")
    path_customers_active = os.path.join(path_temp,"admin_active.json")

    if not os.path.exists(path_temp):
        os.mkdir(path_temp)

    if os.path.exists(path_customers_active):
        with open(path_customers_active, "r") as f:
            json_customers_active = json.load(f)
            last_ticket_id = json_customers_active["last_ticket_id"]
            start_date = json_customers_active["last_date"]
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            days_for_analyzed = list_date(start_date, datetime.today())
            admin_active_temp = json_customers_active["admin_active"]
    else:
        admin_active_temp = {}
        last_ticket_id = 1
        start_date = datetime.strptime("2019-01-01", "%Y-%m-%d") 
        days_for_analyzed = list_date(start_date, datetime.today())

    last_ticket = Ticket.last_ticket()
    last_ticket_id_temp = last_ticket.id
    
    if int(last_ticket_id) < last_ticket_id_temp:
        for day_for_analyzed in days_for_analyzed:
            print(f"{name} Recopilando datos de los requerimientos del día {day_for_analyzed}")
            tickets_by_day = Ticket.tickets_by_date(day_for_analyzed)
            if not tickets_by_day:
                continue

            user_id_temp = []
            for ticket_by_day in tickets_by_day:
                last_ticket_id_temp = ticket_by_day.id
                print(f"{name} Analizando Ticket ID = {ticket_by_day.id}")
                if not ticket_by_day.service_id:
                    continue
                if not ticket_by_day.queue_id == 6:
                    continue
                
                if ticket_by_day.user_id not in user_id_temp:
                    user_id_temp.append(ticket_by_day.user_id)
                    _day_for_analyzed = datetime.strptime(day_for_analyzed, "%Y-%m-%d")
                    year = str(_day_for_analyzed.year)
                    month = str(_day_for_analyzed.month)
                    day = str(_day_for_analyzed.day)

                    count_service_user_id = len(Ticket.tickets_by_queue_user_date(6, ticket_by_day.user_id, last_ticket_id, day_for_analyzed))
                    print(f"count_service_user_id {ticket_by_day.user_id} {day_for_analyzed} {count_service_user_id}")
                    if not count_service_user_id:
                        continue
                    
                    if year not in admin_active_temp:
                        admin_active_temp[year] = {}
                    if ticket_by_day.user_id not in admin_active_temp[year]:
                        admin_active_temp[year][ticket_by_day.user_id] = {}
                    if month not in admin_active_temp[year][ticket_by_day.user_id] :
                        admin_active_temp[year][ticket_by_day.user_id][month] = {}
                    if day not in admin_active_temp[year][ticket_by_day.user_id][month]:
                        admin_active_temp[year][ticket_by_day.user_id][month][day] = count_service_user_id
                    else:
                        admin_active_temp[year][ticket_by_day.user_id][month][day] += count_service_user_id
    
    _customers_active = {
        "admin_active": admin_active_temp,
        "last_date": days_for_analyzed[-1],
        "last_ticket_id": last_ticket_id_temp
    }

    with open(path_customers_active, "w") as f:
        json_customers_active = json.dumps(_customers_active)
        f.write(json_customers_active)

    return admin_active_temp

# print(tickets_admin())

def tickets_admin_service_customer():
    name = "tickets_admin_service_customer"
    """Obtener los tickets diarios atendidos por administrador en plataforma y cliente
    
    Parameters
    ---------
    
    Return
    Dict[year][admin][month][][][day] = len(tickets)
        Diccionario con adminitradores y sus requerimientos atendidos por año
    """
    path_temp = os.path.join(path_analyzer, "temp")
    path_customers_active = os.path.join(path_temp,"admin_active_service_customer.json")

    if not os.path.exists(path_temp):
        os.mkdir(path_temp)

    if os.path.exists(path_customers_active):
        with open(path_customers_active, "r") as f:
            json_customers_active = json.load(f)
            last_ticket_id = json_customers_active["last_ticket_id"]
            start_date = json_customers_active["last_date"]
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            days_for_analyzed = list_date(start_date, datetime.today())
            admin_active_temp = json_customers_active["admin_active_service_customer"]
    else:
        admin_active_temp = {}
        last_ticket_id = 1
        start_date = datetime.strptime("2022-12-01", "%Y-%m-%d") 
        days_for_analyzed = list_date(start_date, datetime.today())

    last_ticket = Ticket.last_ticket()
    last_ticket_id_temp = last_ticket.id
    
    if int(last_ticket_id) < last_ticket_id_temp:
        for day_for_analyzed in days_for_analyzed:
            print(f"{name} Recopilando datos de los requerimientos del día {day_for_analyzed}")
            tickets_by_day = Ticket.tickets_by_date(day_for_analyzed)
            if not tickets_by_day:
                continue

            user_id_temp = []
            for ticket_by_day in tickets_by_day:
                last_ticket_id_temp = ticket_by_day.id
                print(f"{name} Analizando Ticket ID = {ticket_by_day.id}")
                if not ticket_by_day.service_id:
                    continue
                if not ticket_by_day.queue_id == 6:
                    continue
                
                if ticket_by_day.user_id not in user_id_temp:
                    user_id_temp.append(ticket_by_day.user_id)
                    _day_for_analyzed = datetime.strptime(day_for_analyzed, "%Y-%m-%d")
                    year = str(_day_for_analyzed.year)
                    month = str(_day_for_analyzed.month)
                    day = str(_day_for_analyzed.day)

                    count_customer_service_user_id = len(Ticket.tickets_by_queue_user_date_customer_service(6, ticket_by_day.user_id, ticket_by_day.customer_id, ticket_by_day.service_id, last_ticket_id, day_for_analyzed))
                    print(f"count_customer_service_user_id {ticket_by_day.user_id} {day_for_analyzed} {count_customer_service_user_id}")
                    if not count_customer_service_user_id:
                        continue
                    
                    if year not in admin_active_temp:
                        admin_active_temp[year] = {}
                    if ticket_by_day.user_id not in admin_active_temp[year]:
                        admin_active_temp[year][ticket_by_day.user_id] = {}
                    if month not in admin_active_temp[year][ticket_by_day.user_id] :
                        admin_active_temp[year][ticket_by_day.user_id][month] = {}
                    if ticket_by_day.customer_id not in admin_active_temp[year][ticket_by_day.user_id][month]:
                        admin_active_temp[year][ticket_by_day.user_id][month][ticket_by_day.customer_id] ={}
                    if ticket_by_day.service_id not in admin_active_temp[year][ticket_by_day.user_id][month]:
                        admin_active_temp[year][ticket_by_day.user_id][month][ticket_by_day.customer_id][ticket_by_day.service_id] = count_customer_service_user_id
                    else:
                        admin_active_temp[year][ticket_by_day.user_id][month][ticket_by_day.customer_id][ticket_by_day.service_id] += count_customer_service_user_id
    
    _customers_active = {
        "admin_active_service_customer": admin_active_temp,
        "last_date": days_for_analyzed[-1],
        "last_ticket_id": last_ticket_id_temp
    }

    with open(path_customers_active, "w") as f:
        json_customers_active = json.dumps(_customers_active)
        f.write(json_customers_active)

    return admin_active_temp

print(tickets_admin_service_customer())