try:
    from .otrs.models.ticket import Ticket
    from .otrs.models.customer_company import CustomerCompany
    from .otrs.models.service import Service
    from .otrs.models.user import User
    from .qradar import qradar
except:
    from otrs.models.ticket import Ticket
    from otrs.models.customer_company import CustomerCompany
    from otrs.models.service import Service
    from otrs.models.user import User
    from qradar import qradar

import re
import json
from pathlib import Path
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


path_analyzer = Path(__file__).parent
path_temp = Path(f"{path_analyzer}/temp_data_tickets")
if not path_temp.exists():
    path_temp.mkdir()


##########################################
##########Funciones de apoyo#############
##########################################


def list_months_year(year: str):
    """Obtener una lista con los meses del año a analizar

    Parameters
    ---------
    year:str
        El año del cual se quiere hacer el análisis.
    
    Return
    ------
    List(months)
        Una lista de meses
    """

    end_date = datetime.today()+relativedelta(months=1)
    date = f"{year}-1-1"
    month_temp = datetime.strptime(date, "%Y-%m-%d")
    list_months_active = [month_temp.strftime("%Y-%m-%d")]

    if int(year) < end_date.year:
        i=1
        while i<=12:
            month_temp=month_temp+relativedelta(months=1)
            list_months_active.append(month_temp.strftime("%Y-%m-%d"))
            i+=1
    else:
        while True:
            month_temp=month_temp+relativedelta(months=1)
            list_months_active.append(month_temp.strftime("%Y-%m-%d"))
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
    dict_services = {"Undefined": "Undefined"}
    for service in services:
        dict_services[service.id] = service.name

    return dict_services


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
    
    return {
        customer.customer_id: customer.name for customer in customers 
        if customer.customer_id != "EJEMPLO" 
        and customer.customer_id != "BFAL"
    }

def init_tools():
    def_name = "init_tools"
    funs_def= [calendar_spanish,
                     services_actives,
                     users_actives,
                     customers_actives
                    ]
    funs_name = ["calendar_spanish",
                 "services_actives",
                 "users_actives",
                 "customers_actives"
                ]

    for pos, fun_def in  enumerate(funs_def):
        path_active = Path(
            f"{path_temp}/{funs_name[pos]}.json"
            )
        
        _active = { "active": fun_def(),
                   "update_date": datetime.today().strftime("%d-%m-%Y %H:%M:%S")
                   }
        
        with open(path_active, "w") as f:
            json_active = json.dumps(_active)
            f.write(json_active)
    
    print(f"{def_name} ok")


##############################################################
#### OBTENCIÓN DE LA QUE SERA ANALIZADA PARA RESPONDER A: ####
##############################################################


###############################################################
#  1. Cantidad de tickets asociados por Clientes/Administradores
################################################################


def tickets_queue(year: str, type_: str, queue_id: int=6):
    def_name = f"tickets_{type_}_queue_{queue_id}"
    """Obtener los tickets de los Clientes/Administradores durante un año
    con filtros de cola.
    
    Parameters:
    Year: str
        El año que se quiere analizar

    Return
    ------
    Dict[customer/queue=6][Tickets]
        Una diccionario de clientes/administradores con los tickets asociados
    """
    customers_actives_temp = customers_actives()
    if type_ == "customers":
        path_active = Path(
            f"{path_temp}/tickets_customers_by_user_queue_{queue_id}_{year}.json"
        )
    
    elif type_ == "administrators":
        path_active = Path(
            f"{path_temp}/tickets_administrators_by_queue_{queue_id}_{year}.json"
        )
    
    else:
        return f"Tipo:{type_} --> Undefined"

    if path_active.exists():
        with path_active.open("r") as f:
            json_active = json.load(f)
            last_ticket_id = json_active["last_ticket_id"]
            start_date = json_active["last_period"]
            month_temp = datetime.strptime(start_date, "%Y-%m-%d")
            list_months_temp = list_months_year(month_temp.year)
            active_temp = json_active["active"]
    else:
        last_ticket_id = 45
        list_months_temp = list_months_year(year)
        active_temp = {}
    
    try:
        last_ticket_id_temp = Ticket.last_ticket_id_queue_period(
            queue_id, 
            list_months_temp[-2], 
            list_months_temp[-1]
        )
    except:
        last_ticket_id_temp=last_ticket_id
    
    print("Analizando", 
        def_name, 
        last_ticket_id, 
        last_ticket_id_temp, 
        list_months_temp
    )
    
    if int(last_ticket_id) >= last_ticket_id_temp:
        return active_temp
    
    for pos, period in enumerate(list_months_temp):
        
        if pos+1 < len(list_months_temp):
            start_period = period
            end_period =  list_months_temp[pos+1]

            tickets_by_period = Ticket.tickets_by_queue_period(
                last_ticket_id,
                queue_id, 
                start_period,
                end_period
            )
            
            print(f"tickets_by_period {len(tickets_by_period)}")

            if not tickets_by_period:
                continue
            
            period_temp = datetime.strptime(period, "%Y-%m-%d")
            month = period_temp.month
            print(
                f"{def_name} Analizando datos del periodo"
                f"={start_period} al <{end_period}"
                f"--> {len(tickets_by_period)}"
            )
            
            for ticket in tickets_by_period:
                if ticket.customer_id not in customers_actives_temp:
                    continue
                
                if type_ == "customers":
                    type_temp = ticket.customer_id
                else:
                    type_temp = ticket.user_id

                if month not in active_temp:
                    active_temp[month] = {}
                if type_temp not in active_temp[month]:
                    active_temp[month][type_temp] = {}
                if ticket.id not in active_temp[month][type_temp]:
                    last_ticket_id_temp = ticket.id
                    if ticket.last_history:
                        resolution_time = ticket.last_history.change_time - ticket.create_time
                    else:
                        resolution_time = ""
                    active_temp[month][type_temp][ticket.id] = {
                        "tn": ticket.tn,
                        "title": ticket.title,
                        "user_id": ticket.user_id,
                        "customer_id": ticket.customer_id,
                        "service_id": ticket.service_id,
                        "state": ticket.ticket_state.name,
                        "type": ticket.type.name if ticket.type else "Undefined",
                        "ticket_priority": ticket.ticket_priority.name,
                        "sla": ticket.sla.solution_time if ticket.sla else "Undefined",
                        "create_time": str(ticket.create_time),
                        "change_time": str(ticket.change_time),
                        "resolution_time": str(resolution_time)
                    }
    
    _active = {
        "active": active_temp,
        "last_ticket_id": last_ticket_id_temp,
        "last_period": list_months_temp[-2]

    }
    
    with open(path_active, "w") as f:
        json_active = json.dumps(_active)
        f.write(json_active)

    return active_temp


