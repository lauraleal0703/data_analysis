try:
    from .otrs.models import db
    from .otrs.models.user import User
    from .otrs.models.ticket import Ticket
    from .otrs.models.customer_company import CustomerCompany
    from .otrs.models.dynamic_field_value import DynamicFieldValue
    from .qradar import qradar
except:
    from otrs.models import db
    from otrs.models.user import User
    from otrs.models.ticket import Ticket
    from otrs.models.customer_company import CustomerCompany
    from otrs.models.dynamic_field_value import DynamicFieldValue
    from qradar import qradar


from pprint import pprint
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import typing as t


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

    calendar_num = {pos+1: month for pos, month in enumerate(months)}
    calendar_name = {months[i]: i+1 for i in list(range(0, 12))}
    print(def_name, datetime.today())
    return {
        "calendar_num": calendar_num,
        "calendar_name": calendar_name
    }


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
            start_ticket = Ticket.tickets_filtered_with(
                queue_id = queue_id, 
                customer_id = customer,
                first_ticket = True
            )
            if start_ticket:
                start_day: datetime = start_ticket.create_time
                end_ticket = Ticket.tickets_filtered_with(
                    queue_id = queue_id, 
                    customer_id = customer,
                    last_ticket = True
                )
                end_day: datetime = end_ticket.create_time
                end_day_limit = datetime.today() - relativedelta(months=2)
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
    
    start_ticket = Ticket.tickets_filtered_with(
        queue_id = queue_id, 
        customer_id = customer_id,
        first_ticket = True
    )
    if start_ticket:
        start_day = start_ticket.create_time
        end_ticket = Ticket.tickets_filtered_with(
            queue_id = queue_id, 
            customer_id = customer_id,
            last_ticket = True
        )
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


def users_actives() -> dict:
    def_name = "users_actives"
    print(def_name, datetime.today())
    """Obtener un diciconario con id de los usuarios
    y su nombre asociado.
    
    Return
    ------
    {id: name}
        Un diccionario de usuarios
    """
    users = User.all()

    print(def_name, datetime.today())
    return {user.id: user.full_name for user in users}


def users_administrators():
    def_name = "users_administrators"
    print(def_name, datetime.today())
    """Los usuaios administradores son:
    Marcelo Fernandez user_id = 4
    Jose Nicolas user_id = 12
    Angélica Ortega user_id = 22
    Pedro Cerpa C. user_id = 34
    Mauricio Abricot user_id = 42
    Andres Rojas user_id = 47
    Miguel Almendra user_id = 52
    Solange Aravena user_id = 53
    Miguel Gonzalez user_id = 59
    Diego Orellana user_id = 63

    Todos los tickets con cola=6, deben estar asociado a uno de ellos
    """
    administrators = [4, 12, 22, 34, 42, 47, 52, 53, 59, 63]

    administrators_temp = []
    for user_id in administrators:
        end_ticket = Ticket.tickets_filtered_with(
            user_id = user_id,
            last_ticket = True
        )
        end_day = end_ticket.create_time
        end_day_limit = datetime.today() - relativedelta(months=2)
        if end_day < end_day_limit:
            continue
        administrators_temp.append(user_id)

    print(def_name, datetime.today())
    return {
        "administrators_temp": administrators_temp,
        "administrators": administrators
    }


