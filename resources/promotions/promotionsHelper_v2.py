from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from config import db,base
from models.promotions import Promotions as Model, PromotionsSchema as ModelSchema
from models.promotion_rateplan import PromotionRateplan as PRModel, PromotionRateplanSchema as PRModelSchema
from models.promotion_restriction import PromotionRestriction as PResModel, PromotionRestrictionSchema as PResModelSchema
from models.property import Property as PModel, PropertySchema as Pschema
from models.rateplan import RatePlan as RPModel
from models.promotion_discount_type import PromotionDiscountType as PDTModel
from models.book_promotion import BookPromotion as BPModel, BookPromotionSchema as BPModelSchema
from resources.restriction.restricctionHelper import RestricctionFunction as functionsRes
from resources.restriction.restriction_helper_v2 import Restrictions as resFuntions2
from resources.market_segment.marketHelper import Market as functionsMark
from resources.property.propertyHelper import FilterProperty as functionsPro
from common.util import Util
from operator import itemgetter
from sqlalchemy import or_, and_, func
import datetime, decimal
import json
from datetime import datetime as dt
import datetime as dates

class Generate():

    #crea o actualiza
    def create_promotion(self,json_data, id_promotion):
        try:

            data = []
            schema = ModelSchema(exclude=Util.get_default_excludes())
            get_filter = Filter()

            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            #Formateo de nodo de detail_restriction
            if len(json_data["detail_restriction"]) > 0:
                json_data["detail_restriction"][0]["iddef_restriction_by"] = 7
                json_data["detail_restriction"][0]["iddef_restriction_type"] = 4

            if int(id_promotion) == 0:
                Data = Model()
                Data.name = json_data["name"]
                Data.code = json_data["code"]
                Data.discounts = json_data["discounts"]
                bandLength = False
                if len(Data.discounts) > 0:
                    for itm in Data.discounts:
                        infoType = get_filter.get_promotion_discount_type(itm["type"])
                        if str(infoType.code).replace(' ', '').upper() == "LENGTHOFSTAY":
                            bandLength = True
                Data.free_childs = json_data["free_childs"]
                Data.free_childs_conditions = json_data["free_childs_conditions"]
                Data.free_nights = json_data["free_nights"]
                Data.free_nights_conditions = json_data["free_nights_conditions"]
                Data.free_rooms = json_data["free_rooms"]
                Data.free_rooms_conditions = json_data["free_rooms_conditions"]
                if bandLength is True:
                    Data.length_of_stay = {}
                else:
                    if json_data["length_of_stay"]["maxLOS"]["inherit"] == 0:
                        json_data["length_of_stay"]["maxLOS"]["value"] = 0
                    elif json_data["length_of_stay"]["minLOS"]["inherit"] == 0:
                        json_data["length_of_stay"]["minLOS"]["value"] = 0
                    else:
                        if json_data["length_of_stay"]["maxLOS"]["value"] == 0:
                            raise Exception("Length_of_stay-maxLOS-value is Zero: "+str(json_data["length_of_stay"]["maxLOS"]["value"]))
                        elif json_data["length_of_stay"]["minLOS"]["value"] == 0:
                            raise Exception("Length_of_stay-minLOS-value is Zero: "+str(json_data["length_of_stay"]["minLOS"]["value"]))
                        else:
                            if json_data["length_of_stay"]["maxLOS"]["value"] < json_data["length_of_stay"]["minLOS"]["value"]:
                                raise Exception("Length_of_stay-maxLOS-value("+str(json_data["length_of_stay"]["maxLOS"]["value"])+") < or = length_of_stay-minLOS-value("+str(json_data["length_of_stay"]["minLOS"]["value"])+")")
                    Data.length_of_stay = json_data["length_of_stay"]
                Data.partial_aplication = json_data["partial_aplication"]
                Data.limit_sales = json_data["limit_sales"]
                Data.limit_sales_count = json_data["limit_sales_count"]
                Data.timer = json_data["timer"]
                if Data.timer != 0:
                    Data.days_offset = json_data["days_offset"]
                    Data.time_offset = json_data["time_offset"]
                else:
                    Data.days_offset = 0
                    Data.time_offset = "00:00:00"
                Data.percent_cross_out = json_data["percent_cross_out"]
                Data.estado = 1
                Data.usuario_creacion = user_name
                db.session.add(Data)
                db.session.commit()
                data = schema.dump(Data)
                id_promotion = Data.idop_promotions
                if len(json_data["rate_plans"]) > 0:
                    rate_plans = self.create_promotion_rateplan(json_data["rate_plans"],id_promotion)
                if len(json_data["detail_restriction"]) > 0:
                    detail_restriction = self.create_promotion_restriction(json_data["detail_restriction"],id_promotion)            
            else:
                #data = None
                model = Model.query.get(id_promotion)
                if request.json.get("name") != None:
                    model.name = json_data["name"]
                if request.json.get("code") != None:
                    model.code = json_data["code"]
                bandLength = False
                if request.json.get("discounts") != None:
                    model.discounts = json_data["discounts"]
                    if len(model.discounts) > 0:
                        for itm in model.discounts:
                            infoType = get_filter.get_promotion_discount_type(itm["type"])
                            if str(infoType.code).replace(' ', '').upper() == "LENGTHOFSTAY":
                                bandLength = True
                if request.json.get("free_childs") != None:
                    model.free_childs = json_data["free_childs"]
                if request.json.get("free_childs_conditions") != None:
                    model.free_childs_conditions = json_data["free_childs_conditions"]
                if request.json.get("free_nights") != None:
                    model.free_nights = json_data["free_nights"]
                if request.json.get("free_nights_conditions") != None:
                    model.free_nights_conditions = json_data["free_nights_conditions"]
                if request.json.get("free_rooms") != None:
                    model.free_rooms = json_data["free_rooms"]
                if request.json.get("free_rooms_conditions") != None:
                    model.free_rooms_conditions = json_data["free_rooms_conditions"]
                if request.json.get("length_of_stay") != None and bandLength == True:
                    model.length_of_stay = {}
                elif request.json.get("length_of_stay") != None and bandLength == False:
                    if json_data["length_of_stay"]["maxLOS"]["inherit"] == 0:
                        json_data["length_of_stay"]["maxLOS"]["value"] = 0
                    elif json_data["length_of_stay"]["minLOS"]["inherit"] == 0:
                        json_data["length_of_stay"]["minLOS"]["value"] = 0
                    else:
                        if json_data["length_of_stay"]["maxLOS"]["value"] == 0:
                            raise Exception("Length_of_stay-maxLOS-value is Zero: "+str(json_data["length_of_stay"]["maxLOS"]["value"]))
                        elif json_data["length_of_stay"]["minLOS"]["value"] == 0:
                            raise Exception("Length_of_stay-minLOS-value is Zero: "+str(json_data["length_of_stay"]["minLOS"]["value"]))
                        else:
                            if json_data["length_of_stay"]["maxLOS"]["value"] < json_data["length_of_stay"]["minLOS"]["value"]:
                                raise Exception("Length_of_stay-maxLOS-value("+str(json_data["length_of_stay"]["maxLOS"]["value"])+") < or = length_of_stay-minLOS-value("+str(json_data["length_of_stay"]["minLOS"]["value"])+")")
                    model.length_of_stay = json_data["length_of_stay"]
                if request.json.get("partial_aplication") != None:
                    model.partial_aplication = json_data["partial_aplication"]
                if request.json.get("limit_sales") != None:
                    model.limit_sales = json_data["limit_sales"]
                if request.json.get("limit_sales_count") != None:
                    model.limit_sales_count = json_data["limit_sales_count"]
                if request.json.get("timer") != None:
                    model.timer = json_data["timer"]
                    if model.timer != 0:
                        model.days_offset = json_data["days_offset"]
                        model.time_offset = json_data["time_offset"]
                    else:
                        model.days_offset = 0
                        model.time_offset = "00:00:00"
                if request.json.get("percent_cross_out") != None:
                    model.percent_cross_out = json_data["percent_cross_out"]
                if request.json.get("estado") != None:
                    model.estado = json_data["estado"]
                model.usuario_ultima_modificacion = user_name
                db.session.commit()
                data = schema.dump(model)
                if len(json_data["rate_plans"]) > 0:
                    rate_plans = self.create_promotion_rateplan(json_data["rate_plans"],id_promotion)
                if len(json_data["detail_restriction"]) > 0:
                    detail_restriction = self.create_promotion_restriction(json_data["detail_restriction"],id_promotion)
        
        except Exception as ex:
            raise Exception("Error al crear/actualizar promotions: "+str(ex))

        return data
    
    def create_promotion_rateplan(self,json_data,id_promotion):
        try:
            data=None
            schema = PRModelSchema(exclude=Util.get_default_excludes())

            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            dataPR = PRModel.query.filter_by(id_promotion=id_promotion).all()
            dataPromotionsRateplan = schema.dump(dataPR, many=True)
            #Actualizar estado 0
            if len(dataPR) > 0:
                for x in dataPromotionsRateplan:
                    dPP = PRModel.query.get(x['iddef_promotion_rateplan'])
                    dPP.estado = 0
                    db.session.commit()
            #Asignar rateplan
            for item in json_data:
                id_property= item["id_property"]
                if len(item["rate_plans"]) > 0:
                    for item_rateplan in item["rate_plans"]:
                        if len(item_rateplan["rate_plan_rooms"]) > 0:
                            model = PRModel.query.filter_by(id_promotion=id_promotion,id_property=id_property,id_rateplan=item_rateplan["id_rateplan"]).first()
                            if model is None:
                                model = PRModel()
                                model.id_promotion = id_promotion
                                model.id_rateplan = item_rateplan["id_rateplan"]
                                model.id_property = id_property
                                model.rate_plan_rooms = item_rateplan["rate_plan_rooms"]
                                model.estado = 1
                                model.usuario_creacion = user_name
                                db.session.add(model)
                                db.session.commit()
                                data = schema.dump(model)
                            else:
                                model.id_promotion = id_promotion
                                model.id_rateplan = item_rateplan["id_rateplan"]
                                model.id_property = id_property
                                model.rate_plan_rooms = item_rateplan["rate_plan_rooms"]
                                model.estado = 1
                                model.usuario_ultima_modificacion = user_name
                                db.session.commit()
                                data = schema.dump(model)

        except Exception as ex:
            raise Exception("Error al crear/actualizar promotion-rateplan "+str(ex), 'id_property',id_property)

        return data
    
    def create_promotion_restriction(self,json_data,id_promotion):
        try:
            schema = PResModelSchema(exclude=Util.get_default_excludes())
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            dataPRes = PResModel.query.filter_by(id_promotion=id_promotion).all()
            dataPromotionsRestriction = schema.dump(dataPRes, many=True)
            data = None
            #Actualizar estado 0
            if dataPRes != None:
                for x in dataPromotionsRestriction:
                    dPR = PResModel.query.get(x['idop_promotion_restriction'])
                    dPR.estado = 0
                    db.session.commit()
            #Asignar rateplan
            for item in json_data:
                if int(item["iddef_restriction"]) == 0:
                    result_restriction = functionsRes.update_restriction(item,item["iddef_restriction"])
                    Data = PResModel()
                    Data.id_promotion = id_promotion
                    Data.id_restriction = result_restriction["iddef_restriction"]
                    Data.estado = 1
                    Data.usuario_creacion = user_name
                    db.session.add(Data)
                    db.session.commit()
                    data = schema.dump(Data)
                else:
                    model = PResModel.query.filter_by(id_promotion=id_promotion, id_restriction=item["iddef_restriction"]).first()
                    if model is None:
                        Data = PResModel()
                        Data.id_promotion = id_promotion
                        Data.id_restriction = item["iddef_restriction"]
                        Data.estado = 1
                        Data.usuario_creacion = user_name
                        db.session.add(Data)
                        db.session.commit()
                        data = schema.dump(Data)
                    else:
                        model.id_promotion = id_promotion
                        model.id_restriction = item["iddef_restriction"]
                        model.estado = 1
                        model.usuario_ultima_modificacion = user_name
                        db.session.commit()
                        data = schema.dump(model)

                    result_restriction = functionsRes.update_restriction(item,item["iddef_restriction"])
        
        except Exception as ex:
            raise Exception("Error al crear/actualizar promotion-restriction "+str(ex))

        return data
    
