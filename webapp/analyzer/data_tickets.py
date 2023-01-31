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

def customers_actives():
    """Obtener un diciconario con el nombre de los clientes
    
    Return
    ------
    {id: customer_id.name}
        Una diccionario de clientes
    """
    customers = CustomerCompany.all()

    dict_customer = {"AS": "Adaptive Security"}
    for customer in customers:
        if customer.customer_id != "Adaptive Security":
            dict_customer[customer.customer_id] = customer.name

    return dict_customer


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
    
    print(last_ticket_id, last_ticket_id_temp, list_months_temp)
    
    if int(last_ticket_id) < last_ticket_id_temp and (last_ticket_id_temp-int(last_ticket_id) ) > 100:
        for pos, period in enumerate(list_months_temp):
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
                                resolution_time = "Undefined"
                            else:
                                resolution_time = ticket.last_history.change_time - ticket.create_time
                            
                            customers_active_temp[year][month][customer_temp][ticket.id] = {"service_id": ticket.service_id,
                                "admin": ticket.user_id,
                                "title": ticket.title,
                                "tn": ticket.tn,
                                "resolution_time": str(resolution_time),
                                "state": ticket.ticket_state.name,
                                "type": ticket.type.name if ticket.type else "Undefined",
                                "sla": ticket.sla.solution_time if ticket.sla else "Undefined",
                                "create_time": str(ticket.create_time),
                                "change_time": str(ticket.change_time)
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

a_ = tickets_queue_customers()

##########################################################################################
###Reponde a la pregunta: Cantidad de tickets generados por plataformas en cada usuario
##########################################################################################


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

    print(last_ticket_id, last_ticket_id_temp, list_months_temp)
    
    if int(last_ticket_id) < last_ticket_id_temp and (last_ticket_id_temp-int(last_ticket_id) ) > 100:
        for pos, period in enumerate(list_months_temp):
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
                                resolution_time = "Undefined"
                            else:
                                resolution_time = ticket.last_history.change_time - ticket.create_time
                         
                            customers_active_temp[year][month][ticket.user_id][ticket.id] = {"customer_id": customer_temp,
                                "service_id": ticket.service_id,
                                "admin": ticket.user_id,
                                "title": ticket.title,
                                "tn": ticket.tn,
                                "resolution_time": str(resolution_time),
                                "state": ticket.ticket_state.name,
                                "type": ticket.type.name if ticket.type else "Undefined",
                                "sla": ticket.sla.solution_time if ticket.sla else "Undefined",
                                "create_time": str(ticket.create_time),
                                "change_time": str(ticket.change_time)
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

b_ = tickets_queue_users()


'''
def tickets_offenses():
    name = "tickets_offenses"
    """Obtener los tickets que en su title tiene la palabra ofensa
    
    Parameters
    ---------
    
    Return
    Dict[customer][moth] = {ticket_id: }
        Diccionario con los clientes y sus tickets levantados
    """
    path_temp = os.path.join(path_analyzer, "temp")
    path_tickets_offenses = os.path.join(path_temp,"tickets_offenses.json")

    if not os.path.exists(path_temp):
        os.mkdir(path_temp)

    if os.path.exists(path_tickets_offenses):
        with open(path_tickets_offenses, "r") as f:
            json_tickets_offenses = json.load(f)
            last_ticket_id = json_tickets_offenses["last_ticket_id"]
            start_date = json_tickets_offenses["last_date"]
            list_months_temp = list_months(start_date)
            tickets_offenses_temp = json_tickets_offenses["tickets_offenses"]

    else:
        tickets_offenses_temp = {}
        last_ticket_id = 100
        start_date = "2019-1-1" 
        list_months_temp = list_months(start_date)

    try:
        customers = ['AS']+[customer.customer_id for customer in CustomerCompany.all() if customer.customer_id != "Adaptive Security"]
        last_ticket = Ticket.last_ticket_offense()
        last_ticket_id_temp = last_ticket.id
    except:
        last_ticket_id_temp=last_ticket_id
        customers=[]

    print(last_ticket_id, last_ticket_id_temp, list_months_temp)
    
    if int(last_ticket_id) < last_ticket_id_temp and (last_ticket_id_temp-int(last_ticket_id) ) > 100:
        for pos, period in enumerate(list_months_temp):
            print(f"{name} Recopilando datos del periodo {period}")
            if pos+1 < len(list_months_temp):
                start_period = period
                end_period =  list_months_temp[pos+1]
                try:
                    tickets_by_period = Ticket.tickets_offenses_by_period(start_period, end_period)
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
    
    
    
    
    for date in list_date:
        inicio_date = datetime.now()
        print(f"Inicio {inicio_date} ---> {date}")
        if date.split("-")[1] not in ticket_offenses_year:
            ticket_offenses_year[date.split("-")[1]] = {}

        if date.split("-")[2] not in ticket_offenses_year[date.split("-")[1]]:
            ticket_offenses_year[date.split("-")[1]][date.split("-")[2]] = {
                "handwork": {
                    "success": {
                        "low": {},
                        "mean": {},
                        "high": {}
                    },
                    "fails": {
                        "low": {},
                        "mean": {},
                        "high": {}
                    },
                    "undefined": {
                        "low": {},
                        "mean": {},
                        "high": {}
                    }
                },
                "automatic": {
                    "success": {
                        "low": {},
                        "mean": {},
                        "high": {}
                    },
                    "fails": {
                        "low": {},
                        "mean": {},
                        "high": {}
                    },
                    "undefined": {
                        "low": {},
                        "mean": {},
                        "high": {}
                    }
                },
                "undefined": {}
            }
        
        # Obtenter la data de OTRS según date
        data_otrs = db.session.query(Ticket).filter(
                        Ticket.create_time>=f"{date} 00:00:00",
                        Ticket.create_time<f"{date} 23:00:00")

        # Recorrer cada ticket generado en OTRS para sacar su id 
        # Con ese id ingresar a QRadar y obtener la fecha de inicio
        # Con las fechas ya obtenidad hacer el calculo del SLA de respuesta
        for ticket in data_otrs:
            if len(re.findall(r"Ofensa", ticket.title)) > 0 and len(re.findall(r"\d{5,}", ticket.title)) > 0 and len(set(re.findall(r"\d{5,}|-|\d{5,}", ticket.title))) == 2:
                id_offense = re.findall(r"\d{5,}", ticket.title)
                data_qradar = tools_qradar.start_time_offenses(id_offense[0])
                create_time_otrs = ticket.create_time + timedelta(hours=1)
                start_time_qradar = "0"
                response_time = "0"
                print(f" id_offense: {id_offense[0]} --create_time_otrs:{create_time_otrs} --data_qradar:{data_qradar}")
                handwork = re.findall(r"Ofensa N°", ticket.title)
                if handwork:
                    if data_qradar:
                        start_time_qradar = datetime.fromtimestamp(data_qradar)
                        response_time = create_time_otrs - start_time_qradar
                        ideal_response_time = timedelta(minutes=15)
                        if response_time <= ideal_response_time:
                            if len(re.findall(r"Criticidad|Baja", ticket.title)) > 1:
                                ticket_offenses_year[date.split("-")[1]][date.split("-")[2]]["handwork"]["success"]["low"][ticket.tn] = {
                                    "id_qradar": id_offense[0],
                                    "id_otrs": ticket.id,
                                    "title": ticket.title,
                                    "start_time": str(start_time_qradar),
                                    "create_time": str(create_time_otrs),
                                    "response_time": str(response_time)
                                }
                            elif len(re.findall(r"Criticidad|Media", ticket.title)) > 1:
                                ticket_offenses_year[date.split("-")[1]][date.split("-")[2]]["handwork"]["success"]["mean"][ticket.tn] = {
                                    "id_qradar": id_offense[0],
                                    "id_otrs": ticket.id,
                                    "title": ticket.title,
                                    "start_time": str(start_time_qradar),
                                    "create_time": str(create_time_otrs),
                                    "response_time": str(response_time)
                                }
                            elif len(re.findall(r"Criticidad|Alta", ticket.title)) > 1:
                                ticket_offenses_year[date.split("-")[1]][date.split("-")[2]]["handwork"]["success"]["high"][ticket.tn] = {
                                    "id_qradar": id_offense[0],
                                    "id_otrs": ticket.id,
                                    "title": ticket.title,
                                    "start_time": str(start_time_qradar),
                                    "create_time": str(create_time_otrs),
                                    "response_time": str(response_time)
                                }
                            else:
                                print(f"---Alert handwork success {ticket.tn} {ticket.title}")
                        else:
                            if len(re.findall(r"Criticidad|Baja", ticket.title)) > 1:
                                ticket_offenses_year[date.split("-")[1]][date.split("-")[2]]["handwork"]["fails"]["low"][ticket.tn] = {
                                    "id_qradar": id_offense[0],
                                    "id_otrs": ticket.id,
                                    "title": ticket.title,
                                    "start_time": str(start_time_qradar),
                                    "create_time": str(create_time_otrs),
                                    "response_time": str(response_time)
                                }
                            elif len(re.findall(r"Criticidad|Media", ticket.title)) > 1:
                                ticket_offenses_year[date.split("-")[1]][date.split("-")[2]]["handwork"]["fails"]["mean"][ticket.tn] = {
                                    "id_qradar": id_offense[0],
                                    "id_otrs": ticket.id,
                                    "title": ticket.title,
                                    "start_time": str(start_time_qradar),
                                    "create_time": str(create_time_otrs),
                                    "response_time": str(response_time)
                                }
                            elif len(re.findall(r"Criticidad|Alta", ticket.title)) > 1:
                                ticket_offenses_year[date.split("-")[1]][date.split("-")[2]]["handwork"]["fails"]["high"][ticket.tn] = {
                                    "id_qradar": id_offense[0],
                                    "id_otrs": ticket.id,
                                    "title": ticket.title,
                                    "start_time": str(start_time_qradar),
                                    "create_time": str(create_time_otrs),
                                    "response_time": str(response_time)
                                }
                            else:
                                print(f"---Alert handwork fails {ticket.tn} {ticket.title}")
                    else:
                        if len(re.findall(r"Criticidad|Baja", ticket.title)) > 1:
                            ticket_offenses_year[date.split("-")[1]][date.split("-")[2]]["handwork"]["undefined"]["low"][ticket.tn] = {
                                "id_qradar": id_offense[0],
                                "id_otrs": ticket.id,
                                "title": ticket.title,
                                "start_time": str(start_time_qradar),
                                "create_time": str(create_time_otrs),
                                "response_time": str(response_time)
                            }
                        elif len(re.findall(r"Criticidad|Media", ticket.title)) > 1:
                            ticket_offenses_year[date.split("-")[1]][date.split("-")[2]]["handwork"]["undefined"]["mean"][ticket.tn] = {
                                "id_qradar": id_offense[0],
                                "id_otrs": ticket.id,
                                "title": ticket.title,
                                "start_time": str(start_time_qradar),
                                "create_time": str(create_time_otrs),
                                "response_time": str(response_time)
                            }
                        elif len(re.findall(r"Criticidad|Alta", ticket.title)) > 1:
                            ticket_offenses_year[date.split("-")[1]][date.split("-")[2]]["handwork"]["undefined"]["high"][ticket.tn] = {
                                "id_qradar": id_offense[0],
                                "id_otrs": ticket.id,
                                "title": ticket.title,
                                "start_time": str(start_time_qradar),
                                "create_time": str(create_time_otrs),
                                "response_time": str(response_time)
                            }
                else:
                    if data_qradar:
                        start_time_qradar = datetime.fromtimestamp(data_qradar)
                        response_time = create_time_otrs - start_time_qradar
                        ideal_response_time = timedelta(minutes=15)
                        if response_time <= ideal_response_time:
                            if len(re.findall(r"Criticidad|Baja", ticket.title)) > 1:
                                ticket_offenses_year[date.split("-")[1]][date.split("-")[2]]["automatic"]["success"]["low"][ticket.tn] = {
                                    "id_qradar": id_offense[0],
                                    "id_otrs": ticket.id,
                                    "title": ticket.title,
                                    "start_time": str(start_time_qradar),
                                    "create_time": str(create_time_otrs),
                                    "response_time": str(response_time)
                                }
                            elif len(re.findall(r"Criticidad|Media", ticket.title)) > 1:
                                ticket_offenses_year[date.split("-")[1]][date.split("-")[2]]["automatic"]["success"]["mean"][ticket.tn] = {
                                    "id_qradar": id_offense[0],
                                    "id_otrs": ticket.id,
                                    "title": ticket.title,
                                    "start_time": str(start_time_qradar),
                                    "create_time": str(create_time_otrs),
                                    "response_time": str(response_time)
                                }
                            elif len(re.findall(r"Criticidad|Alta", ticket.title)) > 1:
                                ticket_offenses_year[date.split("-")[1]][date.split("-")[2]]["automatic"]["success"]["high"][ticket.tn] = {
                                    "id_qradar": id_offense[0],
                                    "id_otrs": ticket.id,
                                    "title": ticket.title,
                                    "start_time": str(start_time_qradar),
                                    "create_time": str(create_time_otrs),
                                    "response_time": str(response_time)
                                }
                            else:
                                print(f"---Alert automatic success {ticket.tn} {ticket.title}")
                        else:
                            if len(re.findall(r"Criticidad|Baja", ticket.title)) > 1:
                                ticket_offenses_year[date.split("-")[1]][date.split("-")[2]]["automatic"]["fails"]["low"][ticket.tn] = {
                                    "id_qradar": id_offense[0],
                                    "id_otrs": ticket.id,
                                    "title": ticket.title,
                                    "start_time": str(start_time_qradar),
                                    "create_time": str(create_time_otrs),
                                    "response_time": str(response_time)
                                }
                            elif len(re.findall(r"Criticidad|Media", ticket.title)) > 1:
                                ticket_offenses_year[date.split("-")[1]][date.split("-")[2]]["automatic"]["fails"]["mean"][ticket.tn] = {
                                    "id_qradar": id_offense[0],
                                    "id_otrs": ticket.id,
                                    "title": ticket.title,
                                    "start_time": str(start_time_qradar),
                                    "create_time": str(create_time_otrs),
                                    "response_time": str(response_time)
                                }
                            elif len(re.findall(r"Criticidad|Alta", ticket.title)) > 1:
                                ticket_offenses_year[date.split("-")[1]][date.split("-")[2]]["automatic"]["fails"]["high"][ticket.tn] = {
                                    "id_qradar": id_offense[0],
                                    "id_otrs": ticket.id,
                                    "title": ticket.title,
                                    "start_time": str(start_time_qradar),
                                    "create_time": str(create_time_otrs),
                                    "response_time": str(response_time)
                                }
                            else:
                                print(f"---Alert automatic fails {ticket.tn} {ticket.title}")
                    else:
                        if len(re.findall(r"Criticidad|Baja", ticket.title)) > 1:
                            ticket_offenses_year[date.split("-")[1]][date.split("-")[2]]["automatic"]["undefined"]["low"][ticket.tn] = {
                                "id_qradar": id_offense[0],
                                "id_otrs": ticket.id,
                                "title": ticket.title,
                                "start_time": str(start_time_qradar),
                                "create_time": str(create_time_otrs),
                                "response_time": str(response_time)
                            }
                        elif len(re.findall(r"Criticidad|Media", ticket.title)) > 1:
                            ticket_offenses_year[date.split("-")[1]][date.split("-")[2]]["automatic"]["undefined"]["mean"][ticket.tn] = {
                                "id_qradar": id_offense[0],
                                "id_otrs": ticket.id,
                                "title": ticket.title,
                                "start_time": str(start_time_qradar),
                                "create_time": str(create_time_otrs),
                                "response_time": str(response_time)
                            }
                        elif len(re.findall(r"Criticidad|Alta", ticket.title)) > 1:
                            ticket_offenses_year[date.split("-")[1]][date.split("-")[2]]["automatic"]["undefined"]["high"][ticket.tn] = {
                                "id_qradar": id_offense[0],
                                "id_otrs": ticket.id,
                                "title": ticket.title,
                                "start_time": str(start_time_qradar),
                                "create_time": str(create_time_otrs),
                                "response_time": str(response_time)
                            }
            else:
                ticket_offenses_year[date.split("-")[1]][date.split("-")[2]]["undefined"][ticket.tn] = {
                    "id": ticket.id,
                    "title": ticket.title,
                    "star_time": str(ticket.create_time)
                }
                print(ticket.tn, ticket.id, ticket.title)
        
        fin_date = datetime.now()
        print(f"Fin {fin_date} ---> {date}")
        print(f"Tiempo de ejecución {fin_date-inicio_date}")
        print("\n")
    
    tools_data.save_data_json(f"ticket_offenses_year_{year}", ticket_offenses_year)

print(f"Tiempo de ejecución {datetime.now()-inicio}")
print("---Fin---")
'''