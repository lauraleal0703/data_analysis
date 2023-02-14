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

import json
from pprint import pprint
from pathlib import Path
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta


path_analyzer = Path(__file__).parent
path_temp = Path(f"{path_analyzer}/temp_otrs_data_tickets")
if not path_temp.exists():
    path_temp.mkdir()



#########################################
##########Funciones de apoyo#############
##########################################


def list_months_year(year, month: str=None):
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
    if month:
        date = f"{year}-{month}-1"
    
    month_temp = datetime.strptime(date, "%Y-%m-%d")
    list_months_active = [month_temp.strftime("%Y-%m-%d")]

    if int(year) < end_date.year:
        while True:
            month_temp=month_temp+relativedelta(months=1)
            list_months_active.append(month_temp.strftime("%Y-%m-%d"))
            if month_temp.month == 12:
                month_temp=month_temp+relativedelta(months=1)
                list_months_active.append(month_temp.strftime("%Y-%m-%d"))
                break
    else:
        while True:
            month_temp=month_temp+relativedelta(months=1)
            list_months_active.append(month_temp.strftime("%Y-%m-%d"))
            if month_temp.month == end_date.month:
                break
            month_temp=month_temp
            
    return list_months_active


def list_date(start: str, end: str):
    """Obtener una lista con los dias a analizar
    Parameters
    ---------
    start:str
        El dia de inicio del cual se quiere hacer el análisis.
    end:str
        El dia de fin hasta el cual se quiere hacer el análisis.
    
    Return
    ------
    List(days)
        Una lista de dias
    """

    start = datetime.strptime(start, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")
    today_temp = datetime.today()
    if end > today_temp:
        end = today_temp + timedelta(days=1)
    
    lista_fechas = [str(start + timedelta(days=d)).split(" ")[0] for d in range((end - start).days)]
    
    return lista_fechas


###############################################
########## Funciones de limpieza ##############
###############################################


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


def customers_() -> dict:
    """Obtener un diciconario con id de los clientes
    y su nombre asociado.
    Se elimino al cliente EJEMPLO
    Se elimino el cliente BFAL porque tiene un solo ticket
    
    Return
    ------
    {id: name}
        Un diccionario de clientes
    """
    customers = CustomerCompany.all()

    return {
        customer.customer_id: customer.name for customer in customers 
        if customer.customer_id != "EJEMPLO" 
        and customer.customer_id != "BFAL"
    }


def customers_by_queue(queue_id: int, customer_id: str=None) -> dict:
    """Obtener un diciconario con id de los clientes
    y las fechas en las que han estado activos en AS
    durante los ultimos 3 meses
    
    Parameters
    ----------
    queue_id: int
        La cola de los tickets
        *queue_id=6 son los tickets administrativos
    
    Return
    ------
    {id: 
        "start": "%Y-%m-%d", 
        "end": "%Y-%m-%d"
        "years_actives": [year]}
        
        Un diccionario de clientes
    """
    
    customers_temp = customers_()
    customers_actives_temp  = {}
    for customer in customers_temp:
        start_ticket = Ticket.ticktets_filtered_with(
            queue_id = queue_id,
            customer_id = customer,
            first_id = True
        )
        if start_ticket:
            start_day = start_ticket.create_time
            end_ticket = Ticket.ticktets_filtered_with(
                queue_id = queue_id,
                customer_id = customer,
                last_id = True
            )
            end_day = end_ticket.create_time
            end_day_limit = datetime.today() - relativedelta(months=3)
            if end_day < end_day_limit:
                continue
            list_year_temp = [int(start_day.year)]
            if start_day.year < end_day.year:
                year_init = int(start_day.year)
                while True:
                    next_year = year_init+1
                    list_year_temp.append(next_year)
                    if next_year == int(end_day.year):
                        break
                    year_init = next_year 
            customers_actives_temp[customer] = {
                "start": datetime.strftime(start_day, "%Y-%m-%d"),
                "end": datetime.strftime(end_day, "%Y-%m-%d"),
                "years_actives":  sorted(list_year_temp)
            }
    
    if customer_id:
        return customers_actives_temp[customer_id]
    else:
        return customers_actives_temp


def users_actives():
    """Obtener un diciconario con los usuarios
    
    Return
    ------
    {id: user_id_active.full_name}
        Una diccionario de user_id_active
    """
    users = User.all()

    return {user.id: user.full_name for user in users}


def users_administrators():
    """ A hoy 08/02/2023 los usuaios administradores son:
    Jose Nicolas user_id = 12
    Pedro Cerpa C. user_id = 34
    Andres Rojas user_id = 47
    Miguel Almendra user_id = 52
    Solange Aravena user_id = 53
    Miguel Gonzalez user_id = 59
    Diego Orellana user_id = 63
    Todos los tickets con cola=6, deben estar asociado a uno de ellos
    """
    admin = [12, 34, 47, 52, 53, 59, 63]

    return admin


def users_analysts():
    """ A hoy 08/02/2023 los usuaios administradores son:
    Francisco Sepulveda user_id = 29
    Jonathan Finschi user_id =45
    Cristopher Ulloa user_id = 54
    Sugy Nam user_id = 56
    Mauricio Retamales user_id = 64
    Nicolas Garrido user_id = 65
    
    Todos los tickets con cola=9, deben estar asociado a uno de ellos
    """
    analysts = [29, 45, 54, 56, 64, 65]
    
    return analysts


def init_cleaning_functions():
    def_name = "init_cleaning_functions"
    funs_def = [
        calendar_spanish,
        customers_,
        users_actives
    ]
    funs_name = [
        "calendar_spanish",
        "customers_",
        "users_actives"
    ]

    for pos, fun_def in  enumerate(funs_def):
        _active = { 
            "active": fun_def(),
            "update_date": datetime.today().strftime("%d-%m-%Y %H:%M:%S")
        }
        path_active = Path(f"{path_temp}/{funs_name[pos]}.json")
        with open(path_active, "w") as f:
            json_active = json.dumps(_active)
            f.write(json_active)
    
    print(f"{def_name} OK")


########################################## 
##########Funciones de Análisis###########
##########################################


def sla_tickets(combinations: dict, historys: list):
    """Llenar el diccionario con los diferentes
    estados de un ticket"""
    quantity = len(historys)
    name_temp = ""
    for pos, history in enumerate(historys):
        name_filtered = history.name.split("%%")[1:3]
        name_filtered = " TO ".join(name_filtered)
        if pos > 0:
            name_temp += " -> " + name_filtered
        else:
            name_temp += name_filtered
    if name_temp not in combinations:
        combinations[name_temp] = (quantity, history.ticket_id)

    # combinations[name_temp] = (quantity, history.ticket_id)


def add_ticket_queue(active_temp, ticket, month, day, resolution_time):
    """Agregar el ticket al camino correspondiente"""
    
    if ticket.customer_id not in active_temp:
        active_temp[ticket.customer_id] = {}
    
    if ticket.user_id not in active_temp:
        active_temp[ticket.user_id] = {}

    if month not in active_temp[ticket.customer_id]:
        active_temp[ticket.customer_id][month] = {}
    
    if month not in active_temp[ticket.user_id]:
        active_temp[ticket.user_id][month] = {}

    if day not in active_temp[ticket.customer_id][month]:
        active_temp[ticket.customer_id][month][day] = {}
    
    if day not in active_temp[ticket.user_id][month]:
        active_temp[ticket.user_id][month][day] = {}
    
    ticket_data = {
        "tn": ticket.tn,
        "title": ticket.title,
        "user_id": ticket.user_id,
        "responsible_user_id": ticket.responsible_user_id,
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

    active_temp[ticket.customer_id][month][day][ticket.id] = ticket_data
    active_temp[ticket.user_id][month][day][ticket.id] = ticket_data


def tickets_by_queue(
        year: str, 
        queue_id: int,
        customers_actives: list, 
        users_actives: list
    )-> dict:
    def_name = f"tickets_by_queue_{queue_id}_{year}"
    """Obtener todos los tickets de una cola en un año dado

    Parameters
    ----------
    path_temp: Path
        Dirección donde se guardaran los datos

    Return
    ------
    Dict[customer_id/queue=6][Tickets]
        Un diccionario de tickets asociados al cliente
    """

    path_queue_id = Path(f"{path_temp}/queue_id_{queue_id}")

    if not path_queue_id.exists():
        path_queue_id.mkdir()
    
    path_active = Path(f"{path_queue_id}/tickets_by_{year}.json")

    if path_active.exists():
        with path_active.open("r") as f:
            json_active = json.load(f)
            last_ticket_id = json_active["last_ticket_id"]
            init_date = datetime.strptime(json_active["last_day"], "%Y-%m-%d")
            list_months_temp = list_months_year(init_date.year, init_date.month)
            active_temp = json_active["active"]
            combinations_sla = json_active["combinations_sla"]
    else:
        last_ticket_id = 45
        list_months_temp = list_months_year(year)
        active_temp = {}
        combinations_sla = {}
    
    last_ticket = Ticket.ticktets_filtered_with(queue_id=queue_id, last_id=True)
    last_ticket_id_temp = last_ticket.id
    
    print("\nAnalizando", def_name, last_ticket_id, last_ticket_id_temp, 
        list_months_temp[-2], list_months_temp[-1])
    
    if int(last_ticket_id) == last_ticket_id_temp:
        return active_temp
    
    for pos, period in enumerate(list_months_temp):
        if pos+1 < len(list_months_temp):
            month = ""
            total_month = 0
            list_date_temp = list_date(period, list_months_temp[pos+1])
            
            for pos, date_temp in enumerate(list_date_temp):
                total_day = 0
                date_temp_format = datetime.strptime(date_temp, "%Y-%m-%d")
                
                tickets_by_period = Ticket.ticktets_filtered_with(
                    last_ticket_id = last_ticket_id,
                    queue_id = queue_id, 
                    day = date_temp
                )

                print(f"{def_name} Analizando datos del día {date_temp}"
                    f"--> {len(tickets_by_period)}")
                
                month = date_temp_format.month
                day = date_temp_format.day
                
                if not tickets_by_period:
                    continue

                for ticket in tickets_by_period:
                    
                    if ticket.customer_id not in customers_actives:
                        continue
                    
                    if ticket.user_id not in users_actives:
                        if "not_corresponding_user" not in active_temp:
                            active_temp["not_corresponding_user"] = {}
                        
                        active_temp["not_corresponding_user"][ticket.id] = {
                            "tn": ticket.tn,
                            "title": ticket.title,
                            "user_id": ticket.user_id,
                            "user_name": ticket.user.full_name,
                            "create_time": str(ticket.create_time),
                        }
                        continue

                    if "total_year" not in active_temp:
                        active_temp["total_year"] = 1
                    else:
                        active_temp["total_year"] += 1
                    
                    total_month += 1
                    total_day += 1
                    last_ticket_id_temp = ticket.id

                    if  ticket.historys:
                        sla_tickets(combinations_sla, ticket.historys)
                    
                    if ticket.last_history:
                        resolution_time = ticket.last_history.create_time - ticket.create_time
                    else:
                        resolution_time = ticket.change_time - ticket.create_time
                    
                    add_ticket_queue(active_temp, ticket, month, day, resolution_time)
                
                name_month_temp = f"total_month_{month}"
                if name_month_temp not in active_temp:
                    active_temp[name_month_temp] = {}
                if day not in active_temp[name_month_temp]:
                    active_temp[name_month_temp][day] = total_day
                else:
                    active_temp[name_month_temp][day] += total_day

            name_temp = "total_months" 
            if name_temp not in active_temp:
                active_temp[name_temp] = {}
            if month not in active_temp[name_temp]:
                active_temp[name_temp][month] = total_month
            else:
                active_temp[name_temp][month] += total_month

    
    combinations_sla_ = sorted(combinations_sla.items(), key=lambda x:x[1])
    _active = {
        "active": active_temp,
        "last_ticket_id": last_ticket_id_temp,
        "last_day": date_temp,
        "combinations_sla": combinations_sla,
        "combinations_sla_order": combinations_sla_
    }
    
    with open(path_active, "w") as f:
        json_active = json.dumps(_active)
        f.write(json_active)


def tickets_by_user(
        type_: str,
        year: str,
        customers_actives: list, 
        user_id:  int,
        queue_id: int
    )-> dict:
    def_name = f"tickets_by_user_id_{user_id}_{year}"
    """Obtener todos los tickets de un usuario en un
    año dado

    Parameters
    ----------
    path_temp: Path
        Dirección donde se guardaran los datos

    Return
    ------
    Dict[user_id][Tickets]
        Un diccionario de tickets asociados al usuario
    """

    path_user = Path(f"{path_temp}/user_{type_}")

    if not path_user.exists():
        path_user.mkdir()
    
    path_active = Path(f"{path_user}/tickets_by_user_id_{user_id}_{year}.json")

    if path_active.exists():
        with path_active.open("r") as f:
            json_active = json.load(f)
            last_ticket_id = json_active["last_ticket_id"]
            init_date = datetime.strptime(json_active["last_day"], "%Y-%m-%d")
            list_months_temp = list_months_year(init_date.year, init_date.month)
            active_temp = json_active["active"]
    else:
        last_ticket_id = 45
        list_months_temp = list_months_year(year)
        active_temp = {}
    
    last_ticket = Ticket.ticktets_filtered_with(user_id = user_id, last_id = True)
    last_ticket_id_temp = last_ticket.id
    
    print("\nAnalizando", def_name, last_ticket_id, last_ticket_id_temp, 
        list_months_temp[-2], list_months_temp[-1])
    
    if int(last_ticket_id) == last_ticket_id_temp:
        return active_temp
    
    for pos, period in enumerate(list_months_temp):
        if pos+1 < len(list_months_temp):
            list_date_temp = list_date(period, list_months_temp[pos+1])
            
            for pos, date_temp in enumerate(list_date_temp):
                
                tickets_by_period = Ticket.ticktets_filtered_with(
                    last_ticket_id = last_ticket_id,
                    user_id = user_id, 
                    day = date_temp
                )

                print(f"{def_name} Analizando datos del día {date_temp}"
                    f"--> {len(tickets_by_period)}")
                
                if not tickets_by_period:
                    continue

                for ticket in tickets_by_period:
                    if ticket.customer_id not in customers_actives:
                        continue
                    queue_id_temp = ticket.queue_id
                    if queue_id_temp == queue_id:
                        continue
    
                    if queue_id_temp not in active_temp:
                        active_temp[queue_id_temp] = {}
                    active_temp[queue_id_temp][ticket.id] = {
                        "title": ticket.title,
                        "tn": ticket.tn,
                        "create_time": str(ticket.create_time)
                    }
    _active = {
        "active": active_temp,
        "last_ticket_id": last_ticket_id_temp,
        "last_day": date_temp
    }
    
    with open(path_active, "w") as f:
        json_active = json.dumps(_active)
        f.write(json_active)


def add_ticket_customer(active_temp, ticket, month, day, resolution_time):
    """Agregar el ticket al camino correspondiente"""
    
    if ticket.customer_id not in active_temp:
        active_temp[ticket.customer_id] = {}
    
    if month not in active_temp[ticket.customer_id]:
        active_temp[ticket.customer_id][month] = {}

    if day not in active_temp[ticket.customer_id][month]:
        active_temp[ticket.customer_id][month][day] = {}
    
    ticket_data = {
        "tn": ticket.tn,
        "title": ticket.title,
        "user_id": ticket.user_id,
        "responsible_user_id": ticket.responsible_user_id,
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

    active_temp[ticket.customer_id][month][day][ticket.id] = ticket_data


def tickets_by_customer(
        year: str, 
        queue_id: int,
        customer_id: str, 
        users_actives: list
    )-> dict:
    def_name = f"tickets_by_{customer_id}_queue_{queue_id}_{year}"
    """Obtener todos los tickets de una cola en un año dado

    Parameters
    ----------
    path_temp: Path
        Dirección donde se guardaran los datos

    Return
    ------
    Dict[customer_id/queue=6][Tickets]
        Un diccionario de tickets asociados al cliente
    """

    path_customer_id = Path(f"{path_temp}/{customer_id}")

    if not path_customer_id.exists():
        path_customer_id.mkdir()
    
    path_active = Path(f"{path_customer_id}/tickets_by_queue_id_{queue_id}_{year}.json")

    if path_active.exists():
        with path_active.open("r") as f:
            json_active = json.load(f)
            last_ticket_id = json_active["last_ticket_id"]
            init_date = datetime.strptime(json_active["last_day"], "%Y-%m-%d")
            list_months_temp = list_months_year(init_date.year, init_date.month)
            active_temp = json_active["active"]
            combinations_sla = json_active["combinations_sla"]
    else:
        last_ticket_id = 45
        list_months_temp = list_months_year(year)
        active_temp = {}
        combinations_sla = {}
    
    last_ticket = Ticket.ticktets_filtered_with(
        queue_id=queue_id,
        customer_id=customer_id,
        last_id=True)
    last_ticket_id_temp = last_ticket.id
    
    print("\nAnalizando", def_name, last_ticket_id, last_ticket_id_temp, 
        list_months_temp[-2], list_months_temp[-1])
    
    if int(last_ticket_id) == last_ticket_id_temp:
        return active_temp
    
    for pos, period in enumerate(list_months_temp):
        if pos+1 < len(list_months_temp):
            month = ""
            total_month = 0
            list_date_temp = list_date(period, list_months_temp[pos+1])
            
            for pos, date_temp in enumerate(list_date_temp):
                total_day = 0
                date_temp_format = datetime.strptime(date_temp, "%Y-%m-%d")
                
                tickets_by_period = Ticket.ticktets_filtered_with(
                    last_ticket_id = last_ticket_id,
                    queue_id = queue_id,
                    customer_id=customer_id, 
                    day = date_temp
                )

                print(f"{def_name} Analizando datos del día {date_temp}"
                    f"--> {len(tickets_by_period)}")
                
                month = date_temp_format.month
                day = date_temp_format.day
                
                if not tickets_by_period:
                    continue

                for ticket in tickets_by_period:
                    
                    if ticket.user_id not in users_actives:
                        if "not_corresponding_user" not in active_temp:
                            active_temp["not_corresponding_user"] = {}
                        
                        active_temp["not_corresponding_user"][ticket.id] = {
                            "tn": ticket.tn,
                            "title": ticket.title,
                            "user_id": ticket.user_id,
                            "user_name": ticket.user.full_name,
                            "create_time": str(ticket.create_time),
                        }
                        continue

                    if "total_year" not in active_temp:
                        active_temp["total_year"] = 1
                    else:
                        active_temp["total_year"] += 1
                    
                    total_month += 1
                    total_day += 1
                    last_ticket_id_temp = ticket.id
                    
                    if  ticket.historys:
                        sla_tickets(combinations_sla, ticket.historys)
                    
                    if ticket.last_history:
                        resolution_time = ticket.last_history.create_time - ticket.create_time
                    else:
                        resolution_time = ticket.change_time - ticket.create_time
                    
                    add_ticket_customer(active_temp, ticket, month, day, resolution_time)
                
                name_month_temp = f"total_month_{month}"
                if name_month_temp not in active_temp:
                    active_temp[name_month_temp] = {}
                if day not in active_temp[name_month_temp]:
                    active_temp[name_month_temp][day] = total_day
                else:
                    active_temp[name_month_temp][day] += total_day

            name_temp = "total_months" 
            if name_temp not in active_temp:
                active_temp[name_temp] = {}
            if month not in active_temp[name_temp]:
                active_temp[name_temp][month] = total_month
            else:
                active_temp[name_temp][month] += total_month
    

    combinations_sla_ = sorted(combinations_sla.items(), key=lambda x:x[1])
    _active = {
        "active": active_temp,
        "last_ticket_id": last_ticket_id_temp,
        "last_day": date_temp,
        "combinations_sla": combinations_sla,
        "combinations_sla_order": combinations_sla_
    }
    
    with open(path_active, "w") as f:
        json_active = json.dumps(_active)
        f.write(json_active)


def get_tickets_():
    def_name = "get_tickets_by_queue"
    """Obtener los datos de la función tickets_by_queue
    por si la carpeta temp_otrs_data_tickets se elimina
    o se quiere actualizar"""
    
    queues_id = [6, 9]
    years = ["2023", "2022"]
    years = ["2023"]
    for queue_id in queues_id:
        customers_actives = customers_by_queue(queue_id=queue_id)
        if queue_id == 6:
            users_actives = users_administrators()
        if queue_id == 9:
            users_actives = users_analysts()
        for year in years:
            tickets_by_queue(
                year=year, 
                queue_id=queue_id, 
                customers_actives=customers_actives, 
                users_actives=users_actives
            )
    
    # types_ = ["administrators", "analysts"]
    # years = ["2023", "2022"]
    # years = ["2023"]
    # for type_ in types_:
    #     customers_actives = list(customers_().keys())
    #     if type_ == "administrators":
    #         users_actives = users_administrators()
    #         queue_id = 6
    #     if type_ == "analysts":
    #         users_actives = users_analysts()
    #         queue_id = 9
    #     for user_id in users_actives:
    #         for year in years:
    #             tickets_by_user(
    #                 type_=type_,
    #                 year=year,
    #                 customers_actives=customers_actives, 
    #                 user_id=user_id,
    #                 queue_id=queue_id
    #             )

    
    # queues_id = [6, 9]
    # years = ["2023", "2022"]
    # years = ["2023"]
    # for queue_id in queues_id:
    #     customers_actives = customers_by_queue(queue_id=queue_id)
    #     if queue_id == 6:
    #         users_actives = users_administrators()
    #     if queue_id == 9:
    #         users_actives = users_analysts()
    #     for customer_id in customers_actives:
    #         for year in years:
    #             tickets_by_customer(
    #                 year=year, 
    #                 queue_id=queue_id, 
    #                 customer_id=customer_id, 
    #                 users_actives=users_actives
    #             )
    
    return f"{def_name} Data actualizada en la carpeta temp_otrs_data_tickets"


def update_data():
    init_cleaning_functions()
    get_tickets_()
    print("Data de la carpeta temp_portal_clientes actualizada")

# update_data()


def dic_sla(path_temp):
    def_name = "dic_sla"
    dict_sla = {}
    queues_id = [6, 9]
    years = ["2023", "2022"]
    years = ["2023"]
    for queue_id in queues_id:
        for year in years:
            path_queue_id = Path(f"{path_temp}/queue_id_{queue_id}")
            path_active = Path(f"{path_queue_id}/tickets_by_{year}.json")

            if path_active.exists():
                with path_active.open("r") as f:
                    json_active = json.load(f)
                    combinations_sla = json_active["combinations_sla_order"]
                    print(len(combinations_sla))
                    for combinations in combinations_sla:
                        if combinations[0] not in dict_sla:
                            dict_sla[combinations[0]] = combinations[1]
    

    dict_sla_ = sorted(dict_sla.items(), key=lambda x:x[1])
    _active = { 
        "active": dict_sla,
        "active_order": dict_sla_,
        "update_date": datetime.today().strftime("%d-%m-%Y %H:%M:%S")
    }
    
    path_active = Path(f"{path_temp}/{def_name}.json")
    with open(path_active, "w") as f:
        json_active = json.dumps(_active)
        f.write(json_active)
    
    print(len(dict_sla))
    
    return dict_sla

# dic_sla(path_temp)