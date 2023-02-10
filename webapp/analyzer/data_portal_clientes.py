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
path_temp = Path(f"{path_analyzer}/temp_data_portal_clientes")
if not path_temp.exists():
    path_temp.mkdir()



#########################################
##########Funciones de apoyo#############
##########################################

def list_months_year(year):
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


def customers_actives() -> dict:
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


def customers_by_period(queue_id: int=6, customer_id: str=None) -> dict:
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
    
    customers_temp = customers_actives()
    customers_actives_temp  = {}
    for customer in customers_temp:
        start_ticket = Ticket.first_ticket_customer_(queue_id, customer)
        if start_ticket:
            start_day = start_ticket.create_time
            end_ticket = Ticket.last_ticket_customer_(queue_id, customer)
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


def init_cleaning_functions():
    def_name = "init_cleaning_functions"
    funs_def= [
        calendar_spanish,
        customers_actives,
        customers_by_period]
    funs_name = [
        "calendar_spanish",
        "customers_actives",
        "customers_by_period"]

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


##########################################
##########Funciones de Análisis###########
##########################################


def tickets_customer(customer_id: str, year: str, queue_id: int=6):
    def_name = f"tickets_{customer_id}_{year}_by_queue_{queue_id}"
    """Obtener todos los tickets de un cliente
    con filtros de cola.

    Parameters
    ----------
    path_temp: Path
        Dirección donde se guardaran los datos

    Return
    ------
    Dict[customer_id/queue=6][Tickets]
        Un diccionario de tickets asociados al cliente
    """

    customer_temp = customers_by_period(customer_id=customer_id)
    
    path_customer = Path(
        f"{path_temp}/{customer_id}"
    )

    if not path_customer.exists():
        path_customer.mkdir()
    
    path_active = Path(
        f"{path_customer}/tickets_{customer_id}_by_queue_{queue_id}_{year}.json"
    )

    if path_active.exists():
        with path_active.open("r") as f:
            json_active = json.load(f)
            last_ticket_id = json_active["last_ticket_id"]
            start_date = json_active["last_period"]
            init_customer = datetime.strptime(start_date, "%Y-%m-%d")
            list_months_temp = list_months_year(init_customer.year)
            active_temp = json_active["active"]
    else:
        last_ticket_id = 45
        list_months_temp = list_months_year(year)
        active_temp = {}
        init_customer = datetime.strptime(customer_temp["start"], "%Y-%m-%d")
    
    try:
        last_ticket_id_temp = Ticket.last_ticket_id_customer_queue_period(
            queue_id,
            customer_id, 
            list_months_temp[-2], 
            list_months_temp[-1]
        )
    except:
        last_ticket_id_temp=last_ticket_id
    
    print("Analizando", 
        def_name, 
        last_ticket_id, 
        last_ticket_id_temp, 
        list_months_temp[-2], 
        list_months_temp[-1]
    )
    
    if int(last_ticket_id) >= last_ticket_id_temp:
        return active_temp
    

    for pos, period in enumerate(list_months_temp):
        if pos+1 < len(list_months_temp):
            month = ""
            total_month = 0
            list_date_temp = list_date(period, list_months_temp[pos+1])
            for pos, date_temp in enumerate(list_date_temp):
                total_day = 0
                date_temp_format = datetime.strptime(date_temp, "%Y-%m-%d")
                if date_temp_format < init_customer:
                    continue
                try:
                    tickets_by_period = Ticket.tickets_by_id_customer(
                        last_ticket_id,
                        queue_id,
                        customer_id, 
                        date_temp,
                        date_temp
                    )
                except:
                    tickets_by_period = []

                total_month += len(tickets_by_period)
                total_day += len(tickets_by_period)
                
                print(
                    f"{def_name} Analizando datos del día {date_temp}"
                    f"--> {len(tickets_by_period)}"
                )
                
                month = date_temp_format.month
                day = date_temp_format.day
                
                if "total_year" not in active_temp:
                    active_temp["total_year"] = len(tickets_by_period)
                else:
                    active_temp["total_year"] += len(tickets_by_period)
                
                if month not in active_temp:
                    active_temp[month] = {}
                
                if day not in active_temp[month]:
                    active_temp[month][day] = {}

                for ticket in tickets_by_period:
                    last_ticket_id_temp = ticket.id
                    resolution_time = ticket.last_history.change_time - ticket.create_time
                    active_temp[month][day][ticket.id] = {
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
                
                if "total_day" not in active_temp[month][day]:
                    active_temp[month][day]["total_day"] = total_day
                else:
                    active_temp[month][day]["total_day"] += total_day
            
            if month and month in active_temp:
                if "total_month" not in active_temp[month]:
                    active_temp[month]["total_month"] = total_month
                else:
                    active_temp[month]["total_month"] += total_month

    _active = {
        "active": active_temp,
        "last_ticket_id": last_ticket_id_temp,
        "last_period": list_months_temp[-2],
    }
    
    with open(path_active, "w") as f:
        json_active = json.dumps(_active)
        f.write(json_active)

    return active_temp


def get_data_folder_temp_portal_clientes():
    def_name = "get_data_folder_temp_portal_clientes"
    """Obtener los datos de la función tickets_customer
    por si la carpeta temp_portal_clientes se elimina"""
    
    customers = customers_by_period()
    
    for customer in customers:
        years = customers[customer]["years_actives"]
        years.reverse()
        years = [years[0]]
        for year in years:
            tickets_customer(customer, str(year))
    
    return f"{def_name} Data actualizada en la carpeta temp_portal_clientes"


def update_data():
    init_cleaning_functions()
    get_data_folder_temp_portal_clientes()
    print("Data de la carpeta temp_portal_clientes actualizada")

# update_data()