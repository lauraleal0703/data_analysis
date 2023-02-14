try:
    from .otrs.models import db
    from .otrs.models.ticket import Ticket
    from .otrs.models.customer_company import CustomerCompany
    from .qradar import qradar
except:
    from otrs.models import db
    from otrs.models.ticket import Ticket
    from otrs.models.customer_company import CustomerCompany
    from qradar import qradar


from pprint import pprint
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta


#####################################################
##########Funciones de Obtención de datos ###########
#####################################################

def calendar_spanish():
    def_name = "calendar_spanish"
    print(def_name, datetime.today())
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

    print(def_name, datetime.today())
    return {pos+1: month for pos, month in enumerate(months)}


def customers_actives() -> dict:
    def_name = "customers_actives"
    print(def_name, datetime.today())
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

    print(def_name, datetime.today())
    return {
        customer.customer_id: customer.name for customer in customers 
        if customer.customer_id != "EJEMPLO" 
        and customer.customer_id != "BFAL"
    }


def customers_by_period(
        queue_id: int, 
        customer_id: str=None
    ) -> dict:
    def_name = "customers_by_period"
    print(def_name, datetime.today())
    """Obtener un diciconario con id de los clientes
    y las fechas en las que han estado activos en AS
    Se toman los activos de los ultimos 3 meses
    
    Parameters
    ----------
    queue_id: int
        ID de la cola
    customer_id: int
        ID del cliente
    
    Return
    ------
    {customer_id: 
        "name": str,
        "start": "%Y-%m-%d", 
        "end": "%Y-%m-%d"
        "years_actives": [year]}
        
        Un diccionario de clientes/cliente
    """
    customers_actives_temp  = {}
    customers_temp = customers_actives()
    
    if not customer_id:
        for customer in customers_temp:
            start_ticket = Ticket.first_ticket_customer(queue_id, customer)
            if start_ticket:
                start_day = start_ticket.create_time
                end_ticket = Ticket.last_ticket_customer(queue_id, customer)
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
                    "name": customers_temp[customer],
                    "start": datetime.strftime(start_day, "%Y-%m-%d"),
                    "end": datetime.strftime(end_day, "%Y-%m-%d"),
                    "years_actives":  sorted(list_year_temp)
                }

        print(def_name, datetime.today())
        return customers_actives_temp
    
    start_ticket = Ticket.first_ticket_customer(queue_id, customer_id)
    if start_ticket:
        start_day = start_ticket.create_time
        end_ticket = Ticket.last_ticket_customer(queue_id, customer_id)
        end_day = end_ticket.create_time
        list_year_temp = [int(start_day.year)]
        if start_day.year < end_day.year:
            year_init = int(start_day.year)
            while True:
                next_year = year_init+1
                list_year_temp.append(next_year)
                if next_year == int(end_day.year):
                    break
                year_init = next_year 
        customers_actives_temp = {
            "name": customers_temp[customer_id],
            "start": datetime.strftime(start_day, "%Y-%m-%d"),
            "end": datetime.strftime(end_day, "%Y-%m-%d"),
            "years_actives":  sorted(list_year_temp)
        }
   
    print(def_name, datetime.today())
    return customers_actives_temp

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


