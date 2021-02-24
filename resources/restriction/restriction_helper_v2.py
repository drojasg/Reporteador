from models.restriction import RestrictionDataRestrictionDetailSchema as ResDataResDetSchema
from config import db, base
from common.util import Util
import json
from datetime import datetime

class Restrictions():
    id_restriction_detail=0
    id_restriction=0
    specific_channel=0
    travel_window_start=None
    travel_window_end=None
    market_targeting=0
    geo_targeting_country=None
    restriction_default=None
    device=None
    restriction_by=0
    restriction_type=0
    estado_restriction=1
    estado_detail=1
    isAll=False, 
    useBooking=True
    min_los=0
    max_los=0
    value_room=""
    value_hotel_id=0
    value_rate_plan_id=0
    use_min_los=True
    use_max_los=True
    use_value=True
    booking_window_date = None
    booking_window_time = None
    bookable_weekday = None
    list_restrictions=[]
    params = {}

    def __init__(self, id_restriction_detail=0, id_restriction=0, specific_channel=0, \
        travel_window_start=None, travel_window_end=None, market_targeting=0, \
        geo_targeting_country=None, restriction_default=None, device=None, restriction_by=0, \
        restriction_type=0, estado_restriction=1, estado_detail=1, isAll=False, useBooking=True, \
        min_los=0, max_los=0, value_room="", value_hotel_id=0, value_rate_plan_id=0, \
        use_min_los=True, use_max_los=True, use_value=True):
        self.id_restriction_detail=id_restriction_detail
        self.id_restriction=id_restriction
        self.specific_channel=specific_channel
        self.travel_window_start=travel_window_start
        self.travel_window_end=travel_window_end
        self.market_targeting=market_targeting
        self.geo_targeting_country=geo_targeting_country
        self.restriction_default=restriction_default
        self.device=device
        self.restriction_by=restriction_by
        self.restriction_type=restriction_type
        self.estado_restriction=estado_restriction
        self.estado_detail=estado_detail
        self.isAll=isAll
        self.useBooking=useBooking
        self.min_los=min_los
        self.max_los=max_los
        self.value_room=value_room
        self.value_hotel_id=value_hotel_id
        self.value_rate_plan_id=value_rate_plan_id
        self.use_min_los=use_min_los
        self.use_max_los=use_max_los
        self.use_value=use_value

    def __get_day_of_the_week(self, weekday):
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

    def __validate_json_row(self, row):
        valid = True

        #Se validan las opciones y arrays (opción 0 en válida por default)
        if self.specific_channel > 0:
            if (int(row["channel_option"]) == 1 and self.specific_channel not in row["specific_channels"]) or \
            (int(row["channel_option"]) == 2 and self.specific_channel in row["specific_channels"]):
                valid = False

        if self.bookable_weekday is not None:
            if (int(row["bookable_weekdays_option"]) == 1 and self.bookable_weekday not in row["bookable_weekdays"]) or \
            (int(row["bookable_weekdays_option"]) == 2 and self.bookable_weekday in row["bookable_weekdays"]):
                valid = False

        if self.market_targeting > 0:
            if (int(row["market_option"]) == 1 and self.market_targeting not in row["market_targeting"]) or \
            (int(row["market_option"]) == 2 and self.market_targeting in row["market_targeting"]):
                valid = False

        if self.geo_targeting_country is not None:
            if (int(row["geo_targeting_option"]) == 1 and self.geo_targeting_country not in row["geo_targeting_countries"]) or \
            (int(row["geo_targeting_option"]) == 2 and self.geo_targeting_country in row["geo_targeting_countries"]):
                valid = False

        #Se validan las opciones y diccionarios (opción 0 en válida por default)
        if self.restriction_by == 3:
            if self.use_value and (self.restriction_type == 1 or self.restriction_type == 2 or self.restriction_type == 3):
                if ("room" in row["value"] and row["value"]["room"] == self.value_room) \
                and ("hotel_id" in row["value"] and row["value"]["hotel_id"] == self.value_hotel_id):
                    pass
                else:
                    valid = False

        if self.restriction_by == 4:
            if self.use_value and self.restriction_type == 1:
                if ("room" in row["value"] and row["value"]["room"] == self.value_room) \
                and ("hotel_id" in row["value"] and row["value"]["hotel_id"] == self.value_hotel_id):
                    if self.value_rate_plan_id > 0:
                        if "rate_plan_id" in row["value"] and row["value"]["rate_plan_id"] == self.value_rate_plan_id:
                            pass
                        else:
                            valid = False
                else:
                    valid = False

        if(self.restriction_by == 5):
            if(self.use_value and self.restriction_type == 1):
                if "hotel_id" in row["value"] and row["value"]["hotel_id"] == self.value_hotel_id:
                    pass
                else:
                    valid = False

        #Se validan fechan en array de diccionarios
        if self.booking_window_date is not None:
            if int(row["booking_window_option"]) != 0:
                bwd_flag = False
                for bwd in row["booking_window_dates"]:
                    if (int(row["booking_window_option"]) == 1 and (self.booking_window_date >= bwd["start_date"] and self.booking_window_date <= bwd["end_date"]))\
                    or (int(row["booking_window_option"]) == 2 and (self.booking_window_date < bwd["start_date"] and self.booking_window_date > bwd["end_date"])):
                        bwd_flag = True
                if not bwd_flag:
                    valid = False

        if self.booking_window_time is not None:
            bwt_flag = True
            for bwt in row["booking_window_times"]:
                if self.booking_window_time >= bwt["start_time"] and self.booking_window_time <= bwt["end_time"]:
                    pass
                else:
                    bwt_flag = False
            if not bwt_flag:
                valid = False

        if self.travel_window_start is not None and self.travel_window_end:
            if int(row["travel_window_option"]) != 0:
                tw_flag = False
                for tw in row["travel_window"]:
                    if (int(row["travel_window_option"]) == 1 and (tw["start_date"] <= self.travel_window_end and tw["end_date"] >= self.travel_window_start))\
                    or (int(row["travel_window_option"]) == 2 and (self.travel_window_start < tw["start_date"] or self.travel_window_end > tw["end_date"])):
                        tw_flag = True
                if not tw_flag:
                    valid = False

        return valid

    def __set_list_restrictions(self):
        self.list_restrictions=[]
        params={}

        # Si parámetro "useBooking" es True se obtendrán Fecha, hora y dia de la semana actuales (HOY)
        # y con ello se tomará en cuenta en los filtros
        if self.useBooking:
            self.booking_window_date = datetime.today().strftime('%Y-%m-%d') # Se obtiene fecha actual
            self.booking_window_time = datetime.today().strftime('%H:%M') # Se obtiene hora actual
            self.bookable_weekday = self.__get_day_of_the_week(datetime.today().weekday()) # Se obtiene el día de la semana

        schema = ResDataResDetSchema(exclude=Util.get_default_excludes())

        query = "SELECT res.*, res_det.iddef_restriction_detail, res_det.channel_option, res_det.specific_channels, \
        res_det.travel_window_option, res_det.travel_window, res_det.booking_window_option, res_det.booking_window_dates, \
        res_det.bookable_weekdays_option, res_det.bookable_weekdays, res_det.booking_window_times, res_det.geo_targeting_option, \
        res_det.geo_targeting_countries, res_det.market_option, res_det.market_targeting, res_det.device_type_option, \
        res_det.restriction_default, res_det.min_los, res_det.max_los, res_det.value \
        FROM def_restriction_detail AS res_det \
        JOIN def_restriction AS res ON res.iddef_restriction = res_det.iddef_restriction"

        if not self.isAll:
            query += self.__get_where_query()

        #query += " GROUP BY res.iddef_restriction;"
            
        data = db.session.execute(query, params).fetchall()
        self.list_restrictions = schema.dump(data, many=True)

        #Algunos campos JSON se recuperan como string, por ello se ejecuta una conversión a Dict si se detecta como string
        for dato_index, dato_value in enumerate(self.list_restrictions):
            if isinstance(self.list_restrictions[dato_index]["geo_targeting_countries"], str): self.list_restrictions[dato_index]["geo_targeting_countries"] = json.loads(self.list_restrictions[dato_index]["geo_targeting_countries"])
            if isinstance(self.list_restrictions[dato_index]["specific_channels"], str): self.list_restrictions[dato_index]["specific_channels"] = json.loads(self.list_restrictions[dato_index]["specific_channels"])
            if isinstance(self.list_restrictions[dato_index]["travel_window"], str): self.list_restrictions[dato_index]["travel_window"] = json.loads(self.list_restrictions[dato_index]["travel_window"])
            if isinstance(self.list_restrictions[dato_index]["bookable_weekdays"], str): self.list_restrictions[dato_index]["bookable_weekdays"] = json.loads(self.list_restrictions[dato_index]["bookable_weekdays"])
            if isinstance(self.list_restrictions[dato_index]["market_targeting"], str): self.list_restrictions[dato_index]["market_targeting"] = json.loads(self.list_restrictions[dato_index]["market_targeting"])
            if isinstance(self.list_restrictions[dato_index]["booking_window_times"], str): self.list_restrictions[dato_index]["booking_window_times"] = json.loads(self.list_restrictions[dato_index]["booking_window_times"])
            if isinstance(self.list_restrictions[dato_index]["booking_window_dates"], str): self.list_restrictions[dato_index]["booking_window_dates"] = json.loads(self.list_restrictions[dato_index]["booking_window_dates"])
            if isinstance(self.list_restrictions[dato_index]["value"], str): self.list_restrictions[dato_index]["value"] = json.loads(self.list_restrictions[dato_index]["value"])

        #Se validan los datos
        temp_list_restrictions = []
        #temp_list_restrictions = [elem_restriction for elem_restriction in self.list_restrictions if self.__validate_json_row(elem_restriction)]
        for elem_restriction in self.list_restrictions:
            if self.__validate_json_row(elem_restriction):
                if next((elem_temp for elem_temp in temp_list_restrictions if elem_temp["iddef_restriction"] == elem_restriction["iddef_restriction"]), None) is not None:
                    #Si hay un detalle perteneciente a la misma restriccion agregada en la lista temporal, se omite el agregarla
                    pass
                else:
                    temp_list_restrictions.append(elem_restriction)

        self.list_restrictions = temp_list_restrictions

    def __get_where_query(self):
        query_where = ""
        previous_where = False # Bandera para identificar si se ha agregado algo "query_where"

        #Se crea el query para consultas basica del "query_where"
        if(self.id_restriction_detail > 0):
            query_where += " AND " if previous_where else " WHERE "
            previous_where = True
            query_where += f"res_det.iddef_restriction_detail = {self.id_restriction_detail}"

        if(self.id_restriction > 0):
            query_where += " AND " if previous_where else " WHERE "
            previous_where = True
            query_where += f"res.iddef_restriction = {self.id_restriction}"

        if(self.device is not None):
            query_where += " AND " if previous_where else " WHERE "
            previous_where = True
            query_where += f"res_det.device_type_option = {self.device}"

        if(self.restriction_default is not None):
            query_where += " AND " if previous_where else " WHERE "
            previous_where = True
            query_where += f"res_det.restriction_default = {self.restriction_default}"

        if(self.restriction_by > 0):
            query_where += " AND " if previous_where else " WHERE "
            previous_where = True
            query_where += f"res.iddef_restriction_by = {self.restriction_by}"

            if(self.restriction_by == 3):
                if(self.use_min_los and self.restriction_type == 2):
                    query_where += " AND " if previous_where else " WHERE "
                    previous_where = True
                    query_where += f"res_det.min_los = {self.min_los}"
                elif(self.use_max_los and self.restriction_type == 3):
                    query_where += " AND " if previous_where else " WHERE "
                    previous_where = True
                    query_where += f"res_det.max_los = {self.max_los}"

        if(self.restriction_type > 0):
            query_where += " AND " if previous_where else " WHERE "
            previous_where = True
            query_where += f"res.iddef_restriction_type = {self.restriction_type}"

        if(self.estado_restriction is not None):
            query_where += " AND " if previous_where else " WHERE "
            previous_where = True
            query_where += f"res.estado = {self.estado_restriction}"

        if(self.estado_detail is not None):
            query_where += " AND " if previous_where else " WHERE "
            previous_where = True
            query_where += f"res_det.estado = {self.estado_detail}"

        return query_where

    def get_restriction_details(self):
        self.__set_list_restrictions()
        return self.list_restrictions
