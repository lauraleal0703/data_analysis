try:
    from .qradar import qradar
    from webapp.analyzer import get_otrs
except:
    from qradar import qradar
    import get_otrs


from dateutil.relativedelta import relativedelta
from pprint import pprint
from datetime import datetime
from googletrans import Translator

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


def dates_actives():
    """Hay información de 3 meses atrás en QRadar"""
    def_name = "dates_actives"
    logging.debug(def_name)
    month_init = datetime.today() - relativedelta(months=3)
    date_init_ = f"{month_init.year}-{month_init.month}-01"
    date_init = datetime.strptime(date_init_, "%Y-%m-%d")
    dict_date = {
        1: {
            "date": date_init_, 
            "date_name": datetime.strftime(date_init, "%m-%Y")
        }
    }
    i = 2
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
    customer: str,
    date: str,
    aql_name: str
) -> str:
    """Las AQL"""
    def_name = "aql"
    logging.debug(def_name)

    start = date
    stop = datetime.strptime(date, "%Y-%m-%d") + relativedelta(months=1)
    stop = datetime.strftime(stop, "%Y-%m-%d")
    
    if customer == "AAN":
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
    
    if customer == "SURA":
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
            # Detalle_drop = f'''SELECT logsourcename(logSourceId) AS 'Origen de registro', "ClientIP" AS 'ClientIP (personalizado)', "ClientCountry" AS 'ClientCountry (personalizado)', "ClientRequestHost" AS 'ClientRequestHost (personalizado)', "ClientRequestPath" AS 'ClientRequestPath (personalizado)', UniqueCount(logSourceId) AS 'Origen de registro (Recuento exclusivo)', UniqueCount("FirewallMatchesActions") AS 'FirewallMatchesActions (personalizado) (Recuento exclusivo)', SUM("eventCount") AS 'Recuento de sucesos (Suma)', MIN("startTime") AS 'Hora de inicio (Mínimo)', COUNT(*) AS 'Recuento' from events where ( "FirewallMatchesActions"='["block"]' AND (logSourceId='3612') or (logSourceId='3613') or (logSourceId='3663') or (logSourceId='3664') or (logSourceId='3665') ) GROUP BY "ClientIP", "ClientCountry", "ClientRequestHost", "ClientRequestPath" order by "Recuento" desc start '{start} 00:00' stop '{stop} 00:00'
            # '''
            ##Excepción ENERO 2023
            Detalle_drop = '''SELECT "ClientIP" AS 'ClientIP (personalizado)', "ClientCountry" AS 'ClientCountry (personalizado)', "ClientRequestHost" AS 'ClientRequestHost (personalizado)', "ClientRequestPath" AS 'ClientRequestPath (personalizado)', UniqueCount(logSourceId) AS 'Origen de registro (Recuento exclusivo)', UniqueCount("FirewallMatchesActions") AS 'FirewallMatchesActions (personalizado) (Recuento exclusivo)', SUM("eventCount") AS 'Recuento de sucesos (Suma)', MIN("startTime") AS 'Hora de inicio (Mínimo)', COUNT(*) AS 'Recuento' from events where ( ( ("ClientIP"<'143.198.234.131') or ("ClientIP">'143.198.234.131' and "ClientIP"<'165.227.99.174') or ("ClientIP">'165.227.99.174' and "ClientIP"<'167.172.245.180') or ("ClientIP">'167.172.245.180') AND "FirewallMatchesActions"='["block"]' ) AND (logSourceId='3612') or (logSourceId='3613') or (logSourceId='3663') or (logSourceId='3664') or (logSourceId='3665') ) GROUP BY "ClientIP", "ClientCountry", "ClientRequestHost", "ClientRequestPath" order by "Recuento" desc start '2023-01-01 00:00' stop '2023-01-31 23:59'
            '''
            logging.debug(def_name)
            return Detalle_drop



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
    customer: str,
    date: str,
    aql_name: str = "Eventos_totales_Log_Source"
) -> dict:
    """Datos para la grafica de 
    """
    def_name = "event_total_log_source"
    logging.debug(def_name)

    calendar = get_otrs.calendar_spanish()
    calendar = calendar["calendar_num"]
    date_ = datetime.strptime(date, "%Y-%m-%d")
    year = date_.year
    name_date = date_.month
    name_date = calendar[name_date]

    create_id_searches = qradar.ariel_searches_post(
        query_expression = aql(
            customer = customer,
            date = date,
            aql_name = aql_name
        )
    )

    data = qradar.ariel_results(
        search_id = create_id_searches
    )

    if len(data["events"]) == 0:
        logging.error(def_name)
        return {}
    
    logging.info(f'TOTAL DE EVENTOS {def_name} {len(data["events"])}')
    print("EVENTOS DEL TIPO")
    pprint(data["events"][0])

    total = 0
    dict_total_events = {}
    for event in data["events"]:
        name_event = event["Origen de registro"]
        recuento_event =  int(event["Recuento de sucesos (Suma)"])
        total += recuento_event
        dict_total_events[name_event] = recuento_event
    
    dict_total_events["Total"] = total
    logging.debug(def_name)
    return dict_total_events