def get_tickets_customer_years(
        customer_id: str,
        queue_id: int
    ) -> dict:
    def_name = "get_tickets_customer_years"
    print(def_name, datetime.today())
    """Obtener los datos de los años activos de un customer_id
    en una cola dada.
    
    Da los datos directos para la gráfica.
    https://www.highcharts.com/demo/column-basic

    Parameters
    ----------
    queue_id: int
        ID de la cola
    customer_id: int
        ID del cliente
    
    Return
    ------
    dict
    """
    if queue_id == 6:
        users =  users_administrators()
    if queue_id == 9:
        users = users_analysts

    customer = customers_by_period(
        queue_id = queue_id,
        customer_id=customer_id
    )
    years = customer["years_actives"]
    years.reverse()
    customer_name = customer["name"]

    data_grah_temp = []
    data_x = []
    data_total = {}
    data_tickets = {}
    data_user_total = {}
    data_user_not_total = {}
    data_user = {}
    data_service_total = {}
    data_service = {}
    for year in years:
        data_x.append(year)
        data_temp = Ticket.ticktets_filtered_with(
            start_period = f"{year}-01-01",
            end_period = f"{year}-12-31", 
            customer_id = customer_id, 
            queue_id = queue_id
        )
        
        data_grah_temp.append(len(data_temp))
        data_total[year] = len(data_temp)
        data_tickets[year] = data_temp

        data_user_total[year] = {}
        data_user_not_total[year] = {}
        data_user[year] = {}
        data_service_total[year] = {}
        data_service[year] = {}

        for ticket in data_temp:
            if ticket.user_id not in users:
                if "user_not" not in data_user[year]:
                    data_user[year]["user_not"] = {}
                if ticket.user_id not in data_user[year]["user_not"]:
                    data_user_not_total[year][ticket.user_id] =  {
                        "user": {
                            "name": ticket.user.full_name
                        },
                        "total": 1
                    }
                    data_user[year]["user_not"][ticket.user_id] = {
                        "user": {
                            "name": ticket.user.full_name
                        },
                        "tickets": [ticket]
                    }
                    
                else:
                    data_user[year]["user_not"][ticket.user_id]["tickets"].append(ticket)
                    data_user_not_total[year][ticket.user_id]["total"] += 1
            
            else:  
                if ticket.user_id not in data_user[year]:
                    data_user_total[year][ticket.user_id] = {
                        "user": {
                            "name": ticket.user.full_name
                        },
                        "total": 1
                    }
                    data_user[year][ticket.user_id] = {
                        "user": {
                            "name": ticket.user.full_name
                        },
                        "tickets": [ticket]
                    }
                else:
                    data_user[year][ticket.user_id]["tickets"].append(ticket)
                    data_user_total[year][ticket.user_id]["total"] += 1


            if ticket.service_id not in data_service[year]:
                data_service_total[year][ticket.service_id] = {
                    "service": {
                            "name": ticket.service.name if ticket.service else "Undefined"
                        },
                    "total": 1
                }
                data_service[year][ticket.service_id] = {
                    "service": {
                        "name": ticket.service.name if ticket.service else "Undefined"
                    },
                    "tickets": [ticket]
                }
            else:
                data_service[year][ticket.service_id]["tickets"].append(ticket)
                data_service_total[year][ticket.service_id]["total"] += 1
    
    total_tickets = sum(data_grah_temp)
    data_grah = [{"name": "Tickets", "data": data_grah_temp}]
    
    print(def_name, datetime.today())
    db.session.commit()
    return {
        "customer_name": customer_name,
        "data_total": data_total,
        "data_tickets": data_tickets,
        "data_service": data_service,
        "data_service_total": data_service_total, 
        "data_x": data_x, 
        "data_y": data_grah, 
        "total_tickets": total_tickets,
        "data_user": data_user,
        "data_user_total": data_user_total,
        "data_user_not_total": data_user_not_total
    }