def users_analysts():
    def_name = "users_analysts"
    print(def_name, datetime.today())
    """Los usuaios analistas son:
    José Sanhueza user_id = 13
    Camila Rojas user_id = 26
    Francisco Sepulveda user_id = 29
    Julio Briceño F. user_id = 30
    Emilio Venegas A. user_id = 32
    Matias Zavala user_id = 38
    Jonathan Finschi user_id = 45
    Cristopher Ulloa user_id = 54
    Sugy Nam user_id = 56
    Mauricio Bahamondes user_id = 60
    Mauricio Retamales user_id = 64
    Nicolas Garrido user_id = 65
    
    Todos los tickets con cola=9, deben estar asociado a uno de ellos
    """
    analysts = [13, 26, 29, 30, 32, 38, 45, 54, 56, 60, 64, 65]

    analysts_temp = []
    for user_id in analysts:
        end_ticket = Ticket.tickets_filtered_with(
            user_id = user_id,
            last_ticket = True
        )
        end_day = end_ticket.create_time
        end_day_limit = datetime.today() - relativedelta(months=2)
        if end_day < end_day_limit:
            continue
        analysts_temp.append(user_id)
    
    print(def_name, datetime.today())
    return {
        "analysts_temp": analysts_temp,
        "analysts": analysts
    }


def users_infra():
    def_name = "users_infra"
    print(def_name, datetime.today())
    """Los usuaios infra son:

    Jaime Nuñez user_id = 14
    Ricardo Perez C user_id = 2
    
    
    Todos los tickets con cola= , deben estar asociado a uno de ellos
    """
    infra = [2, 14]

    infra_temp = []
    for user_id in infra:
        end_ticket = Ticket.tickets_filtered_with(
            user_id = user_id,
            last_ticket = True
        )
        end_day = end_ticket.create_time
        end_day_limit = datetime.today() - relativedelta(months=2)
        if end_day < end_day_limit:
            continue
        infra_temp.append(user_id)

    print(def_name, datetime.today())
    return {
        "infra_temp": infra_temp,
        "infra": infra
    }


##################################################################
#### Da respuesta a: 
# 1. Cantidad de tickets generados por clientes
# 2. Cantidad de tickets generados por plataformas en cada cliente
###################################################################


def get_count_tickets_customers_years(
        queue_id: int
    ) -> dict:
    def_name = "get_count_tickets_customers_years"
    print(def_name, datetime.today())
    """Obtener un recuento de los tickets de todos los clientes
    
    Da los datos directos para la gráfica.
    https://www.highcharts.com/demo/column-basic

    Parameters
    ----------
    queue_id: int
        ID de la cola
    
    Return
    ------
    dict
    """
    customers = customers_by_period(queue_id = queue_id)
    customers_temp = list(customers.keys()) 
    years = list(range(datetime.today().year, 2018, -1))
    total_tickets_customers = {}
    dict_tickets_customers: t.Dict[str, t.List] = {}
    total_tickets = 0
    total_tickets_customers_year = {}
    for year in years:
        total_tickets_customers_year[year] = {}
        for customer_id in customers_temp:
            data_temp = Ticket.tickets_period_filtered_with(
                start_period = f"{year}-01-01",
                end_period = f"{year}-12-31", 
                customer_id = customer_id,
                queue_id = queue_id,
                count = True
            )

            if customer_id not in total_tickets_customers_year:
                total_tickets_customers_year[year][customer_id] = data_temp
            else:
                total_tickets_customers_year[year][customer_id] += data_temp

            if customer_id not in total_tickets_customers:
                total_tickets_customers[customer_id] = data_temp
                dict_tickets_customers[customer_id] = [data_temp]
                total_tickets = data_temp
            else:
                total_tickets_customers[customer_id] += data_temp
                dict_tickets_customers[customer_id].append(data_temp)
                total_tickets += data_temp
                
        
    total_tickets_customers = sorted(
        total_tickets_customers.items(),
        key=lambda x:x[1],
        reverse=True
    )

    dict_year_total = {}
    for year_ in total_tickets_customers_year:
        dict_year_total_temp_y = []
        dict_year_total[year_] = {
            "data_grah_x": [],
            "data_grah_y": [],
            "total": 0
        }
        order_desc = sorted(
            total_tickets_customers_year[year_].items(),
            key=lambda x:x[1],
            reverse=True
        )
        for cust in order_desc:
            if cust[1] != 0:
                dict_year_total[year_]["data_grah_x"].append(cust[0])
                dict_year_total_temp_y.append(cust[1])
                dict_year_total[year_]["total"] += cust[1]
        
        dict_year_total[year_]["data_grah_y"].append({
            "name": year_,
            "data": dict_year_total_temp_y
        })

    ##Ordenando DESC
    data_x = []
    total_tickets_years = []
    for customer_temp in total_tickets_customers:
        customer_id = customer_temp[0]
        data_x.append(customer_id)
        total_tickets_years.append(customer_temp[1])

    data_grah = [{
        "name": "Total",
        "data": total_tickets_years
    }]

    for pos, year in enumerate(years):
        tickets_year = []
        for customer_id in data_x:
            data_temp = dict_tickets_customers[customer_id][pos]
            tickets_year.append(data_temp)
            data_grah_temp = {
                "name": year,
                "data": tickets_year
            }

        data_grah.append(data_grah_temp)

    total_tickets = '{:,}'.format(total_tickets).replace(',','.')
    print(def_name, datetime.today())
    db.session.commit()
    return {
        "total_tickets_customers": total_tickets_customers,
        "data_grah_x": data_x,
        "data_grah_y": data_grah,
        "total_tickets": total_tickets,
        "dict_year_total": dict_year_total
    }