class Filter():

    #Metodo para obtener las restrincciones
    def get_detail_restriction(self,id_promotion):
        data = None
        data_restriction = PResModel.query.filter_by(id_promotion=id_promotion, estado=1).first()
        if data_restriction is None:
            raise Exception ("No se encontraron Restrictions relacionados a la Promotion")
        else:
            data_detail_restriction = functionsRes.getRestrictionDetailInfo(id_restriction=data_restriction.id_restriction)

        if data_detail_restriction is not None:
            data = data_detail_restriction

        return data
    
    #Metodo para obtener las rateplan
    def get_promotion_rateplan(self,id_promotion):
        result_properties = []
        data_properties = PModel.query.filter_by(estado=1).all()
        if len(data_properties) > 0:
            for item_property in data_properties:
                id_property = item_property.iddef_property
                result_plans = []
                result_plans = self.get_property_rateplan(id_promotion,id_property)
                obj_property = {
                    "iddef_property":item_property.iddef_property,
                    "rate_plans":result_plans
                }
                result_properties.append(obj_property)

        return result_properties
    
    #Metodo para consultar rateplan por propiedad
    def get_property_rateplan(self,id_promotion,id_property):
        result_plans = []
        data_rateplan = PRModel.query.filter_by(id_promotion=id_promotion, id_property=id_property, estado=1).all()
        if len(data_rateplan) > 0:
            code = ""
            rate_code_clever = ""
            for item_plan in data_rateplan:
                rateplan_inf = RPModel.query.filter_by(idop_rateplan=item_plan.id_rateplan, estado=1).first()
                if rateplan_inf is not None:
                    code = rateplan_inf.code
                    rate_code_clever = rateplan_inf.rate_code_clever
                obj_plans = {
                    "idop_rateplan":item_plan.id_rateplan,
                    "code":code,
                    "rate_code_clever":rate_code_clever,
                    "rate_plan_rooms":item_plan.rate_plan_rooms
                }
                result_plans.append(obj_plans)

        return result_plans
    
    #Metodo para obtener disconunt type
    def get_promotion_discount_type(self,id_type):
        data=None

        data_type = PDTModel.query.filter_by(iddef_promotion_discount_type=id_type, estado=1).first()
        
        if data_type is not None:
            data = data_type

        return data
    

    #obtener promociones
    def get_promotions(self,ids_promotion=None,code=None,totalNigths=None,totalRooms=None):
        schema = ModelSchema(exclude=Util.get_default_excludes())
        result, conditions = [], []
        conditionsOr, conditionsOr2 = [], []
        conditionsAnd, conditionsAnd2, conditionsAnd22, conditionsAnd23 = [], [], [], []
        
        if ids_promotion is not None:
            conditions.append(Model.idop_promotions.in_(ids_promotion))
        if code is not None:
            conditions.append(Model.code == code)
        if totalNigths is not None:
            conditionsAnd.append(Model.free_nights==0)
            conditionsOr.append(and_(*conditionsAnd))
            conditionsAnd2.append(Model.free_nights==1)
            conditionsAnd2.append(func.json_extract(Model.free_nights_conditions, '$.paid') <= totalNigths)
            conditionsOr.append(and_(*conditionsAnd2))
            conditions.append(or_(*conditionsOr))
        if totalRooms is None:
            conditionsAnd22.append(Model.free_rooms==0)
            conditionsOr2.append(and_(*conditionsAnd22))
            conditionsAnd23.append(Model.free_rooms==1)
            conditionsAnd23.append(func.json_extract(Model.free_rooms_conditions, '$.paid') <= totalRooms)
            conditionsOr2.append(and_(*conditionsAnd23))
            conditions.append(or_(*conditionsOr2))
        
        data_promotions = Model.query.filter(and_(*conditions,Model.estado==1)).all()
        
        if len(data_promotions) > 0:
            result = schema.dump(data_promotions, many=True)

        return result
    
    #Filtrar book_promotion
    def get_book_promotion(self,id_book=None,id_promotion=None,isAll=True,count=True):
        conditions = []

        if id_book is not None:
            conditions.append(BPModel.idbook_hotel==id_book)
        if id_promotion is not None:
            conditions.append(BPModel.idop_promotions==id_promotion)
        if isAll:
            if count:
                data_promotions = BPModel.query.filter(and_(*conditions,BPModel.estado==1)).count()
            else:
                data_promotions = BPModel.query.filter(and_(*conditions,BPModel.estado==1)).all()
        else:
            data_promotions = BPModel.query.filter(and_(*conditions,BPModel.estado==1)).first()

        return data_promotions

