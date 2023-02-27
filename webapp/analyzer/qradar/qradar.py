import warnings
warnings.filterwarnings("ignore")

import time
import requests
from datetime import datetime
import typing as t
from pprint import pprint


######################################################
#------------Consumo de APIS de QRadar ---------------
######################################################

def curl_qradar_get(
        script: str, 
        headers: t.Optional[dict] = None, 
        params: t.Optional[dict] = None
    ) -> dict:
    # def_name = "curl_qradar_get"
    # print(def_name, datetime.today())
    """Función base para las llamadas a QRadar método get"""

    url_api = "https://172.16.17.10/api"
    r = requests.get(
            f"{url_api}/{script}",
            auth = ("lleal", "wn4GQ*ndMHWKif"),
            verify = False,
            headers = headers,
            params = params
        )
    
    # print(def_name, datetime.today())
    return r.json()



def curl_qradar_post(
        script: str, 
        headers: t.Optional[dict] = None, 
        params: t.Optional[dict] = None
    ) -> dict:
    # def_name = "curl_qradar_post"
    # print(def_name, datetime.today())
    """Función base para las llamadas a QRadar metodo post"""

    url_api = "https://172.16.17.10/api"
    r = requests.post(
            f"{url_api}/{script}",
            auth = ("lleal", "wn4GQ*ndMHWKif"),
            verify = False,
            headers = headers,
            params = params
        )
    
    # print(def_name, datetime.today())
    return r.json()


###################--siem--#################################
def offenses(
        headers: t.Optional[dict] = None, 
        params: t.Optional[dict] = None
    )-> dict:
    def_name = "offenses"
    print(def_name, datetime.today())
    """siem
    
    Parameters
    ---------
    En el headers solo se tiene la opción del rango
    headers = {"Range": "items=0-5"}
    Para los params se tienen las opciones de:
    fields, filter, sort. Un ejemplo de su uso sería.
    params={
            "fields": "id,description,start_time,log_sources",
            "filter": "id=59439",
            "sort":"+start_time"
            }
    Return
    ------
 
    """
    print(def_name, datetime.today())
    return curl_qradar_get(
        "siem/offenses", 
        header = headers, 
        params = params
    )


def start_time_offense(id_offense: str):
    """siem --> start_time_offense
    
    Parameters:
    ID de la ofensa
        En el titulo del ticket que se genera en OTRS se tiene el ID 
        de la ofensa, por el cual se puede consultar.
    
    ---------
    
    Return
    ------
    date en formato Datetime, que es el formato de ticket.create_time
    """
    def_name = "start_time_offense"
    print(def_name, datetime.today())

    data_id_offense = offenses(
        params={
            "fields": "start_time",
            "filter": f"id={id_offense}"
        }
    )

    if data_id_offense:
        print(def_name, datetime.today())
        return  datetime.fromtimestamp(
            int(data_id_offense[0]["start_time"])/1000
        )
    
    else:
        print(def_name, datetime.today())
        return []


###################--ariel--#################################


def ariel_searches_post(query_expression: str)-> dict:
    """Crea la consulta con un ID especifico
    
    Parameters:
    query_expression: str
        Es la AQL
    """
    def_name = "ariel_searches_post"
    print(def_name, datetime.today())
    
    create_searches = curl_qradar_post(
                            "ariel/searches", 
                            params={
                                "query_expression": query_expression
                            }
                        )

    print(def_name, datetime.today())
    return str(create_searches["search_id"])


def ariel_results(search_id: str):
    """Toma el ID de la búsqueda y trate los datos que se tienen asociados"""
    def_name = "ariel_results"
    print(def_name, datetime.today())

    """Consulta si la búsqueda esta completa"""
    search = curl_qradar_get(
        f"ariel/searches/{search_id}"
    )
    completed = search["completed"]

    print(".En while.")
    while not completed:
        search = curl_qradar_get(
            f"ariel/searches/{search_id}"
        )
        completed = search["completed"]
        time.sleep(2)
        
    print(def_name, datetime.today())
    return curl_qradar_get(
        f"ariel/searches/{search_id}/results"
    )