def get_tickets_customer_months_year(
        customer_id: str,
        queue_id: int,
        year: str
    ) -> dict:
    def_name = "get_tickets_customer_months_year"
    print(def_name, datetime.today())
    """Obtener los datos de los meses de un año de un customer_id
    en una cola dada.
    
    Da los datos directos para la gráfica.
    https://www.highcharts.com/demo/column-basic

    Parameters
    ----------
    queue_id: int
        ID de la cola
    customer_id: int
        ID del cliente
    year:
        Año de estudio
    
    Return
    ------
    dict{}
    """
    if queue_id == 6:
        users =  users_administrators()
    if queue_id == 9:
        users = users_analysts

    calendar = calendar_spanish()
    customer = customers_by_period(
        queue_id = queue_id,
        customer_id=customer_id
    )
    customer_name = customer["name"]

    data_total = {}
    data_tickets = {}
    data_user = {}
    data_user_total = {}
    data_user_not_total = {}
    data_service = {}
    data_service_total = {}
    data_temp = Ticket.ticktets_filtered_with(
        start_period = f"{year}-01-01",
        end_period = f"{year}-12-31", 
        customer_id = customer_id, 
        queue_id = queue_id
    )

    for ticket in data_temp:
        date = ticket.create_time
        month = date.month
        
        if month not in data_total:
            data_total[month] = {
                "name": calendar[month],
                "total": 1
            }
        else:
            data_total[month]["total"] += 1
        
        if month not in data_tickets:
            data_tickets[month] = {
                "name": calendar[month],
                "tickets": [ticket]
            }
        else:
            data_tickets[month]["tickets"].append(ticket)
        
        if month not in data_user:
            data_user[month] = {}
            data_service[month] = {}
            data_service_total[month] = {}

        
        if ticket.user_id not in users:
            if "user_not" not in data_user[month]:
                data_user[month]["user_not"] = {}
            
            if ticket.user_id not in data_user[month]["user_not"]:
                if month not in data_user_not_total:
                    data_user_not_total[month] = {}
                data_user_not_total[month][ticket.user_id] =  {
                    "user": {
                        "name": ticket.user.full_name
                    },
                    "total": 1
                }
                data_user[month]["user_not"][ticket.user_id] = {
                    "user": {
                        "name": ticket.user.full_name
                    },
                    "tickets": [ticket]
                }
                
            else:
                data_user[month]["user_not"][ticket.user_id]["tickets"].append(ticket)
                data_user_not_total[month][ticket.user_id]["total"] += 1
        
        else:  
            if ticket.user_id not in data_user[month]:
                if month not in data_user_total:
                    data_user_total[month] = {}
                data_user_total[month][ticket.user_id] = {
                    "user": {
                        "name": ticket.user.full_name
                    },
                    "total": 1
                }
                data_user[month][ticket.user_id] = {
                    "user": {
                        "name": ticket.user.full_name
                    },
                    "tickets": [ticket]
                }
            else:
                data_user[month][ticket.user_id]["tickets"].append(ticket)
                data_user_total[month][ticket.user_id]["total"] += 1
        
        if ticket.service_id not in data_service[month]:
            data_service_total[month][ticket.service_id] = {
                "service": {
                        "name": ticket.service.name if ticket.service else "Undefined"
                    },
                "total": 1
            }
            data_service[month][ticket.service_id] = {
                "service": {
                    "name": ticket.service.name if ticket.service else "Undefined"
                },
                "tickets": [ticket]
            }
        else:
            data_service[month][ticket.service_id]["tickets"].append(ticket)
            data_service_total[month][ticket.service_id]["total"] += 1
    
    data_grah_temp = []
    data_x = []
    for mont_ in data_total:
        data_x.insert(0, data_total[mont_]["name"])
        data_grah_temp.insert(0, data_total[mont_]["total"])
    
    data_total_sorted = sorted(data_total.items(), key=lambda x:x[0], reverse=True)
    total_tickets = sum(data_grah_temp)
    data_grah = [{"name": "Tickets", "data": data_grah_temp}]

    print(def_name, datetime.today())
    db.session.commit()
    return {
        "customer_name": customer_name,
        "data_total": data_total,
        "data_total_sorted": data_total_sorted,
        "data_tickets": data_tickets,
        "data_service": data_service,
        "data_service_total": data_service_total, 
        "data_x": data_x, 
        "data_y": data_grah, 
        "total_tickets": total_tickets,
        "data_user": data_user,
        "data_user_total": data_user_total,
        "data_user_not_total": data_user_not_total
    }

# get_tickets_customer_months_year("AAN", 6, "2023")