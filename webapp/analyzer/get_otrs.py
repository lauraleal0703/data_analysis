from webapp.models import db
from webapp.models.user import User
from webapp.models.ticket import Ticket
from webapp.models.customer_company import CustomerCompany
from webapp.models.dynamic_field_value import DynamicFieldValue
from webapp.analyzer.qradar import qradar

import orjson
import typing as t
from pathlib import Path
from pprint import pprint
from datetime import datetime
from dateutil.relativedelta import relativedelta



import logging
logging.basicConfig(
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
        level=logging.DEBUG
    )


###############################################################################
############################### Funciones de Soporte ##########################
###############################################################################


def calendar_spanish():
    """Obtener un diciconario con los meses del año en español
    
    Return
    ------
    calendar_spanish
        Una diccionario de calendar_spanish
    """
    def_name = "calendar_spanish"
    logging.debug(def_name)

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
    logging.debug(def_name)
    return {
        "calendar_num": calendar_num,
        "calendar_name": calendar_name
    }


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
    def_name = "customers_actives"
    logging.debug(def_name)
    customers = CustomerCompany.all()
    logging.debug(def_name)
    return {
        customer.customer_id: customer.name for customer in customers 
        if customer.customer_id != "EJEMPLO" 
        and customer.customer_id != "BFAL"
    }


def customers_by_period(
    queue_id: int, 
    customer_id: str=None
) -> dict:
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
    def_name = f"customers_by_period_queue_id_{queue_id}"
    logging.debug(def_name)
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

        logging.debug(def_name)
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
   
    logging.debug(def_name)
    return customers_actives_temp



def users_actives() -> dict:
    """Obtener un diciconario con id de los usuarios
    y su nombre asociado.
    
    Return
    ------
    {"id": name}
        Un diccionario de usuarios
    """
    def_name = "users_actives"
    logging.debug(def_name)
    users = User.all()
    logging.debug(def_name)
    return {str(user.id): user.full_name for user in users}


def get_time_users(
    users: list
) -> dict:
    """Busca si el usuario esta o no activo"""
    def_name = "get_time_user"
    logging.debug(def_name)

    return []

    list_users = []
    for user_id in users:
        end_ticket = Ticket.tickets_filtered_with(
            user_id = user_id,
            last_ticket = True
        )
        end_day = end_ticket.create_time
        end_day_limit = datetime.today() - relativedelta(months=2)
        if end_day < end_day_limit:
            continue
        list_users.append(user_id)
    
    logging.debug(def_name)
    return list_users


def users_administrators():
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
    def_name = "users_administrators"
    logging.debug(def_name)
    administrators = [4, 12, 22, 34, 42, 47, 52, 53, 59, 63]

    administrators_temp = get_time_users(
        users = administrators
    )

    logging.debug(def_name)
    return {
        "administrators_temp": administrators_temp,
        "administrators": administrators
    }


def users_analysts():
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
    def_name = "users_analysts"
    logging.debug(def_name)
    analysts = [13, 26, 29, 30, 32, 38, 45, 54, 56, 60, 64, 65]

    analysts_temp = get_time_users(
        users = analysts
    )
    
    logging.debug(def_name)
    return {
        "analysts_temp": analysts_temp,
        "analysts": analysts
    }


def users_infra():
    """Los usuaios infra son:

    Jaime Nuñez user_id = 14
    Ricardo Perez C user_id = 2
    
    
    Todos los tickets con cola= , deben estar asociado a uno de ellos
    """
    def_name = "users_infra"
    logging.debug(def_name)
    infra = [2, 14]

    infra_temp = get_time_users(
        users = infra
    )

    logging.debug(def_name)
    return {
        "infra_temp": infra_temp,
        "infra": infra
    }


###############################################################################
##################### Funciones Para rendertemple #############################
###############################################################################