# get_count_tickets_customers_years(6)
# exit()

def get_tickets_customer_years(
        queue_id: int,
        customer_id: str
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
        users = users["administrators"]
    if queue_id == 9:
        users = users_analysts()
        users = users["analysts"]

    customer = customers_by_period(
        queue_id = queue_id,
        customer_id = customer_id
    )

    years: list = customer["years_actives"]
    years.reverse()
    customer_name = customer["name"]

    data_x = []
    data_total = {}
    data_tickets = {}
    data_user_total = {}
    data_user_not_total = {}
    data_user = {}
    data_service_total = {}
    data_service = {}
    data_grah_temp = []
    for year in years:
        data_x.append(year)
        data_temp = Ticket.tickets_period_filtered_with(
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
            ticket: Ticket
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
                    data_user[year]["user_not"][ticket.user_id]["tickets"].append(
                        ticket
                    )
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
                            "name": (
                                ticket.service.name
                                if ticket.service else "Undefined"
                            )
                        },
                    "total": 1
                }
                data_service[year][ticket.service_id] = {
                    "service": {
                        "name": (
                            ticket.service.name 
                            if ticket.service else "Undefined"
                        )
                    },
                    "tickets": [ticket]
                }
            else:
                data_service[year][ticket.service_id]["tickets"].append(ticket)
                data_service_total[year][ticket.service_id]["total"] += 1
    
    total_tickets = sum(data_grah_temp)
    data_grah = [{"name": "Tickets", "data": data_grah_temp}]
    
    data_x_service = []
    dict_service_temp = {}
    for year_ in data_service:
        data_x_service.append(year_)
        for service_ in data_service[year_]:
            if service_ not in dict_service_temp:
                dict_service_temp[service_] = (
                    data_service[year_][service_]["service"]["name"]
                )
    
    dict_service: t.Dict[t.Union[int, str], t.List] = {}
    for service_temp in dict_service_temp:
        dict_service[service_temp] = []
        for year_temp in data_service:
            if service_temp in data_service[year_temp]:
                total = len(data_service[year_temp][service_temp]["tickets"])
            else:
                total = 0
            dict_service[service_temp].append(total)

    dict_service_sum = {ser: sum(dict_service[ser])  for ser in dict_service}
    dict_service_sum = sorted(
        dict_service_sum.items(),
        key=lambda x:x[1], 
        reverse=True
    )

    data_grah_service = []
    for service_temp in dict_service_sum:
        service_temp = service_temp[0]
        dato_temp = {
            "name": dict_service_temp[service_temp],
            "data": dict_service[service_temp]
        }
        data_grah_service.append(dato_temp)

    total_tickets = '{:,}'.format(total_tickets).replace(',','.')
    print(def_name, datetime.today())
    db.session.commit()
    return {
        "customer_name": customer_name,
        "data_total": data_total,
        "data_tickets": data_tickets,
        "data_service": data_service,
        "data_service_total": data_service_total, 
        "data_grah_x": data_x, 
        "data_grah_y": data_grah, 
        "total_tickets": total_tickets,
        "data_user": data_user,
        "data_user_total": data_user_total,
        "data_user_not_total": data_user_not_total,
        "data_grah_service": data_grah_service, 
        "data_x_service": data_x_service
    }