# print(event_total_log_source("SURA", "2023-01-01"))


def total_accept_per_dominio_pais(
    customer: str,
    date: str,
    aql_name: str = "Total_Accept_per_dominio_Pais"
) -> dict:
    """Datos para la grafica de 
    """
    def_name = "total_accept_per_dominio_pais"
    logging.debug(def_name)
    
    calendar = get_otrs.calendar_spanish()
    calendar = calendar["calendar_num"]
    date_ = datetime.strptime(date, "%Y-%m-%d")
    year = date_.year
    name_date = date_.month
    name_date = calendar[name_date]

    create_id_searches = qradar.ariel_searches_post(
        query_expression = aql(
            customer = customer,
            date = date,
            aql_name = aql_name
        )
    )

    data = qradar.ariel_results(
        search_id = create_id_searches
    )
    
    if len(data["events"]) == 0:
        logging.error(def_name)
        return {}
    
    logging.info(f'TOTAL DE EVENTOS {def_name} {len(data["events"])}')
    print("EVENTOS DEL TIPO")
    pprint(data["events"][0])

    paises = qradar.nombre_pais()
    total = 0
    dict_total_events = {}
    dict_events_dominio_pais = {}
    for event in data["events"]:
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
    
    dict_total_events["Total"] = total

    logging.debug(def_name)
    return {
        "dict_total_events": dict_total_events,
        "dict_events_dominio_pais": dict_events_dominio_pais
    }
# pprint(total_accept_per_dominio_pais("SURA", "2023-01-01"))


def detalle_drop(
    customer: str,
    date: str,
    aql_name: str = "Detalle_drop"
) -> dict:
    """Datos para la grafica de 
    """
    def_name = "detalle_drop"
    logging.debug(def_name)

    calendar = get_otrs.calendar_spanish()
    calendar = calendar["calendar_num"]
    date_ = datetime.strptime(date, "%Y-%m-%d")
    year = date_.year
    name_date = date_.month
    name_date = calendar[name_date]

    create_id_searches = qradar.ariel_searches_post(
        query_expression = aql(
            customer = customer,
            date = date,
            aql_name = aql_name
        )
    )

    # data = qradar.ariel_results(
    #     search_id = create_id_searches,
    #     headers = {"Range": "items=0-569293"}
    # )
    data = qradar.ariel_results(
        search_id = create_id_searches
    )
    
    if len(data["events"]) == 0:
        logging.error(def_name)
        return {}
    
    logging.info(f'TOTAL DE EVENTOS {def_name} {len(data["events"])}')
    print("EVENTOS DEL TIPO")
    pprint(data["events"][0])

    exit()
    paises = qradar.nombre_pais()
    total = 0
    dict_total_events = {}
    dict_events_dominio_pais = {}
    for event in data["events"]:
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
    
    dict_total_events["Total"] = total

    logging.debug(def_name)
    return {
        "dict_total_events": dict_total_events,
        "dict_events_dominio_pais": dict_events_dominio_pais
    }
# pprint(detalle_drop("SURA", "2023-01-01"))


