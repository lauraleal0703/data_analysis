import json
from pprint import pprint
from pathlib import Path
from typing import TypeVar, List
from typing import Union


path_analyzer = Path(__file__).parent
path_temp = Path(f"{path_analyzer}/temp_data_tickets")


#############################################
############### GET DATA TEMP ################
#############################################


def get_update_date(path_temp: Path) -> dict:
    """Obtener el dia de la ultima actualización
    de los datos

    Parameters
    ---------
    
    Return
    ------
    Dict
    """
    path_active = Path(f"{path_temp}/users_actives.json")
    with path_active.open("r") as f:
        json_active = json.load(f)
        active_temp = json_active["update_date"]
    
    return active_temp


def get_list_year(path_temp: Path, type_:str) -> dict:
    """Obtener una lista con los años que se tiene data

    Parameters
    ---------
    
    Return
    ------
    List(year)
        Una lista de años
    """
    
    dict_json_year = {}
    for path in path_temp.glob("tickets*.json"):
        path_name_temp = path.name.split("_")
        year_temp = path_name_temp[-1].split(".")
        name_path = path_name_temp[1]
        if name_path not in dict_json_year:
            dict_json_year[name_path] = [year_temp[0]]
        else:
            dict_json_year[name_path].append(year_temp[0])
    
    if type_ in dict_json_year:
        return dict_json_year[type_]
    else:
        return []


def get_list_offenses_year(path_temp: Path, type_:str) -> Union[dict, list]:
    """Obtener un dict con los años de las ofensas

    Parameters
    ---------
    
    Return
    ------
    List(year)
        Una lista de años
    """
    
    dict_json_year = {}
    for path in path_temp.glob("tickets_offenses*.json"):
        
        path_name_temp = path.name.split("_")
        year_temp = path_name_temp[-1].split(".")
        name_path = "_".join(path_name_temp[2:-1])
        if name_path not in dict_json_year:
            dict_json_year[name_path] = [year_temp[0]]
        else:
            dict_json_year[name_path].append(year_temp[0])
     
    if type_ in dict_json_year:
        return dict_json_year[type_]
    else:
        return []


def get_tools_json_temp(path_temp: Path, name: str) -> dict:
    """Obtener los json de la carpeta temp

    Parameters
    ---------
    
    Return
    ------
    Dict
    """
    path_active = Path(f"{path_temp}/{name}.json")
    if path_active.exists():
        with path_active.open("r") as f:
            json_active = json.load(f)
            active_temp = json_active["active"]

        return active_temp
        
    return {}

def get_tickets_json_temp(path_temp: Path, type_: str, year: str) -> dict:
    """Obtener los json de la carpeta temp

    Parameters
    ---------
    
    Return
    ------
    Dict
    """

    queue_id = 6
    if type_:
        if type_ == "customers":
            path_active = Path(
                f"{path_temp}/tickets_customers_by_user_queue_{queue_id}_{year}.json"
            )
        
        elif type_ == "administrators":
            path_active = Path(
                f"{path_temp}/tickets_administrators_by_queue_{queue_id}_{year}.json"
            )

        if path_active.exists():
            with path_active.open("r") as f:
                json_active = json.load(f)
                active_temp = json_active["active"]

            return active_temp
    
    return {}


def get_offenses_json_temp(path_temp: Path, type_: str, year: str) -> dict:
    """Obtener los json de la carpeta temp

    Parameters
    ---------
    
    Return
    ------
    Dict
    """

    path_active = Path(
        f"{path_temp}/tickets_offenses_{type_}_{year}.json"
    )
        
    if path_active.exists():
        with path_active.open("r") as f:
            json_active = json.load(f)
            active_temp = json_active["active"]
    
        return active_temp
    
    return {}

    