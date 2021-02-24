from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.restriction_detail import RestrictionDetailSchema as ModelSchema, RestrictionDetail as Model, RestrictionDetailRoomRateplan as ModelRoomRateplan
from models.restriction import Restriction, RestrictionSchema
from models.room_type_category import RoomTypeCategory as rtcModel
from models.rateplan import RatePlan as rpModel
from common.util import Util
from resources.restriction.restricctionHelper import RestricctionFunction as funtions
from resources.restriction.restriction_helper_v2 import Restrictions as resFuntions2
from datetime import datetime as dt, timedelta, date


class RestrictionDetail(Resource):
    # @base.access_middleware
    def get(self,id):
        try:
            isAll = request.args.get("all")
            arrai = []
            data = Model()
            
            if isAll is not None:
                data = Model.query.all()
            else:
                data = db.session.query(Model).\
                                    join(Restriction, Restriction.iddef_restriction == Model.iddef_restriction)\
                                    .filter(Model.iddef_restriction == id)
                                  
                        
            schema = ModelSchema(exclude=Util.get_default_excludes(), many=True)
            datos = schema.dump(data)
               
            if data is None:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": {}
                }
            else:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": datos
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
            
        return response

    def ListaToJson(self, lista):
        item_data = {}
        for index, value in enumerate(lista):
            item_data[index] = value
        data = json.dumps(item_data)
        return data
        
        
    def JsonToList(self, jsonTo):
        item_array = []
        for index, value in jsonTo.items():
            item_array.append(value)
        return item_array


class RestrictionDetailRoomRateplan(Resource):
    #api-restrictiondetail-get-closedates
    # @base.access_middleware
    def post(self):
        try:
            json_data = request.get_json(force=True)
            load_schema = ModelRoomRateplan()
            data = load_schema.load(json_data)

            travel_window_start = data["travel_window_start"].strftime("%Y-%m-%d")
            travel_window_end = data["travel_window_end"].strftime("%Y-%m-%d")
            idproperty = data["idproperty"]
            idroom = data["idroom"]
            restriction_by = 4
            restriction_type = 1
            new_restriction_details_close = []
            ids_rateplans = []
            list_dates = [temp_date for temp_date in RestrictionDetailRoomRateplan.daterange(data["travel_window_start"], data["travel_window_end"])]

            room = rtcModel.query.filter(rtcModel.iddef_room_type_category==idroom, rtcModel.iddef_property==idproperty).one()
            room_code = room.room_code

            #Obtenemos las fechas de cierres
            # restriction_details_close = funtions.getRestrictionDetails(travel_window_start=travel_window_start, travel_window_end=travel_window_end, \
            #     value_room=room_code, value_hotel_id=idproperty, restriction_by=restriction_by, restriction_type=restriction_type, \
            #     useBooking=False, use_min_los=False, use_max_los=False, use_value=True)

            obj = resFuntions2(travel_window_start=travel_window_start, travel_window_end=travel_window_end, \
                value_room=room_code, value_hotel_id=idproperty, restriction_by=restriction_by, restriction_type=restriction_type, \
                useBooking=False, use_min_los=False, use_max_los=False, use_value=True)
            restriction_details_close = obj.get_restriction_details()

            #Se obtienen los ids de rateplans
            for res_det in restriction_details_close:
                if(int(res_det["travel_window_option"]) == 1):
                    for id_rateplan in res_det["value"]["rate_plan_id"]:
                        if id_rateplan not in ids_rateplans:
                            ids_rateplans.append(id_rateplan)

            #Se consultan rateplans
            rateplan_list = rpModel.query.filter(rpModel.idop_rateplan.in_(ids_rateplans)).all()

            #Se validan los días con las restricciones y se separan por rateplan
            closeItems = []
            for temp_rateplan in rateplan_list:
                list_close_dates = []
                for temp_date in list_dates:
                    close_value = False
                    for res_det in restriction_details_close:
                        if(int(res_det["travel_window_option"]) == 1 and 
                        (res_det["value"] is not None and res_det["value"] != {} and res_det["value"] != "null" and 
                        temp_rateplan.idop_rateplan in res_det["value"]["rate_plan_id"])):
                            for travel_window_date in res_det["travel_window"]:
                                temp_start_date = dt.strptime(travel_window_date["start_date"], '%Y-%m-%d').date()
                                temp_end_date = dt.strptime(travel_window_date["end_date"], '%Y-%m-%d').date()
                                if temp_date >= temp_start_date and temp_date <= temp_end_date:
                                    close_value = True
                    list_close_dates.append({"efective_date": temp_date.strftime("%Y-%m-%d"), "close": close_value})

                closeDateTemp = {
                    "id_rateplan":temp_rateplan.idop_rateplan,
                    "name":temp_rateplan.code,
                    "dates":list_close_dates
                }
                if(closeDateTemp not in closeItems): closeItems.append(closeDateTemp)

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": closeItems
            }
        except ValidationError as error:
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data": {}
            }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
            
        return response

    @staticmethod
    def daterange(start_date, end_date):
        for n in range(int ((end_date - start_date).days+1)):
            yield start_date + timedelta(n)

# Clase creada para probar funciones
class Test(Resource):
    # @base.access_middleware
    def get(self):
        try:
            isAll = request.args.get("all")
            data = 1

            # datos = funtions.getRestrictionDetails(specific_channel=3,booking_window_date="2020-02-11",booking_window_time="13:00",travel_window_start="2020-02-21",travel_window_end="2020-02-24")
            obj = resFuntions2(specific_channel=3,booking_window_date="2020-02-11",booking_window_time="13:00",travel_window_start="2020-02-21",travel_window_end="2020-02-24")
            datos = obj.get_restriction_details()

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": datos
            }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
            
        return response
