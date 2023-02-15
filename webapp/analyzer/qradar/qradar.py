import warnings
warnings.filterwarnings("ignore")

import requests
from datetime import datetime


######################################################
#------------Consumo de APIS de QRadar ---------------
######################################################


def curl_qradar(script: str, headers=None, params=None):
    """Función base para las llamadas a QRadar

    Parameters
    ---------
    
    Return
    ------
 
    """

    url_api = "https://172.16.17.10/api"
    r = requests.get(
        f"{url_api}/{script}",
        auth=("lleal", "wn4GQ*ndMHWKif"),
        verify=False,
        headers=headers,
        params=params)
    if r.status_code == 200:
        return r.json()
    else:
        return []


def offenses(headers=None, params=None):
    """siem
    
    Parameters
    ---------
    
    Return
    ------
 
    """

    return curl_qradar("siem/offenses", headers=headers, params=params)


def start_time_offense(id_offense: str):
    """siem --> start_time_offense
    
    Parameters
    ---------
    
    Return
    ------
 
    """
    data_id_offense = offenses(
        params={
            "fields": "start_time",
            "filter": f"id={id_offense}"
        }
    )

    if data_id_offense:
        return  datetime.fromtimestamp(int(data_id_offense[0]["start_time"])/1000)
    
    else:
        return []
