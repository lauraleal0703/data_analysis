import warnings
warnings.filterwarnings("ignore")

import time
import requests
import typing as t
from pprint import pprint
from datetime import datetime

import logging
logging.basicConfig(
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
        level=logging.DEBUG
    )


######################################################
#------------Consumo de APIS de QRadar ---------------
######################################################

def curl_qradar_get(
        script: str, 
        headers: t.Optional[dict] = None, 
        params: t.Optional[dict] = None
    ) -> dict:
    """Función base para las llamadas a QRadar método get"""
    def_name = "curl_qradar_get"
    logging.debug(def_name)

    url_api = "https://172.16.17.10/api"
    r = requests.get(
            f"{url_api}/{script}",
            auth = ("lleal", "wn4GQ*ndMHWKif"),
            verify = False,
            headers = headers,
            params = params
        )
    
    logging.debug(def_name)
    return r.json()



def curl_qradar_post(
        script: str, 
        headers: t.Optional[dict] = None, 
        params: t.Optional[dict] = None
    ) -> dict:
    """Función base para las llamadas a QRadar metodo post"""
    def_name = "curl_qradar_post"
    logging.debug(def_name)

    url_api = "https://172.16.17.10/api"
    r = requests.post(
            f"{url_api}/{script}",
            auth = ("lleal", "wn4GQ*ndMHWKif"),
            verify = False,
            headers = headers,
            params = params
        )
    
    logging.debug(def_name)
    return r.json()


