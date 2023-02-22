try:
    from .qradar import qradar
except:
    from qradar import qradar

from webapp.analyzer import get_otrs
from dateutil.relativedelta import relativedelta
from pprint import pprint
from datetime import datetime
from googletrans import Translator, constants


##########################
#######--Arbor############
##########################


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
    date: str,
    aql_name: str
) -> str:
    """Las AQL"""
    def_name = "aql"
    print(def_name, datetime.today())

    start = date
    stop = datetime.strptime(date, "%Y-%m-%d") + relativedelta(months=1)
    stop = datetime.strftime(stop, "%Y-%m-%d")
    if aql_name == "AAN_Informe_Arbor_1":
        AAN_Informe_Arbor_1 = f'''SELECT QIDNAME(qid) AS 'Nombre de suceso', UniqueCount(logSourceId) AS 'Origen de registro (Recuento exclusivo)', SUM("eventCount") AS 'Recuento de sucesos (Suma)', MIN("startTime") AS 'Hora de inicio (Mínimo)', UniqueCount(category) AS 'Categoría de nivel bajo (Recuento exclusivo)', UniqueCount("sourceIP") AS 'IP de origen (Recuento exclusivo)', UniqueCount("sourcePort") AS 'Puerto de origen (Recuento exclusivo)', UniqueCount("destinationIP") AS 'IP de destino (Recuento exclusivo)', UniqueCount("destinationPort") AS 'Puerto de destino (Recuento exclusivo)', COUNT(*) AS 'Recuento' from events where logSourceId='2277' GROUP BY qid order by "Recuento" desc start '{start} 00:00' stop '{stop} 00:00'
        '''

        print(def_name, datetime.today())
        return AAN_Informe_Arbor_1


def blocked_events(
    date: str,
    aql_name: str
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
    for pos, event in enumerate(data["events"]):
        name_event = event["Nombre de suceso"]
        name_event = translator.translate(name_event, dest="es")
        name_event = name_event.text
        recuento_event =  event["Recuento de sucesos (Suma)"]
        total += int(recuento_event)
        if pos == 0:
            data_grah_temp = {
                "name": name_event,
                "y": recuento_event,
                "sliced": True,
                "selected": True
            }
        else:
            data_grah_temp = {
                "name": name_event,
                "y": recuento_event
            }
        
        data_grah[0]["data"].append(data_grah_temp)
    
    total = '{:,}'.format(total).replace(',','.')

    return {
        "year": year,
        "name_date": name_date,
        "data_grah": data_grah,
        "total": total
    }

def total_blocked_events():
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
    
    return {
        "data_grah_x": data_grah_x,
        "data_grah_y": data_grah_y,
        "total": total
    }



##########EJEMPLO##############

# AAN Informe Arbor 1
# SELECT QIDNAME(qid) AS 'Nombre de suceso', UniqueCount(logSourceId) AS 'Origen de registro (Recuento exclusivo)', SUM("eventCount") AS 'Recuento de sucesos (Suma)', MIN("startTime") AS 'Hora de inicio (Mínimo)', UniqueCount(category) AS 'Categoría de nivel bajo (Recuento exclusivo)', UniqueCount("sourceIP") AS 'IP de origen (Recuento exclusivo)', UniqueCount("sourcePort") AS 'Puerto de origen (Recuento exclusivo)', UniqueCount("destinationIP") AS 'IP de destino (Recuento exclusivo)', UniqueCount("destinationPort") AS 'Puerto de destino (Recuento exclusivo)', COUNT(*) AS 'Recuento' from events where logSourceId='2277' GROUP BY qid order by "Recuento" desc last 5 minutes


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
