try:
    from .qradar import qradar
    from webapp.analyzer import get_otrs
except:
    from qradar import qradar
    import get_otrs

import orjson
import typing as t
from pathlib import Path
from pprint import pprint
from datetime import datetime
from googletrans import Translator
from dateutil.relativedelta import relativedelta

import logging
logging.basicConfig(
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
        level=logging.DEBUG
    )


###############################################################################
################################--QRadar--#####################################
################################--SOPORTE--####################################
###############################################################################

"""Resumen:
 Evertec: 
    *Solange ve: IPS (Firepower) y WAF (A10)
    *Jose ve: PAM
"""
dates = ["2023-02-01", "2023-01-01", "2022-12-01"]
def dates_actives() -> list:
    """OJO, MEJOR ACTUALIZAR MANUAL
    Hay información de 3 meses atrás en QRadar"""
    def_name = "dates_actives"
    logging.debug(def_name)
    
    month_init = datetime.today() - relativedelta(months=4)
    date_init_ = f"{month_init.year}-{month_init.month}-01"
    date_init = datetime.strptime(date_init_, "%Y-%m-%d")
    dict_date = {}
    i = 1
    while i < 5:
        date_temp = date_init + relativedelta(months=1)
        dict_date[i] = {
            "date": datetime.strftime(date_temp, "%Y-%m-%d"), 
            "date_name": datetime.strftime(date_temp, "%m-%Y")
        }
        i += 1
        date_init = date_temp

    dict_date = sorted(
        dict_date.items(),
        key=lambda x:x[0], 
        reverse=True
    )

    logging.debug(def_name)
    return dict_date


def aql(
    customer_id: str,
    date: str,
    aql_name: str
) -> str:
    """Las AQL"""
    def_name = "aql"
    logging.debug(def_name)

    start = date
    stop = datetime.strptime(date, "%Y-%m-%d") + relativedelta(months=1)
    stop = datetime.strftime(stop, "%Y-%m-%d")
    
    if customer_id == "AAN":
        if aql_name == "Informe_Arbor_1":
            Informe_Arbor_1 = f'''SELECT QIDNAME(qid) AS 'Nombre de suceso', UniqueCount(logSourceId) AS 'Origen de registro (Recuento exclusivo)', SUM("eventCount") AS 'Recuento de sucesos (Suma)', MIN("startTime") AS 'Hora de inicio (Mínimo)', UniqueCount(category) AS 'Categoría de nivel bajo (Recuento exclusivo)', UniqueCount("sourceIP") AS 'IP de origen (Recuento exclusivo)', UniqueCount("sourcePort") AS 'Puerto de origen (Recuento exclusivo)', UniqueCount("destinationIP") AS 'IP de destino (Recuento exclusivo)', UniqueCount("destinationPort") AS 'Puerto de destino (Recuento exclusivo)', COUNT(*) AS 'Recuento' from events where logSourceId='2277' GROUP BY qid order by "Recuento" desc start '{start} 00:00' stop '{stop} 00:00'
            '''
            logging.debug(def_name)
            return Informe_Arbor_1
        
        if aql_name == "TOP_10_Paises":
            TOP_10_Paises = f'''SELECT "sourceGeographicLocation" AS 'País/región geográfica de origen', UniqueCount(qid) AS 'Nombre de suceso (Recuento exclusivo)', UniqueCount(logSourceId) AS 'Origen de registro (Recuento exclusivo)', SUM("eventCount") AS 'Recuento de sucesos (Suma)', MIN("startTime") AS 'Hora de inicio (Mínimo)', UniqueCount(category) AS 'Categoría de nivel bajo (Recuento exclusivo)', UniqueCount("sourceIP") AS 'IP de origen (Recuento exclusivo)', UniqueCount("sourcePort") AS 'Puerto de origen (Recuento exclusivo)', UniqueCount("destinationIP") AS 'IP de destino (Recuento exclusivo)', UniqueCount("destinationPort") AS 'Puerto de destino (Recuento exclusivo)', COUNT(*) AS 'Recuento' from events where ( logSourceId='2277' AND qid != '38750074' ) GROUP BY "sourceGeographicLocation" order by "Recuento de sucesos (Suma)" desc start '{start} 00:00' stop '{stop} 00:00'
            '''
            logging.debug(def_name)
            return TOP_10_Paises
    
    if customer_id == "SURA":
        if aql_name == "Eventos_totales_Log_Source":
            Eventos_totales_Log_Source = f'''SELECT logsourcename(logSourceId) AS 'Origen de registro', SUM("eventCount") AS 'Recuento de sucesos (Suma)', MIN("startTime") AS 'Hora de inicio (Mínimo)', COUNT(*) AS 'Recuento' from events where "domainId"='11' GROUP BY logSourceId order by "Recuento" desc start '{start} 00:00' stop '{stop} 00:00'
            '''
            logging.debug(def_name)
            return Eventos_totales_Log_Source
        
        if aql_name == "Total_Accept_per_dominio_Pais":
            Total_Accept_per_dominio_Pais = f'''SELECT logsourcename(logSourceId) AS 'Origen de registro', "ClientRequestHost" AS 'ClientRequestHost (personalizado)', "ClientCountry" AS 'ClientCountry (personalizado)', UniqueCount(logSourceId) AS 'Origen de registro (Recuento exclusivo)', SUM("eventCount") AS 'Recuento de sucesos (Suma)', COUNT(*) AS 'Recuento' from events where ( "FirewallMatchesActions" != '["block"]' AND "domainId"='11' ) GROUP BY "ClientRequestHost", "ClientCountry" order by "Recuento" desc start '{start} 00:00' stop '{stop} 00:00'
            '''
            logging.debug(def_name)
            return Total_Accept_per_dominio_Pais

         
        if aql_name == "Detalle_drop":
            Detalle_drop = f'''SELECT logsourcename(logSourceId) AS 'Origen de registro', "ClientIP" AS 'ClientIP (personalizado)', "ClientCountry" AS 'ClientCountry (personalizado)', "ClientRequestHost" AS 'ClientRequestHost (personalizado)', "ClientRequestPath" AS 'ClientRequestPath (personalizado)', UniqueCount(logSourceId) AS 'Origen de registro (Recuento exclusivo)', UniqueCount("FirewallMatchesActions") AS 'FirewallMatchesActions (personalizado) (Recuento exclusivo)', SUM("eventCount") AS 'Recuento de sucesos (Suma)', MIN("startTime") AS 'Hora de inicio (Mínimo)', COUNT(*) AS 'Recuento' from events where ( "FirewallMatchesActions"='["block"]' AND (logSourceId='3612') or (logSourceId='3613') or (logSourceId='3663') or (logSourceId='3664') or (logSourceId='3665') ) GROUP BY "ClientIP", "ClientCountry", "ClientRequestHost", "ClientRequestPath" order by "Recuento" desc start '{start} 00:00' stop '{stop} 00:00'
            '''
            ##Excepción ENERO 2023
            # Detalle_drop = '''SELECT logsourcename(logSourceId) AS 'Origen de registro', "ClientIP" AS 'ClientIP (personalizado)', "ClientCountry" AS 'ClientCountry (personalizado)', "ClientRequestHost" AS 'ClientRequestHost (personalizado)', "ClientRequestPath" AS 'ClientRequestPath (personalizado)', UniqueCount(logSourceId) AS 'Origen de registro (Recuento exclusivo)', UniqueCount("FirewallMatchesActions") AS 'FirewallMatchesActions (personalizado) (Recuento exclusivo)', SUM("eventCount") AS 'Recuento de sucesos (Suma)', MIN("startTime") AS 'Hora de inicio (Mínimo)', COUNT(*) AS 'Recuento' from events where ( ( ("ClientIP"<'143.198.234.131') or ("ClientIP">'143.198.234.131' and "ClientIP"<'165.227.99.174') or ("ClientIP">'165.227.99.174' and "ClientIP"<'167.172.245.180') or ("ClientIP">'167.172.245.180') AND "FirewallMatchesActions"='["block"]' ) AND (logSourceId='3612') or (logSourceId='3613') or (logSourceId='3663') or (logSourceId='3664') or (logSourceId='3665') ) GROUP BY "ClientIP", "ClientCountry", "ClientRequestHost", "ClientRequestPath" order by "Recuento" desc start '2023-01-01 00:00' stop '2023-01-31 23:59'
            # '''
            logging.debug(def_name)
            return Detalle_drop
        
    if customer_id == "EVERTEC":
        if aql_name == "EVERTEC_LLEAL_Test2":
            EVERTEC_LLEAL_Test2 = f'''SELECT QIDNAME(qid) as 'Nombre de suceso',"From" as 'From (personalizado)',"Impact" as 'Impact (personalizado)',"eventCount" as 'Recuento de sucesos',"startTime" as 'Hora de inicio',"sourceIP" as 'IP de origen',categoryname(category) as 'Categoría de nivel bajo',"Priority" as 'Priority (personalizado)',"sourcePort" as 'Puerto de origen',"destinationPort" as 'Puerto de destino',"destinationIP" as 'IP de destino',"Classification" as 'Classification (personalizado)' from events where ("creEventList"='120176') or ("creEventList"='120180') or ("creEventList"='120181') or ("creEventList"='120182') or ("creEventList"='125185') or ("creEventList"='125234') or ("creEventList"='125444') or ("creEventList"='125445') or ("creEventList"='125446') or ("creEventList"='125447') or ("creEventList"='125448') or ("creEventList"='125449') or ("creEventList"='125450') or ("creEventList"='125805') or ("creEventList"='125806') or ("creEventList"='125807') order by "startTime" desc start '{start} 00:00' stop '{stop} 00:00'
            '''
            logging.debug(def_name)
            return EVERTEC_LLEAL_Test2