# get_tickets_customer_years(6, "AAN")
# exit()

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
        users = users["administrators"]
    if queue_id == 9:
        users = users_analysts()
        users = users["analysts"]

    calendar = calendar_spanish()
    calendar = calendar["calendar_num"]
    customer = customers_by_period(
        queue_id = queue_id,
        customer_id=customer_id
    )
    customer_name = customer["name"]

    data_total = {}
    data_tickets: t.Dict[int, t.Dict[str, list]] = {}
    data_user = {}
    data_user_total = {}
    data_user_not_total = {}
    data_service: t.Dict[int, t.Dict[int, t.Dict[str, list]]] = {}
    data_service_total = {}
    data_temp = Ticket.tickets_period_filtered_with(
        start_period = f"{year}-01-01",
        end_period = f"{year}-12-31", 
        customer_id = customer_id, 
        queue_id = queue_id
    )

    for ticket in data_temp:
        ticket: Ticket
        date: datetime = ticket.create_time
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
                data_user[month]["user_not"][ticket.user_id]["tickets"].append(
                    ticket
                )
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
                        "name": (
                            ticket.service.name 
                            if ticket.service else "Undefined"
                        )
                    },
                "total": 1
            }
            data_service[month][ticket.service_id] = {
                "service": {
                    "name": (
                        ticket.service.name 
                        if ticket.service else "Undefined"
                    )
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
    
    data_total_sorted = sorted(
        data_total.items(),
        key=lambda x:x[0], 
        reverse=True
    )
    total_tickets = sum(data_grah_temp)
    data_grah = [{"name": "Tickets", "data": data_grah_temp}]

    data_x_service = []
    months_temp = []
    dict_service_temp = {}
    for month_ in data_service:
        data_x_service.insert(0, calendar[month_])
        months_temp.insert(0, month_)
        for service_ in data_service[month_]:
            if service_ not in dict_service_temp:
                dict_service_temp[service_] = {
                    "name": data_service[month_][service_]["service"]["name"],
                    "total": len(data_service[month_][service_]["tickets"])
                }
            else:
                dict_service_temp[service_]["total"] += len(
                    data_service[month_][service_]["tickets"]
                )

    dict_service_temp_desc = sorted(
        dict_service_temp.items(), 
        key=lambda x:x[1]["total"], 
        reverse=True
    )
    list_service_temp = list(
        service_id[0] for service_id in dict_service_temp_desc
    )
    
    dict_service: t.Dict[t.Union[int, str], t.List] = {}
    for service_temp in list_service_temp:
        dict_service[service_temp] = []
        for month_temp in months_temp:
            if service_temp in data_service[month_temp]:
                total = len(data_service[month_temp][service_temp]["tickets"])
            else:
                total = 0
            dict_service[service_temp].append(total)

    data_grah_service = []
    data_x_service_total = []
    data_grah_service_total = []
    for service_temp in list_service_temp:
        data_x_service_total.append(dict_service_temp[service_temp]["name"])
        data_grah_service_total.append(dict_service_temp[service_temp]["total"])
        dato_temp = {
            "name": dict_service_temp[service_temp]["name"],
            "data": dict_service[service_temp]
        }
        data_grah_service.append(dato_temp)
    
    data_grah_service_total = [{
        "name": "Tickets", 
        "data": data_grah_service_total
    }]

    total_tickets = '{:,}'.format(total_tickets).replace(',','.')
    print(def_name, datetime.today())
    db.session.commit()
    return {
        "customer_name": customer_name,
        "data_total": data_total,
        "data_total_sorted": data_total_sorted,
        "data_tickets": data_tickets,
        "data_service": data_service,
        "data_service_total": data_service_total, 
        "data_grah_x": data_x, 
        "data_grah_y": data_grah, 
        "total_tickets": total_tickets,
        "data_user": data_user,
        "data_user_total": data_user_total,
        "data_user_not_total": data_user_not_total,
        "data_grah_service": data_grah_service, 
        "data_x_service": data_x_service,
        "data_x_service_total": data_x_service_total,
        "data_grah_service_total": data_grah_service_total
    }

# get_tickets_customer_months_year("Experian", 6, "2023")

####################################################
###Migueñ Suarez
#####Resumen de tickest en conflicto
######################################################


def get_tickets_conflic(
        time: str
):
    """Obtener los tickets que no tienen
    servicio asociado o el usuario es de otra cola"""
    def_name = "get_tickets_conflic"
    print(def_name, datetime.today())
    
    queues_id = [6, 9]
    data_total = {}
    for queue_id in queues_id:
        customers = customers_by_period(queue_id=queue_id)
        customers = list(customers.keys())
        if queue_id == 6:
            users =  users_administrators()
            users = users["administrators"]
        if queue_id == 9:
            users = users_analysts()
            users = users["analysts"]
        data = Ticket.tickets_conflict(
            time = time,
            queue_id = queue_id,
            users_id = users,
            customers = customers
        )
        if data:
            data_total[queue_id] = data
 
    print(def_name, datetime.today())
    return data_total



######################################################
#### Da respuesta a: 
# 3. Cantidad de tickets atendidos por administrador
# 4. Cantidad de tickets atendidos por administrador, 
# por plataforma, por cliente
######################################################


def get_count_tickets_users_years(
        queue_id: int
    ) -> dict:
    def_name = "get_count_tickets_customers_years"
    print(def_name, datetime.today())
    """Obtener un recuento de los tickets de todos los
    usuarios de las colas
    
    Da los datos directos para la gráfica.
    https://www.highcharts.com/demo/column-basic

    Parameters
    ----------
    queue_id: int
        ID de la cola
    
    Return
    ------
    dict
    """
    users_actives_temp = users_actives()
    if queue_id == 6:
        users =  users_administrators()
        users = users["administrators_temp"]
    if queue_id == 9:
        users = users_analysts()
        users = users["analysts_temp"]
    
    years = list(range(datetime.today().year, 2018, -1))
    total_tickets_users = {}
    dict_tickets_users: t.Dict[int, t.List] = {}
    total_tickets = 0
    total_tickets_years = {}
    for year in years:
        total_tickets_years[year] = {}
        for user_id in users:
            data_temp = Ticket.tickets_period_filtered_with(
                start_period = f"{year}-01-01",
                end_period = f"{year}-12-31",
                user_id = user_id,
                count = True
            )

            if user_id not in total_tickets_years[year]:
                total_tickets_years[year][user_id] =  {
                    "user":{
                        "name": users_actives_temp[user_id]
                    },
                    "total": int(data_temp)
                }
            else:
                total_tickets_years[year][user_id]["total"] += int(data_temp)
                
            if user_id not in total_tickets_users:
                total_tickets_users[user_id] = {
                    "user":{
                        "name": users_actives_temp[user_id]
                    },
                    "total": data_temp
                }
                
                data_temp
                dict_tickets_users[user_id] = [data_temp]
                total_tickets = data_temp
            else:
                total_tickets_users[user_id]["total"] += data_temp
                dict_tickets_users[user_id].append(data_temp)
                total_tickets += data_temp


    dict_year_total = {} 
    for year_ in total_tickets_years:
        dict_year_total[year_] = {
            "data_grah_x": [],
            "data_grah_y": [],
            "total": 0
        }
        for user_ in total_tickets_years[year_]:
            if total_tickets_years[year_][user_]["total"] != 0:
                dict_year_total[year_]["data_grah_x"].append(
                    total_tickets_years[year_][user_]["user"]["name"])
                dict_year_total[year_]["data_grah_y"].append(
                    total_tickets_years[year_][user_]["total"])
        
        dict_year_total[year_]["total"] = sum(dict_year_total[year_]["data_grah_y"])  
        

    pprint(dict_year_total)


    total_tickets_users = sorted(
        total_tickets_users.items(), 
        key=lambda x:x[1]["total"], 
        reverse=True
    )
    
    ##Ordenando DESC
    data_x = []
    users = []
    for user_temp in total_tickets_users:
        user_id = user_temp[0]
        users.append(user_id)
        data_x.append(user_temp[1]["user"]["name"])

    data_grah = []
    for pos, year in enumerate(years):
        tickets_year = []
        for user_id in users:
            data_temp = dict_tickets_users[user_id][pos]
            tickets_year.append(data_temp)
            data_grah_temp = {
                "name": year,
                "data": tickets_year
            }

        data_grah.append(data_grah_temp)

    total_tickets = '{:,}'.format(total_tickets).replace(',','.')
    print(def_name, datetime.today())
    db.session.commit()
    return {
        "total_tickets_users": total_tickets_users,
        "data_grah_x": data_x,
        "data_grah_y": data_grah,
        "total_tickets": total_tickets
    }

# get_count_tickets_users_years(6)

def make_search(
    search: str,
    search_id: t.Union[int, str],
    name: t.Union[int, str],
    date: int,
    dict_tickets: dict,
    ticket: Ticket
    )-> None:
    """Crear los datos de un parametro especifico"""
    if search not in dict_tickets[date]:
        dict_tickets[date][search] = {}
    if search_id not in dict_tickets[date][search]:
        dict_tickets[date][search][search_id] = {
            "name": name,
            "tickets": [ticket],
            "total": 1
        }
    else:
        dict_tickets[date][search][search_id]["tickets"].append(ticket)
        dict_tickets[date][search][search_id]["total"] += 1


def search_grah(
        search: str, 
        dict_tickets: dict,
        data_grah_y: list
    )-> dict:
    def_name = "search_grah"
    print(def_name, datetime.today())
    """Obtener los datos de la grafica de un parametro especifico"""

    search_temp = [] 
    for date in dict_tickets:
        for search_id in dict_tickets[date][search]:
            if search_id not in search_temp:
                search_temp.append(search_id)
    
    for search_id in search_temp:
        data_temp = []
        for date in dict_tickets:
            if search_id in dict_tickets[date][search]:
                total_ = dict_tickets[date][search][search_id]["total"]
                name_ = dict_tickets[date][search][search_id]["name"]
            else:
                total_ = 0
            data_temp.append(total_)
        
        data_grah_y.append({
            "name": name_,
            "data": data_temp
        })
    
    return data_grah_y


def get_tickets_users_years(
        user_id: int,
        year: t.Optional[int] = None,
        month: t.Optional[str] = None
    ) -> dict:
    def_name = "get_tickets_users_years"
    print(def_name, datetime.today())
    """Obtener todos los tickets de un usuario
    en toda su estadia o en un año en especifico
    
    Da los datos directos para la gráfica.
    https://www.highcharts.com/demo/column-basic

    Parameters
    ----------
    queue_id: int
        ID de la cola
    
    Return
    ------
    dict
    """
    calendar_spanish_ = calendar_spanish()
    calendar_spanish_temp = calendar_spanish_["calendar_num"]
    calendar_spanish_temp_ = calendar_spanish_["calendar_name"]
    users_actives_temp = users_actives()
    customers_actives_temp = customers_actives()
    user_name = users_actives_temp[user_id]

    if not year:
        dates = list(range(datetime.today().year, 2018, -1))
    else:
        dates = [year]
    
    if month:
        month = calendar_spanish_temp_[month]

    dict_tickets = {}
    for date in dates:
        if month:
            data_temp = Ticket.tickets_period_filtered_with(
            start_period = f"{date}-{month}-01",
            end_period = f"{date}-{month+1}-01",
            user_id = user_id
        )
        else:
            data_temp = Ticket.tickets_period_filtered_with(
                start_period = f"{date}-01-01",
                end_period = f"{date+1}-01-01",
                user_id = user_id
            )
        
        if not data_temp:
            continue
        
        for ticket in data_temp:
            ticket: Ticket

            if ticket.customer_id not in customers_actives_temp:
                continue

            if year:
                date_temp: datetime = ticket.create_time
                date = calendar_spanish_temp[date_temp.month]
            
            if month:
                date_temp: datetime = ticket.create_time
                date = date_temp.day
            
            if date not in dict_tickets:
                dict_tickets[date] = {}
            
            if "total" not in dict_tickets[date]:
                dict_tickets[date]["total"] = {
                    "total": 1,
                    "tickets": [ticket]
                }
            else:
                dict_tickets[date]["total"]["total"] += 1
                dict_tickets[date]["total"]["tickets"].append(ticket)

            make_search(
                search = "queues",
                search_id = ticket.queue_id,
                name = ticket.queue.name,
                date = date,
                dict_tickets = dict_tickets,
                ticket = ticket
            )

            make_search(
                search = "services",
                search_id = ticket.service_id,
                name = ticket.service.name if ticket.service else ticket.service_id,
                date = date,
                dict_tickets = dict_tickets,
                ticket = ticket
            )

            make_search(
                search = "customers",
                search_id = ticket.customer_id,
                name = ticket.customer_id,
                date = date,
                dict_tickets = dict_tickets,
                ticket = ticket
            )

    data_x = []
    data_y = []
    data_total = {}
    for date in dict_tickets:
        data_total[date] = dict_tickets[date]["total"]["total"]
        data_x.append(date)
        data_y.append(dict_tickets[date]["total"]["total"])
    
    data_grah_y = [{
        "name": "Tickets",
        "data": data_y
    }]

    data_grah_y_ = search_grah(
        search = "queues",
        dict_tickets = dict_tickets,
        data_grah_y = data_grah_y.copy()
    )

    data_grah_general =  {
        "user_name": user_name,
        "total_tickets": sum(data_y),
        "data_grah_x": data_x,
        "data_grah_y": data_grah_y_
    }

    data_grah_y_services = search_grah(
        search = "services",
        dict_tickets = dict_tickets,
        data_grah_y = data_grah_y.copy()
    )
    
    data_grah_services =  {
        "user_name": user_name,
        "total_tickets": sum(data_y),
        "data_grah_x": data_x,
        "data_grah_y": data_grah_y_services
    }

    data_grah_y_customers = search_grah(
        search = "customers",
        dict_tickets = dict_tickets,
        data_grah_y = data_grah_y.copy()
    )
    
    data_grah_customers =  {
        "user_name": user_name,
        "total_tickets": sum(data_y),
        "data_grah_x": data_x,
        "data_grah_y": data_grah_y_customers
    }

    print(def_name, datetime.today())
    db.session.commit()
    return {
        "dict_tickets": dict_tickets,
        "data_total_table": data_total,
        "data_grah_general": data_grah_general,
        "data_grah_services": data_grah_services,
        "data_grah_customers": data_grah_customers
    }

# get_tickets_users_years(52)
# exit()

###Prueba dado un ticket.id, se tiene el ID de QRadar
# test = DynamicFieldValue.get_offense_id(45796)
# print(test)
# OK


''' 
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
'''