def tabla_reque_acep_boque_per_dominio(
        customer: str,
        date: str,
) -> dict:
    """Datos para la 
    """
    def_name = "tabla_reque_acep_boque_per_dominio"
    logging.debug(def_name)

    total_requirements = event_total_log_source(
        customer = customer,
        date = date
    )
    requirements_drop = detalle_drop(
         customer = customer,
        date = date
    )
    requirements_accep = total_accept_per_dominio_pais(
        customer = customer,
        date = date
    )


    total_requirements_drop = requirements_drop["dict_total_events"]
    total_requirements_accep = requirements_accep["dict_total_events"]
    pprint(total_requirements)
    pprint(total_requirements_accep)
    pprint(total_requirements_drop)

    dict_dominio ={}
    for dominio in total_requirements:
        dict_dominio[dominio] = {
            "Total de Requerimientos": '{:,}'.format(total_requirements[dominio]).replace(',','.'), 
            "Requerimientos Aceptados": '{:,}'.format(total_requirements_accep[dominio]).replace(',','.'),
            "Requerimientos Bloqueados": '{:,}'.format(total_requirements_drop[dominio]).replace(',','.')
        }
    

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
# pprint(tabla_reque_acep_boque_per_dominio("SURA", "2023-01-01"))


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
    customer: str,
    date: str,
    aql_name: str = "Informe_Arbor_1"
) -> dict:
    """Datos para la grafica de eventos bloquedos del informe de Arbor
    https://www.highcharts.com/demo/pie-basic
    """
    def_name = "blocked_events"
    logging.debug(def_name)

    calendar = get_otrs.calendar_spanish()
    calendar = calendar["calendar_num"]
    date_ = datetime.strptime(date, "%Y-%m-%d")
    year = date_.year
    name_date = date_.month
    name_date = calendar[name_date]

    create_id_searches = qradar.ariel_searches_post(
        query_expression = aql(
            customer = customer,
            date = date,
            aql_name = aql_name
        )
    )
    data = qradar.ariel_results(
        search_id = create_id_searches
    )
    
    if len(data["events"]) == 0:
        logging.error(def_name)
        return {}
    
    logging.info(f'TOTAL DE EVENTOS {def_name} {len(data["events"])}')
    print("EVENTOS DEL TIPO")
    pprint(data["events"][0])

    data_grah = [{
        "name": "Brands",
        "colorByPoint": True,
        "data": []
    }]
    translator = Translator()
    total = 0
    dict_events_desc = {}
    for event in data["events"]:
        name_event = event["Nombre de suceso"]
        name_event = translator.translate(name_event, dest="es")
        name_event = name_event.text
        recuento_event =  event["Recuento de sucesos (Suma)"]
        total += int(recuento_event)
        dict_events_desc[name_event] = recuento_event
    
    dict_events_desc = sorted(
        dict_events_desc.items(),
        key=lambda x:x[1], 
        reverse=True
    )
    for pos, event_ in enumerate(dict_events_desc):
        if pos == 0:
            data_grah_temp = {
                "name": event_[0],
                "y": event_[1],
                "sliced": True,
                "selected": True
            }
        else:
            data_grah_temp = {
                "name": event_[0],
                "y": event_[1]
            }
        
        data_grah[0]["data"].append(data_grah_temp)
    
    total = '{:,}'.format(total).replace(',','.')
    
    logging.debug(def_name)
    return {
        "year": year,
        "name_date": name_date,
        "data_grah": data_grah,
        "total": total
    }


def total_blocked_events():
    """Datos totales de los eventos
    https://www.highcharts.com/demo/column-basic
    """
    def_name = "total_blocked_events"
    logging.debug(def_name)

    data_grah_x = [
        "01-2023", 
        "12-2022",
        "11-2022"
    ]
    data_grah_y_temp = [
        3862522,
        3236739,
        3121628
    ]
    total = sum(data_grah_y_temp)
    total = '{:,}'.format(total).replace(',','.')
    data_grah_y = [{"name": "Eventos Bloqueados", "data": data_grah_y_temp}]
    
    logging.debug(def_name)
    return {
        "data_grah_x": data_grah_x,
        "data_grah_y": data_grah_y,
        "total": total
    }


def events_paises(
    customer: str,
    date: str,
    aql_name: str = "TOP_10_Paises"
) -> dict:
    """Datos para la grafica de top de paises
    https://www.highcharts.com/demo/column-basic
    https://www.highcharts.com/demo/column-stacked-percent
    """
    def_name = "events_paises"
    logging.debug(def_name)

    calendar = get_otrs.calendar_spanish()
    calendar = calendar["calendar_num"]
    date_ = datetime.strptime(date, "%Y-%m-%d")
    year = date_.year
    name_date = date_.month
    name_date = calendar[name_date]

    create_id_searches = qradar.ariel_searches_post(
        query_expression = aql(
            customer = customer,
            date = date,
            aql_name = aql_name
        )
    )
    data = qradar.ariel_results(
        search_id = create_id_searches
    )
    
    if len(data["events"]) == 0:
        logging.error(def_name)
        return {}
    
    logging.info(f'TOTAL DE EVENTOS {def_name} {len(data["events"])}')
    print("EVENTOS DEL TIPO")
    pprint(data["events"][0])
    
    translator = Translator()
    dict_paises = {}
    dict_continents = {}
    for pos, event in enumerate(data["events"]):
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

    logging.debug(def_name)
    return {
        "year": year,
        "name_date": name_date,
        "data_grah_top_paises": data_grah_top_paises,
        "data_grah_continent": data_grah_continent,
        "data_grah_top_continent_pais": data_grah_top_continent_pais,
        "data_grah_top_continent_pais_porcent": data_grah_top_continent_pais_porcent
    }


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