def get_json(
    def_name: str,
    customer_id: str,
    date: str,
    aql_name: str,
    refresh: bool = False
) -> dict:
    """Funcion que permite traer la data de QRadar y guardarla
    en data_qradar para que lueego la consulta sea más rápida"""
    
    """Siempre se debe comprobar el directorio"""
    path_data_qradar: Path = Path(__file__).parent/"data_qradar"
    if not path_data_qradar.exists():
        path_data_qradar.mkdir()
    
    current_path = path_data_qradar / f"{date}_{customer_id}_{def_name}.json"
    
    if refresh and current_path.exists():
        logging.info("Borrando json")
        current_path.unlink()

    if not current_path.exists():
        logging.info(f"Creando JSON {current_path}")
        create_id_searches = qradar.ariel_searches_post(
            query_expression = aql(
                customer_id = customer_id,
                date = date,
                aql_name = aql_name
            )
        )
        data = {"data": qradar.ariel_results(
            search_id = create_id_searches
            ),
            "current_date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }
        current_path.touch()
        f = current_path.open("wb")
        f.write(orjson.dumps(data))
        f.close()
    else:
        logging.info(f"Abriendo JSON {current_path}")
        f = open(str(current_path), "rb")
        data = orjson.loads(f.read())

    if "data" not in data:
        data = {
            "data": data,
            "current_date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }
    
    if len(data["data"]["events"]) == 0:
        logging.error(def_name)
        return {}
    
    logging.info(f'TOTAL DE EVENTOS {def_name} -> Total: {len(data["data"]["events"])}')
    # logging.info("EVENTOS DEL TIPO")
    # pprint(data["events"][0])
    return data


###############################################################################
##############################--Cloudflare--###################################
###############################################################################


def customers_cloudflare():
    """Los clientes que cuentan con el servicio Arbor son:
    * AFP capital  es SURA
    * SBPay 
    * Adaptive Security
    * UDLA

    UPD NO ES QRadar
    """
    def_name = "customers_cloudflare"
    logging.debug(def_name)
    customers = get_otrs.customers_actives()

    customers_cloudflare = [
        "SURA",
        "SBPay",
        "UDLA",
        "Adaptive Security"
    ]
    
    dict_customers_cloudflare = {
        customer: customers[customer] for customer in customers_cloudflare
    }

    logging.debug(def_name)
    return dict_customers_cloudflare
# print(customers_cloudflare())


def event_total_log_source(
    customer_id: str,
    date: str,
    aql_name: str = "Eventos_totales_Log_Source",
    refresh: bool = False
) -> dict:
    """Datos para la grafica de 
    """
    def_name = f"eventos_totales_Log_Source"
    logging.debug(def_name)

    path_data_qradar: Path = Path(__file__).parent/"data_qradar"
    if not path_data_qradar.exists():
        path_data_qradar.mkdir()
    
    current_path = path_data_qradar / f"{date}_{customer_id}_{def_name}_dict_info_final.json"
    if refresh and current_path.exists():
        logging.info("Borrando json")
        current_path.unlink()

    if not current_path.exists():
        logging.info(f"Creando JSON {current_path}")

        calendar = get_otrs.calendar_spanish()
        calendar = calendar["calendar_num"]
        date_ = datetime.strptime(date, "%Y-%m-%d")
        year = date_.year
        name_date = date_.month
        name_date = calendar[name_date]

        data = get_json(
            def_name = def_name,
            customer_id = customer_id,
            date = date,
            aql_name = aql_name
        )
    
        total = 0
        dict_total_events = {}
        for event in data["data"]["events"]:
            name_event = event["Origen de registro"]
            recuento_event =  int(event["Recuento de sucesos (Suma)"])
            total += recuento_event
            dict_total_events[name_event] = recuento_event
        
        dict_total_events["Total"] = '{:,}'.format(total).replace(',','.')
        data = {
            "dict_total_events": dict_total_events,
            "name_date": name_date,
            "year": year,
            "current_date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }
        current_path.touch()
        f = current_path.open("wb")
        f.write(orjson.dumps(data))
        f.close()
    else:
        logging.info(f"Abriendo JSON {current_path}")
        f = open(str(current_path), "rb")
        data = orjson.loads(f.read())

    logging.debug(def_name)
    return data
# for date in dates:
#     print("date", date)
#     print(event_total_log_source("SURA", date))


def total_accept_per_dominio_pais(
    customer_id: str,
    date: str,
    aql_name: str = "Total_Accept_per_dominio_Pais",
    refresh: bool = False
) -> dict:
    """Datos para la grafica de 
    """
    def_name = f"total_accept_per_dominio_pais"
    logging.debug(def_name)
    
    calendar = get_otrs.calendar_spanish()
    calendar = calendar["calendar_num"]
    date_ = datetime.strptime(date, "%Y-%m-%d")
    year = date_.year
    name_date = date_.month
    name_date = calendar[name_date]

    path_data_qradar: Path = Path(__file__).parent/"data_qradar"
    if not path_data_qradar.exists():
        path_data_qradar.mkdir()

    current_path = path_data_qradar / f"{date}_{customer_id}_{def_name}_dict_info_final.json"
    if not current_path.exists():
        logging.info(f"Creando JSON {current_path}")

        data = get_json(
            def_name = def_name,
            customer_id = customer_id,
            date = date,
            aql_name = aql_name
        )

        paises = qradar.nombre_pais()
        total = 0
        dict_total_events = {}
        dict_events_dominio_pais = {}
        for event in data["data"]["events"]:
            if not event["ClientCountry (personalizado)"]:
                event["ClientCountry (personalizado)"] = "None"
            pais = paises[event["ClientCountry (personalizado)"]]
            name_dominio = event["Origen de registro"]
            recuento_event =  int(event["Recuento de sucesos (Suma)"])
            total += recuento_event
            
            if name_dominio not in dict_events_dominio_pais:
                dict_events_dominio_pais[name_dominio] = {
                    "paises": {},
                    "Total": recuento_event
                }
            else:
                dict_events_dominio_pais[name_dominio]["Total"] += recuento_event

            if pais not in dict_events_dominio_pais[name_dominio]["paises"]:
                dict_events_dominio_pais[name_dominio]["paises"][pais] = recuento_event
            else:
                dict_events_dominio_pais[name_dominio]["paises"][pais] += recuento_event
            
            if name_dominio not in dict_total_events:
                dict_total_events[name_dominio] = recuento_event
            else:
                dict_total_events[name_dominio] += recuento_event
        
        dict_total_events["Total"] = '{:,}'.format(total).replace(',','.')

        data = {
            "dict_total_events": dict_total_events,
            "dict_events_dominio_pais": dict_events_dominio_pais,
            "name_date": name_date,
            "year": year
        }
        current_path.touch()
        f = current_path.open("wb")
        f.write(orjson.dumps(data))
        f.close()
    else:
        logging.info(f"Abriendo JSON {current_path}")
        f = open(str(current_path), "rb")
        data = orjson.loads(f.read())


    logging.debug(def_name)
    return data
# for date in dates:
#     print("date", date)
#     pprint(total_accept_per_dominio_pais("SURA", date))


def detalle_drop(
    customer_id: str,
    date: str,
    aql_name: str = "Detalle_drop",
    refresh: bool = False
) -> dict:
    """Datos para la grafica de 
    """
    def_name = f"detalle_drop"
    logging.debug(def_name)

    calendar = get_otrs.calendar_spanish()
    calendar = calendar["calendar_num"]
    date_ = datetime.strptime(date, "%Y-%m-%d")
    year = date_.year
    name_date = date_.month
    name_date = calendar[name_date]

    path_data_qradar: Path = Path(__file__).parent/"data_qradar"
    if not path_data_qradar.exists():
        path_data_qradar.mkdir()

    current_path = path_data_qradar / f"{date}_{customer_id}_{def_name}_dict_info_final.json"
    if not current_path.exists():
        logging.info(f"Creando JSON {current_path}")

        data = get_json(
            def_name = def_name,
            customer_id = customer_id,
            date = date,
            aql_name = aql_name
        )
        
        paises = qradar.nombre_pais()
        total = 0
        dict_total_events = {}
        dict_events_dominio_pais = {}
        for event in data["data"]["events"]:
            if not event["ClientCountry (personalizado)"]:
                event["ClientCountry (personalizado)"] = "None"
            pais = paises[event["ClientCountry (personalizado)"]]
            name_dominio = event["Origen de registro"]
            recuento_event =  int(event["Recuento de sucesos (Suma)"])
            total += recuento_event
            
            if name_dominio not in dict_events_dominio_pais:
                dict_events_dominio_pais[name_dominio] = {
                    "paises": {},
                    "Total": recuento_event
                }
            else:
                dict_events_dominio_pais[name_dominio]["Total"] += recuento_event

            if pais not in dict_events_dominio_pais[name_dominio]["paises"]:
                dict_events_dominio_pais[name_dominio]["paises"][pais] = recuento_event
            else:
                dict_events_dominio_pais[name_dominio]["paises"][pais] += recuento_event
            
            if name_dominio not in dict_total_events:
                dict_total_events[name_dominio] = recuento_event
            else:
                dict_total_events[name_dominio] += recuento_event
        
        dict_total_events["Total"] = '{:,}'.format(total).replace(',','.')

        data =  {
            "dict_total_events": dict_total_events,
            "dict_events_dominio_pais": dict_events_dominio_pais,
            "name_date": name_date,
            "year": year
        }
        current_path.touch()
        f = current_path.open("wb")
        f.write(orjson.dumps(data))
        f.close()
    else:
        logging.info(f"Abriendo JSON {current_path}")
        f = open(str(current_path), "rb")
        data = orjson.loads(f.read())


    logging.debug(def_name)
    return data
# for date in dates:
#     print("date", date)
#     print(detalle_drop("SURA", date))


def tabla_reque_acep_boque_per_dominio(
    customer: str,
    date: str,
    refresh: bool = False
) -> dict:
    """Datos para la 
    """
    def_name = "tabla_reque_acep_boque_per_dominio"
    logging.debug(def_name)

    total_requirements_ = event_total_log_source(
        customer = customer,
        date = date
    )
    logging.info("total_requirements")
    pprint(total_requirements_)
    total_requirements = total_requirements_["dict_total_events"]
    logging.info("total_requirements_")
    pprint(total_requirements)

    requirements_accep = total_accept_per_dominio_pais(
        customer = customer,
        date = date
    )
    logging.info("requirements_accep")
    # pprint(requirements_accep)
    
    total_requirements_accep = requirements_accep["dict_total_events"]
    logging.info("total_requirements_accep")
    pprint(total_requirements_accep)

    requirements_drop = detalle_drop(
         customer = customer,
        date = date
    )
    logging.info("requirements_drop")
    # pprint(requirements_drop)
    
    total_requirements_drop = requirements_drop["dict_total_events"]
    logging.info("total_requirements_drop")
    pprint(total_requirements_drop)
    
    dict_dominio ={}
    for dominio in total_requirements:
        if dominio == "Total":
             dict_dominio[dominio] = {
                "Total de Requerimientos": total_requirements[dominio], 
                "Requerimientos Aceptados": total_requirements_accep[dominio],
                "Requerimientos Bloqueados": total_requirements_drop[dominio]
            }
        dict_dominio[dominio] = {
            "Total de Requerimientos": total_requirements[dominio], 
            "Requerimientos Aceptados": total_requirements_accep[dominio],
            "Requerimientos Bloqueados": total_requirements_drop[dominio]
        }
        # dict_dominio[dominio] = {
        #     "Total de Requerimientos": '{:,}'.format(total_requirements[dominio]).replace(',','.'), 
        #     "Requerimientos Aceptados": '{:,}'.format(total_requirements_accep[dominio]).replace(',','.'),
        #     "Requerimientos Bloqueados": '{:,}'.format(total_requirements_drop[dominio]).replace(',','.')
        # }

    
    logging.info("TABLA 1")
    logging.info(dict_dominio)

    total_requirements_drop_paises = requirements_drop["dict_events_dominio_pais"]
    total_requirements_accep_paises = requirements_accep["dict_events_dominio_pais"]

    for dominio in total_requirements:
        if dominio != "Total":
            print(dominio)
            a = total_requirements_drop_paises[dominio]["paises"]
            a = sorted(
                a.items(),
                key=lambda x:x[1], 
                reverse=True
            )
            print(a)
            b = total_requirements_accep_paises[dominio]["paises"]
            b = sorted(
                b.items(),
                key=lambda x:x[1], 
                reverse=True
            )
            print(b)


    logging.debug(def_name)
    return dict_dominio
# for date in dates:
#     print("date", date)
#     pprint(tabla_reque_acep_boque_per_dominio("SURA", date))


###############################################################################
##############################--Firepower--###################################
###############################################################################

def customers_firepower():
    """Los clientes que cuentan con el servicio son:
    * EVERTEC
    """
    def_name = "customers_firepower"
    logging.debug(def_name)
    customers = get_otrs.customers_actives()

    customers_firepower = [
        "EVERTEC"
    ]
    
    dict_customers_firepower = {
        customer: customers[customer] for customer in customers_firepower
    }
    
    logging.debug(def_name)
    return dict_customers_firepower


def create_dict_top3_top_10(
    clasification_top: str,
    ips_evertec: list,
    dict_base: dict,
    ip: tuple,
    position_top3: str,
    position_top10: str
):
    """Llenar el dict"""
    if ip[0] in ips_evertec:
        identificacion = "Red Evertec"
    else:
        identificacion = "Desconodida"
    
    if position_top3 not in dict_base:
        dict_base[position_top3] = {}
    
    if clasification_top not in dict_base[position_top3]:
        dict_base[position_top3][clasification_top] = {}

    if "ips_destino" not in dict_base[position_top3][clasification_top]:
        dict_base[position_top3][clasification_top]["ips_destino"] = {}

    if "ips_destino" not in dict_base[position_top3][clasification_top]:
        dict_base[position_top3][clasification_top]["ips_destino"] = {}
    
    if position_top10 not in dict_base[position_top3][clasification_top]["ips_destino"]:
        dict_base[position_top3][clasification_top]["ips_destino"][position_top10] = {}

    if "ips" not in dict_base[position_top3][clasification_top]["ips_destino"][position_top10]:
        dict_base[position_top3][clasification_top]["ips_destino"][position_top10]["ips"] = {}

    if ip[0] not in dict_base[position_top3][clasification_top]["ips_destino"][position_top10]["ips"]:
        dict_base[position_top3][clasification_top]["ips_destino"][position_top10]["ips"][ip[0]] = {
            "identification": identificacion,
            "total": ip[1]["total"],
            "ips_origen": ip[1]["ips_origen"]
        }
    
    # print(dict_base.keys())


def create_data_table(dict_base: dict) -> dict:
    """Crear el dict para la tabla"""
    dict_info_final = {}
    for pos_final in dict_base:
        dict_info_final[pos_final] = {}
        for clas_ in dict_base[pos_final]:
            dict_info_final[pos_final][clas_] = {}
            for top10_ip in dict_base[pos_final][clas_]["ips_destino"]:
                dict_info_final[pos_final][clas_][top10_ip] = {}
                for ip in dict_base[pos_final][clas_]["ips_destino"][top10_ip]["ips"]:
                    ip = str(ip)
                    dict_info_final[pos_final][clas_][top10_ip][ip] = {
                        "Identificación/Riesgo": dict_base[pos_final][clas_]["ips_destino"][top10_ip]["ips"][ip]["identification"],
                        "Cantidad de eventos": dict_base[pos_final][clas_]["ips_destino"][top10_ip]["ips"][ip]["total"],
                        "ips_origen": {}
                    }

                    ips_origen = dict_base[pos_final][clas_]["ips_destino"][top10_ip]["ips"][ip]["ips_origen"]
                    ips_origen_desc = sorted(
                        ips_origen.items(),
                        key=lambda x:x[1], 
                        reverse=True
                    )

                    for pos_origen, ip_origen_ in enumerate(ips_origen_desc):
                        ip_origen_temp = str(ip_origen_[0])
                        # risk = qradar.curl_score_ip_get(ip=ip_origen_temp)
                        riesgo = "Por calcular"
                        # risk = 1
                        # if risk < int(4):
                        #     riesgo = f"Desconocido/Bajo({risk})"
                        # if risk >= int(4) and risk < int(7):
                        #     riesgo = f"Desconocido/Medio({risk})"
                        # if risk >= int(7):
                        #     riesgo = f"Desconocido/Alto({risk})"
                        data_ = dict_base[pos_final][clas_]["ips_destino"][top10_ip]["ips"][ip]["ips_origen"][ip_origen_temp]
                        dict_info_final[pos_final][clas_][top10_ip][ip]["ips_origen"][pos_origen+1] = {}
                        dict_info_final[pos_final][clas_][top10_ip][ip]["ips_origen"][pos_origen+1][ip_origen_temp] = {
                            "Cantidad de eventos": data_,
                            "Identificación/Riesgo": riesgo
                        }
    # print(dict_info_final.keys())
    return dict_info_final


def total_firepower(
    customer_id: str,
    date: str,
    aql_name: str = "EVERTEC_LLEAL_Test2",
    refresh: bool = False
) -> dict:
    """Datos para la grafica de 
    """
    def_name = f"total_firepower"
    logging.debug(def_name)
    
    calendar = get_otrs.calendar_spanish()
    calendar = calendar["calendar_num"]
    date_ = datetime.strptime(date, "%Y-%m-%d")
    year = date_.year
    name_date = date_.month
    name_date = calendar[name_date]

    data = get_json(
        def_name = def_name,
        customer_id = customer_id,
        date = date,
        aql_name = aql_name,
        refresh = refresh
    )

    total = 0
    dict_clasifications = {}
    dict_clasifications_ip = {}
    for event in data["data"]["events"]:
        clasification = event["Classification (personalizado)"]
        recuento_event =  int(event["Recuento de sucesos"])
        if clasification not in dict_clasifications:
            dict_clasifications[clasification] = recuento_event
        else: 
            dict_clasifications[clasification] += recuento_event
        
        ip_destino = event['IP de destino']
        ip_origen = event['IP de origen']
        if clasification not in dict_clasifications_ip:
            dict_clasifications_ip[clasification] = {"ips_destino": {}}
        
        if ip_destino not in dict_clasifications_ip[clasification]["ips_destino"]:
            dict_clasifications_ip[clasification]["ips_destino"][ip_destino] = {
                "ips_origen": {ip_origen: recuento_event},
                "total": recuento_event
            }  
        else:
            dict_clasifications_ip[clasification]["ips_destino"][ip_destino]["total"] += recuento_event
        
        if ip_origen not in dict_clasifications_ip[clasification]["ips_destino"][ip_destino]["ips_origen"]:
            dict_clasifications_ip[clasification]["ips_destino"][ip_destino]["ips_origen"][ip_origen] = recuento_event
        else:
            dict_clasifications_ip[clasification]["ips_destino"][ip_destino]["ips_origen"][ip_origen] += recuento_event
        
        total += recuento_event
    dict_clasifications["Total"] = total

    dict_clasifications_desc = sorted(
        dict_clasifications.items(),
        key=lambda x:x[1], 
        reverse=True
    )

    data_grah_x = []
    data_grah_y_temp = []
    data_grah_y_temp_percentage = []
    for value in dict_clasifications_desc[1:]:
        data_grah_x.append(value[0])
        data_grah_y_temp.append(value[1])
        data_grah_y_temp_percentage.append((value[1]*100)/dict_clasifications["Total"])

    data_grah_y = [{"name": "Eventos", "data": data_grah_y_temp}]
    data_grah_y_percentage = [{"name": "Eventos", "data": data_grah_y_temp_percentage}]
    total = '{:,}'.format(total).replace(',','.')
    
    data_grah = {
        "data_grah_x": data_grah_x,
        "data_grah_y": data_grah_y,
        "total": total
    }

    data_grah_percentage = {
        "data_grah_x": data_grah_x,
        "data_grah_y": data_grah_y_percentage,
        "total": total
    }

    clasificationes_top = []
    for pos, clasification_ in enumerate(dict_clasifications_desc):
        if pos == 0:
            continue
        clasificationes_top.append(clasification_[0])
        
    logging.info(f"clasificationes_top {len(clasificationes_top)}")
    ips_evertec = qradar.ips_evertec()
    dict_clasification_top3_top_10 = {}
    dict_clasification_all_top = {}
    for position_top3, clasification_top in enumerate(clasificationes_top):
        position_top3 = str(position_top3+1)
        ips_destino = dict_clasifications_ip[clasification_top]["ips_destino"]
        ips_destino_desc = sorted(
            ips_destino.items(),
            key=lambda x:x[1]["total"], 
            reverse=True
        )
        
        for position_top10, ip in enumerate(ips_destino_desc):
            position_top10 = str(position_top10+1)
            create_dict_top3_top_10(
                clasification_top = clasification_top,
                ips_evertec = ips_evertec,
                dict_base = dict_clasification_all_top,
                ip = ip,
                position_top3 = position_top3,
                position_top10 = position_top10
            )
                
            if position_top3 > "3":
                continue
            if position_top10 > "9":
                continue
            
            create_dict_top3_top_10(
                clasification_top = clasification_top,
                ips_evertec = ips_evertec,
                dict_base = dict_clasification_top3_top_10,
                ip = ip,
                position_top3 = position_top3,
                position_top10 = position_top10
            )
                    
        table_top = create_data_table(
            dict_base = dict_clasification_top3_top_10
        )

        table_all = create_data_table(
            dict_base = dict_clasification_all_top
        )  

    return {
        "data_grah_percentage": data_grah_percentage,
        "data_grah": data_grah,
        "table_top": table_top,
        "table_all": table_all,
        "name_date": name_date,
        "year": year,
        "current_date": data["current_date"]
    } 
# for date in dates:
#     print("date", date)
#     pprint(total_firepower(customer = "EVERTEC", date = date))


###############################################################################
#################################--Arbor--#####################################
###############################################################################


def customers_arbor():
    """Los clientes que cuentan con el servicio Arbor son:
    * AAN
    """
    def_name = "customers_arbor"
    logging.debug(def_name)

    customers = get_otrs.customers_actives()
    customers_arbor = ["AAN"]
    
    dict_customers_arbor = {
        customer: customers[customer] for customer in customers_arbor
    }

    logging.debug(def_name)
    return dict_customers_arbor


def blocked_events(
    customer_id: str,
    date: str,
    aql_name: str = "Informe_Arbor_1",
    refresh: bool = False
) -> dict:
    """Datos para la grafica de eventos bloquedos del informe de Arbor
    https://www.highcharts.com/demo/pie-basic
    """
    def_name = f"blocked_events"
    
    path_data_qradar: Path = Path(__file__).parent/"data_qradar"
    if not path_data_qradar.exists():
        path_data_qradar.mkdir()
    
    current_path = path_data_qradar / f"{date}_{customer_id}_{def_name}_dict_info_final.json"
    if refresh and current_path.exists():
        logging.info("Borrando json")
        current_path.unlink()
        current_path_all =  path_data_qradar / f"{date}_{customer_id}_{def_name}.json"
        current_path_all.unlink()

    if not current_path.exists():
        logging.info(f"Creando JSON {current_path}")

        calendar = get_otrs.calendar_spanish()
        calendar = calendar["calendar_num"]
        date_ = datetime.strptime(date, "%Y-%m-%d")
        year = date_.year
        name_date = date_.month
        name_date = calendar[name_date]

        data = get_json(
            def_name = def_name,
            customer_id = customer_id,
            date = date,
            aql_name = aql_name
        )

        data_grah_torta = {
            "data_grah": [{
                "name": "Brands",
                "colorByPoint": True,
                "data": []
            }],
            "total": 0,
            "name_date": name_date,
            "year": year
        }
        data_grah_torta_percentage = {
            "data_grah": [{
                "name": "Brands",
                "colorByPoint": True,
                "data": []
            }],
            "total": 0,
            "name_date": name_date,
            "year": year
        }
        translator = Translator()
        total = 0
        dict_events = {}
        for event in data["data"]["events"]:
            name_event = event["Nombre de suceso"]
            name_event = translator.translate(name_event, dest="es")
            name_event = name_event.text
            recuento_event =  event["Recuento de sucesos (Suma)"]
            total += int(recuento_event)
            dict_events[name_event] = recuento_event
        
        dict_events["Total"] = total

        dict_events_desc = sorted(
            dict_events.items(),
            key=lambda x:x[1], 
            reverse=True
        )

        data_grah_x = []
        data_grah_y_temp = []
        data_grah_y_temp_percentage = []
        for clasifi in dict_events_desc[1:]:
            data_grah_x.append(clasifi[0])
            data_grah_y_temp.append(int(clasifi[1]))
            data_grah_y_temp_percentage.append(int(clasifi[1]*100)/dict_events["Total"])

        data_grah_y = [{"name": "Eventos", "data": data_grah_y_temp}]
        data_grah_y_percentage =  [{"name": "Eventos", "data": data_grah_y_temp_percentage}]
        
        total = '{:,}'.format(total).replace(',','.')

        data_grah_barras = {
            "data_grah_x": data_grah_x,
            "data_grah_y": data_grah_y,
            "total": total,
            "name_date": name_date,
            "year": year
        }

        data_grah_barras_percentage = {
            "data_grah_x": data_grah_x,
            "data_grah_y": data_grah_y_percentage,
            "total": total,
            "name_date": name_date,
            "year": year
        }

        for pos, event_ in enumerate(dict_events_desc[1:]):
            if pos == 0:
                data_grah_temp = {
                    "name": event_[0],
                    "y": event_[1],
                    "sliced": True,
                    "selected": True
                }
                data_grah_temp_percentage = {
                    "name": event_[0],
                    "y": (event_[1]*100)/dict_events["Total"],
                    "sliced": True,
                    "selected": True
                }
            else:
                data_grah_temp = {
                    "name": event_[0],
                    "y": event_[1]
                }
                data_grah_temp_percentage = {
                    "name": event_[0],
                    "y": (event_[1]*100)/dict_events["Total"]
                }
            
            data_grah_torta["data_grah"][0]["data"].append(data_grah_temp)
            data_grah_torta["total"] = total
            data_grah_torta_percentage["data_grah"][0]["data"].append(data_grah_temp_percentage)
            data_grah_torta_percentage["total"] = total
        
        data_qradar =  {
            "total": dict_events["Total"],
            "data_grah_torta": data_grah_torta,
            "data_grah_torta_percentage": data_grah_torta_percentage,
            "data_grah_barras": data_grah_barras,
            "data_grah_barras_percentage": data_grah_barras_percentage,
            "current_date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }
        current_path.touch()
        f = current_path.open("wb")
        f.write(orjson.dumps(data_qradar))
        f.close()
    else:
        logging.info(f"Abriendo JSON {current_path}")
        f = open(str(current_path), "rb")
        data_qradar = orjson.loads(f.read())
    
    logging.debug(def_name)
    return data_qradar
# for date in dates:
#     print("date", date)
#     pprint(blocked_events("AAN", date))


def events_paises(
    customer_id: str,
    date: str,
    aql_name: str = "TOP_10_Paises",
    refresh: bool = False
) -> dict:
    """Datos para la grafica de top de paises
    https://www.highcharts.com/demo/column-basic
    https://www.highcharts.com/demo/column-stacked-percent
    """
    def_name = f"events_paises"
    
    path_data_qradar: Path = Path(__file__).parent/"data_qradar"
    if not path_data_qradar.exists():
        path_data_qradar.mkdir()
    
    current_path = path_data_qradar / f"{date}_{customer_id}_{def_name}_dict_info_final.json"
    if refresh and current_path.exists():
        logging.info("Borrando json")
        current_path.unlink()
        current_path_all =  path_data_qradar / f"{date}_{customer_id}_{def_name}.json"
        current_path_all.unlink()

    if not current_path.exists():
        logging.info(f"Creando JSON {current_path}")
        
        calendar = get_otrs.calendar_spanish()
        calendar = calendar["calendar_num"]
        date_ = datetime.strptime(date, "%Y-%m-%d")
        year = date_.year
        name_date = date_.month
        name_date = calendar[name_date]

        
        data = get_json(
            def_name = def_name,
            customer_id = customer_id,
            date = date,
            aql_name = aql_name
        )
        
        translator = Translator()
        dict_paises = {}
        dict_continents = {}
        for pos, event in enumerate(data["data"]["events"]):
            name_event = event["País/región geográfica de origen"]
            pais_ = name_event.split(".")
            recuento_event =  event["Recuento de sucesos (Suma)"]
            if len(pais_) > 1:
                continet = translator.translate(pais_[0], dest="es")
                continet = continet.text
                if pais_[1] == "China":
                    pais_temp = pais_[1]
                else:
                    pais_temp = translator.translate(pais_[1], dest="es")
                    pais_temp = pais_temp.text
                if continet not in dict_continents:
                    dict_continents[continet] = {
                        "paises":  [pais_temp],
                        "total": int(recuento_event)
                    }
                else:
                    dict_continents[continet]["paises"].append(pais_temp)
                    dict_continents[continet]["total"] += int(recuento_event)
            
            name_event = f"{continet}.{pais_temp}"
            dict_paises[name_event] = int(recuento_event)
        
        dict_continents_ = sorted(
            dict_continents.items(),
            key=lambda x:x[1]["total"], 
            reverse=True
        )

        data_grah_x_continent = []
        data_grah_y_temp = []
        total_continent = 0
        for continent in dict_continents_:
            data_grah_x_continent.append(continent[0])
            data_grah_y_temp.append(int(continent[1]["total"]))
            total_continent += int(continent[1]["total"])
        
        data_grah_y_continent = [{"name": "Eventos", "data": data_grah_y_temp}]
        total_continent = '{:,}'.format(total_continent).replace(',','.')
        data_grah_continent = {
            "data_grah_x": data_grah_x_continent,
            "data_grah_y": data_grah_y_continent,
            "total": total_continent
        }

        dict_paises_desc = sorted(
            dict_paises.items(),
            key=lambda x:x[1], 
            reverse=True
        )

        data_grah_x_top_paises = []
        data_grah_y_temp = []
        order_continet_top_10 = []
        total_top_paises = 0
        data_grah_x_top_continent_pais = []
        for pos, pais in enumerate(dict_paises_desc):
            if pos < 10:
                name_ = pais[0].split(".")
                if len(name_) == 2:
                    name_continent = name_[0]
                    name_pais = name_[1]
                else:
                    name_ = pais[0].split(" ")
                    name_continent = name_[0]
                    name_pais = name_[1::]

                if name_continent not in data_grah_x_top_continent_pais:
                    data_grah_x_top_continent_pais.append(name_continent)
                    order_continet_top_10.append(dict_continents[name_continent]["total"])
                data_grah_x_top_paises.append(name_pais)
                data_grah_y_temp.append(pais[1])
                total_top_paises += int(pais[1])

        data_grah_y_top_paises = [{"name": "Eventos", "data": data_grah_y_temp}]
        total_top_paises = '{:,}'.format(total_top_paises).replace(',','.')
        
        data_grah_top_paises = {
            "data_grah_x": data_grah_x_top_paises,
            "data_grah_y": data_grah_y_top_paises,
            "total": total_top_paises
        }

        data_grah_y_top_continent_pais_porcent = []
        data_grah_y_top_continent_pais = []
        data_y_porcent = []
        data_y_porcent_dif = []
        for pos_continent, continent_ in enumerate(data_grah_x_top_continent_pais):
            data_y_ = []
            data_y_porcent_temp = 0
            for pais_continent in data_grah_x_top_paises:
                if pais_continent in dict_continents[continent_]["paises"]:
                    name_complete = f"{continent_}.{pais_continent}"
                    data_y_.append(dict_paises[name_complete])
                    data_y_porcent_temp += dict_paises[name_complete]
                else:
                    data_y_.append(0)
                
            data_y_porcent.append(data_y_porcent_temp)
            dif = order_continet_top_10[pos_continent] - data_y_porcent_temp
            data_y_porcent_dif.append(dif)

            data_grah_y_top_continent_pais.append({
                    "name": continent_,
                    "data": data_y_
                }
            )

        data_grah_y_top_continent_pais_porcent.append({
                "name": "Total",
                "data": data_y_porcent
            }
        )

        data_grah_y_top_continent_pais_porcent.append({
                "name": "Diferencia",
                "data": data_y_porcent_dif
            }
        )

        data_grah_top_continent_pais = {
            "data_grah_x": data_grah_x_top_paises,
            "data_grah_y": data_grah_y_top_continent_pais,
            "total": total_top_paises
        }

        data_grah_top_continent_pais_porcent = {
            "data_grah_x": data_grah_x_top_continent_pais,
            "data_grah_y": data_grah_y_top_continent_pais_porcent,
            "total": total_top_paises
        }

        data_qradar = {
            "year": year,
            "name_date": name_date,
            "data_grah_top_paises": data_grah_top_paises,
            "data_grah_continent": data_grah_continent,
            "data_grah_top_continent_pais": data_grah_top_continent_pais,
            "data_grah_top_continent_pais_porcent": data_grah_top_continent_pais_porcent,
            "current_date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }

        current_path.touch()
        f = current_path.open("wb")
        f.write(orjson.dumps(data_qradar))
        f.close()
    else:
        logging.info(f"Abriendo JSON {current_path}")
        f = open(str(current_path), "rb")
        data_qradar = orjson.loads(f.read())

    logging.debug(def_name)
    return data_qradar
# for date in dates:
#     print("date", date)
#     pprint(events_paises("AAN", date))


###############################################################################
#################################--TOTAL--#####################################
###############################################################################


def total_events(
    service: str,
    customer_id: str
) -> dict:
    """Datos totales de los eventos
    https://www.highcharts.com/demo/column-basic
    """
    def_name = "total_blocked_events"
    logging.debug(def_name)

    if service == "firepower":
        if customer_id == "EVERTEC":
            data_grah_x = []
            data_grah_y_temp = []
            for date in dates_actives():
                date = date[1]["date"]
                data_grah_x.append(date)
                data_grah_y_temp.append(blocked_events(
                    customer_id = customer_id,
                    date = date
                )["total"])
            total = sum(data_grah_y_temp)
            total = '{:,}'.format(total).replace(',','.')
            data_grah_y = [{"name": "Eventos Bloqueados", "data": data_grah_y_temp}]

            data = {
                "data_grah_x": data_grah_x,
                "data_grah_y": data_grah_y,
                "total": total
            }

    if service == "arbor":
        if customer_id == "AAN":
            data_grah_x = []
            data_grah_y_temp = []
            for date in dates_actives():
                date = date[1]["date"]
                data_grah_x.append(date)
                data_grah_y_temp.append(blocked_events(
                    customer_id = customer_id,
                    date = date
                )["total"])
            total = sum(data_grah_y_temp)
            total = '{:,}'.format(total).replace(',','.')
            data_grah_y = [{"name": "Eventos Bloqueados", "data": data_grah_y_temp}]

            data = {
                "data_grah_x": data_grah_x,
                "data_grah_y": data_grah_y,
                "total": total
            }
        
    logging.debug(def_name)
    return data









# def update_all():
#     ##############--Cloudflare--############
#     for date in dates:
#         print("date", date)
#         event_total_log_source("SURA", date)

#     for date in dates:
#         print("date", date)
#         total_accept_per_dominio_pais("SURA", date)

#     for date in dates:
#         print("date", date)
#         detalle_drop("SURA", date)

#     for date in dates:
#         print("date", date)
#         tabla_reque_acep_boque_per_dominio("SURA", date)

#     ################--Firepower--#########
#     for date in dates:
#         print("date", date)
#         total_firepower(customer = "EVERTEC", date = date)

#     #################--Arbor--#########
#     for date in dates:
#         print("date", date)
#         blocked_events("AAN", date)

#     for date in dates:
#         print("date", date)
#         events_paises("AAN", date)

# update_all()

##########EJEMPLO##############
# test = qradar.start_time_offense("64754")
# print("test", test)

# test_1 = qradar.offenses(
#     headers={"Range": "items=0-2"}
#     # params={
#     #     "fields": "id",
#     # }
# )

# print("test_1")
# pprint(test_1)


# data = qradar.offenses(
#             params={
#             "filter": "id=62857"
#             }
#         )


# epoch = data[0]["start_time"]
# fecha_chl = qradar.epoch2date(epoch)
# print(fecha_chl)


# data = qradar.offenses(
#             headers={"Range": "items=0-5"
#             }, 
#             params={
#                 "fields": "id,description,start_time,log_sources",
#                 "filter": "id=59439",
#                 "sort":"+start_time"
#             }
#         )