def get_data_folder_temp_tickets_customer_administrators_queue():
    def_name = "get_data_folder_temp_tickets_customer_administrators_queue"
    """Obtener los datos de la función tickets_customer_administrators_queue
    por la carpeta temp se elimina"""
    
    list_years_temp = list(range(datetime.today().year,2018,-1))
    types_temp = ["customers", "administrators"]
    for type_temp in types_temp:
        for year in list_years_temp:
            tickets_queue(str(year), type_temp)
    
    return f"{def_name} Data actualizada en la carpeta temp"


##############################################################
#  2. Cantidad de tickets generados por Ofensas
##############################################################


def tickets_offenses(year: str, type_: str):
    def_name = f"tickets_offenses_{type_}"
    """Obtener los tickets de las ofensas manuales/automaticas 
    durante un año.
    
    Parameters:
    Year: str
        El año que se quiere analizar

    Return
    ------
    Dict[customer/user_id][Tickets]
        Una diccionario de clientes/usuario con los tickets asociados
    """
    customers_actives_temp = customers_actives()

    types_temp = ["automatic", 
                  "automatic_intervention_manual_user", 
                  "automatic_intervention_manual_customer",
                  "handwork_customers", 
                  "handwork_user"
                  ]
    if type_ in types_temp:
        path_active = Path(
            f"{path_temp}/tickets_offenses_{type_}_{year}.json"
        )
    
    else:
        return f"Tipo:{type_} --> Undefined"
   
    if path_active.exists():
        with path_active.open("r") as f:
            json_active = json.load(f)
            last_ticket_id = json_active["last_ticket_id"]
            start_date = json_active["last_period"]
            month_temp = datetime.strptime(start_date, "%Y-%m-%d")
            list_months_temp = list_months_year(month_temp.year)
            active_temp = json_active["active"]
    else:
        last_ticket_id = 45
        list_months_temp = list_months_year(year)
        active_temp = {}
    
    if type_ ==  "automatic":
        try:
            last_ticket_id_temp = Ticket.last_ticket_id_offense_automatic(
                list_months_temp[-2], 
                list_months_temp[-1]
            )
        except:
            last_ticket_id_temp=last_ticket_id
    elif type_ ==  "automatic_intervention_manual":
        try:
            last_ticket_id_temp = Ticket.last_ticket_id_offense_automatic_intervention_manual(
                list_months_temp[-2], 
                list_months_temp[-1]
            )
        except:
            last_ticket_id_temp=last_ticket_id
    else:
        try:
            last_ticket_id_temp = Ticket.last_ticket_id_offense_handwork(
                list_months_temp[-2], 
                list_months_temp[-1]
            )
        except:
            last_ticket_id_temp=last_ticket_id
    
    if not last_ticket_id_temp:
        print(f"NO HAY tickets del tipo {type_} en el año {year}")
        return active_temp

    print("Analizando", 
        def_name, 
        last_ticket_id, 
        last_ticket_id_temp, 
        list_months_temp
    )
    
    offense_id_repeated = []
    offense_id_temp = []
    if int(last_ticket_id) >= last_ticket_id_temp:
        return active_temp

    for pos, period in enumerate(list_months_temp):
        
        if pos+1 < len(list_months_temp):
            start_period = period
            end_period =  list_months_temp[pos+1]
    
            if type_ ==  "automatic":
                try:
                    tickets_by_period = Ticket.tickets_offenses_automatic_by_period(
                        last_ticket_id,
                        start_period, 
                        end_period
                    )
                except:
                    tickets_by_period = []
            elif type_ == "automatic_intervention_manual_user" or type_ == "automatic_intervention_manual_customer":
                try:
                    tickets_by_period = Ticket.tickets_offenses_automatic_intervention_manual_by_period(
                        last_ticket_id,
                        start_period, 
                        end_period
                    )
                except:
                    tickets_by_period = []
            else:
                try:
                    tickets_by_period = Ticket.tickets_offenses_handwork_by_period(
                        last_ticket_id,
                        start_period, 
                        end_period
                    )
                except:
                    tickets_by_period = []

            if not tickets_by_period:
                continue
            
            period_temp = datetime.strptime(period, "%Y-%m-%d")
            month = period_temp.month
            print(
                f"{def_name} Analizando datos del periodo"
                f"={start_period} al <{end_period}"
                f"--> {len(tickets_by_period)}"
            )
            
            for ticket in tickets_by_period:
                if ticket.customer_id not in customers_actives_temp:
                    continue
                
                offense_id = re.findall(r"\d{5,}", ticket.title)
                response_time = ""
                str_sla = ""
                start_time_qradar = ""
                if offense_id:
                    offense_id = offense_id[0]
                    if offense_id not in offense_id_temp:
                        offense_id_temp.append(offense_id)
                    else:
                        offense_id_repeated.append([
                            offense_id, 
                            ticket.tn, 
                            ticket.title
                        ])

                    start_time_qradar = qradar.start_time_offense(offense_id)
                    if start_time_qradar:
                        response_time = (ticket.create_time  + timedelta(hours=1)) - start_time_qradar
                        ideal_response_time = timedelta(minutes=15)
                        if response_time <= ideal_response_time:
                            str_sla = "Cumple"
                        else:
                            str_sla = "No Cumple"
                
                if type_ == "handwork_user" or type_ == "automatic_intervention_manual_user":
                    type_temp = ticket.user_id
                else:
                    type_temp = ticket.customer_id

                if month not in active_temp:
                    active_temp[month] = {}
                if type_temp not in active_temp[month]:
                    active_temp[month][type_temp] = {}
                if ticket.id not in active_temp[month][type_temp]:
                    last_ticket_id_temp = ticket.id
                    if ticket.last_history:
                        resolution_time = ticket.last_history.change_time - ticket.create_time
                    else:
                        resolution_time = ""
                    active_temp[month][type_temp][ticket.id] = {
                        "tn": ticket.tn,
                        "title": ticket.title,
                        "user_id": ticket.user_id,
                        "customer_id": ticket.customer_id,
                        "service_id": ticket.service_id,
                        "state": ticket.ticket_state.name,
                        "type": ticket.type.name if ticket.type else "Undefined",
                        "ticket_priority": ticket.ticket_priority.name,
                        "sla": ticket.sla.solution_time if ticket.sla else "Undefined",
                        "create_time": str(ticket.create_time),
                        "change_time": str(ticket.change_time),
                        "resolution_time": str(resolution_time),
                        "id_offense": offense_id if offense_id else "Undefined",
                        "response_time": str(response_time) if response_time else "Undefined",
                        "str_sla": str_sla if str_sla else "Undefined",
                        "start_time_qradar": str(start_time_qradar)
                    }
                
    _active = {
        "active": active_temp,
        "last_ticket_id": last_ticket_id_temp,
        "last_period": list_months_temp[-2],
        "offense_id_repeated": offense_id_repeated
    }
    
    with open(path_active, "w") as f:
        json_active = json.dumps(_active)
        f.write(json_active)

    return active_temp


def get_data_folder_temp_tickets_offenses():
    def_name = "get_data_folder_temp_tickets_offenses"
    """Obtener los datos de la función tickets_offenses
    por si la carpeta temp se elimina"""
    
    list_years_temp = list(range(datetime.today().year,2018,-1))
    types_temp = ["automatic",
                  "automatic_intervention_manual",
                  "automatic_intervention_manual_customer", 
                  "handwork_customers",
                  "handwork_user"
                  ]
    for type_temp in types_temp:
        for year in list_years_temp:
            tickets_offenses(str(year), type_temp)
    
    return f"{def_name} Data actualizada en la carpeta temp"


def update_data():
    init_tools()
    get_data_folder_temp_tickets_customer_administrators_queue() 
    get_data_folder_temp_tickets_offenses()

    print("Data de la carpeta temp actualizada")

# update_data()