def get_count_tickets_years(
    queue_id: int,
    users: bool = False,
    customers: bool = False,
    refresh: bool = False
) -> dict:
    """Obtener un recuento de los tickets de todos
    los años de los users/customers
    Lo ideal seria a los tickes de los usuarios filtralos por queue_id,
    pero hay usuarios que tienen tickets de varias colas

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
    logging.info(f"---> Variables de entrada {queue_id} {users} {customers} {refresh}")

    if customers:
        def_name = f"get_count_tickets_years_customers_queue_id_{queue_id}"
    if users:
        def_name = f"get_count_tickets_years_users_queue_id_{queue_id}"

    path_data_qradar: Path = Path(__file__).parent/"data_otrs_temp"
    if not path_data_qradar.exists():
        path_data_qradar.mkdir()
    
    current_path = path_data_qradar / f"{def_name}.json"
    if refresh and current_path.exists():
        logging.info(f"Borrando {current_path}")
        current_path.unlink()

    if not current_path.exists():
        logging.info(f"Creando {current_path}")
    
        if customers:
            customers_active = customers_by_period(queue_id = queue_id)
            searchs_temp = list(customers_active.keys())

        if users:
            customers_active = customers_actives()
            list_customers_active = list(customers_active.keys())
            users_active = users_actives()
            if queue_id == 6:
                users_queue =  users_administrators()
                searchs_temp = users_queue["administrators"]
            if queue_id == 9:
                users_queue = users_analysts()
                searchs_temp = users_queue["analysts"]

        total_search = 0
        total_tickets_search = {}
        dict_tickets_search = {}
        total_tickets_search_years = {}
        
        if queue_id == 6:
            years = list(range(datetime.today().year, 2017, -1))
        if queue_id == 9:
            years = list(range(datetime.today().year, 2018, -1))

        for year in years:
            total_tickets_search_years[year] = {}
            
            for search_id in searchs_temp:
                
                if customers:
                    data_temp = Ticket.tickets_period_filtered_with(
                        start_period = f"{year}-01-01",
                        end_period = f"{year+1}-01-01", 
                        customer_id = search_id,
                        queue_id = queue_id,
                        count = True
                    )

                    if search_id not in total_tickets_search:
                        total_tickets_search[search_id] = {
                            "search": {
                                "name": search_id
                            },
                            "total": data_temp
                        }
                        dict_tickets_search[search_id] = [data_temp]
                    else:
                        total_tickets_search[search_id]["total"] += data_temp
                        dict_tickets_search[search_id].append(data_temp)
                
                if users:
                    data_temp = Ticket.tickets_period_filtered_with(
                        start_period = f"{year}-01-01",
                        end_period = f"{year+1}-01-01",
                        customers = list_customers_active,
                        user_id = search_id,
                        count = True
                    )
                    if search_id not in total_tickets_search:
                        total_tickets_search[search_id] =  {
                            "search":{
                                "name": users_active[str(search_id)]
                            },
                            "total": data_temp
                        }
                        dict_tickets_search[search_id] = [data_temp]
                    else:
                        total_tickets_search[search_id]["total"] += data_temp
                        dict_tickets_search[search_id].append(data_temp)
                    
                    search_id = users_active[str(search_id)]

                
                total_search += data_temp

                if search_id not in total_tickets_search_years:
                    total_tickets_search_years[year][search_id] = data_temp
                else:
                    total_tickets_search_years[year][search_id] += data_temp

        dict_year_total = {}
        for year_ in total_tickets_search_years:
            year_ = str(year_)
            dict_year_total_temp_y = []
            dict_year_total[year_] = {
                "data_grah_x": [],
                "data_grah_y": [],
                "total": 0
            }
            order_desc = sorted(
                total_tickets_search_years[int(year_)].items(),
                key=lambda x:x[1],
                reverse=True
            )
            for cust in order_desc:
                if cust[1] != 0:
                    dict_year_total[year_]["data_grah_x"].append(cust[0])
                    dict_year_total_temp_y.append(cust[1])
                total = sum(dict_year_total_temp_y)
                total = '{:,}'.format(total).replace(',','.')
                dict_year_total[year_]["total"] = total
            
            dict_year_total[year_]["data_grah_y"].append({
                "name": "Tickets",
                "data": dict_year_total_temp_y
            })

        ##Ordenando DESC
        total_tickets_search = sorted(
            total_tickets_search.items(),
            key=lambda x:x[1]["total"],
            reverse=True
        )
    
        data_x = []
        searches = []
        total_tickets_years = []
        for pos, search_temp in enumerate(total_tickets_search):
            searches.append(search_temp[0])
            data_x.append(search_temp[1]["search"]["name"])
            total_tickets_years.append(search_temp[1]["total"])
            total_tickets_search[pos][1]["total"] = '{:,}'.format(search_temp[1]["total"]).replace(',','.')
    
        data_grah = []
        for pos, year in enumerate(years):
            tickets_year = []
            for search_id in searches:
                data_temp = dict_tickets_search[search_id][pos]
                tickets_year.append(data_temp)
                data_grah_temp = {
                    "name": year,
                    "data": tickets_year
                }
            data_grah.append(data_grah_temp)
        
        data_grah_temp = {
            "name": "Total",
            "data": total_tickets_years
        }
        data_grah.append(data_grah_temp)

        data_temp_otrs = {
            "total_tickets": '{:,}'.format(total_search).replace(',','.'),
            "list_total_tickets": total_tickets_search,
            "dict_year_total": dict_year_total,
            "data_grah_x": data_x,
            "data_grah_y": data_grah,
            "current_date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }

        current_path.touch()
        f = current_path.open("wb")
        f.write(orjson.dumps(data_temp_otrs))
        f.close()
    else:
        logging.info(f"Abriendo JSON {current_path}")
        f = open(str(current_path), "rb")
        data_temp_otrs = orjson.loads(f.read())
    
    logging.debug(def_name)
    return data_temp_otrs


def make_search(
    search: str,
    search_id: t.Union[int, str],
    name: t.Union[int, str],
    date: int,
    dict_tickets: dict,
    ticket: Ticket
) -> None:
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
    data_total = dict
)-> dict:
    """Obtener los datos de la grafica de un parametro especifico"""

    search_temp = []
    dict_grah_year = {}
    for date in dict_tickets:
        data_grah_x = []
        data_grah_y_temp = []
        order_desc = sorted(
            dict_tickets[date][search].items(),
            key=lambda x:x[1]["total"],
            reverse=True
        )
        for search_ in order_desc:
            search_id = search_[0]
            data_grah_x.append(dict_tickets[date][search][search_id]["name"])
            data_grah_y_temp.append(dict_tickets[date][search][search_id]["total"])
            
            if search_id not in search_temp:
                search_temp.append(search_id)
        data_grah = {
            "data_grah_x": data_grah_x,
            "data_grah_y": [{ 
                "name": "Tickets",
                "data": data_grah_y_temp
            }],
            "total" : '{:,}'.format(sum(data_grah_y_temp)).replace(',','.')
        }
        dict_grah_year[date] = data_grah
   
    data_grah_y = []
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
    data_grah_y.append(data_total)
    
    return {
        "data_grah_y": data_grah_y,
        "dict_grah_year": dict_grah_year
    }


def get_tickets_filtred(
    user_id: t.Optional[str] = None,
    customer_id: t.Optional[str] = None,
    queue_id: t.Optional[str] = None,
    year: t.Optional[str] = None,
    month: t.Optional[str] = None,
    users: bool = False,
    customers: bool = False,
    refresh: bool = False
) -> dict:
    """Obtener todos los tickets de un usuario
    en toda su estadia o en un año en especifico
    Lo ideal seria usar el queue_id en la
    list_customers_active 
    
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
    logging.info(f"---> Variables de entrada {user_id} {customer_id} {queue_id} {year} {month} {users} {customers} {refresh}")
    if customers:
        if year and month:
            def_name = f"get_tickets_filtred_customers_{customer_id}_{queue_id}_{year}_{month}"
        elif year:
            def_name = f"get_tickets_filtred_customers_{customer_id}_{queue_id}_{year}"
        else:
            def_name = f"get_tickets_filtred_customers_{customer_id}_{queue_id}"
    if users:
        if year and month:
            def_name = f"get_tickets_filtred_users_{user_id}_{queue_id}_{year}_{month}"
        elif year:
            def_name = f"get_tickets_filtred_users_{user_id}_{queue_id}_{year}"
        else:
            def_name = f"get_tickets_filtred_users_{user_id}_{queue_id}"
    

    path_data_qradar: Path = Path(__file__).parent/"data_otrs_temp"
    if not path_data_qradar.exists():
        path_data_qradar.mkdir()
    
    current_path = path_data_qradar / f"{def_name}.json"
    if refresh and current_path.exists():
        logging.info(f"Borrando {current_path}")
        current_path.unlink()

    if not current_path.exists():
        logging.info(f"Creando {current_path}")
    
    current_path = path_data_qradar / f"{def_name}.json"
    if not current_path.exists():
        logging.info(f"Creando {current_path}")
        calendar_spanish_ = calendar_spanish()
        calendar_spanish_temp = calendar_spanish_["calendar_num"]
        calendar_spanish_temp_ = calendar_spanish_["calendar_name"]
        
        users_actives_temp = users_actives()
        customers_active = customers_actives()

        
        if users:
            list_customers_active = list(customers_active.keys())
            user_name = users_actives_temp[user_id]
            dates = list(range(datetime.today().year, 2017, -1))

        if customers:
            if queue_id == 6:
                users_active =  users_administrators()
                users_temp = users_active["administrators"]
            if queue_id == 9:
                users_active = users_analysts()
                users_temp = users_active["analysts"]

            customer = customers_by_period(
                queue_id = queue_id,
                customer_id = customer_id
            )
            dates: list = customer["years_actives"]
            dates.reverse()
            customer_name = customer["name"]

        if year:
            dates = [year]
        
        if month:
            month = calendar_spanish_temp_[month]

        dict_tickets = {}
        for date in dates:
            if users:
                if month:
                    if month == 12:
                        data_temp = Ticket.tickets_period_filtered_with(
                            start_period = f"{date}-{month}-01",
                            end_period = f"{int(date)+1}-01-01",
                            user_id = user_id,
                            customers = list_customers_active
                        )
                        logging.info(f"FinQ {def_name} Nº={len(data_temp)}")
                    else:
                        data_temp = Ticket.tickets_period_filtered_with(
                            start_period = f"{date}-{month}-01",
                            end_period = f"{date}-{int(month)+1}-01",
                            user_id = user_id,
                            customers = list_customers_active
                        )
                        logging.info(f"FinQ {def_name} Nº={len(data_temp)}")
                else:
                    data_temp = Ticket.tickets_period_filtered_with(
                        start_period = f"{date}-01-01",
                        end_period = f"{int(date)+1}-01-01",
                        user_id = user_id,
                        customers = list_customers_active
                    )
                    logging.info(f"FinQ {def_name} Nº={len(data_temp)}")
            
            if customers:
                if month:
                    if month == 12:
                        data_temp = Ticket.tickets_period_filtered_with(
                            start_period = f"{date}-{month}-01",
                            end_period = f"{int(date)+1}-01-01",
                            queue_id = queue_id,
                            customer_id = customer_id 
                        )
                        logging.info(f"FinQ {def_name} Nº={len(data_temp)}")
                    else:
                        data_temp = Ticket.tickets_period_filtered_with(
                            start_period = f"{date}-{month}-01",
                            end_period = f"{date}-{int(month)+1}-01",
                            queue_id = queue_id,
                            customer_id = customer_id
                        )
                        logging.info(f"FinQ {def_name} Nº={len(data_temp)}")
                else:
                    data_temp = Ticket.tickets_period_filtered_with(
                        start_period = f"{date}-01-01",
                        end_period = f"{int(date)+1}-01-01", 
                        queue_id = queue_id,
                        customer_id = customer_id
                    )
                    logging.info(f"FinQ {def_name} Nº={len(data_temp)}")
                
            if not data_temp:
                continue
            
            for ticket in data_temp:
                ticket : Ticket
                ticket_json = Ticket.tojson(ticket)

                if year:
                    date_temp: datetime = ticket.create_time
                    date = calendar_spanish_temp[date_temp.month]
                
                if month:
                    date_temp: datetime = ticket.create_time
                    date = str(date_temp.day)
                
                date = str(date)
                if date not in dict_tickets:
                    dict_tickets[date] = {}
                
                if "total" not in dict_tickets[date]:
                    dict_tickets[date]["total"] = {
                        "total": 1,
                        "tickets": [ticket_json]
                    }
                else:
                    dict_tickets[date]["total"]["total"] += 1
                    dict_tickets[date]["total"]["tickets"].append(ticket_json)

                if users:
                    make_search(
                        search = "queues",
                        search_id = str(ticket.queue_id),
                        name = ticket.queue.name,
                        date = date,
                        dict_tickets = dict_tickets,
                        ticket = ticket_json
                    )

                    make_search(
                        search = "customers",
                        search_id = ticket.customer_id,
                        name = ticket.customer_id,
                        date = date,
                        dict_tickets = dict_tickets,
                        ticket = ticket_json
                    )

                if customers:
                    make_search(
                        search = "users",
                        search_id = str(ticket.user_id),
                        name = ticket.user.full_name,
                        date = date,
                        dict_tickets = dict_tickets,
                        ticket = ticket_json
                    )

                make_search(
                    search = "services",
                    search_id = str(ticket.service_id),
                    name = ticket.service.name if ticket.service else ticket.service_id,
                    date = date,
                    dict_tickets = dict_tickets,
                    ticket = ticket_json
                )

        data_x = []
        data_y = []
        data_total = {}
        for date in dict_tickets:
            data_total[date] = dict_tickets[date]["total"]["total"]
            data_x.append(date)
            data_y.append(dict_tickets[date]["total"]["total"])
        
        data_grah_y_temp = {
            "name": "Total",
            "data": data_y
        }

        if users:
            data_grah_y = search_grah(
                search = "queues",
                dict_tickets = dict_tickets,
                data_total = data_grah_y_temp
            )
            data_grah_general =  {
                "user_name": user_name,
                "total_tickets": '{:,}'.format(sum(data_y)).replace(',','.'),
                "data_grah_x": data_x,
                "data_grah_y": data_grah_y["data_grah_y"]
            }

            data_grah_y_customers = search_grah(
                search = "customers",
                dict_tickets = dict_tickets,
                data_total = data_grah_y_temp
            )
            data_grah_customers =  {
                "user_name": user_name,
                "total_tickets": '{:,}'.format(sum(data_y)).replace(',','.'),
                "data_grah_x": data_x,
                "data_grah_y": data_grah_y_customers["data_grah_y"]
            }
            data_grah_date_customers = data_grah_y_customers["dict_grah_year"]

            data_grah_y_services = search_grah(
                search = "services",
                dict_tickets = dict_tickets,
                data_total = data_grah_y_temp
            )
            data_grah_services =  {
                "user_name": user_name,
                "total_tickets": '{:,}'.format(sum(data_y)).replace(',','.'),
                "data_grah_x": data_x,
                "data_grah_y": data_grah_y_services["data_grah_y"]
            }
            data_grah_date_services = data_grah_y_services["dict_grah_year"]
        
        if customers:
            data_grah_general =  {
                "customer_name": customer_name,
                "total_tickets": '{:,}'.format(sum(data_y)).replace(',','.'),
                "data_grah_x": data_x,
                "data_grah_y": [data_grah_y_temp]
            }

            data_grah_y = search_grah(
                search = "users",
                dict_tickets = dict_tickets,
                data_total = data_grah_y_temp
            )
            data_grah_users =  {
                "customer_name": customer_name,
                "total_tickets": '{:,}'.format(sum(data_y)).replace(',','.'),
                "data_grah_x": data_x,
                "data_grah_y": data_grah_y["data_grah_y"]
            }
            data_grah_date_users = data_grah_y["dict_grah_year"]

            data_grah_y_services = search_grah(
                search = "services",
                dict_tickets = dict_tickets,
                data_total = data_grah_y_temp
            )
            data_grah_services =  {
                "customer_name": customer_name,
                "total_tickets": '{:,}'.format(sum(data_y)).replace(',','.'),
                "data_grah_x": data_x,
                "data_grah_y": data_grah_y_services["data_grah_y"]
            }
            data_grah_date_services = data_grah_y_services["dict_grah_year"]

        if users:
            data_temp_otrs ={
                "dict_tickets": dict_tickets,
                "data_total_table": data_total,
                "data_grah_general": data_grah_general,
                "data_grah_customers": data_grah_customers,
                "data_grah_date_customers": data_grah_date_customers,
                "data_grah_services": data_grah_services,
                "data_grah_date_services": data_grah_date_services,
                "current_date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            }
            current_path.touch()
            f = current_path.open("wb")
            f.write(orjson.dumps(data_temp_otrs))
            f.close()
        
        if customers:
            data_temp_otrs = {
                "dict_tickets": dict_tickets,
                "data_total_table": data_total,
                "data_grah_general": data_grah_general,
                "data_grah_users": data_grah_users,
                "data_grah_date_users": data_grah_date_users,
                "data_grah_services": data_grah_services,
                "data_grah_date_services": data_grah_date_services,
                "current_date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            }
            current_path.touch()
            f = current_path.open("wb")
            f.write(orjson.dumps(data_temp_otrs))
            f.close()
    else:
        logging.info(f"Abriendo JSON {current_path}")
        f = open(str(current_path), "rb")
        data_temp_otrs = orjson.loads(f.read())
    
    logging.debug(def_name)
    return data_temp_otrs


###############################################################################
######################## Miguel Suarez ########################################
########################## Resumen de tickest en conflicto ####################
###############################################################################


def get_tickets_conflic(
    time: str,
    refresh: bool = False
):
    """Obtener los tickets que no tienen
    servicio asociado o el usuario es de otra cola"""
    def_name = "get_tickets_conflic"
    
    path_data_qradar: Path = Path(__file__).parent/"data_otrs_temp"
    if not path_data_qradar.exists():
        path_data_qradar.mkdir()
    
    current_path = path_data_qradar / f"{def_name}.json"
    if refresh and current_path.exists():
        logging.info("Borrando json")
        current_path.unlink()

    if not current_path.exists():
        logging.info(f"Creando JSON {current_path}")
    
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
            logging.info(f"IniciaQ {def_name} queue_id:{queue_id}")
            
            data_total[str(queue_id)] = []

            data_temp = Ticket.tickets_conflict(
                time = time,
                queue_id = queue_id,
                users_id = users,
                customers = customers
            )
            logging.info(f"FinQ {def_name} queue_id:{queue_id} Nº={len(data_temp)}")
            
            if data_temp:
                for ticket in data_temp:
                    data_total[str(queue_id)].append(Ticket.tojson(ticket))
        
        data_temp_otrs = {
            "data_total": data_total,
            "current_date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }
        current_path.touch()
        f = current_path.open("wb")
        f.write(orjson.dumps(data_temp_otrs))
        f.close()
    else:
        logging.info(f"Abriendo JSON {current_path}")
        f = open(str(current_path), "rb")
        data_temp_otrs = orjson.loads(f.read())
    
    logging.debug(def_name)
    return data_temp_otrs



###############################################################################
############################# EJEMPLOS ########################################
###############################################################################


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
