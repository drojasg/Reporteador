from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from config import db,base
from models.promotions import Promotions as Model, PromotionsSchema as ModelSchema
from models.promotion_rateplan import PromotionRateplan as PRModel, PromotionRateplanSchema as PRModelSchema
from models.rateplan import RatePlan as RPModel
from models.promotion_restriction import PromotionRestriction as PResModel, PromotionRestrictionSchema as PResModelSchema
from models.promotion_discount_type import PromotionDiscountType as PDTModel
from models.property import Property as PModel, PropertySchema as Pschema
from models.book_promotion import BookPromotion as BPModel, BookPromotionSchema as BPModelSchema
from resources.rates.RatesHelper import RatesFunctions as funtions
from resources.restriction.restricctionHelper import RestricctionFunction as functionsRes
from common.util import Util
from operator import itemgetter
from sqlalchemy import or_, and_, func
import datetime, decimal
import json
from datetime import datetime as dt

class PromotionsFunction():
    #Metodo para actualizar o crear Promotions
    @staticmethod
    def update_promotions(json_data,id_promotions):
        try:
            data = []
            schema = ModelSchema(exclude=Util.get_default_excludes())
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            #Formateo de nodo de detail_restriction
            if len(json_data["detail_restriction"]) > 0:
                for x in json_data["detail_restriction"]:
                    x["iddef_restriction_by"] = 7
                    x["iddef_restriction_type"] = 4

            if int(id_promotions) == 0:
                Data = Model()
                Data.name = json_data["name"]
                Data.code = json_data["code"]
                Data.discounts = json_data["discounts"]
                bandLength = False
                if len(Data.discounts) > 0:
                    for itm in Data.discounts:
                        infoType = PromotionsFunction.get_promotion_discount_type(itm["type"])
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
                Data.estado = 1
                Data.usuario_creacion = user_name
                db.session.add(Data)
                db.session.commit()
                data = schema.dump(Data)
                id_promotion = Data.idop_promotions
                if len(json_data["rate_plans"]) > 0:
                    rate_plans = PromotionsFunction.update_promotion_rateplan(json_data["rate_plans"],id_promotion)
                if len(json_data["detail_restriction"]) > 0:
                    detail_restriction = PromotionsFunction.update_promotion_restriction(json_data["detail_restriction"],id_promotion)            
            else:
                #data = None
                model = Model.query.get(id_promotions)
                if request.json.get("name") != None:
                    model.name = json_data["name"]
                if request.json.get("code") != None:
                    model.code = json_data["code"]
                bandLength = False
                if request.json.get("discounts") != None:
                    model.discounts = json_data["discounts"]
                    if len(model.discounts) > 0:
                        for itm in model.discounts:
                            infoType = PromotionsFunction.get_promotion_discount_type(itm["type"])
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
                if request.json.get("estado") != None:
                    model.estado = json_data["estado"]
                model.usuario_ultima_modificacion = user_name
                db.session.commit()
                data = schema.dump(model)
                if len(json_data["rate_plans"]) > 0:
                    rate_plans = PromotionsFunction.update_promotion_rateplan(json_data["rate_plans"],id_promotions)
                if len(json_data["detail_restriction"]) > 0:
                    detail_restriction = PromotionsFunction.update_promotion_restriction(json_data["detail_restriction"],id_promotions)
        
        except Exception as ex:
            raise Exception("Error al crear/actualizar promotions: "+str(ex))

        return data
    
    #Metodo para actualizar o crear promotion-rateplan
    @staticmethod
    def update_promotion_rateplan(json_data,id_promotion):
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

    #Metodo para actualizar o crear promotion-rateplan
    @staticmethod
    def update_promotion_restriction(json_data,id_promotion):
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

    #Metodo para obtener las restrincciones
    @staticmethod
    def get_detail_restriction(id_promotion):
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
    @staticmethod
    def get_promotion_rateplan(id_promotion):
        result_properties = []
        data_properties = PModel.query.filter_by(estado=1).all()
        if len(data_properties) > 0:
            for item_property in data_properties:
                id_property = item_property.iddef_property
                result_plans = []
                result_plans = PromotionsFunction.get_property_rateplan(id_promotion,id_property)
                obj_property = {
                    "iddef_property":item_property.iddef_property,
                    "rate_plans":result_plans
                }
                result_properties.append(obj_property)

        return result_properties

    #Metodo para consultar rateplan por propiedad
    @staticmethod
    def get_property_rateplan(id_promotion,id_property):
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
    @staticmethod
    def get_promotion_discount_type(id_type):
        data=None

        data_type = PDTModel.query.filter_by(iddef_promotion_discount_type=id_type, estado=1).first()
        
        if data_type is not None:
            data = data_type

        return data
    
    """ #Metodo para obtener book_promotion
    @staticmethod
    def get_book_promotion(id_book=None,id_promotion=None,isAll=True,count=True):
        conditions = []

        if id_book is not None:
            conditions.append(BPModel.idbook_hotel==id_book)
        if id_promotion is not None:
            conditions.append(BPModel.idbook_promotion==id_promotion)
        if isAll:
            if count:
                data_promotions = BPModel.query.filter(and_(*conditions,BPModel.estado==1)).count()
            else:
                data_promotions = BPModel.query.filter(and_(*conditions,BPModel.estado==1)).all()
        else:
            data_promotions = BPModel.query.filter(and_(*conditions,BPModel.estado==1)).first()

        return data_promotions

    #Metodo para obtener promotions para reserva
    @staticmethod
    def get_promotions_by_booking(date_start=None,date_end=None,market=None,\
    hotel=None,lang_code=None,total_rooms=None):
        data = []
        if total_rooms == None:
            raise Exception("Rooms no encontrado, favor de verificar")
        #Obtenemos informacion de los cuartos seleccionados
        totalRooms = 0
        totalAdults = 0
        totalChildrens = 0
        for x in total_rooms:
            totalRooms += 1
            adults = x["adults"]
            totalAdults += adults
            childrens = x["children"]
            totalChildrens += childrens
        #Obtenemos informacion del mercado seleccionado
        if market == None:
            market = "CR"
        msData = funtions.getMarketInfo(market)
        id_market = msData.iddef_market_segment
        #Obtenemos informacion del mercado seleccionado
        if hotel != None:
            hotel = funtions.getHotelInfo(hotel)
            id_property = hotel.iddef_property
        #Obtenemos informacion del mercado seleccionado
        if lang_code == None:
            lang_code = "EN"
        #Obtenemos fecha actual
        booking_date = dt.now()
        #Obtenemos informacion de las fechas seleccionadas
        if date_start != None and date_end !=None:
            totalNigths = date_end - date_start
            totalNigths = totalNigths.days
            totalDays = date_start - booking_date
            totalDays = totalDays.days
        #Obtenemos informacion de las restrincciones
        data_restrictions = functionsRes.getRestrictionDetails(travel_window_start=date_start.strftime("%Y-%m-%d"), \
        travel_window_end=date_end.strftime("%Y-%m-%d"), restriction_by=7, restriction_type=4, market_targeting=id_market)
        if len(data_restrictions) > 0:
            #Se extraen los ids de restricciones
            ids_restrictions = [restriction_elem["iddef_restriction"] for restriction_elem in data_restrictions] #print('ids_restrictions', ids_restrictions)
            #Se obtine informacion de las promociones
            data_pro_rest = PResModel.query.filter(PResModel.id_restriction.in_(ids_restrictions), PResModel.estado==1).all()
            if len(data_pro_rest) > 0:
                ids_promotions = [promotion_elem.id_promotion for promotion_elem in data_pro_rest] #print('restrictions_ids_promotions', ids_promotions)
                #Se obtiene informacion de las promociones                
                ids_rateplans = [rateplan_elem["idop_rate_plan"] for rateplan_elem in total_rooms]
                ids_rooms = [room_elem["iddef_room_type"] for room_elem in total_rooms]
                id_room = ''+str(ids_rooms)+''
                data_pro_rate = PRModel.query.filter(PRModel.id_promotion.in_(ids_promotions),\
                PRModel.id_property==id_property,PRModel.id_rateplan.in_(ids_rateplans),\
                func.json_contains(PRModel.rate_plan_rooms,id_room),PRModel.estado==1).all()
                if len(data_pro_rate) > 0:
                    result_data = []
                    result_data2 = []
                    result_data3 = []
                    ids_promotion = [promotion_ele.id_promotion for promotion_ele in data_pro_rate] #print('rateplans_ids_promotion', ids_promotion)
                    #Validacion children, nigth y rooms
                    dataPromotions = PromotionsFunction.get_promotions(ids_promotion=ids_promotion,\
                    totalChildrens=totalChildrens,totalNigths=totalNigths,totalRooms=totalRooms)
                    if len(dataPromotions) > 0:
                        for itx in dataPromotions:
                            if itx["free_childs"] != 0:
                                totalmax = 0
                                for xchild in itx["free_childs_conditions"]:
                                    tmax = xchild["max"]
                                    totalmax += tmax
                                if totalChildrens <= totalmax:
                                    result_data.append(itx)
                            else:
                                result_data.append(itx)
                    #Validacion length
                    if len(result_data) > 0:
                        for itx4 in result_data:
                            if itx4["length_of_stay"]["maxLOS"]["inherit"] != 0 and itx4["length_of_stay"]["minLOS"]["inherit"] !=0:
                                if totalNigths <= itx4["length_of_stay"]["maxLOS"]["value"] and totalNigths >= itx4["length_of_stay"]["minLOS"]["value"]:
                                    result_data2.append(itx4)
                            elif itx4["length_of_stay"]["maxLOS"]["inherit"] == 0 and itx4["length_of_stay"]["minLOS"]["inherit"] !=0:
                                if totalNigths >= itx4["length_of_stay"]["minLOS"]["value"]:
                                    result_data2.append(itx4)
                            elif itx4["length_of_stay"]["maxLOS"]["inherit"] != 0 and itx4["length_of_stay"]["minLOS"]["inherit"] ==0:
                                if totalNigths <= itx4["length_of_stay"]["maxLOS"]["value"]:
                                    result_data2.append(itx4)
                    #Validacion limit_sales
                    if len(result_data2) > 0:
                        for itx5 in result_data2:
                            if itx5["limit_sales"] != 0:
                                #Obtenemos informacion de book_promotion
                                total_book = PromotionsFunction.get_book_promotion(id_promotion=itx5["idop_promotions"])
                                if int(total_book) > 0:
                                    if total_book < itx5["limit_sales_count"]:
                                        result_data3.append(itx5)
                                else:
                                    result_data3.append(itx5)
                            else:
                                result_data3.append(itx5)
                    #Validacion discount
                    if len(result_data3) > 0:
                        bandDiscount = False
                        for itx6 in result_data3:
                            for typeX in itx6["discounts"]:
                                if typeX["type"] == 1:
                                    bandDiscount = True
                                elif typeX["type"] == 2:
                                    if totalDays >= typeX["days"]:
                                        bandDiscount = True
                                    else:
                                        bandDiscount = False
                                elif typeX["type"] == 3:
                                    if totalDays <= typeX["days"]:
                                        bandDiscount = True
                                    else:
                                        bandDiscount = False
                                elif typeX["type"] == 4:
                                    if totalNigths >= typeX["days"]:
                                        bandDiscount = True
                                    else:
                                        bandDiscount = False
                            if bandDiscount is True:
                                data.append(itx6)
                    #if len(data) > 0:
                        #ids_prt_filts = [pr_ele["idop_promotions"] for pr_ele in data]
        return data

    @staticmethod
    def get_promotions(ids_promotion=None,totalChildrens=None,totalNigths=None,totalRooms=None):
        schema = ModelSchema(exclude=Util.get_default_excludes())
        result = []
        conditions = []
        conditionsOr = []
        conditionsAnd = []
        conditionsAnd2 = []
        conditionsOr2 = []
        conditionsAnd22 = []
        conditionsAnd23 = []
        if ids_promotion is not None:
            conditions.append(Model.idop_promotions.in_(ids_promotion))
        if totalChildrens is not None:
            if int(totalChildrens) > 0:
                conditions.append(Model.free_childs==1)
            else:
                conditions.append(Model.free_childs==0)
        if totalNigths is not None:
            conditionsAnd.append(Model.free_nights==0)
            conditionsOr.append(and_(*conditionsAnd))
            conditionsAnd2.append(Model.free_nights==1)
            conditionsAnd2.append(func.json_extract(Model.free_nights_conditions, '$.paid') <= totalNigths)
            conditionsOr.append(and_(*conditionsAnd2))
            conditions.append(or_(*conditionsOr))
        if totalRooms is not None:
            conditionsAnd22.append(Model.free_rooms==0)
            conditionsOr2.append(and_(*conditionsAnd22))
            conditionsAnd23.append(Model.free_rooms==1)
            conditionsAnd23.append(func.json_extract(Model.free_rooms_conditions, '$.paid') <= totalRooms)
            conditionsOr2.append(and_(*conditionsAnd23))
            conditions.append(or_(*conditionsOr2))
        data_promotions = Model.query.filter(and_(*conditions,Model.estado==1)).all()
        if len(data_promotions) > 0:
            result = schema.dump(data_promotions, many=True)

        return result """