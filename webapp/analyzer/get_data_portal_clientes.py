import json
from pprint import pprint
from pathlib import Path
from typing import TypeVar, List
from typing import Union


path_analyzer = Path(__file__).parent
path_temp = Path(f"{path_analyzer}/temp_portal_clientes")


#####################################################
##########Funciones de Obtención de datos ###########
#####################################################

def get_update_date(path_temp: Path) -> str:
    """Obtener el dia de la ultima actualización
    de los datos

    Parameters
    ---------
    
    Return
    ------
    Date en str
    """
    path_active = Path(f"{path_temp}/customers_by_period.json")
    active_temp = ""
    if path_active.exists():
        with path_active.open("r") as f:
            json_active = json.load(f)
            active_temp = json_active["update_date"]
    
    return active_temp


def get_customers_period(path_temp: Path) -> list:
    """Obtener los customers

    Parameters
    ---------
    
    Return
    ------
    List[customers]
    """
    path_active = Path(f"{path_temp}/customers_by_period.json")
    list_temp = []
    if path_active.exists():
        with path_active.open("r") as f:
            json_active = json.load(f)
            active_temp = json_active["active"]
            list_temp = list(active_temp.keys())
    
    return list_temp


def get_customer_years(
        path_temp: Path, 
        customer_id: str) -> list:
    """Obtener los años activos de un customer

    Parameters
    ---------
    customer_id: str
        ID del customer
    
    Return
    ------
    List[year]
    """
    path_active = Path(f"{path_temp}/customers_by_period.json")
    active_temp = {}
    if path_active.exists():
        with path_active.open("r") as f:
            json_active = json.load(f)
            active_temp = json_active["active"][customer_id]["years_actives"]
            active_temp.reverse()

    return active_temp


def get_tickets_customer_years(
        path_temp: Path, 
        customer_id: str,
        queue_id: int=6) -> list:
    """Obtener los años activos de un customer
    y los tickets gestionados por AS
    Da los datos directos para la gráfica.

    Parameters
    ---------
    customer_id: str
        ID del customer
    
    Return
    ------
    dict{data_x: ...
        data_y: ...}
    """

    years = get_customer_years(path_temp, customer_id)
    data_grah_temp = []
    data_x = []
    for year in years:
        path_active = Path(
            f"{path_temp}/{customer_id}/tickets_{customer_id}_by_queue_{queue_id}_{year}.json"
        )
        if path_active.exists():
            with path_active.open("r") as f:
                json_active = json.load(f)
                active_temp = json_active["active"]["total_year"]
            
                data_grah_temp.append(active_temp)
                data_x.append(year)
    
    total_tickets = sum(data_grah_temp)
    data_grah = [{"name": "Tickets", "data": data_grah_temp}]

    return {"data_x": data_x, "data_y": data_grah, "total_tickets": total_tickets}


def get_customer_months_year(
        path_temp: Path, 
        customer_id: str, 
        year: str, 
        queue_id: int=6) -> dict:
    """Obtener los meses ativos del customer
     en el año indicado. 

    Parameters
    ---------
    customer_id: str
        ID del customer
    year: str
        Año de análisis
    queue_id: int
        En este caso estamos en la cola 6, administradores
    
    Return
    ------
    list[meses]
    """
    path_active = Path(f"{path_temp}/calendar_spanish.json")
    with path_active.open("r") as f:
        json_active = json.load(f)
        calendar = json_active["active"]

    path_customer = Path(
        f"{path_temp}/{customer_id}"
    )

    path_active = Path(
        f"{path_customer}/tickets_{customer_id}_by_queue_{queue_id}_{year}.json"
    )
    
    dict_month = {}
    if path_active.exists():
        with path_active.open("r") as f:
            json_active = json.load(f)
            active_temp = json_active["active"]
    
            months = list(active_temp.keys())
            months.reverse()
            dict_month = {month: calendar[month] for month in months if month in calendar}
        
    return dict_month


def get_tickets_customer_months_year(
        path_temp: Path, 
        customer_id: str,
        year: str,
        queue_id: int=6) -> list:
    """Obtener los meses activos de un customer
    en un año definido y los tickets gestionados por AS
    Da los datos directos para la gráfica.

    Parameters
    ---------
    customer_id: str
        ID del customer
    year: str
        Año de análisis
    queue_id: int
        En este caso estamos en la cola 6, administradores
    
    Return
    ------
    dict{data_x: ...
        data_y: ...}
    """

    months = get_customer_months_year(path_temp, customer_id, year)
    data_grah_temp = []
    data_x = []
    months_actives = {}
    for month in months:
        path_active = Path(
            f"{path_temp}/{customer_id}/tickets_{customer_id}_by_queue_{queue_id}_{year}.json"
        )
        if path_active.exists():
            with path_active.open("r") as f:
                json_active = json.load(f)
                active_temp = json_active["active"][month]["total_month"]
            
                data_grah_temp.append(active_temp)
                data_x.append(months[month])
                months_actives[month] = months[month]
    
    total_tickets = sum(data_grah_temp)
    data_grah = [{"name": "Tickets", "data": data_grah_temp}]

    return {"months_actives": months_actives,
            "data_x": data_x, 
            "data_y": data_grah, 
            "total_tickets": total_tickets}



def get_customer_months_year(
        path_temp: Path, 
        customer_id: str, 
        year: str, 
        queue_id: int=6) -> dict:
    """Obtener los meses ativos del customer
     en el año indicado. 

    Parameters
    ---------
    customer_id: str
        ID del customer
    year: str
        Año de análisis
    queue_id: int
        En este caso estamos en la cola 6, administradores
    
    Return
    ------
    list[meses]
    """
    path_active = Path(f"{path_temp}/calendar_spanish.json")
    with path_active.open("r") as f:
        json_active = json.load(f)
        calendar = json_active["active"]

    path_customer = Path(
        f"{path_temp}/{customer_id}"
    )

    path_active = Path(
        f"{path_customer}/tickets_{customer_id}_by_queue_{queue_id}_{year}.json"
    )
    
    dict_month = {}
    if path_active.exists():
        with path_active.open("r") as f:
            json_active = json.load(f)
            active_temp = json_active["active"]
    
            months = list(active_temp.keys())
            months.reverse()
            dict_month = {month: calendar[month] for month in months if month in calendar}
        
    return dict_month

# print(get_tickets_customer_months_year(path_temp, "AAN", "2023"))