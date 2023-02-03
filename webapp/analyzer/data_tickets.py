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
from pprint import pprint
from pathlib import Path
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


path_analyzer = Path(__file__).parent
path_temp = Path(f"{path_analyzer}/temp")
if not path_temp.exists():
    path_temp.mkdir()

##########################################
##########Funciones de apoyo#############
##########################################


def list_months_year(year: str, start_date: str=None):
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

    """
    NOTA: Como el servidor del laboratorio, no tiene algunas
    "conexiones" colocando el mode_ = lab solo consulta los datos 
    que tiene en la carpeta ten sin hacer ningún requerimientos 
    exterior.
    """

    current_mode = "dev"
    # current_mode = "lab"

    if current_mode != "dev":
        end_date = datetime.strptime("2023-01-01", "%Y-%m-%d")
    else:
        end_date = datetime.today()+relativedelta(months=1)

    if start_date:
        date = start_date
    else:
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
    """Obtener una lista con los dias a anlizar

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
    
    lista_fechas = [str(start + timedelta(days=d)).split(" ")[0] for d in range((end - start).days + 1)]
    
    return lista_fechas

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
    # services = Service.all()
    services = {1: 'CSOC::Administración::Firewall', 
        2: 'CSOC::Administración::Network Security::FireEye NX', 
        3: 'CSOC::Administración::Email Security::IronPort', 
        4: 'CSOC::Administración::Patch Management::BigFix', 
        5: 'CSOC::Administración::Bóveda Contraseñas::Password Safe', 
        6: 'CSOC::Administración::Auditing::PB Auditor', 
        7: 'CSOC', 
        8: 'CSOC::Administración::WAF', 
        9: 'CSOC::Administración::WAF::F5 ASM', 
        10: 'CSOC::Administración::Firewall::CheckPoint', 
        11: 'CSOC::Administración::Firewall::PALO ALTO (PAN)', 
        12: 'CSOC::Monitoreo::SIEM', 
        13: 'Palo Alto', 
        14: 'CSOC::Administración::Firewall::PaloAlto', 
        15: 'CSOC::Administración::Patch Management::BigFix::Administracion 5x8 Parchado BigFix',
        16: 'Retina', 
        17: 'CSOC::Administración::Scanner Vulnerabilidades::Retina', 
        18: 'CSOC::Administración::Network Security::Firemon', 
        19: 'Arquitectura e Infraestructura::Solicitudes Internas', 
        20: 'CSOC::Administración::Wireless::Aruba', 
        21: 'CSOC::Administración::Mobile::MDM Airwatch', 
        22: 'CSOC::Administración::WAF::Cloudflare', 
        23: 'CSOC::Administración::Email', 
        24: 'CSOC::Administración::Scanner Vulnerabilidades',
        25: 'CSOC::Administración', 26: 'CSOC::Monitoreo', 
        27: 'CSOC::Monitoreo::Nagios', 28: 'CSOC::Administración::Wireless', 29: 'CSOC::Administración::Patch Management', 30: 'CSOC::Administración::Bóveda Contraseñas', 31: 'CSOC::Administración::Scanner Vulnerabilidades::OpenVas', 32: 'CSOC::Administración::Firewall::Fortigate', 33: 'CSOC::Administración::Network Security', 34: 'CSOC::Administración::Host Security', 35: 'CSOC::Administración::Host Security::Fireeye HX', 36: 'CSOC::Administración::Email Security', 37: 'CSOC::Administración::Email Security::Fireeye EX', 38: 'CSOC::Administración::Mobile', 39: 'Arquitectura e Infraestructura', 40: 'CSOC::Administración::Auditing', 41: 'CSOC::Administración::Host Security::McAfee AV', 42: 'CSOC::Administración::Manager', 43: 'CSOC::Administración::Manager::Fireeye CM', 44: 'CSOC::Soporte', 45: 'CSOC::Soporte::Bóveda Contraseñas', 46: 'CSOC::Soporte::Bóveda Contraseñas::Password Safe', 47: 'CSOC::Administración::Host Security::Cylance', 48: 'CSOC::Administración::Base de Datos', 49: 'CSOC::Administración::Base de Datos::Firewall Database', 50: 'CSOC::Administración::Base de Datos::Firewall Database::Imperva', 51: 'CSOC::Administración::Anti-DoS', 52: 'CSOC::Administración::Anti-DoS::Arbor Pravail', 53: 'CSOC::Soporte::Firewall', 54: 'CSOC::Soporte::Firewall::Fortigate', 55: 'CSOC::Administración::Anti-DoS::Cloudflare', 56: 'CSOC::Administración::Host Security::Cisco AMP', 57: 'CSOC::Administración::Anti-DoS::Cisco Umbrella', 58: 'CSOC::Administración::Email Security::Cisco CES', 59: 'CSOC::Administración::Multifactor', 60: 'CSOC::Administración::Multifactor::Cisco DUO', 61: 'CSOC::Administración::Scanner Vulnerabilidades::Tenable IO', 62: 'CSOC::Soporte::Base de Datos', 63: 'CSOC::Soporte::Base de Datos::Firewall Database', 64: 'CSOC::Soporte::Base de Datos::Firewall Database::Guardium', 65: 'CSOC::Administración::Email Security::Fireeye ETP Cloud', 66: 'CSOC::Administración::Scanner Vulnerabilidades::Cymulate', 67: 'CSOC::Administración::Acceso Privilegiado', 68: 'CSOC::Administración::Acceso Privilegiado::Privilege Remote Access (PRA)', 69: 'CSOC::Administración::Reportes', 70: 'CSOC::Administración::WAF::A10', 71: 'CSOC::Administración::Network Security::Cisco Firepower', 72: 'CSOC::Administración::Host Security::Trendmicro', 73: 'CSOC::Soporte::Host Security', 74: 'CSOC::Soporte::Host Security::PowerBroker for Windows', 75: 'CSOC::Administración::Host Security::DeepSecurity'}

    #{service.id: service.name for service in services}

    return services


def users_actives():
    """Obtener un diciconario con los usuarios
    
    Return
    ------
    {id: user_id_active.full_name}
        Una diccionario de user_id_active
    """
    # users = User.all()
    # {user.id: user.full_name for user in users}
    users = {1: 'Admin OTRS', 2: 'Ricardo Perez C.', 3: 'Rolando Zurita', 4: 'Marcelo Fernandez', 5: 'Eduardo Aceto', 6: 'Martin Plaza', 7: 'Juan Fredes', 8: 'Maiker Ramirez', 9: 'Walter Villavicencio', 10: 'Lelis Cuicas', 11: 'Miguel Cofre', 12: 'Jose Nicolas', 13: 'Jose Sanhueza', 14: 'Jaime Nuñez', 15: 'Esteban Flores', 16: 'Israel Guevara', 17: 'Fabian Figueroa', 18: 'Fabian Escobar', 19: 'Javiera Diaz', 20: 'Cristian Gómez', 21: 'Test OTRS', 22: 'Angélica Ortega', 23: 'Julio Marini', 24: 'Karina Vilches', 25: 'Viviana Acuña', 26: 'Camila Rojas', 27: 'Vanessa Pérez', 28: 'Miguel Rosales', 29: 'Francisco Sepulveda', 30: 'Juan Briceño F.', 31: 'Gonzalo Vidal', 32: 'Emilio Venegas A.', 33: 'Fernando Muñoz C.', 34: 'Pedro Cerpa C.', 35: 'Auto Ofensa', 36: 'Sebastian Vidal A.', 37: 'Roberto Cornejo C.', 38: 'Matías Zavala', 39: 'Andrés Alcaide', 40: 'Valter Mardones S.', 41: 'Lorenzo Polanco', 42: 'Mauricio Abricot', 43: 'Jorge Sandoval L.', 44: 'Miguel Suarez Z.', 45: 'Jonathan Finschi', 46: 'Raul Grossling', 47: 'Andrés Rojas', 48: 'Elisa Molina', 49: 'José Levinao', 50: 'Ignacio Rivera A.', 51: 'CSOC Adaptive Security', 52: 'Miguel Almendra V.', 53: 'Solange Aravena H.', 54: 'Cristopher Ulloa', 55: 'Jorge Bastidas', 56: 'Sugy Nam', 57: 'Yamila Gorrin', 58: 'Dorian Malfert M.', 59: 'Miguel González M.', 60: 'Mauricio Bahamondes', 61: 'Maverik Castro', 62: 'Camilo Burgos', 63: 'Diego Orellana V.', 64: 'Mauricio Retamales', 65: 'Nicolas Garrido', 66: 'Cristian Alva', 67: 'Laura Leal C.'}
 

    return users

users_actives()

def customers_actives():
    """Obtener un diciconario con el nombre de los clientes
    
    Return
    ------
    {id: customer_id.name}
        Una diccionario de clientes
    """
    # customers = CustomerCompany.all()

    # dict_customer = {"AS": "Adaptive Security"}
    # for customer in customers:
    #     if customer.customer_id != "Adaptive Security":
    #         dict_customer[customer.customer_id] = customer.name
    
    dict_temp = {'AS': 'Adaptive Security', 'AAN': 'Aguas Andinas', 'AIEP': 'Instituto Profesional AIEP', 'Banco BICE': 'Banco BICE', 'BCH': 'Banco de Chile', 'BCI': 'Banco de Creditos e Inversiones', 'BDO': 'BDO Chile', 'BES': 'Banco Estado', 'BFAL': 'Banco Falabella', 'BTG': 'BTG Pactual', 'CAS': 'Clínica Alemana', 'CCA': 'Centro de Compensación Automatizado', 'CMPC': 'CMPC', 'COO': 'Coopeuch', 'EJEMPLO': 'EJEMPLO', 'EMSA': 'EMARESA', 'EVERTEC': 'Evertec', 'Experian': 'Experian', 'PRISA': 'PRILOGIC', 'PROVIDA': 'Provida', 'SBPay': 'SBPay', 'SCOTIABANK': 'Banco Scotiabank', 'SMU': 'SMU', 'SURA': 'SURA', 'UAI': 'Universidad Adolfo Ibañez', 'UDLA': 'Universidad de las Américas', 'UDP': 'Universidad Diego Portales', 'UNAB': 'Universidad Andrés Bello', 'VCYT': 'Viña Concha y Toro'}
    
    return dict_temp

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

    if type_ == "customers":
        path_active = Path(
            f"{path_temp}/tickets_customers_by_user_queue_{queue_id}_{year}.json"
        )
    
    elif type_ == "administrators":
        path_active = Path(
            f"{path_temp}/tickets_administrators_queue_{queue_id}_{year}.json"
        )
    
    else:
        return f"Tipo:{type_} --> Undefined"

    if path_active.exists():
        with path_active.open("r") as f:
            json_active = json.load(f)
            last_ticket_id = json_active["last_ticket_id"]
            start_date = json_active["last_period"]
            month_temp = datetime.strptime(start_date, "%Y-%m-%d")
            list_months_temp = list_months_year(month_temp.year, start_date)
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
    
    if (last_ticket_id_temp-int(last_ticket_id)) < 5:
        return active_temp
    
    for pos, period in enumerate(list_months_temp):
        
        if pos+1 < len(list_months_temp):
            start_period = period
            end_period =  list_months_temp[pos+1]
            list_date_temp = list_date(start_period, end_period)

            for pos, date_temp in enumerate(list_date_temp):
                if pos+1 < len(list_date_temp):
                    star_ = date_temp
                    end_ = list_date_temp[pos+1]
                
                try:
                    tickets_by_period = Ticket.tickets_by_queue_period(
                        last_ticket_id,
                        6, 
                        star_,
                        end_
                    )
                except:
                    tickets_by_period = []

                if not tickets_by_period:
                    continue
                
                period_temp = datetime.strptime(date_temp, "%Y-%m-%d")
                month = period_temp.month
                day = period_temp.day
                print(
                    f"{def_name} Analizando datos del periodo"
                    f"={star_} al <{end_}"
                    f"--> {len(tickets_by_period)}"
                )
                
                for ticket in tickets_by_period:
                    customer_temp = ticket.customer_id
                    if customer_temp == "Adaptive Security":
                        customer_temp = "AS"
                    
                    if type_ == "customers":
                        type_temp = customer_temp
                    else:
                        type_temp = ticket.user_id

                    if month not in active_temp:
                        active_temp[month] = {}
                    if day not in active_temp[month]:
                        active_temp[month][day] = {}
                    if type_temp not in active_temp[month][day]:
                        active_temp[month][day][type_temp] = {}
                    if ticket.id not in active_temp[month][day][type_temp]:
                        last_ticket_id_temp = ticket.id
                        resolution_time = ticket.last_history.change_time - ticket.create_time
                        active_temp[month][day][type_temp][ticket.id] = {
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

#get_data_folder_temp_tickets_customer_administrators_queue() 


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

    types_temp = ["automatic", "handwork_customers", "handwork_user"]
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
            list_months_temp = list_months_year(month_temp.year, start_date)
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
    
    if (last_ticket_id_temp-int(last_ticket_id)) < 50:
        return active_temp

    for pos, period in enumerate(list_months_temp):
        
        if pos+1 < len(list_months_temp):
            start_period = period
            end_period =  list_months_temp[pos+1]
            list_date_temp = list_date(start_period, end_period)

            for pos, date_temp in enumerate(list_date_temp):
                if pos+1 < len(list_date_temp):
                    star_ = date_temp
                    end_ = list_date_temp[pos+1]
            
                if type_ ==  "automatic":
                    try:
                        tickets_by_period = Ticket.tickets_offenses_automatic_by_period(
                            last_ticket_id,
                            star_, 
                            end_
                        )
                    except:
                        tickets_by_period = []
                else:
                    try:
                        tickets_by_period = Ticket.tickets_offenses_handwork_by_period(
                            last_ticket_id,
                            star_, 
                            end_
                        )
                    except:
                        tickets_by_period = []

                if not tickets_by_period:
                    continue
                
                period_temp = datetime.strptime(date_temp, "%Y-%m-%d")
                month = period_temp.month
                day = period_temp.day
                print(f"""{def_name} Analizando datos del periodo 
                    ={star_} al <{end_} 
                    --> {len(tickets_by_period)}"""
                )
                
                for ticket in tickets_by_period:
                    offense_id = re.findall(r"\d{5,}", ticket.title)
                    response_time = ""
                    str_sla = ""
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
                            response_time = ticket.create_time - start_time_qradar
                            ideal_response_time = timedelta(minutes=15)
                            if response_time <= ideal_response_time:
                                str_sla = "Cumple"
                            else:
                                str_sla = "No Cumple"

                    customer_temp = ticket.customer_id
                    if customer_temp == "Adaptive Security":
                        customer_temp = "AS"
                    
                    if type_ == "handwork_user":
                        type_temp == ticket.user_id
                    else:
                        type_temp = customer_temp

                    if month not in active_temp:
                        active_temp[month] = {}
                    if day not in active_temp[month][day]:
                        active_temp[month][day] = {}
                    if type_temp not in active_temp[month][day]:
                        active_temp[month][day][type_temp] = {}
                    if ticket.id not in active_temp[month][day][type_temp]:
                        last_ticket_id_temp = ticket.id
                        resolution_time = ticket.last_history.change_time - ticket.create_time
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
                            "str_sla": str_sla if str_sla else "Undefined"
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
    
    list_years_temp = list(range(2018,datetime.today().year+1))
    types_temp = ["automatic", "handwork_customers", "handwork_user"]
    for type_temp in types_temp:
        for year in list_years_temp:
            tickets_offenses(str(year), type_temp)
    
    return f"{def_name} Data actualizada en la carpeta temp"

# get_data_folder_temp_tickets_offenses()


##############################################################
############### ANÁLISIS DE LA DATA OBTENIDA ################
##############################################################

def get_list_year(path_temp: Path):
    """Obtener una lista con los años que se tiene data

    Parameters
    ---------
    
    Return
    ------
    List(year)
        Una lista de años
    """

    dict_json_year = {}
    for path in path_temp.glob("*.json"):
        path_name_temp = path.name.split("_")
        year_temp = path_name_temp[-1].split(".")
        name_path = path_name_temp[1]
        if name_path not in dict_json_year:
            dict_json_year[name_path] = [year_temp[0]]
        else:
            dict_json_year[name_path].append(year_temp[0])
        

    return dict_json_year

# print(get_list_year(path_temp))


#############################################
############### Funcion Lab ################
#############################################

def get_json_tem(year, type_):

    path_analyzer = Path(__file__).parent
    path_temp = Path(f"{path_analyzer}/temp_")
    queue_id = 6
    if type_ == "customers":
        path_active = Path(
            f"{path_temp}/tickets_customers_by_user_queue_{queue_id}_{year}.json"
        )
    
    elif type_ == "administrators":
        path_active = Path(
            f"{path_temp}/tickets_administrators_queue_{queue_id}_{year}.json"
        )
   
    with path_active.open("r") as f:
        json_active = json.load(f)
        active_temp = json_active["active"]
    
    return active_temp