###################--siem--#################################
def offenses(
        headers: t.Optional[dict] = None, 
        params: t.Optional[dict] = None
    )-> dict:
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
    def_name = "offenses"
    logging.debug(def_name)
    return curl_qradar_get(
        script= "siem/offenses", 
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
    logging.debug(def_name)

    data_id_offense = offenses(
        params={
            "fields": "start_time",
            "filter": f"id={id_offense}"
        }
    )

    if data_id_offense:
        logging.debug(def_name)
        return  datetime.fromtimestamp(
            int(data_id_offense[0]["start_time"])/1000
        )
    
    else:
        logging.error(def_name)
        return []


###################--ariel--#################################


def ariel_searches_post(query_expression: str)-> dict:
    """Crea la consulta con un ID especifico
    
    Parameters:
    query_expression: str
        Es la AQL
    """
    def_name = "ariel_searches_post"
    logging.debug(def_name)
    
    create_searches = curl_qradar_post(
        script = "ariel/searches", 
        params = {
            "query_expression": query_expression
        }
    )

    logging.debug(def_name)
    return str(create_searches["search_id"])


def ariel_results(
        search_id: str,
        headers : t.Optional[dict] = None):
    """Toma el ID de la búsqueda y trate los datos que se tienen asociados"""
    def_name = "ariel_results"
    logging.debug(def_name)
    logging.info(f"search_id {search_id}")
    
    """Consulta si la búsqueda esta completa"""
    search = curl_qradar_get(
        script = f"ariel/searches/{search_id}"
    )
    completed = search["completed"]

    logging.info("...start while")
    while not completed:
        search = curl_qradar_get(
            script = f"ariel/searches/{search_id}"
        )
        completed = search["completed"]
        time.sleep(4)
    logging.info("end while...") 
    
    logging.debug(def_name)
    if headers:
        return curl_qradar_get(
            script = f"ariel/searches/{search_id}/results",
            headers = headers
        )
    else:
        return curl_qradar_get(
            script = f"ariel/searches/{search_id}/results"
        )


###################--SOPORTE--#################################


def nombre_pais():
    """Retorna un diccionario que tiene como key el codigo del país que entrega QRadar
    y su valor es el nombre del país"""
    text_paises = '''ac Isla Ascension
    ad Andorra
    ae Emiratos Árabes Unidos
    af Afganistán
    ag Antigua y Barbuda
    ai Anguilla
    al Albania
    am Armenia
    an Antillas holandesas (Ahora suprimido –debido a que en 2010 se acordó la disolución política del territorio en el Caribe, en 2015 se creó este ccTLD)
    ao Angola
    aq Antátida
    ar Argentina
    as Samoa Americana
    at Austria
    au Australia
    aw Aruba
    ax Åland (todavía .aland.fi hasta marzo de 2015)
    az Azerbaiyán
    ba Bosnia-Herzegovina
    bb Barbados
    bd Bangladés
    be Bélgica
    bf Burkina Faso
    bg Bulgaria
    bh Baréin
    bi Burundi
    bj Benín
    bl Saint-Barthélemy
    bm Bermudas
    bn Brunéi
    bo Boliva
    br Brasil
    bq Bonaire, Saba, San Eustaquio
    bs Bahamas
    bt Bután
    bv Isla Bouvet (aún no es posible su registro)
    bw Botsvana
    by Bielorrusia
    bz Belice
    ca Canadá
    cc Islas Cocos
    cd República Democrática del Congo
    cf República Centroafricana
    cg República del Congo
    ch Suiza
    ci Costa de Marfil
    ck Islas Cook
    cl Chile
    cm Camerún
    cn República Popular China
    co Colombia
    cr Costa Rica
    cs Checoslovaquia (ahora eliminado)
    cu Cuba
    cv Cabo Verde
    cw Curaçao
    cx Isla de Navidad
    cy Chipre
    cz Chequia
    dd República Democrática Alemana (nunca fue activado)
    de Alemania
    dj Djibouti
    dk Dinamarca
    dm Dominica
    do República Dominicana
    dz Algeria
    ec Ecuador
    ee Estonia
    eg Egipto
    eh Sahara Occidental (no activado debido al conflicto político entre el gobierno del Sahara Occidental y Marruecos)
    er Eritrea
    es España
    et Etiopía
    eu Unión Europea
    fi Finlandia
    fj Fiji
    fk Islas Malvinas
    fm Micronesia
    fo Feroe
    fr Francia
    ga Gabun
    gb Reino Unido
    gd Granada
    ge Georgia
    gf Guyana Francesa
    gg Guernsey
    gh Ghana
    gi Gibraltar
    gl Groenlandia
    gm Gambia
    gn Guinea
    gp Guadalupe
    gq Guinea Ecuatorial
    gr Grecia
    gs Georgia del Sur y las Islas Sandwich del Sur
    gt Guatemala
    gu Guam
    gw Guinea-Bissau
    gy Guayana
    hk Hong Kong
    hm Islas Heard y McDonald
    hn Honduras
    hr Croacia
    ht Haití
    hu Hungría
    id Indonesia
    ie Irlanda
    il Israel
    im Isla de Man
    in India
    io Territorio Británico del Océano Índico
    iq Irak
    ir Irán
    is Islandia
    it Italia
    je Jersey
    jm Jamaica
    jo Jordania
    jp Japón
    ke Kenia
    kg Kirguistán
    kh Camboya
    ki Kiribati
    km Comoras
    kn St. Kitts y Nevis
    kp Corea del Norte
    kr Corea del Sur
    kw Kuwait
    ky Islas Caimán
    kz Kazajstán
    la Laos
    lb Líbano
    lc Santa Lucia
    li Liechtenstein
    lk Sri Lanka
    lr Liberia
    ls Lesoto
    lt Lituania
    lu Luxemburgo
    lv Letonia
    ly Libia
    ma Marruecos
    mc Mónaco
    md Moldavia
    me Montenegro
    mf Saint-Martin
    mg Madagascar
    mh Islas Marshall
    mk Macedonia
    ml Mali
    mm Myanmar
    mn Mongolia
    mo Macau
    mp Islas Marinas del Norte
    mq Martinica
    mr Mauritania
    ms Montserrat
    mt Malta
    mu República de Mauricio
    mv Maledivas
    mw Malawi
    mx México
    my Malasia
    mz Mozambique
    na Namibia
    nc Caledonia
    ne Níger
    nf Isla Norfolk
    ng Nigeria
    ni Nicaragua
    nl Países Bajos
    no Noruega
    np Nepal
    nr Nauru
    nu Niue
    nz Nueva Zelanda
    om Omán
    pa Panamá
    pe Perú
    pf Polinesia Francesa
    pg Papua Nueva Guinea
    ph Filipinas
    pk Pakistán
    pl Polonia
    pm Saint Pedro y Miquelón
    pn Islas Pitcairn
    pr Puerto Rico
    ps Estado de Palestina
    pt Portugal
    pw Palau
    py Paraguay
    qa Katar
    re Reunión
    ro Rumania
    rs Serbia
    ru Rusia
    rw Ruanda
    sa Arabia Saudita
    sb Islas Salomón
    sc Seychelles
    sd Sudán
    se Suecia
    sg Singapur
    sh St. Helena
    si Eslovenia
    sj Svalbard y Jan Mayen (aún no es posible su registro)
    sk Eslovaquia
    sl Sierra Leona
    sm San Marino
    sn Senegal
    so Somalia
    sr Surinam
    ss Sudán del Sur
    st Santo Tomé y Príncipe
    su Unión Soviética (desde la disulución se utiliza el TLD ruso)
    sv El Salvador
    sx Sint Maarten
    sy Siria
    sz Swazilandia
    tc Islas Turcas y Caicos
    td Chad
    tf Tierras Australes y Antárticas Francesas
    tg Togo
    th Tailandia
    tj Tayikistán
    tk Tokelau
    tl Timor Occidental (anteriormente .tp)
    tm Turkmenistán
    tn Túnez
    to Tonga
    tp Timor Oriental (ahora eliminado – sustituido desde 2002 con .tl)
    tr Turquía, República Turca del Norte de Chipre
    tt Trinidad y Tobago
    tv Tuvalu
    tw Taiwán
    tz Tanzania
    ua Ucrania
    ug Uganda
    uk Reino Unido
    um Islas Ultramarinas Menores de Estados Unidos (ahora eliminado)
    us Estados Unidos
    uy Uruguay
    uz Uzbekistán
    va Ciudad del Vaticano
    vc St. Vincente y las Granadinas
    ve Venezuela
    vg Islas Vírgenes Británicas
    vi Islas Vírgenes de los EE.UU
    vn Vietnam
    vu Vanuatu
    wf Wallis y Futuna (también .fr)
    ws Samoa
    ye Yemen
    yt Mayotte (región francesa – también .fr)
    yu Yugoslavia (ahora eliminado – después de la disolución se utilizó, hasta 2010, el TLD de Serbia y Montenegro)
    za Sudáfrica
    zm Zambia
    zr Zaire (ahora eliminado, utiliza .cd desde el cambio del nombre del país en 1997)
    zw Zimbabue
    xk Kosovo
    xx Desconocido
    t1 Other'''
    text_paises = text_paises.split("\n")
    dict_paises = {}
    for pais in text_paises:
        pais = pais.strip()
        pais = pais.split(" ")
        name =  pais[1::]
        dict_paises[pais[0]] = " ".join(name)
    
    return dict_paises