class FilterPublic():
    #Metodo para obtener promotions para reserva
    def get_promotions_by_booking(self,date_start=None,date_end=None,market=None,\
    hotel=None,include_free_room=True,\
    list_rateplan=None, list_room=None):
        data = []
        totalRooms = 0
        booking_date = dt.now().date()
        booking_time = dt.now().time()
        get_filter = Filter()
        get_mark = functionsMark()
        getPro = functionsPro()
        #Obtenemos informacion de los cuartos seleccionados
        if list_rateplan is not None:
            if not isinstance(list_rateplan,list):
                list_rateplan = [list_rateplan]
        else:
            raise Exception("Rateplan no encontrado, favor de verificar")
        if list_room is not None:
            if isinstance(list_room,list):
                totalRooms = len(list_room)
            else:
                list_room = [list_room]
        else:
            raise Exception("Room no encontrado, favor de verificar")

        #Obtenemos informacion del mercado seleccionado
        if market != None:
            msData = get_mark.getMarketInfo(market)
            id_market = msData.iddef_market_segment
        #Obtenemos informacion de la propiedad seleccionado
        if hotel != None:
            hotel = getPro.getHotelInfo(hotel)
            id_property = hotel.iddef_property
        #Obtenemos informacion de las fechas seleccionadas
        if date_start != None and date_end !=None:
            totalNigths = (date_end - date_start).days
            totalDays = (date_start - booking_date).days
            date_start = date_start.strftime("%Y-%m-%d")
            date_end = date_end - dates.timedelta(days=1)
            date_end = date_end.strftime("%Y-%m-%d")
            booking_date = booking_date.strftime("%Y-%m-%d")
        
        #Se obtiene informacion de restricciones
        # data_restrictions = functionsRes.getRestrictionDetails(travel_window_start=date_start, \
        # travel_window_end=date_end, restriction_by=7, restriction_type=4, market_targeting=id_market)
        obj = resFuntions2(travel_window_start=date_start, \
        travel_window_end=date_end, restriction_by=7, restriction_type=4, market_targeting=id_market)
        data_restrictions = obj.get_restriction_details()
        
        if len(data_restrictions) > 0:
            #se valida restricciones
            ids_restrictions = FilterPublic.validate_restrictions(self,data_restrictions,date_start,date_end,booking_date,include_free_room)
            #se obtiene promociones respecto a restricciones, ratepla, cuarto, propiedad
            data_pro_rest = PResModel.query.filter(PResModel.estado==1,\
            PResModel.id_restriction.in_(ids_restrictions)).all()
            
            if len(data_pro_rest) > 0:
                ids_promotions = [promotion_elem.id_promotion for promotion_elem in data_pro_rest]
                
                #se obtiene promociones respecto a ratepla, cuarto, propiedad
                data_pro_rate = PRModel.query.filter(PRModel.id_promotion.in_(ids_promotions),\
                PRModel.id_property==id_property,PRModel.id_rateplan.in_(list_rateplan),\
                func.json_contains(PRModel.rate_plan_rooms,''+str(list_room)+''),PRModel.estado==1).all()
                
                if len(data_pro_rate) > 0:
                    ids_promotion = [promotion_elem.id_promotion for promotion_elem in data_pro_rate]
                    #Validacion nigth, length, free_niths, free_rooms
                    dataPromotions = get_filter.get_promotions(ids_promotion=ids_promotion,\
                    totalNigths=totalNigths,totalRooms=totalRooms)
                    
                    if len(dataPromotions) > 0:
                        for itx in dataPromotions:
                            bandLength, bandDiscount, bandLimitSales, bandFreeRooms = True, True, True, True
                            #Validacion length
                            if len(itx["length_of_stay"]) > 0:
                                bandLength = False
                                if itx["length_of_stay"]["maxLOS"]["inherit"] == 0 and itx["length_of_stay"]["minLOS"]["inherit"] == 1:
                                    if itx["length_of_stay"]["minLOS"]["value"] > 0:
                                        if totalNigths >= itx["length_of_stay"]["minLOS"]["value"]:
                                            bandLength = True
                                elif itx["length_of_stay"]["maxLOS"]["inherit"] == 1 and itx["length_of_stay"]["minLOS"]["inherit"] == 0:
                                    if itx["length_of_stay"]["maxLOS"]["value"] > 0:
                                        if totalNigths <= itx["length_of_stay"]["maxLOS"]["value"]:
                                            bandLength = True
                                elif itx["length_of_stay"]["maxLOS"]["inherit"] == 1 and itx["length_of_stay"]["minLOS"]["inherit"] == 1:
                                    if itx["length_of_stay"]["maxLOS"]["value"] > 0 and itx["length_of_stay"]["minLOS"]["value"] > 0:
                                        if totalNigths >= itx["length_of_stay"]["minLOS"]["value"] and totalNigths <= itx["length_of_stay"]["maxLOS"]["value"]:
                                            bandLength = True
                                elif itx["length_of_stay"]["maxLOS"]["inherit"] == 0 and itx["length_of_stay"]["minLOS"]["inherit"] == 0:
                                    bandLength = True
                            #Validacion limit_sales
                            if itx["limit_sales"] != 0:
                                bandLimitSales = False
                                #Obtenemos informacion de book_promotion
                                total_book = get_filter.get_book_promotion(id_promotion=itx["idop_promotions"])
                                if int(total_book) > 0:
                                    if total_book < itx["limit_sales_count"]:
                                        bandLimitSales = True
                                else:
                                    bandLimitSales = True
                            #Validacion discount
                            if len(itx["discounts"]) > 0:
                                bandDiscount = False
                                for typeX in itx["discounts"]:
                                    if typeX["type"] == 1:
                                        bandDiscount = True
                                    elif typeX["type"] == 2:
                                        bandDiscount = True if totalDays >= typeX["days"] else False
                                    elif typeX["type"] == 3:
                                        bandDiscount = True if totalDays <= typeX["days"] else False
                                    elif typeX["type"] == 4:
                                        bandDiscount = True if totalNigths >= typeX["days"] else False
                            #validacion include_free_room
                            if include_free_room == False:
                                bandFreeRooms = True if itx["free_rooms"]==0 else False
                            #agregar los que pasaron la validacion
                            if bandLength == True and bandDiscount == True and bandLimitSales == True and bandFreeRooms==True:
                                filter_restriction = list(filter(lambda elem_r: elem_r.id_promotion == itx["idop_promotions"], data_pro_rest))
                                inf_restriction = list(filter(lambda elem_r: elem_r['iddef_restriction'] == filter_restriction[0].id_restriction, data_restrictions))
                                if itx["free_rooms"] == 1:
                                    id_restriction_apply = FilterPublic.validate_restrictions(self,inf_restriction,date_start,date_end,booking_date,include_free_room,band_free_room=True)
                                    if len(id_restriction_apply) > 0:
                                        result_fortmat = FilterPublic.format_promotion(self,itx,data_pro_rate,id_property,\
                                        inf_restriction[0],date_start,date_end,booking_date,booking_time)
                                        data.append(result_fortmat)
                                else:
                                    result_fortmat = FilterPublic.format_promotion(self,itx,data_pro_rate,id_property,\
                                    inf_restriction[0],date_start,date_end,booking_date,booking_time)
                                    data.append(result_fortmat)
                        data.sort(key=lambda x: x.get("priority"),reverse=False)
        
        return data
    
    #generar rango de fechas
    def range_dates_booking(self,date_start,date_end):
        for n in range(int ((date_end - date_start).days+1)):
            yield date_start + dates.timedelta(days=n)

    #obtener rango de fechas validas
    def get_list_range(self,data_dates,option,date_start,date_end):
        if isinstance(date_start,str):
            date_start = dt.strptime(date_start,'%Y-%m-%d').date()
        if isinstance(date_end,str):
            date_end = dt.strptime(date_end,'%Y-%m-%d').date()
        list_dates = []
        for itm_date in FilterPublic.range_dates_booking(self,date_start,date_end):
            for travel_window in data_dates:
                date_format = itm_date.strftime("%Y-%m-%d")
                if int(option) == 0:
                    list_dates.append(date_format)
                elif int(option) == 1:
                    if date_format >= travel_window["start_date"] and date_format <= travel_window["end_date"]:
                        list_dates.append(date_format)
                elif int(option) == 2:
                    if date_format < travel_window["start_date"] or date_format > travel_window["end_date"]:
                        list_dates.append(date_format)

        return list_dates

    #validar fechas restricciones
    def validate_restrictions(self,data_restrictions,date_start,date_end,booking_date,include_free_room,band_free_room=False):
        restrictions = []

        for item in data_restrictions:
            band_travel, band_booking = True, False
            if include_free_room == True and band_free_room ==True:
                band_travel = False
                if int(item["travel_window_option"]) == 0:
                    band_travel = True
                elif int(item["travel_window_option"]) == 1:
                    band_travel = any(x["start_date"] <= date_start and x["end_date"] >= date_end for x in item["travel_window"])
                elif int(item["travel_window_option"]) == 2:
                    band_travel = not any(x["start_date"] <= date_start and x["end_date"] >= date_end for x in item["travel_window"])
            if int(item["booking_window_option"]) == 0:
                band_booking = True
            elif int(item["booking_window_option"]) == 1:
                band_booking = any(booking_date >= y["start_date"] and booking_date <= y["end_date"] for y in item["booking_window_dates"])
            elif int(item["booking_window_option"]) == 2:
                band_booking = not any(booking_date >= y["start_date"] and booking_date <= y["end_date"] for y in item["booking_window_dates"])
            if band_travel == True and band_booking == True:
                restrictions.append(item["iddef_restriction"])

        return restrictions

    def format_promotion(self,itx,data_pro_rate,id_property,inf_restriction,date_start,date_end,booking_date,booking_time):
        priority_weight = 0
        list_free = []
        to_discount = {
            "rates_rooms_avail": [ \
            { "rateplan":promotion_ele.id_rateplan,
            "rooms":promotion_ele.rate_plan_rooms }\
            for promotion_ele in data_pro_rate \
            if promotion_ele.id_property == id_property\
            if promotion_ele.id_promotion == itx["idop_promotions"]],
            "free":[],
            "idop_promotions": itx["idop_promotions"],
            "length_of_stay": itx["length_of_stay"],
            "booking_window_dates":[],
            "travel_window":[],
            "code":itx["code"],
            "abs_value":0.0,
            "per_value":0.0,
            "priority":0,
            "apply_once":False,
            "apply_dates":{
                "dates_travel":[],
                "dates_booking":"1900-01-01",
                "times_booking":"23:59"
            },
            "timer_config":{
                "timer":itx["timer"],
                "days_offset":itx["days_offset"],
                "time_offset":itx["time_offset"]
            },
            "percent_cross_out":itx["percent_cross_out"]
        }
        to_discount["booking_window_dates"] = inf_restriction["booking_window_dates"]
        to_discount["travel_window"] = inf_restriction["travel_window"]
        to_discount["apply_dates"]["dates_travel"] = sorted(set(FilterPublic.get_list_range(self,inf_restriction["travel_window"],inf_restriction["travel_window_option"],date_start,date_end)))
        if int(inf_restriction["booking_window_option"]) == 1:
            for itm_date in inf_restriction["booking_window_dates"]:
                if booking_date <= itm_date["end_date"]:
                    to_discount["apply_dates"]["dates_booking"] = itm_date["end_date"]
            if len(inf_restriction["booking_window_times"]) > 0:
                booking_time = booking_time.strftime("%H-%M")
                for itm_date in inf_restriction["booking_window_times"]:
                    if booking_time <= itm_date["end_time"]:
                        to_discount["apply_dates"]["times_booking"] = itm_date["end_time"]
        if itx["partial_aplication"]==1:
            to_discount["apply_once"]=True
        if itx["free_childs"] == 1:
            #La promocion incluye niños gratis
            for childs in itx["free_childs_conditions"]:
                priority_weight += 3
                free={
                    "type":1,
                    "min":childs["age_id"],
                    "max":childs["free"],
                    "value":0
                }
                list_free.append(free)
        if itx["free_nights"] == 1:
            #La promocion incluye noches gratis
            priority_weight += 4
            free={
                "type":2,
                "min":itx["free_nights_conditions"]["free"],
                "max":itx["free_nights_conditions"]["paid"],
                "value":itx["free_nights_conditions"]["apply_once"]
            }
            list_free.append(free)
        if itx["free_rooms"] == 1:
            #La promocion incluye cuartos gratis
            priority_weight += 5
            free={
                "type":3,
                "min":itx["free_rooms_conditions"]["free"],
                "max":itx["free_rooms_conditions"]["paid"],
                "value":itx["free_rooms_conditions"]["apply_once"]
            }
            list_free.append(free)
        percent_discount = 1.0
        absolute_value = 0
        for discounts in itx["discounts"]:
            if discounts["format"] == 2:
                #La promocion realiza un descuento en porcentajes
                priority_weight += 2
                percent_discount *= (1-(discounts["value"]/100))
            elif discounts["format"] == 1:
                #La promocion realiza un descuento en valor absoluto(Dolares)
                priority_weight += 1
                absolute_value += discounts["value"]
        to_discount["per_discount"]=(1 - percent_discount)
        to_discount["abs_discount"] = absolute_value
        to_discount["priority"]=priority_weight
        to_discount["free"]=list_free
    
        return to_discount
