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


##############################################################################
#################################--Arbor######################################
##############################################################################


def customers_arbor():
    """Los clientes que cuentan con el servicio Arbor son:
    * AAN
    """
    customers = get_otrs.customers_actives()
    customers_arbor = ["AAN"]
    
    dict_customers_arbor = {
        customer: customers[customer] for customer in customers_arbor
    }

    return dict_customers_arbor



def dates_actives():
    """Hay información de 5 meses atrás en QRadar"""
    def_name = "dates_actives"
    print(def_name, datetime.today())
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

    print(def_name, datetime.today())
    return dict_date


def aql(
    customer: str,
    date: str,
    aql_name: str
) -> str:
    """Las AQL"""
    def_name = "aql"
    print(def_name, datetime.today())

    start = date
    stop = datetime.strptime(date, "%Y-%m-%d") + relativedelta(months=1)
    stop = datetime.strftime(stop, "%Y-%m-%d")
    
    if customer == "AAN":
        if aql_name == "Informe_Arbor_1":
            Informe_Arbor_1 = f'''SELECT QIDNAME(qid) AS 'Nombre de suceso', UniqueCount(logSourceId) AS 'Origen de registro (Recuento exclusivo)', SUM("eventCount") AS 'Recuento de sucesos (Suma)', MIN("startTime") AS 'Hora de inicio (Mínimo)', UniqueCount(category) AS 'Categoría de nivel bajo (Recuento exclusivo)', UniqueCount("sourceIP") AS 'IP de origen (Recuento exclusivo)', UniqueCount("sourcePort") AS 'Puerto de origen (Recuento exclusivo)', UniqueCount("destinationIP") AS 'IP de destino (Recuento exclusivo)', UniqueCount("destinationPort") AS 'Puerto de destino (Recuento exclusivo)', COUNT(*) AS 'Recuento' from events where logSourceId='2277' GROUP BY qid order by "Recuento" desc start '{start} 00:00' stop '{stop} 00:00'
            '''
            print(def_name, datetime.today())
            return Informe_Arbor_1
        
        if aql_name == "TOP_10_Paises":
            TOP_10_Paises = f'''SELECT "sourceGeographicLocation" AS 'País/región geográfica de origen', UniqueCount(qid) AS 'Nombre de suceso (Recuento exclusivo)', UniqueCount(logSourceId) AS 'Origen de registro (Recuento exclusivo)', SUM("eventCount") AS 'Recuento de sucesos (Suma)', MIN("startTime") AS 'Hora de inicio (Mínimo)', UniqueCount(category) AS 'Categoría de nivel bajo (Recuento exclusivo)', UniqueCount("sourceIP") AS 'IP de origen (Recuento exclusivo)', UniqueCount("sourcePort") AS 'Puerto de origen (Recuento exclusivo)', UniqueCount("destinationIP") AS 'IP de destino (Recuento exclusivo)', UniqueCount("destinationPort") AS 'Puerto de destino (Recuento exclusivo)', COUNT(*) AS 'Recuento' from events where ( logSourceId='2277' AND qid != '38750074' ) GROUP BY "sourceGeographicLocation" order by "Recuento de sucesos (Suma)" desc start '{start} 00:00' stop '{stop} 00:00'
            '''
            print(def_name, datetime.today())
            return TOP_10_Paises


def blocked_events(
    customer: str,
    date: str,
    aql_name: str = "Informe_Arbor_1"
) -> dict:
    def_name = "blocked_events"
    print(def_name, datetime.today())
    """Datos para la grafica de eventos bloquedos del informe de Arbor
    https://www.highcharts.com/demo/pie-basic
    """
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
    data = qradar.ariel_results(create_id_searches)
    print("Events", len(data["events"]))

    if len(data["events"]) == 0:
        return {}
    
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
    
    print(def_name, datetime.today())
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
    print(def_name, datetime.today())

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
    
    print(def_name, datetime.today())
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
    def_name = "blocked_events"
    print(def_name, datetime.today())
    """Datos para la grafica de top de paises
    https://www.highcharts.com/demo/column-basic
    https://www.highcharts.com/demo/column-stacked-percent
    """
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
    data = qradar.ariel_results(create_id_searches)
    print("Events", len(data["events"]))
    
    if len(data["events"]) == 0:
        return {}
    
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
                    "total": recuento_event
                }
            else:
                dict_continents[continet]["paises"].append(pais_temp)
                dict_continents[continet]["total"] += recuento_event
        
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

    data_grah_y_top_continent_pais = []
    for continent_ in data_grah_x_top_continent_pais:
        data_y_ = []
        for pais_continent in data_grah_x_top_paises:
            if pais_continent in dict_continents[continent_]["paises"]:
                name_complete = f"{continent_}.{pais_continent}"
                data_y_.append(dict_paises[name_complete])
            else:
                data_y_.append(0)
        
        data_grah_y_top_continent_pais.append({
                "name": continent_,
                "data": data_y_
            }
        )

    data_grah_top_continent_pais = {
        "data_grah_x": data_grah_x_top_paises,
        "data_grah_y": data_grah_y_top_continent_pais,
        "total": total_top_paises
    }

    print(def_name, datetime.today())
    return {
        "year": year,
        "name_date": name_date,
        "data_grah_top_paises": data_grah_top_paises,
        "data_grah_continent": data_grah_continent,
        "data_grah_top_continent_pais": data_grah_top_continent_pais
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
