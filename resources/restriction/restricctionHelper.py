from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from config import db, base
from models.restriction import Restriction as ResModel, RestrictionPostSchema2 as PostModelSchema, RestrictionPutSchema2 as PutModelSchema, RestrictionSchema as ModelSchema, RestrictionDataRestrictionDetailSchema as ResDataResDetSchema, RestrictionDetailDataSchema2 as Detailschema
from models.restriction_detail import RestrictionDetail as ResDetModel, RestrictionDetailSchema as ResDetSchema
from models.restriction_by import RestrictionBy as ResByModel
from models.restriction_type import RestrictionType as ResTyModel
from models.property import Property as proModel
from models.opera_restrictions import OperaRestrictions as OpeResModel, OperaRestrictionsSchema as OpeResSchema, OperaRestrictionCloseDateSchema as OpeResCloseSchema
from models.rateplan import RatePlan as RatePlanModel
from models.rate_plan_rooms import RatePlanRooms
from models.rateplan_property import RatePlanProperty
from models.room_type_category import RoomTypeCategory as rtcModel
from common.util import Util
from operator import itemgetter
from sqlalchemy import or_, and_, func
import datetime, decimal
import json
from datetime import datetime as dt, timedelta

class RestricctionFunction():

    def getRestriction(self,booking_window=0,travel_window_start=None, \
    travel_window_end=None, marketing_id=0, country_code=None, channel_id=0, \
    spesific_day=None, divice=0):

        try:
            data = ResModel.query.filter(func.json_extract(ResModel.booking_window_dates, \
            "$[*].end_date")>="2020-02-22", \
            func.json_contains(ResModel.market_targeting, '2')).all()
        except Exception as error:
            data = str(error)

        return data

    # Función para codificar clases especiales de SQLAlchemy
    def alchemyencoder(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            return float(obj)

    # Convierte un objeto ResultProxy de sqlalchemy en un Diccionario
    def ResultProxyToDict(self, obj):
        str_json = json.dumps([dict(row) for row in obj], default=self.alchemyencoder)
        json_result = json.loads(str_json)
        return json_result

    def checkParameterType(self, param_name="", param_value=None, param_type=None, isNone=False, acceptQuotes=False, isDate=False, isDateTime=False):
        #if(isinstance(param_value, param_type) and type(param_value) == param_type):
        if(isinstance(param_value, param_type)):
            if(isinstance(param_value, str) and acceptQuotes == False and ("\"" in param_value or "'" in param_value)):
                raise Exception('Quotes not permitted in {0:s} parameter'.format(param_name))
            elif(isinstance(param_value, str) and isDateTime):
                try:
                    dt.strptime(param_value, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    raise ValueError('Incorrect data format, {0:s} should be YYYY-MM-DD HH:MM:SS'.format(param_name))

                return True
            elif(isinstance(param_value, str) and isDate):
                try:
                    dt.strptime(param_value, '%Y-%m-%d')
                except ValueError:
                    raise ValueError('Incorrect data format, {0:s} should be YYYY-MM-DD'.format(param_name))

                return True
            else:
                return True
        elif(param_value is None and isNone):
            return True
        elif(param_value is not None and isNone):
            raise Exception('Data Type is not Valid, the {0:s} parameter needs to be {1:s} or None'.format(param_name,param_type.__name__))
        else:
            raise Exception('Data Type is not Valid, the {0:s} parameter needs to be {1:s}'.format(param_name,param_type.__name__))

    def getDayOfTheWeek(self, weekday):
        str_days = { 
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday",
        } 
        return str_days.get(weekday, None)

    @staticmethod
    def getRestrictionDetails(id_restriction_detail=0, id_restriction=0, specific_channel=0, \
        travel_window_start=None, travel_window_end=None, market_targeting=0, \
        geo_targeting_country=None, restriction_default=None, device=None, restriction_by=0, \
        restriction_type=0, estado_restriction=1, estado_detail=1, isAll=False, useBooking=True, \
        min_los=0, max_los=0, value_room="", value_hotel_id=0, value_rate_plan_id=0, \
        use_min_los=True, use_max_los=True, use_value=True):
        try:
            schema = ResDataResDetSchema(exclude=Util.get_default_excludes())
            rec_class = RestricctionFunction()
            # Si parámetro "useBooking" es True se obtendrán Fecha, hora y dia de la semana actuales (HOY)
            # y con ello se tomará en cuenta en los filtros
            if useBooking:
                booking_window_date = dt.today().strftime('%Y-%m-%d') # Se obtiene fecha actual
                booking_window_time = dt.today().strftime('%H:%M') # Se obtiene hora actual
                bookable_weekday = rec_class.getDayOfTheWeek(dt.today().weekday()) # Se obtiene el día de la semana
            else:
                booking_window_date = None
                booking_window_time = None
                bookable_weekday = None

            rec_class.checkParameterType(param_name="id_restriction_detail", param_value=id_restriction_detail, param_type=int)
            rec_class.checkParameterType(param_name="id_restriction", param_value=id_restriction, param_type=int)
            rec_class.checkParameterType(param_name="specific_channel", param_value=specific_channel, param_type=int)
            rec_class.checkParameterType(param_name="travel_window_start", param_value=travel_window_start, param_type=str, isNone=True, isDate=True)
            rec_class.checkParameterType(param_name="travel_window_end", param_value=travel_window_end, param_type=str, isNone=True, isDate=True)
            #rec_class.checkParameterType(param_name="booking_window_date", param_value=booking_window_date, param_type=str, isNone=True)
            #rec_class.checkParameterType(param_name="booking_window_time", param_value=booking_window_time, param_type=str, isNone=True)
            #rec_class.checkParameterType(param_name="bookable_weekday", param_value=bookable_weekday, param_type=str, isNone=True)
            rec_class.checkParameterType(param_name="market_targeting", param_value=market_targeting, param_type=int)
            rec_class.checkParameterType(param_name="geo_targeting_country", param_value=geo_targeting_country, param_type=str, isNone=True)
            rec_class.checkParameterType(param_name="restriction_default", param_value=restriction_default, param_type=int, isNone=True)
            rec_class.checkParameterType(param_name="device", param_value=device, param_type=int, isNone=True)
            rec_class.checkParameterType(param_name="restriction_by", param_value=restriction_by, param_type=int)
            rec_class.checkParameterType(param_name="restriction_type", param_value=restriction_type, param_type=int)
            rec_class.checkParameterType(param_name="estado_restriction", param_value=estado_restriction, param_type=int)
            rec_class.checkParameterType(param_name="estado_detail", param_value=estado_detail, param_type=int)
            rec_class.checkParameterType(param_name="isAll", param_value=isAll, param_type=bool)
            rec_class.checkParameterType(param_name="useBooking", param_value=useBooking, param_type=bool)
            rec_class.checkParameterType(param_name="min_los", param_value=min_los, param_type=int)
            rec_class.checkParameterType(param_name="max_los", param_value=max_los, param_type=int)
            rec_class.checkParameterType(param_name="value_room", param_value=value_room, param_type=str)
            rec_class.checkParameterType(param_name="value_hotel_id", param_value=value_hotel_id, param_type=int)
            rec_class.checkParameterType(param_name="value_rate_plan_id", param_value=value_rate_plan_id, param_type=int)

            base_query = "SELECT * FROM def_restriction_detail"
            query = base_query
            params = {}
            query_where = ""
            previous_where = False # Bandera para identificar si se ha agregado algo "query_where"
            query_join = "" # Utilizada para las consultas de fechas en campos array[obj] (campos JSON)
            query_union = "" # Utilizado para las consultas con campos array (campos JSON)
            json_extract = False # Bandera para identificar si se ha agregado el JSON_EXTRACT en "query_where"
            subquery_index = 0 # Indice para identificar los niveles que tendrá la consulta, debido a los campos en formato Array(obj) (campos JSON)
            arr_subquery = []
            res_query_where = "" #Utilizada para filtrar por restrictions
            res_previous_where = False # Bandera para identificar si se ha agregado algo "res_query_where"
            txt_table_previous_union = ""

            if isAll:
                pass
            else:
                #Se crea el query para los campos JSON que contienen un array de Strings|Integers
                if(specific_channel > 0):
                    query_union += " SELECT res_channel.* FROM(" if txt_table_previous_union == "" else " INNER JOIN("
                    query_union += " " + base_query + " WHERE channel_option = 0"
                    query_union += " UNION " + base_query + " WHERE channel_option = 1 AND JSON_CONTAINS(specific_channels, :specific_channel1)"
                    params["specific_channel1"] = str(specific_channel)
                    query_union += " UNION " + base_query + " WHERE channel_option = 2 AND JSON_CONTAINS(specific_channels, :specific_channel2) = 0"
                    params["specific_channel2"] = str(specific_channel)
                    query_union += " ) AS res_channel" if txt_table_previous_union == "" else " ) AS res_channel ON "+txt_table_previous_union+".iddef_restriction_detail"\
                    +" = res_channel.iddef_restriction_detail"
                    if txt_table_previous_union == "": txt_table_previous_union = "res_channel"

                if(bookable_weekday is not None):
                    query_union += " SELECT res_weekday.* FROM(" if txt_table_previous_union == "" else " INNER JOIN("
                    query_union += " " + base_query + " WHERE bookable_weekdays_option = 0"
                    query_union += " UNION " + base_query + " WHERE bookable_weekdays_option = 1 AND JSON_CONTAINS(bookable_weekdays, :bookable_weekday1)"
                    params["bookable_weekday1"] = str('"'+bookable_weekday+'"')
                    query_union += " UNION " + base_query + " WHERE bookable_weekdays_option = 2 AND JSON_CONTAINS(bookable_weekdays, :bookable_weekday2) = 0"
                    params["bookable_weekday2"] = str('"'+bookable_weekday+'"')
                    query_union += " ) AS res_weekday" if txt_table_previous_union == "" else " ) AS res_weekday ON "+txt_table_previous_union+".iddef_restriction_detail"\
                    +" = res_weekday.iddef_restriction_detail"
                    if txt_table_previous_union == "": txt_table_previous_union = "res_weekday"

                if(market_targeting > 0):
                    query_union += " SELECT res_market.* FROM(" if txt_table_previous_union == "" else " INNER JOIN("
                    query_union += " " + base_query + " WHERE market_option = 0"
                    query_union += " UNION " + base_query + " WHERE market_option = 1 AND JSON_CONTAINS(market_targeting, :market_targeting1)"
                    params["market_targeting1"] = str(market_targeting)
                    query_union += " UNION " + base_query + " WHERE market_option = 2 AND JSON_CONTAINS(market_targeting, :market_targeting2) = 0"
                    params["market_targeting2"] = str(market_targeting)
                    query_union += " ) AS res_market" if txt_table_previous_union == "" else " ) AS res_market ON "+txt_table_previous_union+".iddef_restriction_detail"\
                    +" = res_market.iddef_restriction_detail"
                    if txt_table_previous_union == "": txt_table_previous_union = "res_market"

                if(geo_targeting_country is not None):
                    query_union += " SELECT res_geo_targeting.* FROM(" if txt_table_previous_union == "" else " INNER JOIN("
                    query_union += " " + base_query + " WHERE geo_targeting_option = 0"
                    query_union += " UNION " + base_query + " WHERE geo_targeting_option = 1 AND JSON_CONTAINS(geo_targeting_countries, :geo_targeting_country1)"
                    params["geo_targeting_country1"] = str('"'+geo_targeting_country+'"')
                    query_union += " UNION " + base_query + " WHERE geo_targeting_option = 2 AND JSON_CONTAINS(geo_targeting_countries, :geo_targeting_country2) = 0"
                    params["geo_targeting_country2"] = str('"'+geo_targeting_country+'"')
                    query_union += " ) AS res_geo_targeting" if txt_table_previous_union == "" else " ) AS res_geo_targeting ON "+txt_table_previous_union+".iddef_restriction_detail"\
                    +" = res_geo_targeting.iddef_restriction_detail"
                    if txt_table_previous_union == "": txt_table_previous_union = "res_geo_targeting"

                #Se consulta en BD el valor maximo de objetos que contienen los campos JSON con array de objetos
                if(booking_window_date is not None or travel_window_start is not None or travel_window_end is not None or booking_window_time is not None):
                    max_json_length = dict(db.session.execute(str('SELECT MAX(max_data) AS max_data FROM (SELECT MAX(JSON_LENGTH(booking_window_dates)) AS max_data FROM def_restriction_detail UNION SELECT MAX(JSON_LENGTH(travel_window)) AS max_data FROM def_restriction_detail UNION SELECT MAX(JSON_LENGTH(booking_window_times)) AS max_data FROM def_restriction_detail) AS max_lengths;'), {}).fetchone())["max_data"]
                else:
                    max_json_length = 0

                #Se crea el query para consultas basica del "query_where"
                if(id_restriction_detail > 0):
                    query_where += " AND " if(previous_where) else " WHERE "
                    previous_where = True
                    query_where += "iddef_restriction_detail = :iddef_restriction_detail"
                    params["iddef_restriction_detail"] = int(id_restriction_detail)

                if(id_restriction > 0):
                    query_where += " AND " if(previous_where) else " WHERE "
                    previous_where = True
                    query_where += "iddef_restriction = :iddef_restriction"
                    params["iddef_restriction"] = int(id_restriction)

                if(device is not None):
                    query_where += " AND " if(previous_where) else " WHERE "
                    previous_where = True
                    query_where += "device_type_option = :device_type_option"
                    params["device_type_option"] = int(device)

                if(restriction_default is not None):
                    query_where += " AND " if(previous_where) else " WHERE "
                    previous_where = True
                    query_where += "restriction_default = :restriction_default"
                    params["restriction_default"] = int(restriction_default)

                if(restriction_by == 3):
                    if((restriction_type == 1 or restriction_type == 2 or restriction_type == 3) and use_value):
                        query_where += " AND " if(previous_where) else " WHERE "
                        previous_where = True
                        query_where += "JSON_EXTRACT(`value`,'$.room') = :value_room"
                        params["value_room"] = str(value_room)

                        query_where += " AND " if(previous_where) else " WHERE "
                        previous_where = True
                        query_where += "JSON_EXTRACT(`value`,'$.hotel_id') = :value_hotel_id"
                        params["value_hotel_id"] = int(value_hotel_id)

                if(restriction_by == 4):
                    if(restriction_type == 1 and use_value):
                        query_where += " AND " if(previous_where) else " WHERE "
                        previous_where = True
                        query_where += "JSON_EXTRACT(`value`,'$.room') = :value_room"
                        params["value_room"] = str(value_room)

                        query_where += " AND " if(previous_where) else " WHERE "
                        previous_where = True
                        query_where += "JSON_EXTRACT(`value`,'$.hotel_id') = :value_hotel_id"
                        params["value_hotel_id"] = int(value_hotel_id)

                        if value_rate_plan_id > 0:
                            query_where += " AND " if(previous_where) else " WHERE "
                            previous_where = True
                            query_where += "JSON_CONTAINS(JSON_EXTRACT(`value`,'$.rate_plan_id'), :value_rate_plan_id)"
                            params["value_rate_plan_id"] = str(value_rate_plan_id)

                if(restriction_by == 5):
                    if(restriction_type == 1 and use_value):
                        query_where += " AND " if(previous_where) else " WHERE "
                        previous_where = True
                        query_where += "JSON_EXTRACT(`value`,'$.hotel_id') = :value_hotel_id"
                        params["value_hotel_id"] = int(value_hotel_id)

                # if(estado is not None):
                #     query_where += " AND " if(previous_where) else " WHERE "
                #     previous_where = True
                #     query_where += "estado = :estado"
                #     params["estado"] = int(estado)

                # Se crea el CROSS JOIN como apoyo para los campos JSON con array de objetos
                if(max_json_length > 0):
                    query_join += " CROSS JOIN(SELECT 0 idx"
                    for x in range(1,max_json_length):
                        query_join += " UNION ALL SELECT " + str(x)
                    query_join += ") AS n"

                #Se crea el query para los campos JSON con array de objetos
                if(booking_window_date is not None and query_join != ""):
                    text_where = ""
                    subquery_index = len(arr_subquery)
                    text_where = "WHERE " if subquery_index > 0 else ""
                    arr_subquery.insert(subquery_index, {
                        "text":text_where+":booking_window_date1 >= JSON_EXTRACT(booking_window_dates, CONCAT('$[', n"+str(subquery_index)+".idx, '].start_date')) AND :booking_window_date2 <= JSON_EXTRACT(booking_window_dates, CONCAT('$[', n"+str(subquery_index)+".idx, '].end_date'))",
                        "text_alternative":text_where+":booking_window_date1 < JSON_EXTRACT(booking_window_dates, CONCAT('$[', n"+str(subquery_index)+".idx, '].start_date')) AND :booking_window_date2 > JSON_EXTRACT(booking_window_dates, CONCAT('$[', n"+str(subquery_index)+".idx, '].end_date'))",
                        "option":"booking_window_option"})
                    params["booking_window_date1"] = str(booking_window_date)
                    params["booking_window_date2"] = str(booking_window_date)
                    json_extract = True

                if(booking_window_time is not None and query_join != ""):
                    text_where = ""
                    subquery_index = len(arr_subquery)
                    text_where = "WHERE " if subquery_index > 0 else ""
                    arr_subquery.insert(subquery_index, {
                        "text":text_where+"(:booking_window_time1 >= JSON_EXTRACT(booking_window_times, CONCAT('$[', n"+str(subquery_index)+".idx, '].start_time')) AND :booking_window_time2 <= JSON_EXTRACT(booking_window_times, CONCAT('$[', n"+str(subquery_index)+".idx, '].end_time'))) OR JSON_LENGTH(JSON_EXTRACT(booking_window_times, '$')) = 0",
                        "text_alternative":"",
                        "option":""})
                    params["booking_window_time1"] = str(booking_window_time)
                    params["booking_window_time2"] = str(booking_window_time)
                    json_extract = True

                # Son necesarias fecha de inicio y final de travel_window, de otra forma no se agregará a la consulta
                if(travel_window_start is not None and travel_window_end is not None and query_join != ""):
                    text_where = ""
                    subquery_index = len(arr_subquery)
                    text_where = "WHERE " if subquery_index > 0 else ""
                    arr_subquery.insert(subquery_index, {
                        "text":text_where+"(JSON_EXTRACT(travel_window, CONCAT('$[', n"+str(subquery_index)+".idx, '].start_date')) <= :travel_window_end AND JSON_EXTRACT(travel_window, CONCAT('$[', n"+str(subquery_index)+".idx, '].end_date')) >= :travel_window_start)", 
                        "text_alternative":text_where+"(:travel_window_start < JSON_EXTRACT(travel_window, CONCAT('$[', n"+str(subquery_index)+".idx, '].start_date')) OR :travel_window_end > JSON_EXTRACT(travel_window, CONCAT('$[', n"+str(subquery_index)+".idx, '].end_date')))", 
                        "option":"travel_window_option"})
                    params["travel_window_start"] = str(travel_window_start)
                    params["travel_window_end"] = str(travel_window_end)
                    json_extract = True

                query_where0 = ""
                query_where1 = ""
                query_where2 = ""
                if(len(arr_subquery) > 0):
                    query_where0 = " AND "+arr_subquery[0]["option"] + " = 0" if(previous_where) else " WHERE "+arr_subquery[0]["option"] + " = 0"
                    query_where1 = " AND "+arr_subquery[0]["text"] if(previous_where) else " WHERE "+arr_subquery[0]["text"]
                    query_where2 = " AND "+arr_subquery[0]["text_alternative"] if(previous_where) else " WHERE "+arr_subquery[0]["text_alternative"]
                    previous_where = True

                    query_where1 += " AND "+arr_subquery[0]["option"] + " = 1"
                    query_where2 += " AND "+arr_subquery[0]["option"] + " = 2"

                    for temp_subquery_index, temp_subquery_value in enumerate(arr_subquery):
                        query_join_helper =  query_join + str(temp_subquery_index) if query_join != "" else ""
                        if(temp_subquery_index) == 0:
                            if(query_union != ""):
                                if(temp_subquery_value["text_alternative"] == ""):
                                    query = "SELECT rd"+str(temp_subquery_index)+".* FROM (" + "" + query_union +") AS rd"+ str(temp_subquery_index) + query_join_helper + query_where
                                else:
                                    query = "SELECT rd"+str(temp_subquery_index)+".* FROM (" + "" + query_union +") AS rd"+ str(temp_subquery_index) + query_join_helper + query_where + query_where0
                                    query += " UNION SELECT rd"+str(temp_subquery_index)+".* FROM (" + "" + query_union +") AS rd"+ str(temp_subquery_index) + query_join_helper + query_where + query_where1
                                    query += " UNION SELECT rd"+str(temp_subquery_index)+".* FROM (" + "" + query_union +") AS rd"+ str(temp_subquery_index) + query_join_helper + query_where + query_where2
                            else:
                                if(temp_subquery_value["text_alternative"] == ""):
                                    query = "SELECT rd"+str(temp_subquery_index)+".* FROM def_restriction_detail" + " AS rd"+ str(temp_subquery_index) + query_join_helper + query_where
                                else:
                                    query = "SELECT rd"+str(temp_subquery_index)+".* FROM def_restriction_detail" + " AS rd"+ str(temp_subquery_index) + query_join_helper + query_where + query_where0
                                    query += " UNION SELECT rd"+str(temp_subquery_index)+".* FROM def_restriction_detail" + " AS rd"+ str(temp_subquery_index) + query_join_helper + query_where + query_where1
                                    query += " UNION SELECT rd"+str(temp_subquery_index)+".* FROM def_restriction_detail" + " AS rd"+ str(temp_subquery_index) + query_join_helper + query_where + query_where2
                        else:
                            if(temp_subquery_value["text_alternative"] == ""):
                                query = "SELECT rd"+ str(temp_subquery_index) +".* FROM (" + query +")"+ " AS rd"+ str(temp_subquery_index) + query_join_helper +" "+temp_subquery_value["text"]
                            else:
                                temp_query0 = "SELECT rd"+ str(temp_subquery_index) +".* FROM (" + query +")"+ " AS rd"+ str(temp_subquery_index) + query_join_helper + " WHERE "+arr_subquery[temp_subquery_index]["option"] + " = 0"
                                temp_query1 = " UNION SELECT rd"+ str(temp_subquery_index) +".* FROM (" + query +")"+ " AS rd"+ str(temp_subquery_index) + query_join_helper +" "+temp_subquery_value["text"] + " AND "+arr_subquery[temp_subquery_index]["option"] + " = 1"
                                temp_query3 = " UNION SELECT rd"+ str(temp_subquery_index) +".* FROM (" + query +")"+ " AS rd"+ str(temp_subquery_index) + query_join_helper +" "+temp_subquery_value["text_alternative"] + " AND "+arr_subquery[temp_subquery_index]["option"] + " = 2"
                                query = temp_query0+temp_query1+temp_query3
                else:
                    if(query_union != ""):
                        query = "SELECT * FROM (" + query_union + ") AS tbl_json_filtered" + query_join + query_where
                    else:
                        query = query + query_join + query_where

                if(json_extract):
                    query += " GROUP BY iddef_restriction_detail"

                # Se crea el filtro para restrictions
                if(restriction_by > 0):
                    res_query_where += " AND " if(previous_where or len(arr_subquery) == 0) else " WHERE "
                    res_previous_where = True
                    res_query_where += "res.iddef_restriction_by = :iddef_restriction_by"
                    params["iddef_restriction_by"] = int(restriction_by)

                    if(restriction_by == 3):
                        if(restriction_type == 2 and use_min_los):
                            res_query_where += " AND " if(previous_where or len(arr_subquery) == 0) else " WHERE "
                            res_previous_where = True
                            res_query_where += "res_det.min_los = :min_los"
                            params["min_los"] = int(min_los)
                        elif(restriction_type == 3 and use_max_los):
                            res_query_where += " AND " if(previous_where or len(arr_subquery) == 0) else " WHERE "
                            res_previous_where = True
                            res_query_where += "res_det.max_los = :max_los"
                            params["max_los"] = int(max_los)

                if(restriction_type > 0):
                    res_query_where += " AND " if(previous_where or len(arr_subquery) == 0) else " WHERE "
                    res_previous_where = True
                    res_query_where += "res.iddef_restriction_type = :iddef_restriction_type"
                    params["iddef_restriction_type"] = int(restriction_type)

                if(estado_restriction is not None):
                    res_query_where += " AND " if(previous_where or len(arr_subquery) == 0) else " WHERE "
                    res_previous_where = True
                    res_query_where += "res.estado = :estado_restriction"
                    params["estado_restriction"] = int(estado_restriction)

                if(estado_detail is not None):
                    res_query_where += " AND " if(previous_where or len(arr_subquery) == 0) else " WHERE "
                    res_previous_where = True
                    res_query_where += "res_det.estado = :estado_detail"
                    params["estado_detail"] = int(estado_detail)

            query = "SELECT res.*, res_det.iddef_restriction_detail, res_det.channel_option, res_det.specific_channels, res_det.travel_window_option, res_det.travel_window, res_det.booking_window_option, res_det.booking_window_dates, res_det.bookable_weekdays_option, res_det.bookable_weekdays, res_det.booking_window_times, res_det.geo_targeting_option, res_det.geo_targeting_countries, res_det.market_option, res_det.market_targeting, res_det.device_type_option, res_det.restriction_default, res_det.min_los, res_det.max_los, res_det.value FROM("+query+") AS res_det JOIN def_restriction AS res ON res.iddef_restriction = res_det.iddef_restriction"+res_query_where+" GROUP BY res.iddef_restriction"
            query += ";"
            
            data = db.session.execute(query, params).fetchall()
            datos = schema.dump(data, many=True)

            #Algunos campos JSON se recuperan como string, por ello se ejecuta una conversión a Dict si se detecta como string
            for dato_index, dato_value in enumerate(datos):
                if isinstance(datos[dato_index]["geo_targeting_countries"], str): datos[dato_index]["geo_targeting_countries"] = json.loads(datos[dato_index]["geo_targeting_countries"])
                if isinstance(datos[dato_index]["specific_channels"], str): datos[dato_index]["specific_channels"] = json.loads(datos[dato_index]["specific_channels"])
                if isinstance(datos[dato_index]["travel_window"], str): datos[dato_index]["travel_window"] = json.loads(datos[dato_index]["travel_window"])
                if isinstance(datos[dato_index]["bookable_weekdays"], str): datos[dato_index]["bookable_weekdays"] = json.loads(datos[dato_index]["bookable_weekdays"])
                if isinstance(datos[dato_index]["market_targeting"], str): datos[dato_index]["market_targeting"] = json.loads(datos[dato_index]["market_targeting"])
                if isinstance(datos[dato_index]["booking_window_times"], str): datos[dato_index]["booking_window_times"] = json.loads(datos[dato_index]["booking_window_times"])
                if isinstance(datos[dato_index]["booking_window_dates"], str): datos[dato_index]["booking_window_dates"] = json.loads(datos[dato_index]["booking_window_dates"])
                if isinstance(datos[dato_index]["value"], str): datos[dato_index]["value"] = json.loads(datos[dato_index]["value"])

        except Exception as error:
            #datos = str(error)
            raise error

        return datos
    
    #Metodo para actualizar o crear
    @staticmethod
    def update_restriction(json_data_restriction,id_restriction):
        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            if int(id_restriction) == 0:
                schema_load = PostModelSchema(exclude=Util.get_default_excludes())
                json_data = schema_load.load(json_data_restriction)
                data = None
                Data = ResModel()
                Data.name = json_data["name"]
                Data.iddef_restriction_by = json_data["iddef_restriction_by"]
                Data.iddef_restriction_type = json_data["iddef_restriction_type"]
                Data.estado = 1
                Data.usuario_creacion = user_name
                db.session.add(Data)
                db.session.commit()
                data = schema.dump(Data)

                for y in json_data["data"]:
                    DataDetail = ResDetModel()
                    schemaDetail = Detailschema(exclude=Util.get_default_excludes())
                    json_detail = schemaDetail.load(y)
                    DataDetail.device_type_option = json_detail["device_type_option"]
                    DataDetail.iddef_restriction = Data.iddef_restriction
                    DataDetail.travel_window_option = json_detail["travel_window_option"]
                    DataDetail.geo_targeting_option = json_detail["geo_targeting_option"]
                    DataDetail.channel_option = json_detail["channel_option"]
                    DataDetail.bookable_weekdays_option = json_detail["bookable_weekdays_option"]
                    DataDetail.bookable_weekdays = json_detail["bookable_weekdays"]
                    DataDetail.booking_window_dates = json_detail["booking_window_dates"]
                    DataDetail.booking_window_times = json_detail["booking_window_times"]
                    DataDetail.booking_window_option = json_detail["booking_window_option"]
                    DataDetail.restriction_default = json_detail["restriction_default"]
                    DataDetail.market_option = json_detail["market_option"]
                    DataDetail.market_targeting = json_detail["market_targeting"]
                    DataDetail.travel_window = json_detail["travel_window"]
                    DataDetail.geo_targeting_countries = json_detail["geo_targeting_countries"]
                    DataDetail.specific_channels = json_detail["specific_channels"]
                    DataDetail.min_los = json_detail["min_los"]
                    DataDetail.max_los = json_detail["max_los"]
                    DataDetail.value = json_detail["value"]
                    DataDetail.estado = 1
                    DataDetail.usuario_creacion = user_name
                    db.session.add(DataDetail)
                    db.session.commit()
            else:
                schema_load = PutModelSchema(exclude=Util.get_default_excludes())
                json_data = schema_load.load(json_data_restriction)
                data = None
                model = ResModel.query.get(id_restriction)
                #if request.json.get("name") != None:
                if json_data["name"] != None:
                    model.name = json_data["name"]
                #if request.json.get("iddef_restriction_by") != None:
                if json_data["iddef_restriction_by"] != None:
                    model.iddef_restriction_by = json_data["iddef_restriction_by"]
                #if request.json.get("iddef_restriction_type") != None:
                if json_data["iddef_restriction_type"] != None:
                    model.iddef_restriction_type = json_data["iddef_restriction_type"]
                #if json_data["estado"] != None:
                    #model.estado = json_data["estado"]
                model.usuario_ultima_modificacion = user_name
                db.session.commit()
                data = schema.dump(model)

                for x in json_data["data"]:
                    schemaDetail = Detailschema(exclude=Util.get_default_excludes())
                    json_detail = schemaDetail.load(x)
                    if int(x["iddef_restriction_detail"]) == 0:
                        DataDetail = ResDetModel()
                        DataDetail.device_type_option = json_detail["device_type_option"]
                        DataDetail.iddef_restriction = model.iddef_restriction
                        DataDetail.travel_window_option = json_detail["travel_window_option"]
                        DataDetail.geo_targeting_option = json_detail["geo_targeting_option"]
                        DataDetail.channel_option = json_detail["channel_option"]
                        DataDetail.bookable_weekdays_option = json_detail["bookable_weekdays_option"]
                        DataDetail.bookable_weekdays = json_detail["bookable_weekdays"]
                        DataDetail.booking_window_dates = json_detail["booking_window_dates"]
                        DataDetail.booking_window_times = json_detail["booking_window_times"]
                        DataDetail.booking_window_option = json_detail["booking_window_option"]
                        DataDetail.restriction_default = json_detail["restriction_default"]
                        DataDetail.market_option = json_detail["market_option"]
                        DataDetail.market_targeting = json_detail["market_targeting"]
                        DataDetail.travel_window = json_detail["travel_window"]
                        DataDetail.geo_targeting_countries = json_detail["geo_targeting_countries"]
                        DataDetail.specific_channels = json_detail["specific_channels"]
                        DataDetail.specific_channels = json_detail["specific_channels"]
                        DataDetail.min_los = json_detail["min_los"]
                        DataDetail.max_los = json_detail["max_los"]
                        DataDetail.value = json_detail["value"]
                        DataDetail.estado = 1
                        DataDetail.usuario_creacion = user_name
                        db.session.add(DataDetail)
                        db.session.commit()
                    else:
                        modelDetail = ResDetModel.query.get(x["iddef_restriction_detail"])
                        if x["device_type_option"] != None:
                            modelDetail.device_type_option = json_detail["device_type_option"]
                        if x["iddef_restriction"] != None:
                            modelDetail.iddef_restriction = id_restriction
                        if x["travel_window_option"] != None:
                            modelDetail.travel_window_option = json_detail["travel_window_option"]
                        if x["geo_targeting_option"] != None:
                            modelDetail.geo_targeting_option = json_detail["geo_targeting_option"]
                        if x["channel_option"] != None:
                            modelDetail.channel_option = json_detail["channel_option"]
                        if x["bookable_weekdays_option"] != None:
                            modelDetail.bookable_weekdays_option = json_detail["bookable_weekdays_option"]
                        if x["bookable_weekdays"] != None:
                            modelDetail.bookable_weekdays = json_detail["bookable_weekdays"]
                        if x["booking_window_dates"] != None:
                            modelDetail.booking_window_dates = json_detail["booking_window_dates"]
                        if x["booking_window_times"] != None:
                            modelDetail.booking_window_times = json_detail["booking_window_times"]
                        if x["booking_window_option"] != None:
                            modelDetail.booking_window_option = json_detail["booking_window_option"]
                        if x["restriction_default"] != None:
                            modelDetail.restriction_default = json_detail["restriction_default"]
                        if x["market_option"] != None:
                            modelDetail.market_option = json_detail["market_option"]
                        if x["market_targeting"] != None:
                            modelDetail.market_targeting = json_detail["market_targeting"]
                        if x["travel_window"] != None:
                            modelDetail.travel_window = json_detail["travel_window"]
                        if x["geo_targeting_countries"] != None:
                            modelDetail.geo_targeting_countries = json_detail["geo_targeting_countries"]
                        if x["specific_channels"] != None:
                            modelDetail.specific_channels = json_detail["specific_channels"]
                        if x["min_los"] != None:
                            modelDetail.min_los = json_detail["min_los"]
                        if x["max_los"] != None:
                            modelDetail.max_los = json_detail["max_los"]
                        if x["value"] != None:
                            modelDetail.value = json_detail["value"]
                        #if x["estado"] != None:
                            #modelDetail.estado = json_detail["estado"]
                        modelDetail.estado = 1
                        modelDetail.usuario_ultima_modificacion = user_name
                        db.session.commit()
        
        except Exception as ex:
            raise Exception("Error al crear/actualizar restriction "+str(ex))

        return data

    @staticmethod
    def getRestrictionDetailInfo(id_restriction=None):
        data = None
        schemaDetail = ResDetSchema(exclude=Util.get_default_excludes())
        if id_restriction is not None:
            obj_restriction_detail = {}
            dataRestriction = ResModel.query.filter_by(iddef_restriction=id_restriction).first()
            if dataRestriction is not None:
                obj_restriction_detail["iddef_restriction"] = dataRestriction.iddef_restriction
                obj_restriction_detail["name"] = dataRestriction.name
                dataRestrictionDetail = ResDetModel.query.filter_by(iddef_restriction=id_restriction).first()
                if dataRestrictionDetail is not None:
                    obj_restriction_detail["data"] = schemaDetail.dump(dataRestrictionDetail)
                else: 
                    obj_restriction_detail["data"] = []
                data = obj_restriction_detail

        return data
    
    @staticmethod
    def getRestrictionDetailsInfo(id_restriction=None,iddef_restriction_by=None,\
    iddef_restriction_type=None,hotel_id=None,room=None,isAll=True):
        data = None
        conditions = []
        obj_restriction_detail = {}
        schemaDetail = ResDetSchema(exclude=Util.get_default_excludes())

        if id_restriction is not None:
            conditions.append(ResModel.iddef_restriction==id_restriction)
        if iddef_restriction_by is not None:
            conditions.append(ResModel.iddef_restriction_by==iddef_restriction_by)
        if iddef_restriction_type is not None:
            conditions.append(ResModel.iddef_restriction_type==iddef_restriction_type)
        if hotel_id is not None:
            conditions.append(func.json_extract(ResDetModel.value, '$.hotel_id') == hotel_id)
        if room is not None:
            conditions.append(func.json_extract(ResDetModel.value, '$.room') == room)
        if isAll:
            dataRestriction = ResDetModel.query.join(ResModel, ResModel.iddef_restriction==ResDetModel.iddef_restriction\
            ).filter(and_(*conditions)).all()
        else:
            dataRestriction = ResDetModel.query.join(ResModel).filter(and_(*conditions)).first()

        if dataRestriction is not None:
            data = schemaDetail.dump(dataRestriction)

        if len(dataRestriction) > 0:
            data = schemaDetail.dump(dataRestriction, many=True)

        return data

    @staticmethod
    def get_type_opera_restriction(text_type_restriction=""):
        restr_types = {
            "market":1,
            "rateplan":2,
            "room":3,
            "rateplan/room":4,
            "property":5,
            "general_restriction":6,
            "promotions":7
        }

        if text_type_restriction == None or text_type_restriction == "":
            raise Exception("Type restriction empty")
        else:
            text_type_restriction = text_type_restriction.lower()
            return restr_types.get(text_type_restriction, 0)

    # Metodo para obtener o crear la restricción principal donde se insertarán los detalles
    # Retornará un objeto "Restriction"
    @staticmethod
    def get_create_opera_restriction(restriction_type, restriction_type_value=1, user_name="Opera"):
        value_restriction_type = RestricctionFunction.get_type_opera_restriction(restriction_type)
        model = ResModel.query.filter(ResModel.name=="Opera", ResModel.iddef_restriction_by == value_restriction_type, ResModel.iddef_restriction_type==restriction_type_value).first()

        if model is None:
            model = ResModel()
            model.name = "Opera"
            model.iddef_restriction_by = value_restriction_type
            model.iddef_restriction_type = restriction_type_value #1 - close_date, 2 - min_los, 3 - max_los, 4 - apply
            model.estado = 1
            model.usuario_creacion = user_name
            db.session.add(model)
            db.session.commit()
        elif model.estado == 0:
            model.estado = 1
            db.session.commit()
        return model

    #Metodo para insertar restricciones de Opera
    @staticmethod
    def process_opera_restriction(restriction_type,data_restrictions,user_name="admin"):
        #count_success=0
        count_errors=0
        count_inserted=0
        errors=[]  #formato error = [{"data":{},"error":"Error information"}]

        try:
            for info_restriction in data_restrictions:
                try:
                    # main_restriction = RestricctionFunction.get_create_opera_restriction(restriction_type=restriction_type, 
                    #     restriction_type_value=restriction_type_value, user_name=user_name)
                    result = RestricctionFunction.insert_opera_restrictions2(info_restriction=info_restriction,restriction_type=restriction_type,
                        user_name=user_name)
                    if result>0:
                        #count_success+=1
                        count_inserted+=result
                except Exception as ex:
                    count_errors+=1
                    errors.append({"data":data_restrictions,"error":str(ex)})

        except Exception as ex:
            count_errors+=1
            errors.append({"data":{"restriction_type":restriction_type},"error":str(ex)})

        return {
            #"data_success":count_success,
            "inserted_restrictions":count_inserted,
            "data_errors":count_errors,
            "info_errors":errors
        }

    # Metodo para guardar cada restricción de Opera
    # Retornará el numero de elementos (detalles) insertados
    @staticmethod
    def insert_opera_restrictions2(info_restriction,restriction_type,user_name="admin"):
        try:
            result = 0
            confirm_save = False
            if len(info_restriction["restrictions"]) > 0:
                model_property = proModel.query.filter(proModel.property_code==info_restriction["property"],proModel.estado==1).first()
                if model_property is None:
                    raise Exception("Property {0:s} not found".format(info_restriction["property"]))
                else:
                    id_property = model_property.iddef_property
                    value_restriction_by = RestricctionFunction.get_type_opera_restriction(restriction_type)
                    for info_restriction_detail in info_restriction["restrictions"]:
                        estado = 1
                        restriction_type_value = 0
                        restriction_type_value2 = 0
                        restriction_type_value3 = 0
                        estado, estado2, estado3 = 0, 0, 0
                        #divide_dates=False
                        info_date_start = dt.strptime(info_restriction_detail["date_start"], '%Y-%m-%d')
                        info_date_end = dt.strptime(info_restriction_detail["date_end"], '%Y-%m-%d')

                        # Se retiran validaciones ya que se tomarán en cuenta los estado False y 0 en el proceso
                        restriction_type_value = 1 #Fechas cerradas
                        estado = 1 if info_restriction_detail["close"] == True else 0
                        use_close = info_restriction_detail["use_close"]
                        restriction_type_value2 = 2 #min_los
                        estado2 = 1 if info_restriction_detail["min_los"] > 0 else 0
                        use_min = info_restriction_detail["use_min"]
                        restriction_type_value3 = 3 #max_los
                        estado3 = 1 if info_restriction_detail["max_los"] > 0 else 0
                        use_max = info_restriction_detail["use_max"]

                        model_room = rtcModel.query.filter(rtcModel.iddef_property==id_property, rtcModel.room_code==info_restriction["room"],
                            rtcModel.estado==1).first()
                        if model_room is None and value_restriction_by == 3:
                            raise Exception("The room {0:s} is not valid for property {1:s}".format(info_restriction["room"], info_restriction["property"]))
                        elif model_room is None and value_restriction_by != 3:
                            id_room_type = 0
                        else:
                            id_room_type = model_room.iddef_room_type_category

                        #Proceso de fechas cerradas
                        if use_close and restriction_type_value > 0:
                            if value_restriction_by == 3:
                                list_opera_restrictions = OpeResModel.query.filter(
                                    and_(
                                        or_(
                                            and_(OpeResModel.date_start <= info_restriction_detail["date_start"], 
                                                OpeResModel.date_end >= info_restriction_detail["date_end"]),
                                            and_(OpeResModel.date_start >= info_restriction_detail["date_start"], 
                                                OpeResModel.date_end <= info_restriction_detail["date_end"]),
                                            and_(OpeResModel.date_start > info_restriction_detail["date_start"], 
                                                OpeResModel.date_end > info_restriction_detail["date_end"],
                                                OpeResModel.date_start <= info_restriction_detail["date_end"],
                                                OpeResModel.date_end >= info_restriction_detail["date_start"]),
                                            and_(OpeResModel.date_start <= info_restriction_detail["date_start"], 
                                                OpeResModel.date_end < info_restriction_detail["date_end"],
                                                OpeResModel.date_start < info_restriction_detail["date_end"],
                                                OpeResModel.date_end >= info_restriction_detail["date_start"])
                                        )
                                    ),
                                    OpeResModel.id_restriction_by.in_([3,4]), 
                                    OpeResModel.id_restriction_type==restriction_type_value, OpeResModel.id_room_type==id_room_type, 
                                    OpeResModel.id_property==id_property, 
                                    OpeResModel.estado==1).all()
                                # if len(list_opera_restrictions) == 0:
                                #     list_opera_restrictions = OpeResModel.query.filter(
                                #         and_(
                                #             or_(
                                #                 and_(OpeResModel.date_start > info_restriction_detail["date_start"], 
                                #                     OpeResModel.date_end > info_restriction_detail["date_end"],
                                #                     OpeResModel.date_start <= info_restriction_detail["date_end"],
                                #                     OpeResModel.date_end >= info_restriction_detail["date_start"]),
                                #                 and_(OpeResModel.date_start <= info_restriction_detail["date_start"], 
                                #                     OpeResModel.date_end < info_restriction_detail["date_end"],
                                #                     OpeResModel.date_start < info_restriction_detail["date_end"],
                                #                     OpeResModel.date_end >= info_restriction_detail["date_start"])
                                #             )
                                #         ),
                                #         OpeResModel.id_restriction_by.in_([3,4]), 
                                #         OpeResModel.id_restriction_type==restriction_type_value, OpeResModel.id_room_type==id_room_type, 
                                #         OpeResModel.id_property==id_property, 
                                #         OpeResModel.estado==1).all()
                            elif value_restriction_by == 5:
                                id_room_type = 0
                                list_rooms = rtcModel.query.filter(rtcModel.iddef_property==id_property, rtcModel.estado==1).all()
                                list_id_rooms = [obj_rtc.iddef_room_type_category for obj_rtc in list_rooms]
                                list_rooms_update = [] # Se guardarán los id_rooms y la información de las restricciones relacionadas
                                for id_room_type_elem in list_id_rooms:
                                    list_opera_restrictions_temp = OpeResModel.query.filter(
                                        and_(
                                            or_(
                                                and_(OpeResModel.date_start <= info_restriction_detail["date_start"], 
                                                    OpeResModel.date_end >= info_restriction_detail["date_end"]),
                                                and_(OpeResModel.date_start >= info_restriction_detail["date_start"], 
                                                    OpeResModel.date_end <= info_restriction_detail["date_end"]),
                                                and_(OpeResModel.date_start > info_restriction_detail["date_start"], 
                                                    OpeResModel.date_end > info_restriction_detail["date_end"],
                                                    OpeResModel.date_start <= info_restriction_detail["date_end"],
                                                    OpeResModel.date_end >= info_restriction_detail["date_start"]),
                                                and_(OpeResModel.date_start <= info_restriction_detail["date_start"], 
                                                    OpeResModel.date_end < info_restriction_detail["date_end"],
                                                    OpeResModel.date_start < info_restriction_detail["date_end"],
                                                    OpeResModel.date_end >= info_restriction_detail["date_start"])
                                            )
                                        ),
                                        OpeResModel.id_restriction_by.in_([3,4]), 
                                        OpeResModel.id_restriction_type==restriction_type_value, OpeResModel.id_room_type==id_room_type_elem, 
                                        OpeResModel.id_property==id_property, 
                                        OpeResModel.estado==1).all()
                                    list_rooms_update.append({"id_room_type":id_room_type_elem,"list_opera_restrictions":list_opera_restrictions_temp})
                                    # if len(list_opera_restrictions_temp) == 0:
                                    #     list_opera_restrictions_temp = OpeResModel.query.filter(
                                    #         and_(
                                    #             or_(
                                    #                 and_(OpeResModel.date_start > info_restriction_detail["date_start"], 
                                    #                     OpeResModel.date_end > info_restriction_detail["date_end"],
                                    #                     OpeResModel.date_start <= info_restriction_detail["date_end"],
                                    #                     OpeResModel.date_end >= info_restriction_detail["date_start"]),
                                    #                 and_(OpeResModel.date_start <= info_restriction_detail["date_start"], 
                                    #                     OpeResModel.date_end < info_restriction_detail["date_end"],
                                    #                     OpeResModel.date_start < info_restriction_detail["date_end"],
                                    #                     OpeResModel.date_end >= info_restriction_detail["date_start"])
                                    #             )
                                    #         ),
                                    #         OpeResModel.id_restriction_by.in_([3,4]), 
                                    #         OpeResModel.id_restriction_type==restriction_type_value, OpeResModel.id_room_type==id_room_type_elem, 
                                    #         OpeResModel.id_property==id_property, 
                                    #         OpeResModel.estado==1).all()
                                    #     list_rooms_update.append({"id_room_type":id_room_type_elem,"list_opera_restrictions":list_opera_restrictions_temp})
                                    # else:
                                    #     list_rooms_update.append({"id_room_type":id_room_type_elem,"list_opera_restrictions":list_opera_restrictions_temp})
                            else:
                                raise Exception("Restriction_by {0:s} is not valid for Opera information".format(value_restriction_by))

                            if value_restriction_by != 5:
                                cont = 0
                                rows_afected = []
                                while cont < len(list_opera_restrictions):

                                    row = {
                                        "date_start": dt.strptime(list_opera_restrictions[cont].date_start.strftime("%Y-%m-%d"), '%Y-%m-%d'),
                                        "date_end":dt.strptime(list_opera_restrictions[cont].date_end.strftime("%Y-%m-%d"), '%Y-%m-%d'),
                                        "value":list_opera_restrictions[cont].value,
                                        "position":cont
                                    }

                                    rows_afected.append(row)

                                    list_opera_restrictions[cont].estado = 0
                                    list_opera_restrictions[cont].usuario_ultima_modificacion = user_name
                                    db.session.flush()
                                    confirm_save = True
                                    cont += 1


                                date_end_before = info_date_start - datetime.timedelta(days=1)
                                date_start_after = info_date_end + datetime.timedelta(days=1)

                                # Se dividen las fechas cuando chocan con una inserción (se mantienen activas)
                                if len(rows_afected) > 0:
                                    #Creamos nuevos registros
                                    for rows in rows_afected:
                                        date_start = rows["date_start"]
                                        date_end = rows["date_end"]

                                        if date_start < info_date_start and date_end > info_date_end:

                                            new_ope_res_before = OpeResModel()
                                            new_ope_res_before.id_restriction_by = value_restriction_by
                                            new_ope_res_before.id_restriction_type = restriction_type_value
                                            new_ope_res_before.id_room_type = id_room_type
                                            new_ope_res_before.id_property = id_property
                                            new_ope_res_before.id_rateplan = 0
                                            new_ope_res_before.value = rows["value"]
                                            new_ope_res_before.is_override = 0
                                            new_ope_res_before.date_start = date_start
                                            new_ope_res_before.date_end = date_end_before
                                            new_ope_res_before.estado = 1
                                            new_ope_res_before.usuario_creacion = user_name
                                            db.session.add(new_ope_res_before)

                                            new_ope_res_after = OpeResModel()
                                            new_ope_res_after.id_restriction_by = value_restriction_by
                                            new_ope_res_after.id_restriction_type = restriction_type_value
                                            new_ope_res_after.id_room_type = id_room_type
                                            new_ope_res_after.id_property = id_property
                                            new_ope_res_after.id_rateplan = 0
                                            new_ope_res_after.value = rows["value"]
                                            new_ope_res_after.is_override = 0
                                            new_ope_res_after.date_start = date_start_after
                                            new_ope_res_after.date_end = date_end
                                            new_ope_res_after.estado = 1
                                            new_ope_res_after.usuario_creacion = user_name
                                            db.session.add(new_ope_res_after)

                                        elif date_end > info_date_end and date_start >= info_date_start:

                                            new_ope_res = OpeResModel()
                                            new_ope_res.id_restriction_by = value_restriction_by
                                            new_ope_res.id_restriction_type = restriction_type_value
                                            new_ope_res.id_room_type = id_room_type
                                            new_ope_res.id_property = id_property
                                            new_ope_res.id_rateplan = 0
                                            new_ope_res.value = rows["value"]
                                            new_ope_res.is_override = 0
                                            new_ope_res.date_start = date_start_after
                                            new_ope_res.date_end = date_end
                                            new_ope_res.estado = 1
                                            new_ope_res.usuario_creacion = user_name
                                            db.session.add(new_ope_res)

                                        elif date_start < info_date_start and date_end <= info_date_end:
                                            #Creamos un registro para las fechas anteriores
                                            new_ope_res = OpeResModel()
                                            new_ope_res.id_restriction_by = value_restriction_by
                                            new_ope_res.id_restriction_type = restriction_type_value
                                            new_ope_res.id_room_type = id_room_type
                                            new_ope_res.id_property = id_property
                                            new_ope_res.id_rateplan = 0
                                            new_ope_res.value = rows["value"]
                                            new_ope_res.is_override = 0
                                            new_ope_res.date_start = date_start
                                            new_ope_res.date_end = date_end_before
                                            new_ope_res.estado = 1
                                            new_ope_res.usuario_creacion = user_name
                                            db.session.add(new_ope_res)

                                if restriction_type_value == 2: #min_los
                                    info_value = info_restriction_detail["min_los"]
                                elif restriction_type_value == 3: #max_los
                                    info_value = info_restriction_detail["max_los"]
                                else:
                                    info_value = 0

                                if estado > 0:
                                    opeResDataAux = OpeResModel()

                                    opeResDataAux.id_restriction_by = value_restriction_by
                                    opeResDataAux.id_restriction_type = restriction_type_value
                                    opeResDataAux.id_room_type = id_room_type
                                    opeResDataAux.id_property = id_property
                                    opeResDataAux.id_rateplan = 0
                                    opeResDataAux.value = info_value
                                    opeResDataAux.is_override = 0
                                    opeResDataAux.date_start = info_date_start
                                    opeResDataAux.date_end = info_date_end
                                    opeResDataAux.estado = estado
                                    opeResDataAux.usuario_creacion = user_name

                                    db.session.add(opeResDataAux)
                                    db.session.flush()
                                    confirm_save = True

                                    result += 1
                            elif value_restriction_by == 5 and restriction_type_value in (2,3):
                                for obj_room_restriction in list_rooms_update:
                                    cont = 0
                                    rows_afected = []
                                    while cont < len(obj_room_restriction["list_opera_restrictions"]):

                                        row = {
                                            "date_start": dt.strptime(obj_room_restriction["list_opera_restrictions"][cont].date_start.strftime("%Y-%m-%d"), '%Y-%m-%d'),
                                            "date_end":dt.strptime(obj_room_restriction["list_opera_restrictions"][cont].date_end.strftime("%Y-%m-%d"), '%Y-%m-%d'),
                                            "value":obj_room_restriction["list_opera_restrictions"][cont].value,
                                            "position":cont
                                        }

                                        rows_afected.append(row)

                                        obj_room_restriction["list_opera_restrictions"][cont].estado = 0
                                        obj_room_restriction["list_opera_restrictions"][cont].usuario_ultima_modificacion = user_name
                                        db.session.flush()
                                        confirm_save = True
                                        cont += 1


                                    date_end_before = info_date_start - datetime.timedelta(days=1)
                                    date_start_after = info_date_end + datetime.timedelta(days=1)

                                    # Se dividen las fechas cuando chocan con una inserción (se mantienen activas)
                                    if len(rows_afected) > 0:
                                        #Creamos nuevos registros
                                        for rows in rows_afected:
                                            date_start = rows["date_start"]
                                            date_end = rows["date_end"]

                                            if date_start < info_date_start and date_end > info_date_end:

                                                new_ope_res_before = OpeResModel()
                                                new_ope_res_before.id_restriction_by = 3
                                                new_ope_res_before.id_restriction_type = restriction_type_value
                                                new_ope_res_before.id_room_type = obj_room_restriction["id_room_type"]
                                                new_ope_res_before.id_property = id_property
                                                new_ope_res_before.id_rateplan = 0
                                                new_ope_res_before.value = rows["value"]
                                                new_ope_res_before.is_override = 0
                                                new_ope_res_before.date_start = date_start
                                                new_ope_res_before.date_end = date_end_before
                                                new_ope_res_before.estado = 1
                                                new_ope_res_before.usuario_creacion = user_name
                                                db.session.add(new_ope_res_before)

                                                new_ope_res_after = OpeResModel()
                                                new_ope_res_after.id_restriction_by = 3
                                                new_ope_res_after.id_restriction_type = restriction_type_value
                                                new_ope_res_after.id_room_type = obj_room_restriction["id_room_type"]
                                                new_ope_res_after.id_property = id_property
                                                new_ope_res_after.id_rateplan = 0
                                                new_ope_res_after.value = rows["value"]
                                                new_ope_res_after.is_override = 0
                                                new_ope_res_after.date_start = date_start_after
                                                new_ope_res_after.date_end = date_end
                                                new_ope_res_after.estado = 1
                                                new_ope_res_after.usuario_creacion = user_name
                                                db.session.add(new_ope_res_after)

                                            elif date_end > info_date_end and date_start >= info_date_start:

                                                new_ope_res = OpeResModel()
                                                new_ope_res.id_restriction_by = 3
                                                new_ope_res.id_restriction_type = restriction_type_value
                                                new_ope_res.id_room_type = obj_room_restriction["id_room_type"]
                                                new_ope_res.id_property = id_property
                                                new_ope_res.id_rateplan = 0
                                                new_ope_res.value = rows["value"]
                                                new_ope_res.is_override = 0
                                                new_ope_res.date_start = date_start_after
                                                new_ope_res.date_end = date_end
                                                new_ope_res.estado = 1
                                                new_ope_res.usuario_creacion = user_name
                                                db.session.add(new_ope_res)

                                            elif date_start < info_date_start and date_end <= info_date_end:
                                                #Creamos un registro para las fechas anteriores
                                                new_ope_res = OpeResModel()
                                                new_ope_res.id_restriction_by = 3
                                                new_ope_res.id_restriction_type = restriction_type_value
                                                new_ope_res.id_room_type = obj_room_restriction["id_room_type"]
                                                new_ope_res.id_property = id_property
                                                new_ope_res.id_rateplan = 0
                                                new_ope_res.value = rows["value"]
                                                new_ope_res.is_override = 0
                                                new_ope_res.date_start = date_start
                                                new_ope_res.date_end = date_end_before
                                                new_ope_res.estado = 1
                                                new_ope_res.usuario_creacion = user_name
                                                db.session.add(new_ope_res)

                                    if restriction_type_value == 2: #min_los
                                        info_value = info_restriction_detail["min_los"]
                                    elif restriction_type_value == 3: #max_los
                                        info_value = info_restriction_detail["max_los"]
                                    else:
                                        info_value = 0

                                    if estado > 0:
                                        opeResDataAux = OpeResModel()

                                        opeResDataAux.id_restriction_by = 3
                                        opeResDataAux.id_restriction_type = restriction_type_value
                                        opeResDataAux.id_room_type = obj_room_restriction["id_room_type"]
                                        opeResDataAux.id_property = id_property
                                        opeResDataAux.id_rateplan = 0
                                        opeResDataAux.value = info_value
                                        opeResDataAux.is_override = 0
                                        opeResDataAux.date_start = info_date_start
                                        opeResDataAux.date_end = info_date_end
                                        opeResDataAux.estado = estado
                                        opeResDataAux.usuario_creacion = user_name

                                        db.session.add(opeResDataAux)
                                        db.session.flush()
                                        confirm_save = True

                                        result += 1

                        #Proceso de min_los
                        if use_min and restriction_type_value2 > 0:
                            if value_restriction_by == 3:
                                list_opera_restrictions = OpeResModel.query.filter(
                                    and_(
                                        or_(
                                            and_(OpeResModel.date_start <= info_restriction_detail["date_start"], 
                                                OpeResModel.date_end >= info_restriction_detail["date_end"]),
                                            and_(OpeResModel.date_start >= info_restriction_detail["date_start"], 
                                                OpeResModel.date_end <= info_restriction_detail["date_end"]),
                                            and_(OpeResModel.date_start > info_restriction_detail["date_start"], 
                                                OpeResModel.date_end > info_restriction_detail["date_end"],
                                                OpeResModel.date_start <= info_restriction_detail["date_end"],
                                                OpeResModel.date_end >= info_restriction_detail["date_start"]),
                                            and_(OpeResModel.date_start <= info_restriction_detail["date_start"], 
                                                OpeResModel.date_end < info_restriction_detail["date_end"],
                                                OpeResModel.date_start < info_restriction_detail["date_end"],
                                                OpeResModel.date_end >= info_restriction_detail["date_start"])
                                        )
                                    ),
                                    OpeResModel.id_restriction_by.in_([3,4]), 
                                    OpeResModel.id_restriction_type==restriction_type_value2, OpeResModel.id_room_type==id_room_type, 
                                    OpeResModel.id_property==id_property, 
                                    OpeResModel.estado==1).all()
                                # if len(list_opera_restrictions) == 0:
                                #     list_opera_restrictions = OpeResModel.query.filter(
                                #         and_(
                                #             or_(
                                #                 and_(OpeResModel.date_start > info_restriction_detail["date_start"], 
                                #                     OpeResModel.date_end > info_restriction_detail["date_end"],
                                #                     OpeResModel.date_start <= info_restriction_detail["date_end"],
                                #                     OpeResModel.date_end >= info_restriction_detail["date_start"]),
                                #                 and_(OpeResModel.date_start <= info_restriction_detail["date_start"], 
                                #                     OpeResModel.date_end < info_restriction_detail["date_end"],
                                #                     OpeResModel.date_start < info_restriction_detail["date_end"],
                                #                     OpeResModel.date_end >= info_restriction_detail["date_start"])
                                #             )
                                #         ),
                                #         OpeResModel.id_restriction_by.in_([3,4]), 
                                #         OpeResModel.id_restriction_type==restriction_type_value2, OpeResModel.id_room_type==id_room_type, 
                                #         OpeResModel.id_property==id_property, 
                                #         OpeResModel.estado==1).all()
                            elif value_restriction_by == 5:
                                id_room_type = 0
                                list_rooms = rtcModel.query.filter(rtcModel.iddef_property==id_property, rtcModel.estado==1).all()
                                list_id_rooms = [obj_rtc.iddef_room_type_category for obj_rtc in list_rooms]
                                list_rooms_update = [] # Se guardarán los id_rooms y la información de las restricciones relacionadas
                                for id_room_type_elem in list_id_rooms:
                                    list_opera_restrictions_temp = OpeResModel.query.filter(
                                        and_(
                                            or_(
                                                and_(OpeResModel.date_start <= info_restriction_detail["date_start"], 
                                                    OpeResModel.date_end >= info_restriction_detail["date_end"]),
                                                and_(OpeResModel.date_start >= info_restriction_detail["date_start"], 
                                                    OpeResModel.date_end <= info_restriction_detail["date_end"]),
                                                and_(OpeResModel.date_start > info_restriction_detail["date_start"], 
                                                    OpeResModel.date_end > info_restriction_detail["date_end"],
                                                    OpeResModel.date_start <= info_restriction_detail["date_end"],
                                                    OpeResModel.date_end >= info_restriction_detail["date_start"]),
                                                and_(OpeResModel.date_start <= info_restriction_detail["date_start"], 
                                                    OpeResModel.date_end < info_restriction_detail["date_end"],
                                                    OpeResModel.date_start < info_restriction_detail["date_end"],
                                                    OpeResModel.date_end >= info_restriction_detail["date_start"])
                                            )
                                        ),
                                        OpeResModel.id_restriction_by.in_([3,4]), 
                                        OpeResModel.id_restriction_type==restriction_type_value2, OpeResModel.id_room_type==id_room_type_elem, 
                                        OpeResModel.id_property==id_property, 
                                        OpeResModel.estado==1).all()
                                    list_rooms_update.append({"id_room_type":id_room_type_elem,"list_opera_restrictions":list_opera_restrictions_temp})
                                    # if len(list_opera_restrictions_temp) == 0:
                                    #     list_opera_restrictions_temp = OpeResModel.query.filter(
                                    #         and_(
                                    #             or_(
                                    #                 and_(OpeResModel.date_start > info_restriction_detail["date_start"], 
                                    #                     OpeResModel.date_end > info_restriction_detail["date_end"],
                                    #                     OpeResModel.date_start <= info_restriction_detail["date_end"],
                                    #                     OpeResModel.date_end >= info_restriction_detail["date_start"]),
                                    #                 and_(OpeResModel.date_start <= info_restriction_detail["date_start"], 
                                    #                     OpeResModel.date_end < info_restriction_detail["date_end"],
                                    #                     OpeResModel.date_start < info_restriction_detail["date_end"],
                                    #                     OpeResModel.date_end >= info_restriction_detail["date_start"])
                                    #             )
                                    #         ),
                                    #         OpeResModel.id_restriction_by.in_([3,4]), 
                                    #         OpeResModel.id_restriction_type==restriction_type_value2, OpeResModel.id_room_type==id_room_type_elem, 
                                    #         OpeResModel.id_property==id_property, 
                                    #         OpeResModel.estado==1).all()
                                    #     list_rooms_update.append({"id_room_type":id_room_type_elem,"list_opera_restrictions":list_opera_restrictions_temp})
                                    # else:
                                    #     list_rooms_update.append({"id_room_type":id_room_type_elem,"list_opera_restrictions":list_opera_restrictions_temp})
                            else:
                                raise Exception("Restriction_by {0:s} is not valid for Opera information".format(value_restriction_by))

                            if value_restriction_by != 5:
                                cont = 0
                                rows_afected = []
                                while cont < len(list_opera_restrictions):

                                    row = {
                                        "date_start": dt.strptime(list_opera_restrictions[cont].date_start.strftime("%Y-%m-%d"), '%Y-%m-%d'),
                                        "date_end":dt.strptime(list_opera_restrictions[cont].date_end.strftime("%Y-%m-%d"), '%Y-%m-%d'),
                                        "value":list_opera_restrictions[cont].value,
                                        "position":cont
                                    }

                                    rows_afected.append(row)

                                    list_opera_restrictions[cont].estado = 0
                                    list_opera_restrictions[cont].usuario_ultima_modificacion = user_name
                                    db.session.flush()
                                    confirm_save = True
                                    cont += 1


                                date_end_before = info_date_start - datetime.timedelta(days=1)
                                date_start_after = info_date_end + datetime.timedelta(days=1)

                                # Se dividen las fechas cuando chocan con una inserción (se mantienen activas)
                                if len(rows_afected) > 0:
                                    #Creamos nuevos registros
                                    for rows in rows_afected:
                                        date_start = rows["date_start"]
                                        date_end = rows["date_end"]

                                        if date_start < info_date_start and date_end > info_date_end:

                                            new_ope_res_before = OpeResModel()
                                            new_ope_res_before.id_restriction_by = value_restriction_by
                                            new_ope_res_before.id_restriction_type = restriction_type_value2
                                            new_ope_res_before.id_room_type = id_room_type
                                            new_ope_res_before.id_property = id_property
                                            new_ope_res_before.id_rateplan = 0
                                            new_ope_res_before.value = rows["value"]
                                            new_ope_res_before.is_override = 0
                                            new_ope_res_before.date_start = date_start
                                            new_ope_res_before.date_end = date_end_before
                                            new_ope_res_before.estado = 1
                                            new_ope_res_before.usuario_creacion = user_name
                                            db.session.add(new_ope_res_before)

                                            new_ope_res_after = OpeResModel()
                                            new_ope_res_after.id_restriction_by = value_restriction_by
                                            new_ope_res_after.id_restriction_type = restriction_type_value2
                                            new_ope_res_after.id_room_type = id_room_type
                                            new_ope_res_after.id_property = id_property
                                            new_ope_res_after.id_rateplan = 0
                                            new_ope_res_after.value = rows["value"]
                                            new_ope_res_after.is_override = 0
                                            new_ope_res_after.date_start = date_start_after
                                            new_ope_res_after.date_end = date_end
                                            new_ope_res_after.estado = 1
                                            new_ope_res_after.usuario_creacion = user_name
                                            db.session.add(new_ope_res_after)

                                        elif date_end > info_date_end and date_start >= info_date_start:

                                            new_ope_res = OpeResModel()
                                            new_ope_res.id_restriction_by = value_restriction_by
                                            new_ope_res.id_restriction_type = restriction_type_value2
                                            new_ope_res.id_room_type = id_room_type
                                            new_ope_res.id_property = id_property
                                            new_ope_res.id_rateplan = 0
                                            new_ope_res.value = rows["value"]
                                            new_ope_res.is_override = 0
                                            new_ope_res.date_start = date_start_after
                                            new_ope_res.date_end = date_end
                                            new_ope_res.estado = 1
                                            new_ope_res.usuario_creacion = user_name
                                            db.session.add(new_ope_res)

                                        elif date_start < info_date_start and date_end <= info_date_end:
                                            #Creamos un registro para las fechas anteriores
                                            new_ope_res = OpeResModel()
                                            new_ope_res.id_restriction_by = value_restriction_by
                                            new_ope_res.id_restriction_type = restriction_type_value2
                                            new_ope_res.id_room_type = id_room_type
                                            new_ope_res.id_property = id_property
                                            new_ope_res.id_rateplan = 0
                                            new_ope_res.value = rows["value"]
                                            new_ope_res.is_override = 0
                                            new_ope_res.date_start = date_start
                                            new_ope_res.date_end = date_end_before
                                            new_ope_res.estado = 1
                                            new_ope_res.usuario_creacion = user_name
                                            db.session.add(new_ope_res)

                                if restriction_type_value2 == 2: #min_los
                                    info_value = info_restriction_detail["min_los"]
                                elif restriction_type_value2 == 3: #max_los
                                    info_value = info_restriction_detail["max_los"]
                                else:
                                    info_value = 0

                                if estado2 > 0:
                                    opeResDataAux = OpeResModel()

                                    opeResDataAux.id_restriction_by = value_restriction_by
                                    opeResDataAux.id_restriction_type = restriction_type_value2
                                    opeResDataAux.id_room_type = id_room_type
                                    opeResDataAux.id_property = id_property
                                    opeResDataAux.id_rateplan = 0
                                    opeResDataAux.value = info_value
                                    opeResDataAux.is_override = 0
                                    opeResDataAux.date_start = info_date_start
                                    opeResDataAux.date_end = info_date_end
                                    opeResDataAux.estado = estado2
                                    opeResDataAux.usuario_creacion = user_name
    
                                    db.session.add(opeResDataAux)
                                    db.session.flush()
                                    confirm_save = True
    
                                    result += 1
                            elif value_restriction_by == 5 and restriction_type_value2 in (2,3):
                                for obj_room_restriction in list_rooms_update:
                                    cont = 0
                                    rows_afected = []
                                    while cont < len(obj_room_restriction["list_opera_restrictions"]):

                                        row = {
                                            "date_start": dt.strptime(obj_room_restriction["list_opera_restrictions"][cont].date_start.strftime("%Y-%m-%d"), '%Y-%m-%d'),
                                            "date_end":dt.strptime(obj_room_restriction["list_opera_restrictions"][cont].date_end.strftime("%Y-%m-%d"), '%Y-%m-%d'),
                                            "value":obj_room_restriction["list_opera_restrictions"][cont].value,
                                            "position":cont
                                        }

                                        rows_afected.append(row)

                                        obj_room_restriction["list_opera_restrictions"][cont].estado = 0
                                        obj_room_restriction["list_opera_restrictions"][cont].usuario_ultima_modificacion = user_name
                                        db.session.flush()
                                        confirm_save = True
                                        cont += 1


                                    date_end_before = info_date_start - datetime.timedelta(days=1)
                                    date_start_after = info_date_end + datetime.timedelta(days=1)

                                    # Se dividen las fechas cuando chocan con una inserción (se mantienen activas)
                                    if len(rows_afected) > 0:
                                        #Creamos nuevos registros
                                        for rows in rows_afected:
                                            date_start = rows["date_start"]
                                            date_end = rows["date_end"]

                                            if date_start < info_date_start and date_end > info_date_end:

                                                new_ope_res_before = OpeResModel()
                                                new_ope_res_before.id_restriction_by = 3
                                                new_ope_res_before.id_restriction_type = restriction_type_value2
                                                new_ope_res_before.id_room_type = obj_room_restriction["id_room_type"]
                                                new_ope_res_before.id_property = id_property
                                                new_ope_res_before.id_rateplan = 0
                                                new_ope_res_before.value = rows["value"]
                                                new_ope_res_before.is_override = 0
                                                new_ope_res_before.date_start = date_start
                                                new_ope_res_before.date_end = date_end_before
                                                new_ope_res_before.estado = 1
                                                new_ope_res_before.usuario_creacion = user_name
                                                db.session.add(new_ope_res_before)

                                                new_ope_res_after = OpeResModel()
                                                new_ope_res_after.id_restriction_by = 3
                                                new_ope_res_after.id_restriction_type = restriction_type_value2
                                                new_ope_res_after.id_room_type = obj_room_restriction["id_room_type"]
                                                new_ope_res_after.id_property = id_property
                                                new_ope_res_after.id_rateplan = 0
                                                new_ope_res_after.value = rows["value"]
                                                new_ope_res_after.is_override = 0
                                                new_ope_res_after.date_start = date_start_after
                                                new_ope_res_after.date_end = date_end
                                                new_ope_res_after.estado = 1
                                                new_ope_res_after.usuario_creacion = user_name
                                                db.session.add(new_ope_res_after)

                                            elif date_end > info_date_end and date_start >= info_date_start:

                                                new_ope_res = OpeResModel()
                                                new_ope_res.id_restriction_by = 3
                                                new_ope_res.id_restriction_type = restriction_type_value2
                                                new_ope_res.id_room_type = obj_room_restriction["id_room_type"]
                                                new_ope_res.id_property = id_property
                                                new_ope_res.id_rateplan = 0
                                                new_ope_res.value = rows["value"]
                                                new_ope_res.is_override = 0
                                                new_ope_res.date_start = date_start_after
                                                new_ope_res.date_end = date_end
                                                new_ope_res.estado = 1
                                                new_ope_res.usuario_creacion = user_name
                                                db.session.add(new_ope_res)

                                            elif date_start < info_date_start and date_end <= info_date_end:
                                                #Creamos un registro para las fechas anteriores
                                                new_ope_res = OpeResModel()
                                                new_ope_res.id_restriction_by = 3
                                                new_ope_res.id_restriction_type = restriction_type_value2
                                                new_ope_res.id_room_type = obj_room_restriction["id_room_type"]
                                                new_ope_res.id_property = id_property
                                                new_ope_res.id_rateplan = 0
                                                new_ope_res.value = rows["value"]
                                                new_ope_res.is_override = 0
                                                new_ope_res.date_start = date_start
                                                new_ope_res.date_end = date_end_before
                                                new_ope_res.estado = 1
                                                new_ope_res.usuario_creacion = user_name
                                                db.session.add(new_ope_res)

                                    if restriction_type_value2 == 2: #min_los
                                        info_value = info_restriction_detail["min_los"]
                                    elif restriction_type_value2 == 3: #max_los
                                        info_value = info_restriction_detail["max_los"]
                                    else:
                                        info_value = 0

                                    if estado2 > 0:
                                        opeResDataAux = OpeResModel()

                                        opeResDataAux.id_restriction_by = 3
                                        opeResDataAux.id_restriction_type = restriction_type_value2
                                        opeResDataAux.id_room_type = obj_room_restriction["id_room_type"]
                                        opeResDataAux.id_property = id_property
                                        opeResDataAux.id_rateplan = 0
                                        opeResDataAux.value = info_value
                                        opeResDataAux.is_override = 0
                                        opeResDataAux.date_start = info_date_start
                                        opeResDataAux.date_end = info_date_end
                                        opeResDataAux.estado = estado2
                                        opeResDataAux.usuario_creacion = user_name

                                        db.session.add(opeResDataAux)
                                        db.session.flush()
                                        confirm_save = True

                                        result += 1

                        #Proceso de max_los
                        if use_max and restriction_type_value3 > 0:
                            if value_restriction_by == 3:
                                list_opera_restrictions = OpeResModel.query.filter(
                                    and_(
                                        or_(
                                            and_(OpeResModel.date_start <= info_restriction_detail["date_start"], 
                                                OpeResModel.date_end >= info_restriction_detail["date_end"]),
                                            and_(OpeResModel.date_start >= info_restriction_detail["date_start"], 
                                                OpeResModel.date_end <= info_restriction_detail["date_end"]),
                                            and_(OpeResModel.date_start > info_restriction_detail["date_start"], 
                                                OpeResModel.date_end > info_restriction_detail["date_end"],
                                                OpeResModel.date_start <= info_restriction_detail["date_end"],
                                                OpeResModel.date_end >= info_restriction_detail["date_start"]),
                                            and_(OpeResModel.date_start <= info_restriction_detail["date_start"], 
                                                OpeResModel.date_end < info_restriction_detail["date_end"],
                                                OpeResModel.date_start < info_restriction_detail["date_end"],
                                                OpeResModel.date_end >= info_restriction_detail["date_start"])
                                        )
                                    ),
                                    OpeResModel.id_restriction_by.in_([3,4]), 
                                    OpeResModel.id_restriction_type==restriction_type_value3, OpeResModel.id_room_type==id_room_type, 
                                    OpeResModel.id_property==id_property, 
                                    OpeResModel.estado==1).all()
                                # if len(list_opera_restrictions) == 0:
                                #     list_opera_restrictions = OpeResModel.query.filter(
                                #         and_(
                                #             or_(
                                #                 and_(OpeResModel.date_start > info_restriction_detail["date_start"], 
                                #                     OpeResModel.date_end > info_restriction_detail["date_end"],
                                #                     OpeResModel.date_start <= info_restriction_detail["date_end"],
                                #                     OpeResModel.date_end >= info_restriction_detail["date_start"]),
                                #                 and_(OpeResModel.date_start <= info_restriction_detail["date_start"], 
                                #                     OpeResModel.date_end < info_restriction_detail["date_end"],
                                #                     OpeResModel.date_start < info_restriction_detail["date_end"],
                                #                     OpeResModel.date_end >= info_restriction_detail["date_start"])
                                #             )
                                #         ),
                                #         OpeResModel.id_restriction_by.in_([3,4]), 
                                #         OpeResModel.id_restriction_type==restriction_type_value3, OpeResModel.id_room_type==id_room_type, 
                                #         OpeResModel.id_property==id_property, 
                                #         OpeResModel.estado==1).all()
                            elif value_restriction_by == 5:
                                id_room_type = 0
                                list_rooms = rtcModel.query.filter(rtcModel.iddef_property==id_property, rtcModel.estado==1).all()
                                list_id_rooms = [obj_rtc.iddef_room_type_category for obj_rtc in list_rooms]
                                list_rooms_update = [] # Se guardarán los id_rooms y la información de las restricciones relacionadas
                                for id_room_type_elem in list_id_rooms:
                                    list_opera_restrictions_temp = OpeResModel.query.filter(
                                        and_(
                                            or_(
                                                and_(OpeResModel.date_start <= info_restriction_detail["date_start"], 
                                                    OpeResModel.date_end >= info_restriction_detail["date_end"]),
                                                and_(OpeResModel.date_start >= info_restriction_detail["date_start"], 
                                                    OpeResModel.date_end <= info_restriction_detail["date_end"]),
                                                and_(OpeResModel.date_start > info_restriction_detail["date_start"], 
                                                    OpeResModel.date_end > info_restriction_detail["date_end"],
                                                    OpeResModel.date_start <= info_restriction_detail["date_end"],
                                                    OpeResModel.date_end >= info_restriction_detail["date_start"]),
                                                and_(OpeResModel.date_start <= info_restriction_detail["date_start"], 
                                                    OpeResModel.date_end < info_restriction_detail["date_end"],
                                                    OpeResModel.date_start < info_restriction_detail["date_end"],
                                                    OpeResModel.date_end >= info_restriction_detail["date_start"])
                                            )
                                        ),
                                        OpeResModel.id_restriction_by.in_([3,4]), 
                                        OpeResModel.id_restriction_type==restriction_type_value3, OpeResModel.id_room_type==id_room_type_elem, 
                                        OpeResModel.id_property==id_property, 
                                        OpeResModel.estado==1).all()
                                    list_rooms_update.append({"id_room_type":id_room_type_elem,"list_opera_restrictions":list_opera_restrictions_temp})
                                    # if len(list_opera_restrictions_temp) == 0:
                                    #     list_opera_restrictions_temp = OpeResModel.query.filter(
                                    #         and_(
                                    #             or_(
                                    #                 and_(OpeResModel.date_start > info_restriction_detail["date_start"], 
                                    #                     OpeResModel.date_end > info_restriction_detail["date_end"],
                                    #                     OpeResModel.date_start <= info_restriction_detail["date_end"],
                                    #                     OpeResModel.date_end >= info_restriction_detail["date_start"]),
                                    #                 and_(OpeResModel.date_start <= info_restriction_detail["date_start"], 
                                    #                     OpeResModel.date_end < info_restriction_detail["date_end"],
                                    #                     OpeResModel.date_start < info_restriction_detail["date_end"],
                                    #                     OpeResModel.date_end >= info_restriction_detail["date_start"])
                                    #             )
                                    #         ),
                                    #         OpeResModel.id_restriction_by.in_([3,4]), 
                                    #         OpeResModel.id_restriction_type==restriction_type_value3, OpeResModel.id_room_type==id_room_type_elem, 
                                    #         OpeResModel.id_property==id_property, 
                                    #         OpeResModel.estado==1).all()
                                    #     list_rooms_update.append({"id_room_type":id_room_type_elem,"list_opera_restrictions":list_opera_restrictions_temp})
                                    # else:
                                    #     list_rooms_update.append({"id_room_type":id_room_type_elem,"list_opera_restrictions":list_opera_restrictions_temp})
                            else:
                                raise Exception("Restriction_by {0:s} is not valid for Opera information".format(value_restriction_by))

                            if value_restriction_by != 5:
                                cont = 0
                                rows_afected = []
                                while cont < len(list_opera_restrictions):

                                    row = {
                                        "date_start": dt.strptime(list_opera_restrictions[cont].date_start.strftime("%Y-%m-%d"), '%Y-%m-%d'),
                                        "date_end":dt.strptime(list_opera_restrictions[cont].date_end.strftime("%Y-%m-%d"), '%Y-%m-%d'),
                                        "value":list_opera_restrictions[cont].value,
                                        "position":cont
                                    }

                                    rows_afected.append(row)

                                    list_opera_restrictions[cont].estado = 0
                                    list_opera_restrictions[cont].usuario_ultima_modificacion = user_name
                                    db.session.flush()
                                    confirm_save = True
                                    cont += 1


                                date_end_before = info_date_start - datetime.timedelta(days=1)
                                date_start_after = info_date_end + datetime.timedelta(days=1)

                                # Se dividen las fechas cuando chocan con una inserción (se mantienen activas)
                                if len(rows_afected) > 0:
                                    #Creamos nuevos registros
                                    for rows in rows_afected:
                                        date_start = rows["date_start"]
                                        date_end = rows["date_end"]

                                        if date_start < info_date_start and date_end > info_date_end:

                                            new_ope_res_before = OpeResModel()
                                            new_ope_res_before.id_restriction_by = value_restriction_by
                                            new_ope_res_before.id_restriction_type = restriction_type_value3
                                            new_ope_res_before.id_room_type = id_room_type
                                            new_ope_res_before.id_property = id_property
                                            new_ope_res_before.id_rateplan = 0
                                            new_ope_res_before.value = rows["value"]
                                            new_ope_res_before.is_override = 0
                                            new_ope_res_before.date_start = date_start
                                            new_ope_res_before.date_end = date_end_before
                                            new_ope_res_before.estado = 1
                                            new_ope_res_before.usuario_creacion = user_name
                                            db.session.add(new_ope_res_before)

                                            new_ope_res_after = OpeResModel()
                                            new_ope_res_after.id_restriction_by = value_restriction_by
                                            new_ope_res_after.id_restriction_type = restriction_type_value3
                                            new_ope_res_after.id_room_type = id_room_type
                                            new_ope_res_after.id_property = id_property
                                            new_ope_res_after.id_rateplan = 0
                                            new_ope_res_after.value = rows["value"]
                                            new_ope_res_after.is_override = 0
                                            new_ope_res_after.date_start = date_start_after
                                            new_ope_res_after.date_end = date_end
                                            new_ope_res_after.estado = 1
                                            new_ope_res_after.usuario_creacion = user_name
                                            db.session.add(new_ope_res_after)

                                        elif date_end > info_date_end and date_start >= info_date_start:

                                            new_ope_res = OpeResModel()
                                            new_ope_res.id_restriction_by = value_restriction_by
                                            new_ope_res.id_restriction_type = restriction_type_value3
                                            new_ope_res.id_room_type = id_room_type
                                            new_ope_res.id_property = id_property
                                            new_ope_res.id_rateplan = 0
                                            new_ope_res.value = rows["value"]
                                            new_ope_res.is_override = 0
                                            new_ope_res.date_start = date_start_after
                                            new_ope_res.date_end = date_end
                                            new_ope_res.estado = 1
                                            new_ope_res.usuario_creacion = user_name
                                            db.session.add(new_ope_res)

                                        elif date_start < info_date_start and date_end <= info_date_end:
                                            #Creamos un registro para las fechas anteriores
                                            new_ope_res = OpeResModel()
                                            new_ope_res.id_restriction_by = value_restriction_by
                                            new_ope_res.id_restriction_type = restriction_type_value3
                                            new_ope_res.id_room_type = id_room_type
                                            new_ope_res.id_property = id_property
                                            new_ope_res.id_rateplan = 0
                                            new_ope_res.value = rows["value"]
                                            new_ope_res.is_override = 0
                                            new_ope_res.date_start = date_start
                                            new_ope_res.date_end = date_end_before
                                            new_ope_res.estado = 1
                                            new_ope_res.usuario_creacion = user_name
                                            db.session.add(new_ope_res)

                                if restriction_type_value3 == 2: #min_los
                                    info_value = info_restriction_detail["min_los"]
                                elif restriction_type_value3 == 3: #max_los
                                    info_value = info_restriction_detail["max_los"]
                                else:
                                    info_value = 0

                                if estado3 > 0:
                                    opeResDataAux = OpeResModel()

                                    opeResDataAux.id_restriction_by = value_restriction_by
                                    opeResDataAux.id_restriction_type = restriction_type_value3
                                    opeResDataAux.id_room_type = id_room_type
                                    opeResDataAux.id_property = id_property
                                    opeResDataAux.id_rateplan = 0
                                    opeResDataAux.value = info_value
                                    opeResDataAux.is_override = 0
                                    opeResDataAux.date_start = info_date_start
                                    opeResDataAux.date_end = info_date_end
                                    opeResDataAux.estado = estado3
                                    opeResDataAux.usuario_creacion = user_name

                                    db.session.add(opeResDataAux)
                                    db.session.flush()
                                    confirm_save = True

                                    result += 1
                            elif value_restriction_by == 5 and restriction_type_value3 in (2,3):
                                for obj_room_restriction in list_rooms_update:
                                    cont = 0
                                    rows_afected = []
                                    while cont < len(obj_room_restriction["list_opera_restrictions"]):

                                        row = {
                                            "date_start": dt.strptime(obj_room_restriction["list_opera_restrictions"][cont].date_start.strftime("%Y-%m-%d"), '%Y-%m-%d'),
                                            "date_end":dt.strptime(obj_room_restriction["list_opera_restrictions"][cont].date_end.strftime("%Y-%m-%d"), '%Y-%m-%d'),
                                            "value":obj_room_restriction["list_opera_restrictions"][cont].value,
                                            "position":cont
                                        }

                                        rows_afected.append(row)

                                        obj_room_restriction["list_opera_restrictions"][cont].estado = 0
                                        obj_room_restriction["list_opera_restrictions"][cont].usuario_ultima_modificacion = user_name
                                        db.session.flush()
                                        confirm_save = True
                                        cont += 1


                                    date_end_before = info_date_start - datetime.timedelta(days=1)
                                    date_start_after = info_date_end + datetime.timedelta(days=1)

                                    # Se dividen las fechas cuando chocan con una inserción (se mantienen activas)
                                    if len(rows_afected) > 0:
                                        #Creamos nuevos registros
                                        for rows in rows_afected:
                                            date_start = rows["date_start"]
                                            date_end = rows["date_end"]

                                            if date_start < info_date_start and date_end > info_date_end:

                                                new_ope_res_before = OpeResModel()
                                                new_ope_res_before.id_restriction_by = 3
                                                new_ope_res_before.id_restriction_type = restriction_type_value3
                                                new_ope_res_before.id_room_type = obj_room_restriction["id_room_type"]
                                                new_ope_res_before.id_property = id_property
                                                new_ope_res_before.id_rateplan = 0
                                                new_ope_res_before.value = rows["value"]
                                                new_ope_res_before.is_override = 0
                                                new_ope_res_before.date_start = date_start
                                                new_ope_res_before.date_end = date_end_before
                                                new_ope_res_before.estado = 1
                                                new_ope_res_before.usuario_creacion = user_name
                                                db.session.add(new_ope_res_before)

                                                new_ope_res_after = OpeResModel()
                                                new_ope_res_after.id_restriction_by = 3
                                                new_ope_res_after.id_restriction_type = restriction_type_value3
                                                new_ope_res_after.id_room_type = obj_room_restriction["id_room_type"]
                                                new_ope_res_after.id_property = id_property
                                                new_ope_res_after.id_rateplan = 0
                                                new_ope_res_after.value = rows["value"]
                                                new_ope_res_after.is_override = 0
                                                new_ope_res_after.date_start = date_start_after
                                                new_ope_res_after.date_end = date_end
                                                new_ope_res_after.estado = 1
                                                new_ope_res_after.usuario_creacion = user_name
                                                db.session.add(new_ope_res_after)

                                            elif date_end > info_date_end and date_start >= info_date_start:

                                                new_ope_res = OpeResModel()
                                                new_ope_res.id_restriction_by = 3
                                                new_ope_res.id_restriction_type = restriction_type_value3
                                                new_ope_res.id_room_type = obj_room_restriction["id_room_type"]
                                                new_ope_res.id_property = id_property
                                                new_ope_res.id_rateplan = 0
                                                new_ope_res.value = rows["value"]
                                                new_ope_res.is_override = 0
                                                new_ope_res.date_start = date_start_after
                                                new_ope_res.date_end = date_end
                                                new_ope_res.estado = 1
                                                new_ope_res.usuario_creacion = user_name
                                                db.session.add(new_ope_res)

                                            elif date_start < info_date_start and date_end <= info_date_end:
                                                #Creamos un registro para las fechas anteriores
                                                new_ope_res = OpeResModel()
                                                new_ope_res.id_restriction_by = 3
                                                new_ope_res.id_restriction_type = restriction_type_value3
                                                new_ope_res.id_room_type = obj_room_restriction["id_room_type"]
                                                new_ope_res.id_property = id_property
                                                new_ope_res.id_rateplan = 0
                                                new_ope_res.value = rows["value"]
                                                new_ope_res.is_override = 0
                                                new_ope_res.date_start = date_start
                                                new_ope_res.date_end = date_end_before
                                                new_ope_res.estado = 1
                                                new_ope_res.usuario_creacion = user_name
                                                db.session.add(new_ope_res)

                                    if restriction_type_value3 == 2: #min_los
                                        info_value = info_restriction_detail["min_los"]
                                    elif restriction_type_value3 == 3: #max_los
                                        info_value = info_restriction_detail["max_los"]
                                    else:
                                        info_value = 0

                                    if estado3 > 0:
                                        opeResDataAux = OpeResModel()

                                        opeResDataAux.id_restriction_by = 3
                                        opeResDataAux.id_restriction_type = restriction_type_value3
                                        opeResDataAux.id_room_type = obj_room_restriction["id_room_type"]
                                        opeResDataAux.id_property = id_property
                                        opeResDataAux.id_rateplan = 0
                                        opeResDataAux.value = info_value
                                        opeResDataAux.is_override = 0
                                        opeResDataAux.date_start = info_date_start
                                        opeResDataAux.date_end = info_date_end
                                        opeResDataAux.estado = estado3
                                        opeResDataAux.usuario_creacion = user_name

                                        db.session.add(opeResDataAux)
                                        db.session.flush()
                                        confirm_save = True

                                        result += 1

            else:
                raise Exception("Restriction without dates")

            if confirm_save:
                db.session.commit()
        except Exception as ex:
            db.session.rollback()
            raise ex

        return result

    # Metodo para guardar cada restricción (Deprecated)
    # Retornará el numero de elementos (detalles) insertados, los elementos que fueron reactivados (cambiando estado a 1) no se contabilizarán
    # Nota: si regresa 0 la informacón de la tabla "restriction" no se insertará
    @staticmethod
    def insert_opera_restrictions(info_restriction,restriction_type,user_name="Opera"):
        try:
            result = 0
            confirm_save = False
            restriction_type_value = 0

            if len(info_restriction["restrictions"]) > 0:
                model_property = proModel.query.filter(proModel.property_code==info_restriction["property"],proModel.estado==1).first()
                if model_property is None:
                    raise Exception("Property not found")
                else:
                    for info_restriction_detail in info_restriction["restrictions"]:
                        estado = 1

                        if info_restriction_detail["close"] == True:
                            restriction_type_value = 1
                        elif info_restriction_detail["close"] == False and info_restriction_detail["min_los"] > 0 and info_restriction_detail["max_los"] == 0:
                            restriction_type_value = 2
                        elif info_restriction_detail["close"] == False and info_restriction_detail["min_los"] == 0 and info_restriction_detail["max_los"] > 0:
                            restriction_type_value = 3
                        elif info_restriction_detail["close"] == False and info_restriction_detail["min_los"] == 0 and info_restriction_detail["max_los"] == 0:
                            restriction_type_value = 1
                            estado = 0
                        else:
                            raise Exception("Type needs to be close_date, min_los or max_los")

                        model = RestricctionFunction.get_create_opera_restriction(restriction_type=restriction_type, 
                        restriction_type_value=restriction_type_value, user_name=user_name)

                        if model is None:
                            raise Exception("Model is None")
                        elif not isinstance(model, ResModel):
                            raise Exception("Object is not valid")

                        info_value = {}
                        list_data = None
                        if model.iddef_restriction_by == 3:
                            info_value = {"room": info_restriction["room"], "hotel_id": model_property.iddef_property, "rate_plan_id": []}
                            list_data = ResDetModel.query\
                            .join(ResModel, ResDetModel.iddef_restriction==ResModel.iddef_restriction)\
                            .filter(
                                ResDetModel.iddef_restriction==model.iddef_restriction,
                                func.json_extract(ResDetModel.value, "$.room")==info_restriction["room"],
                                func.json_extract(ResDetModel.value, "$.hotel_id")==model_property.iddef_property,
                                func.json_extract(ResDetModel.value, "$.rate_plan_id").like("[]"),
                                ResModel.iddef_restriction_by==restriction_type,
                                ResModel.iddef_restriction_type==restriction_type_value
                            ).all()
                        elif model.iddef_restriction_by == 5:
                            info_value = {"room": "", "hotel_id": model_property.iddef_property, "rate_plan_id": []}
                            list_data = ResDetModel.query\
                            .join(ResModel, ResDetModel.iddef_restriction==ResModel.iddef_restriction)\
                            .filter(
                                ResDetModel.iddef_restriction==model.iddef_restriction,
                                func.json_extract(ResDetModel.value, "$.room")=="",
                                func.json_extract(ResDetModel.value, "$.hotel_id")==model_property.iddef_property,
                                func.json_extract(ResDetModel.value, "$.rate_plan_id").like("[]"),
                                ResModel.iddef_restriction_by==restriction_type,
                                ResModel.iddef_restriction_type==restriction_type_value
                            ).all()

                        if list_data is None:
                            raise Exception("Restriction_by is not valid for Opera information")

                        if len(list_data) == 0:
                            model_detail = ResDetModel()
                            model_detail.iddef_restriction = model.iddef_restriction
                            model_detail.channel_option = 0
                            model_detail.specific_channels = []
                            model_detail.travel_window_option = 1
                            model_detail.travel_window = [{"start_date": info_restriction_detail["date_start"], "end_date": info_restriction_detail["date_end"]}]
                            model_detail.booking_window_option = 0
                            model_detail.booking_window_dates = []
                            model_detail.booking_window_times = []
                            model_detail.bookable_weekdays_option = 0
                            model_detail.bookable_weekdays = []
                            model_detail.market_option = 0
                            model_detail.market_targeting = []
                            model_detail.geo_targeting_option = 0
                            model_detail.geo_targeting_countries = []
                            model_detail.device_type_option = 0
                            model_detail.restriction_default = 0
                            model_detail.min_los = info_restriction_detail["min_los"]
                            model_detail.max_los = info_restriction_detail["max_los"]

                            model_detail.value = info_value
                            model_detail.estado = estado
                            model_detail.usuario_creacion = user_name
                            db.session.add(model_detail)
                            db.session.flush()
                            confirm_save = True
                            result += 1
                        else:
                            for data in list_data:
                                operation = ""
                                new_travel_window = []
                                for idx, travel_window_elem in enumerate(data.travel_window):
                                    travel_window_start = dt.strptime(travel_window_elem["date_start"], '%Y-%m-%d')
                                    travel_window_end = dt.strptime(travel_window_elem["date_end"], '%Y-%m-%d')
                                    info_tr_win_start = dt.strptime(info_restriction_detail["date_start"], '%Y-%m-%d')
                                    info_tr_win_end = dt.strptime(info_restriction_detail["date_end"], '%Y-%m-%d')


                                    if travel_window_elem["date_start"] == info_restriction_detail["date_start"] and travel_window_elem["date_end"] == info_restriction_detail["date_end"]:
                                        operation = "update"
                                        new_travel_window.append({"date_start": info_restriction_detail["date_start"], "date_end": info_restriction_detail["date_end"]})
                                    elif travel_window_start <= info_tr_win_start and travel_window_start < info_tr_win_end and\
                                    travel_window_end >= info_tr_win_start and travel_window_end < info_tr_win_end and\
                                    data.min_los == info_restriction_detail["min_los"] and data.max_los == info_restriction_detail["max_los"]:
                                        operation = "update"



                                if operation == "update":
                                    data.travel_window_option = 1
                                    data.travel_window = [{"date_start": info_restriction_detail["date_start"], "date_end": info_restriction_detail["date_end"]}]
                                    data.min_los = info_restriction_detail["min_los"]
                                    data.max_los = info_restriction_detail["max_los"]
                                    data.estado = 1
                                    db.session.flush()
                                    confirm_save = True
            else:
                raise Exception("Restriction without dates")

            if confirm_save:
                db.session.commit()
        
        except Exception as ex:
            db.session.rollback()
            raise ex

        return result

    #Función para obtener las restricciones de Opera (op_opera_restrictions) por filtros
    @staticmethod
    def getOperaRestrictions(id_restriction_by=None, id_restriction_type=None, id_room_type=None, id_property=None, id_rateplan=None, value=None, 
        is_override=None, date_start=None, date_end=None, estado=1, is_order=False):
        try:
            #schema = OpeResSchema(exclude=Util.get_default_excludes(), many=True)
            conditions = []
            result = None

            if id_restriction_by is not None:
                conditions.append(OpeResModel.id_restriction_by == id_restriction_by)
                #1 - Market, 2 - RatePlan, 3 - Room, 4 - RatePlan/Room, 5 - Property, 6 - General_Restriction, 7 - Promotions

            if id_restriction_type is not None and isinstance(id_restriction_type, list) and len(id_restriction_type) > 0:
                conditions.append(OpeResModel.id_restriction_type.in_(id_restriction_type))
                #1 - close_date, 2 - min_los, 3 - max_los, 4 - apply

            if id_room_type is not None:
                conditions.append(OpeResModel.id_room_type == id_room_type)

            if id_property is not None:
                conditions.append(OpeResModel.id_property == id_property)

            if id_rateplan is not None:
                conditions.append(OpeResModel.id_rateplan == id_rateplan)

            if value is not None:
                conditions.append(OpeResModel.value == value)

            if is_override is not None:
                conditions.append(OpeResModel.is_override == is_override)

            if date_start is not None and date_end is not None:
                #conditions.append(or_(OpeResModel.date_start.between(date_start, date_end), OpeResModel.date_end.between(date_start, date_end)))
                conditions.append(or_(
                        and_(OpeResModel.date_start <= date_start, 
                            OpeResModel.date_end >= date_end),
                        and_(OpeResModel.date_start >= date_start, 
                            OpeResModel.date_end <= date_end),
                        and_(OpeResModel.date_start > date_start, 
                            OpeResModel.date_end > date_end,
                            OpeResModel.date_start <= date_end,
                            OpeResModel.date_end >= date_start),
                        and_(OpeResModel.date_start <= date_start, 
                            OpeResModel.date_end < date_end,
                            OpeResModel.date_start < date_end,
                            OpeResModel.date_end >= date_start)
                    ))


            conditions.append(OpeResModel.estado==estado)
            if is_order is False:
                result = OpeResModel.query.filter(*conditions).all()
            else:
                result = OpeResModel.query.filter(*conditions).order_by(OpeResModel.date_start.asc()).all()
            #result = schema.dump(result)
        except Exception as ex:
            raise ex
        return result
    
    @staticmethod
    def getRestrictionbyRoom(id_type, hotel, room, start_date, end_date):

        query = "SELECT * FROM def_restriction INNER JOIN def_restriction_detail ON def_restriction.iddef_restriction = def_restriction_detail.iddef_restriction"
        query_where = " WHERE def_restriction.iddef_restriction_by = 3 AND def_restriction.iddef_restriction_type = :id_type AND def_restriction.estado = 1 AND JSON_EXTRACT(def_restriction_detail.value,'$.hotel_id') = :hotel AND JSON_EXTRACT(def_restriction_detail.value,'$.room') = :room AND JSON_EXTRACT(def_restriction_detail.value,'$.rate_plan_id') LIKE '[]'"
        query_join = ""
        query_date = ""
        params = {}
        params["id_type"] = int(id_type)
        params["hotel"] = int(hotel)
        params["room"] = str(room)
        max_json_length = dict(db.session.execute(str('SELECT MAX(max_data) AS max_data FROM (SELECT MAX(JSON_LENGTH(travel_window)) AS max_data FROM def_restriction_detail) AS max_lengths;'), {}).fetchone())["max_data"]

        if(max_json_length > 0):
            query_join += " CROSS JOIN(SELECT 0 idx"
            for x in range(1,max_json_length):
                query_join += " UNION ALL SELECT " + str(x)
            query_join += ") AS n"

        if max_json_length > 0:
            query_date = " AND (JSON_EXTRACT(def_restriction_detail.travel_window, CONCAT('$[', n.idx, '].start_date')) <= :start_date AND JSON_EXTRACT(def_restriction_detail.travel_window, CONCAT('$[', n.idx, '].end_date')) >= :end_date)"
            query = query + " "+ query_join + query_where + query_date
            params["start_date"] = str(start_date)
            params["end_date"] = str(end_date)
        else:
            query = query + " "+ query_join + " " + query_where + " AND def_restriction_detail.travel_window LIKE '[]'"

        data = db.session.execute(query, params).first()

        return data

    @staticmethod
    def createOPeraRestrictionsbyRoom(id_restriction_type,id_property,id_rateplan,id_room,value,date_start,date_end):
        try: 
            schema = OpeResSchema(exclude=Util.get_default_excludes())
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            data = None
            Data = OpeResModel()
            Data.id_restriction_by = 4
            Data.id_restriction_type = id_restriction_type
            Data.id_room_type = id_room
            Data.id_property = id_property
            Data.id_rateplan = id_rateplan
            Data.value = value
            Data.is_override = 1
            Data.date_start = date_start
            Data.date_end = date_end
            Data.estado = 1
            Data.usuario_creacion = user_name
            db.session.add(Data)
            db.session.commit()
            data = schema.dump(Data)

        except Exception as ex:
            if id_restriction_type == 1:
                ms = "Error create restriction closed dates "
            else:
                ms = "Error create restriction min_los or max_los "
            raise Exception(ms +str(ex))

        return data
    
    @staticmethod
    def updateOPeraRestrictionsbyRoom(model=None,value=None,estado=1,id_restriction_type=1):
        try: 
            schema = OpeResSchema(exclude=Util.get_default_excludes())
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            data = None
            if model is None:
                raise Exception("Model is None")
            if value is not None:
                model.value = value
            model.estado = estado
            model.usuario_ultima_modificacion = user_name
            db.session.commit()
            data = schema.dump(model)

        except Exception as ex:
            if id_restriction_type == 1:
                ms = "Error update restriction closed dates "
            else:
                ms = "Error update restriction min_los or max_los "
            raise Exception(ms +str(ex))

        return data

    @staticmethod
    def getCloseDatesOperaRestriction(date_start, date_end, property, room, rateplans, all_rateplans=False):
        result = []
        try:
            #Se valida existencia de property
            count_property = proModel.query.filter(proModel.iddef_property==property, proModel.estado==1).with_entities(func.count()).scalar()
            if count_property == 0:
                raise Exception("Property not valid")
            #Se valida existencia del room
            count_room = rtcModel.query.filter(rtcModel.iddef_room_type_category == room, rtcModel.iddef_property==property, rtcModel.estado == 1).with_entities(func.count()).scalar()
            if count_room == 0:
                raise Exception("Room not valid")
            if len(rateplans) > 0:
                if all_rateplans:
                    list_rateplans = RatePlanModel.query\
                    .join(RatePlanRooms, RatePlanModel.idop_rateplan == RatePlanRooms.id_rate_plan)\
                    .join(rtcModel, RatePlanRooms.id_room_type == rtcModel.iddef_room_type_category)\
                    .join(proModel, proModel.iddef_property == rtcModel.iddef_property)\
                    .filter(rtcModel.iddef_property == property, RatePlanModel.idop_rateplan.in_(rateplans), RatePlanRooms.id_room_type == room,
                        RatePlanRooms.estado==1, rtcModel.estado==1, proModel.estado==1)\
                    .all()
                else:
                    list_rateplans = RatePlanModel.query\
                    .join(RatePlanRooms, RatePlanModel.idop_rateplan == RatePlanRooms.id_rate_plan)\
                    .join(rtcModel, RatePlanRooms.id_room_type == rtcModel.iddef_room_type_category)\
                    .join(proModel, proModel.iddef_property == rtcModel.iddef_property)\
                    .filter(rtcModel.iddef_property == property, RatePlanModel.idop_rateplan.in_(rateplans), RatePlanRooms.id_room_type == room,
                        RatePlanModel.estado==1, RatePlanRooms.estado==1, rtcModel.estado==1, proModel.estado==1)\
                    .all()

                if len(list_rateplans) == 0:
                    raise Exception("Rateplans are not valid")
            else:
                if all_rateplans:
                    list_rateplans = RatePlanModel.query\
                    .join(RatePlanRooms, RatePlanModel.idop_rateplan == RatePlanRooms.id_rate_plan)\
                    .join(rtcModel, RatePlanRooms.id_room_type == rtcModel.iddef_room_type_category)\
                    .join(proModel, proModel.iddef_property == rtcModel.iddef_property)\
                    .filter(rtcModel.iddef_property == property, RatePlanRooms.id_room_type == room,
                        RatePlanRooms.estado==1, rtcModel.estado==1, proModel.estado==1)\
                    .all()
                else:
                    list_rateplans = RatePlanModel.query\
                    .join(RatePlanRooms, RatePlanModel.idop_rateplan == RatePlanRooms.id_rate_plan)\
                    .join(rtcModel, RatePlanRooms.id_room_type == rtcModel.iddef_room_type_category)\
                    .join(proModel, proModel.iddef_property == rtcModel.iddef_property)\
                    .filter(rtcModel.iddef_property == property, RatePlanRooms.id_room_type == room,
                        RatePlanModel.estado==1, RatePlanRooms.estado==1, rtcModel.estado==1, proModel.estado==1)\
                    .all()

                if len(list_rateplans) == 0:
                    raise Exception("Property without rateplans")

            list_opera_restrictions = OpeResModel.query.filter(OpeResModel.id_property==property,
                OpeResModel.id_restriction_by.in_([3,4,5]), OpeResModel.id_restriction_type==1,
                OpeResModel.estado==1, or_(
                    and_(OpeResModel.date_start <= date_start, 
                        OpeResModel.date_end >= date_end),
                    and_(OpeResModel.date_start >= date_start, 
                        OpeResModel.date_end <= date_end),
                    and_(OpeResModel.date_start > date_start, 
                        OpeResModel.date_end > date_end,
                        OpeResModel.date_start <= date_end,
                        OpeResModel.date_end >= date_start),
                    and_(OpeResModel.date_start <= date_start, 
                        OpeResModel.date_end < date_end,
                        OpeResModel.date_start < date_end,
                        OpeResModel.date_end >= date_start)
                )).all()

            list_opera_restrictions = sorted(sorted(list_opera_restrictions, key=lambda x: x.fecha_creacion, reverse=True), key=lambda x: x.fecha_ultima_modificacion, reverse=True)

            date_default = dt.strptime('1900-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
            list_dates = list(RestricctionFunction.daterange(date_start, date_end))

            for rateplan_elem in list_rateplans:
                temp_rp_elem = {}
                temp_rp_elem["id_rateplan"] = rateplan_elem.idop_rateplan
                temp_rp_elem["name"] = rateplan_elem.code
                temp_rp_elem["dates"] = []
                for elem_date in list_dates:
                    dict_date = {}
                    priority = {"res_by":0, "override":0, "estado":0, "fecha_mod":date_default}
                    for elem_restriction in list_opera_restrictions:
                        if elem_restriction.date_start <= elem_date and elem_date <= elem_restriction.date_end:
                            date_to_compare = elem_restriction.fecha_creacion if elem_restriction.fecha_ultima_modificacion == date_default else elem_restriction.fecha_ultima_modificacion
                            #RatePlan/Room
                            if elem_restriction.id_restriction_by == 4 and elem_restriction.id_room_type==int(room) and elem_restriction.id_rateplan==rateplan_elem.idop_rateplan and date_to_compare >= priority["fecha_mod"]:
                                if elem_restriction.is_override == 1 and elem_restriction.value == 0:
                                    priority = {"res_by":4, "override":1, "estado":1, "fecha_mod":date_to_compare}
                                elif elem_restriction.is_override == 1 and elem_restriction.value == 1:
                                    priority = {"res_by":4, "override":1, "estado":0, "fecha_mod":date_to_compare}
                                elif elem_restriction.is_override == 0 and priority["override"]==0:
                                    priority = {"res_by":4, "override":0, "estado":1, "fecha_mod":date_to_compare}
                            #Room
                            elif elem_restriction.id_restriction_by == 3 and elem_restriction.id_room_type==int(room) and date_to_compare >= priority["fecha_mod"]:
                                if elem_restriction.is_override == 1 and priority["res_by"] not in [4] and elem_restriction.value == 0:
                                    priority = {"res_by":3, "override":1, "estado":1, "fecha_mod":date_to_compare}
                                elif elem_restriction.is_override == 1 and priority["res_by"] not in [4] and elem_restriction.value == 1:
                                    priority = {"res_by":3, "override":1, "estado":0, "fecha_mod":date_to_compare}
                                elif elem_restriction.is_override == 0 and priority["res_by"] not in [4] and priority["override"]==0:
                                    priority = {"res_by":3, "override":0, "estado":1, "fecha_mod":date_to_compare}
                            #Property
                            elif elem_restriction.id_restriction_by == 5:
                                if elem_restriction.is_override == 1 and priority["res_by"] not in [4,3] and elem_restriction.value == 0 and date_to_compare >= priority["fecha_mod"]:
                                    priority = {"res_by":5, "override":1, "estado":1, "fecha_mod":date_to_compare}
                                elif elem_restriction.is_override == 1 and priority["res_by"] not in [4,3] and elem_restriction.value == 1:
                                    priority = {"res_by":5, "override":1, "estado":0, "fecha_mod":date_to_compare}
                                elif elem_restriction.is_override == 0 and priority["res_by"] not in [4,3] and priority["override"]==0:
                                    priority = {"res_by":5, "override":0, "estado":1, "fecha_mod":date_to_compare}

                    dict_date["efective_date"] = elem_date.strftime("%Y-%m-%d")
                    dict_date["close"] = False if priority["estado"] == 0 else True
                    temp_rp_elem["dates"].append(dict_date)
                result.append(temp_rp_elem)

        except Exception as e:
            raise e

        return result

    @staticmethod
    def getMinLosOperaRestriction(date_start, date_end, property, room, rateplans, all_rateplans=False):
        result = []
        try:
            #Se valida existencia de property
            count_property = proModel.query.filter(proModel.iddef_property==property, proModel.estado==1).with_entities(func.count()).scalar()
            if count_property == 0:
                raise Exception("Property not valid")
            #Se valida existencia del room
            count_room = rtcModel.query.filter(rtcModel.iddef_room_type_category == room, rtcModel.iddef_property==property, rtcModel.estado == 1).with_entities(func.count()).scalar()
            if count_room == 0:
                raise Exception("Room not valid")
            if len(rateplans) > 0:
                if all_rateplans:
                    list_rateplans = RatePlanModel.query\
                    .join(RatePlanRooms, RatePlanModel.idop_rateplan == RatePlanRooms.id_rate_plan)\
                    .join(rtcModel, RatePlanRooms.id_room_type == rtcModel.iddef_room_type_category)\
                    .join(proModel, proModel.iddef_property == rtcModel.iddef_property)\
                    .filter(rtcModel.iddef_property == property, RatePlanModel.idop_rateplan.in_(rateplans), RatePlanRooms.id_room_type == room,
                        RatePlanRooms.estado==1, rtcModel.estado==1, proModel.estado==1)\
                    .all()
                else:
                    list_rateplans = RatePlanModel.query\
                    .join(RatePlanRooms, RatePlanModel.idop_rateplan == RatePlanRooms.id_rate_plan)\
                    .join(rtcModel, RatePlanRooms.id_room_type == rtcModel.iddef_room_type_category)\
                    .join(proModel, proModel.iddef_property == rtcModel.iddef_property)\
                    .filter(rtcModel.iddef_property == property, RatePlanModel.idop_rateplan.in_(rateplans), RatePlanRooms.id_room_type == room,
                        RatePlanModel.estado==1, RatePlanRooms.estado==1, rtcModel.estado==1, proModel.estado==1)\
                    .all()

                if len(list_rateplans) == 0:
                    raise Exception("Rateplans are not valid")
            else:
                if all_rateplans:
                    list_rateplans = RatePlanModel.query\
                    .join(RatePlanRooms, RatePlanModel.idop_rateplan == RatePlanRooms.id_rate_plan)\
                    .join(rtcModel, RatePlanRooms.id_room_type == rtcModel.iddef_room_type_category)\
                    .join(proModel, proModel.iddef_property == rtcModel.iddef_property)\
                    .filter(rtcModel.iddef_property == property, RatePlanRooms.id_room_type == room,
                        RatePlanRooms.estado==1, rtcModel.estado==1, proModel.estado==1)\
                    .all()
                else:
                    list_rateplans = RatePlanModel.query\
                    .join(RatePlanRooms, RatePlanModel.idop_rateplan == RatePlanRooms.id_rate_plan)\
                    .join(rtcModel, RatePlanRooms.id_room_type == rtcModel.iddef_room_type_category)\
                    .join(proModel, proModel.iddef_property == rtcModel.iddef_property)\
                    .filter(rtcModel.iddef_property == property, RatePlanRooms.id_room_type == room,
                        RatePlanModel.estado==1, RatePlanRooms.estado==1, rtcModel.estado==1, proModel.estado==1)\
                    .all()

                if len(list_rateplans) == 0:
                    raise Exception("Property without rateplans")

            list_opera_restrictions = OpeResModel.query.filter(OpeResModel.id_property==property,
                OpeResModel.id_restriction_by.in_([3,4,5]), OpeResModel.id_restriction_type==2,
                OpeResModel.estado==1, or_(
                    and_(OpeResModel.date_start <= date_start, 
                        OpeResModel.date_end >= date_end),
                    and_(OpeResModel.date_start >= date_start, 
                        OpeResModel.date_end <= date_end),
                    and_(OpeResModel.date_start > date_start, 
                        OpeResModel.date_end > date_end,
                        OpeResModel.date_start <= date_end,
                        OpeResModel.date_end >= date_start),
                    and_(OpeResModel.date_start <= date_start, 
                        OpeResModel.date_end < date_end,
                        OpeResModel.date_start < date_end,
                        OpeResModel.date_end >= date_start)
                )).all()

            list_opera_restrictions = sorted(sorted(list_opera_restrictions, key=lambda x: x.fecha_creacion, reverse=True), key=lambda x: x.fecha_ultima_modificacion, reverse=True)

            date_default = dt.strptime('1900-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
            list_dates = list(RestricctionFunction.daterange(date_start, date_end))

            for rateplan_elem in list_rateplans:
                temp_rp_elem = {}
                temp_rp_elem["id_rateplan"] = rateplan_elem.idop_rateplan
                temp_rp_elem["name"] = rateplan_elem.code
                temp_rp_elem["dates"] = []
                for elem_date in list_dates:
                    dict_date = {}
                    priority = {"res_by":0, "override":0, "value":0, "fecha_mod":date_default}
                    for elem_restriction in list_opera_restrictions:
                        if elem_restriction.date_start <= elem_date and elem_date <= elem_restriction.date_end:
                            date_to_compare = elem_restriction.fecha_creacion if elem_restriction.fecha_ultima_modificacion == date_default else elem_restriction.fecha_ultima_modificacion
                            #RatePlan/Room
                            if elem_restriction.id_restriction_by == 4 and elem_restriction.id_room_type==int(room) and elem_restriction.id_rateplan==rateplan_elem.idop_rateplan and date_to_compare >= priority["fecha_mod"]:
                                if elem_restriction.is_override == 1:
                                    priority = {"res_by":4, "override":1, "value":elem_restriction.value, "fecha_mod":date_to_compare}
                                elif elem_restriction.is_override == 0 and priority["override"]==0:
                                    priority = {"res_by":4, "override":0, "value":elem_restriction.value, "fecha_mod":date_to_compare}
                            #Room
                            elif elem_restriction.id_restriction_by == 3 and elem_restriction.id_room_type==int(room) and date_to_compare >= priority["fecha_mod"]:
                                if elem_restriction.is_override == 1 and priority["res_by"] not in [4]:
                                    priority = {"res_by":3, "override":1, "value":elem_restriction.value, "fecha_mod":date_to_compare}
                                elif elem_restriction.is_override == 0 and priority["res_by"] not in [4] and priority["override"]==0:
                                    priority = {"res_by":3, "override":0, "value":elem_restriction.value, "fecha_mod":date_to_compare}
                            #Property
                            elif elem_restriction.id_restriction_by == 5 and date_to_compare >= priority["fecha_mod"]:
                                if elem_restriction.is_override == 1 and priority["res_by"] not in [4,3]:
                                    priority = {"res_by":5, "override":1, "value":elem_restriction.value, "fecha_mod":date_to_compare}
                                elif elem_restriction.is_override == 0 and priority["res_by"] not in [4,3] and priority["override"]==0:
                                    priority = {"res_by":5, "override":0, "value":elem_restriction.value, "fecha_mod":date_to_compare}

                    dict_date["efective_date"] = elem_date.strftime("%Y-%m-%d")
                    dict_date["min_los"] = priority["value"]
                    temp_rp_elem["dates"].append(dict_date)
                result.append(temp_rp_elem)

        except Exception as e:
            raise e

        return result

    @staticmethod
    def getMaxLosOperaRestriction(date_start, date_end, property, room, rateplans, all_rateplans=False):
        result = []
        try:
            #Se valida existencia de property
            count_property = proModel.query.filter(proModel.iddef_property==property, proModel.estado==1).with_entities(func.count()).scalar()
            if count_property == 0:
                raise Exception("Property not valid")
            #Se valida existencia del room
            count_room = rtcModel.query.filter(rtcModel.iddef_room_type_category == room, rtcModel.iddef_property==property, rtcModel.estado == 1).with_entities(func.count()).scalar()
            if count_room == 0:
                raise Exception("Room not valid")
            if len(rateplans) > 0:
                if all_rateplans:
                    list_rateplans = RatePlanModel.query\
                    .join(RatePlanRooms, RatePlanModel.idop_rateplan == RatePlanRooms.id_rate_plan)\
                    .join(rtcModel, RatePlanRooms.id_room_type == rtcModel.iddef_room_type_category)\
                    .join(proModel, proModel.iddef_property == rtcModel.iddef_property)\
                    .filter(rtcModel.iddef_property == property, RatePlanModel.idop_rateplan.in_(rateplans), RatePlanRooms.id_room_type == room,
                        RatePlanRooms.estado==1, rtcModel.estado==1, proModel.estado==1)\
                    .all()
                else:
                    list_rateplans = RatePlanModel.query\
                    .join(RatePlanRooms, RatePlanModel.idop_rateplan == RatePlanRooms.id_rate_plan)\
                    .join(rtcModel, RatePlanRooms.id_room_type == rtcModel.iddef_room_type_category)\
                    .join(proModel, proModel.iddef_property == rtcModel.iddef_property)\
                    .filter(rtcModel.iddef_property == property, RatePlanModel.idop_rateplan.in_(rateplans), RatePlanRooms.id_room_type == room,
                        RatePlanModel.estado==1, RatePlanRooms.estado==1, rtcModel.estado==1, proModel.estado==1)\
                    .all()

                if len(list_rateplans) == 0:
                    raise Exception("Rateplans are not valid")
            else:
                if all_rateplans:
                    list_rateplans = RatePlanModel.query\
                    .join(RatePlanRooms, RatePlanModel.idop_rateplan == RatePlanRooms.id_rate_plan)\
                    .join(rtcModel, RatePlanRooms.id_room_type == rtcModel.iddef_room_type_category)\
                    .join(proModel, proModel.iddef_property == rtcModel.iddef_property)\
                    .filter(rtcModel.iddef_property == property, RatePlanRooms.id_room_type == room,
                        RatePlanRooms.estado==1, rtcModel.estado==1, proModel.estado==1)\
                    .all()
                else:
                    list_rateplans = RatePlanModel.query\
                    .join(RatePlanRooms, RatePlanModel.idop_rateplan == RatePlanRooms.id_rate_plan)\
                    .join(rtcModel, RatePlanRooms.id_room_type == rtcModel.iddef_room_type_category)\
                    .join(proModel, proModel.iddef_property == rtcModel.iddef_property)\
                    .filter(rtcModel.iddef_property == property, RatePlanRooms.id_room_type == room,
                        RatePlanModel.estado==1, RatePlanRooms.estado==1, rtcModel.estado==1, proModel.estado==1)\
                    .all()

                if len(list_rateplans) == 0:
                    raise Exception("Property without rateplans")

            list_opera_restrictions = OpeResModel.query.filter(OpeResModel.id_property==property,
                OpeResModel.id_restriction_by.in_([3,4,5]), OpeResModel.id_restriction_type==3,
                OpeResModel.estado==1, or_(
                    and_(OpeResModel.date_start <= date_start, 
                        OpeResModel.date_end >= date_end),
                    and_(OpeResModel.date_start >= date_start, 
                        OpeResModel.date_end <= date_end),
                    and_(OpeResModel.date_start > date_start, 
                        OpeResModel.date_end > date_end,
                        OpeResModel.date_start <= date_end,
                        OpeResModel.date_end >= date_start),
                    and_(OpeResModel.date_start <= date_start, 
                        OpeResModel.date_end < date_end,
                        OpeResModel.date_start < date_end,
                        OpeResModel.date_end >= date_start)
                )).all()

            list_opera_restrictions = sorted(sorted(list_opera_restrictions, key=lambda x: x.fecha_creacion, reverse=True), key=lambda x: x.fecha_ultima_modificacion, reverse=True)

            date_default = dt.strptime('1900-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
            list_dates = list(RestricctionFunction.daterange(date_start, date_end))

            for rateplan_elem in list_rateplans:
                temp_rp_elem = {}
                temp_rp_elem["id_rateplan"] = rateplan_elem.idop_rateplan
                temp_rp_elem["name"] = rateplan_elem.code
                temp_rp_elem["dates"] = []
                for elem_date in list_dates:
                    dict_date = {}
                    priority = {"res_by":0, "override":0, "value":0, "fecha_mod":date_default}
                    for elem_restriction in list_opera_restrictions:
                        if elem_restriction.date_start <= elem_date and elem_date <= elem_restriction.date_end:
                            date_to_compare = elem_restriction.fecha_creacion if elem_restriction.fecha_ultima_modificacion == date_default else elem_restriction.fecha_ultima_modificacion
                            #RatePlan/Room
                            if elem_restriction.id_restriction_by == 4 and elem_restriction.id_room_type==int(room) and elem_restriction.id_rateplan==rateplan_elem.idop_rateplan and date_to_compare >= priority["fecha_mod"]:
                                if elem_restriction.is_override == 1:
                                    priority = {"res_by":4, "override":1, "value":elem_restriction.value, "fecha_mod":date_to_compare}
                                elif elem_restriction.is_override == 0 and priority["override"]==0:
                                    priority = {"res_by":4, "override":0, "value":elem_restriction.value, "fecha_mod":date_to_compare}
                            #Room
                            elif elem_restriction.id_restriction_by == 3 and elem_restriction.id_room_type==int(room) and date_to_compare >= priority["fecha_mod"]:
                                if elem_restriction.is_override == 1 and priority["res_by"] not in [4]:
                                    priority = {"res_by":3, "override":1, "value":elem_restriction.value, "fecha_mod":date_to_compare}
                                elif elem_restriction.is_override == 0 and priority["res_by"] not in [4] and priority["override"]==0:
                                    priority = {"res_by":3, "override":0, "value":elem_restriction.value, "fecha_mod":date_to_compare}
                            #Property
                            elif elem_restriction.id_restriction_by == 5 and date_to_compare >= priority["fecha_mod"]:
                                if elem_restriction.is_override == 1 and priority["res_by"] not in [4,3]:
                                    priority = {"res_by":5, "override":1, "value":elem_restriction.value, "fecha_mod":date_to_compare}
                                elif elem_restriction.is_override == 0 and priority["res_by"] not in [4,3] and priority["override"]==0:
                                    priority = {"res_by":5, "override":0, "value":elem_restriction.value, "fecha_mod":date_to_compare}

                    dict_date["efective_date"] = elem_date.strftime("%Y-%m-%d")
                    dict_date["max_los"] = priority["value"]
                    temp_rp_elem["dates"].append(dict_date)
                result.append(temp_rp_elem)

        except Exception as e:
            raise e

        return result

    @staticmethod
    def daterange(start_date, end_date):
        for n in range(int ((end_date - start_date).days+1)):
            yield start_date + timedelta(n)