from flask import Flask, request, jsonify, make_response
from flask_restful import Resource
from marshmallow import ValidationError
from config import db
from models.age_code import AgeCode as agcModel
from models.age_range import AgeRange as agrModel
from models.market_segment import MarketSegment as mkModel
from models.country import Country as cnModel
from models.rateplan import RatePlan as rpModel, RatePlanSchema as rtSchema
from models.rateplan_prices import RatePlanPrices as rtpModel, RatePlanPricesSchema as rtpSchema
from models.room_type_category import RoomTypeCategory as rtcModel, RoomTypeCategorySchema as rtcSchema
from models.rate_plan_rooms import RatePlanRooms as rtprModel, RatePlanRoomsSchema as rtprSchema
from models.property import Property as prModel, PropertySchema as prSchema
from models.category_type_pax import CategoryTypePax as ctpModel, CategoryTypePaxSchema as ctpSchema
from models.rates_promotions import RatesPromotions as rpprModel, RatesPromotionsSchema as rpprSchema
from models.cross_out_config import CrossOutConfigSchema as cocModelSchema, CrossOutConfig as cocModel
from models.sistemas import SistemasSchema as sModelSchema, Sistemas as sModel
from models.crossout_rate_plan import CrossoutRatePlanSchema as crpModelSchema, CrossoutRatePlan as crpModel
from models.rateplan_property import RatePlanProperty as rppModel
from models.media_property import MediaProperty as MedPropModel
from models.media import Media as MedModel
from models.media_group import MediaGroup as MedGruModel
from models.media_type import MediaType as MedTypModel
from models.text_lang import TextLang as TextLModel
from models.policy import Policy as poModel
from models.rateplan_policy import RatePlanPolicy as rtpoModel
from models.rateplan_restriction import RatePlanRestriction as rpresModel
from models.crossout_restrictions import CrossoutRastriction as crModel
from models.book_promotion import BookPromotion as BPModel, BookPromotionSchema as BPModelSchema
from models.promotion_restriction import PromotionRestriction as PResModel, PromotionRestrictionSchema as PResModelSchema
from models.promotion_rateplan import PromotionRateplan as PRModel, PromotionRateplanSchema as PRModelSchema
from models.promotions import Promotions as ProModel, PromotionsSchema as ProModelSchema
from models.promo_code import PromoCode as pcModel, GetPromoCodeSchema as GetPMModelSchema
from models.promo_code_date import PromoCodeDate as pcdModel
from models.promo_code_rateplan import PromoCodeRatePlan as pcrpModel, PromoCodeRatePlanSchema as pcrpSchema
from models.promo_code_type_amount import PromoCodeTypeAmount as pctaModel
from models.promo_code_targeting_country import PromoCodeTargetingCountry as pctcModel
from models.book_promo_code import BookPromoCode as bpcModel
from models.brand import Brand as bModel
from resources.exchange_rate.exchange_rate_service import ExchangeRateService as funtionsExchange
from resources.restriction.restricctionHelper import RestricctionFunction as resFuntions
from resources.restriction.restriction_helper_v2 import Restrictions as resFuntions2
from resources.promo_code.promocodeHelper import PromoCodeFunctions as vauchersFunctions
from resources.policy.policyHelper import PolicyFunctions as funtionsPolicy
from common.util import Util
from operator import itemgetter
from sqlalchemy import or_, and_, func
from datetime import datetime, timedelta
import datetime as dates
import types
import requests
import json
from datetime import datetime
import copy
from .rates_helper_v2 import Search

class RatesFunctions():

    @staticmethod
    def get_policy_by_rateplan(idRateplan, booking_start_date, lang_code="EN", refundable = False):

        data = {}

        cancel_policy = ""
        guarantee_policy = ""
        tax_policy = ""        
        #booking_start_date = dates.datetime(booking_start_date.year, booking_start_date.month, booking_start_date.day)
        
        rate_plan_policies = poModel.query.join(rtpoModel, poModel.iddef_policy == rtpoModel.iddef_policy)\
        .filter(rtpoModel.idop_rateplan==idRateplan, rtpoModel.estado==1, poModel.estado==1).all()

        cancelacionList = [ rppol for rppol in rate_plan_policies if rppol.iddef_policy_category == 1]
        garantiaList = [rppol for rppol in rate_plan_policies if rppol.iddef_policy_category == 2]
        taxList = [rppol for rppol in rate_plan_policies if rppol.iddef_policy_category == 3]
        
        if len(cancelacionList) > 0 :
            for cancelItem in cancelacionList:
                policy_detail_cancel = None
                
                #check if is required refundable cancellation policy
                if refundable:
                    policy_detail_cancel = next((item for item in cancelItem.policy_cancel_penalties if item.estado == 1 \
                    and item.is_base == 0 and item.is_refundable == 1 \
                    and (booking_start_date >= item.start_date and booking_start_date <= item.end_date)), None)
                
                #if not found refundable or refundable is false, search for dates
                if not policy_detail_cancel:
                    policy_detail_cancel = next((item for item in cancelItem.policy_cancel_penalties if item.estado == 1 \
                    and item.is_base == 0 and item.is_refundable == 0 \
                    and (booking_start_date >= item.start_date and booking_start_date <= item.end_date)), None)
                
                #if policy was found, get the lang description and break loop
                if policy_detail_cancel:
                    if lang_code.upper() != "ES":
                        cancel_policy = policy_detail_cancel.description_en
                    else:
                        cancel_policy = policy_detail_cancel.description_es
                    break
                else:
                    #in other case, looking for base cancellation and break loop
                    policy_detail_cancel = next((item for item in cancelItem.policy_cancel_penalties if item.estado == 1 \
                        and item.is_base == 1), None)
                    if policy_detail_cancel:
                        if lang_code.upper() != "ES":
                            cancel_policy = policy_detail_cancel.description_en
                        else:
                            cancel_policy = policy_detail_cancel.description_es
                        break
        
        if len(garantiaList) > 0:
            for item in garantiaList:
                for range_date in item.available_dates:
                    start_date = dates.datetime.strptime(range_date.get("start_date"), '%Y-%m-%d')
                    end_date = dates.datetime.strptime(range_date.get("end_date"), '%Y-%m-%d')
                    if booking_start_date >= start_date.date() and booking_start_date <= end_date.date():
                        if lang_code.upper() != "ES":
                            guarantee_policy = item.policy_guarantees[0].description_en
                        else:
                            guarantee_policy = item.policy_guarantees[0].description_es
                        break
            else:
                if lang_code.upper() != "ES":
                    guarantee_policy = garantiaList[0].policy_guarantees[0].description_en
                else:
                    guarantee_policy = garantiaList[0].policy_guarantees[0].description_es
        
        if len(taxList):
            for item in taxList:
                for range_date in item.available_dates:
                    start_date = dates.datetime.strptime(range_date.get("start_date"), '%Y-%m-%d')
                    end_date = dates.datetime.strptime(range_date.get("end_date"), '%Y-%m-%d')
                    if booking_start_date >= start_date.date() and booking_start_date <= end_date.date():
                        if lang_code.upper() != "ES":
                            tax_policy = item.policy_tax_groups[0].description_en
                        else:
                            tax_policy = item.policy_tax_groups[0].description_es
                        break
            else:
                if lang_code.upper() != "ES":
                    tax_policy = taxList[0].policy_tax_groups[0].description_en
                else:
                    tax_policy = taxList[0].policy_tax_groups[0].description_es

        data = {
            "cancel_policy":cancel_policy,
            "guarantee_policy":guarantee_policy,
            "tax_policy":tax_policy
        }

        return data
       
    @staticmethod
    def getBrandInfo(brand_code):

        data = bModel.query.filter(bModel.estado == 1, \
        bModel.code == brand_code).first()

        if data is None:
            raise Exception('Codigo de brand invalido, favor de verificar el codigo {0:s}'.format(brand_code))

        return data
    
    @staticmethod
    def getHotelInfo(property_code):

        data = prModel.query.filter(prModel.estado == 1, \
        prModel.property_code == property_code).first()

        if data is None:
            raise Exception('Codigo de propiedad invalido, favor de verificar el codigo {0:s}'.format(property_code))

        return data

    @staticmethod
    def getMarketInfo(market_code, language="en"):
        
        data = mkModel.query.join(cnModel,cnModel.idmarket_segment==mkModel.iddef_market_segment\
        ).filter(mkModel.estado==1, cnModel.country_code==market_code, cnModel.estado==1).first()

        if data is None:
            raise Exception(Util.t(language, "market_code_not_found"))
        
        return data
    
    @staticmethod
    def getRateplanPropertyRoomInfo(property_id,rateplan_id,roomtype_id):
        
        data = rppModel.query.join(rtprModel,rtprModel.id_rate_plan==rppModel.id_rateplan\
        ).filter(rppModel.estado==1, rtprModel.estado==1,\
        rppModel.id_property==property_id,\
        rppModel.id_rateplan==rateplan_id,\
        rtprModel.id_room_type == roomtype_id).first()

        if data is None:
            raise Exception('Rate Plan no encontrado(asigado), favor de verificar el id: ' + str(rateplan_id))
        
        return data

    @staticmethod
    def getRateplanInfo(rateplanId=None,rate_code=None,property_id=None,date_start=None,\
    date_end=None,market_id=None,bookin_window=False,only_one=True,only_rateplan=False,\
    country=None,validate_lead_time=False,roomid=None,validate_estado=True,language='en'):
        
        conditions = []

        if rate_code == "":
            raise Exception("Campo Rate Plan Code Vacio Favor de Validar")
        
        if property_id is None:
            raise Exception("Se necesita el codigo del la propiedad")

        if only_rateplan == False:
            #Se revisa su hay un "General_Restriction" de tipo "Apply"
            if date_start is not None and date_end is not None and market_id is not None:
                # restriction_details_apply = resFuntions.getRestrictionDetails(travel_window_start=date_start.strftime("%Y-%m-%d"), \
                #     travel_window_end=date_end.strftime("%Y-%m-%d"), restriction_by=6, restriction_type=4, market_targeting=market_id,
                #     geo_targeting_country=country)
                obj = resFuntions2(travel_window_start=date_start.strftime("%Y-%m-%d"), \
                    travel_window_end=date_end.strftime("%Y-%m-%d"), restriction_by=6, restriction_type=4, market_targeting=market_id,
                    geo_targeting_country=country)
                restriction_details_apply = obj.get_restriction_details()
            else:
                restriction_details_apply = []

            if restriction_details_apply is None or len(restriction_details_apply) == 0:
                raise Exception(Util.t(language, "rateplan_not_found"))
            else:
                list_ids_restrictions = [restriction_elem["iddef_restriction"] for restriction_elem in restriction_details_apply]

        if validate_estado == True:
            conditions.append(rpModel.estado==1)
            
        conditions.append(rpModel.id_sistema==1)
        conditions.append(rppModel.id_property==property_id)

        if rateplanId is not None:
            conditions.append(rpModel.idop_rateplan==rateplanId)

        if rate_code is not None:
            conditions.append(rpModel.code==rate_code)

        # if bookin_window:
        #     today = datetime.today().date()
        #     conditions.append(rpModel.booking_window_start<=today)
        #     conditions.append(rpModel.booking_window_end>=today)

        # if market_id is not None:
        #     conditions.append(rpModel.id_market_segment==market_id)

        # if date_start is not None:
        #     conditions.append(rpModel.travel_window_start<=date_start)

        # if date_end is not None:
        #     conditions.append(rpModel.travel_window_end>=date_end)

        # if only_one:
        #     data = rpModel.query.join(rppModel, rppModel.id_rateplan==\
        #     rpModel.idop_rateplan).filter(and_(*conditions,rppModel.estado==1)).all()

        #     if only_rateplan == False:
        #         data_rateplan_restriction = rpresModel.query.filter(rpresModel.idop_rateplan==data.idop_rateplan, rpresModel.iddef_restriction.in_(list_ids_restrictions), rpresModel.estado==1).all()
        #     else:
        #         data_rateplan_restriction = []
        # else:
        data = rpModel.query.join(rppModel, rppModel.id_rateplan==\
        rpModel.idop_rateplan).filter(and_(*conditions,rppModel.estado==1)).all()

        #Si el roomid existe se valida que el rateplan este mapeado con dicha habitacion
        if roomid is not None:
            rateplans_by_room = rpModel.query.join(rtprModel, rtprModel.id_rate_plan==\
            rpModel.idop_rateplan).filter(and_(rtprModel.id_room_type==roomid\
            ,rtprModel.estado==1)).all()

            rateplans_room = [element.idop_rateplan for element in rateplans_by_room]

            aux_rateplan_list = []
            for rateplans in data:
                if rateplans.idop_rateplan in rateplans_room:
                    aux_rateplan_list.append(rateplans)
            
            data = aux_rateplan_list
        
        if only_rateplan == False:
            list_ids_rateplans = [rateplan_elem.idop_rateplan for rateplan_elem in data]

            data_rateplan_restriction = rpresModel.query.filter(rpresModel.idop_rateplan.in_(list_ids_rateplans), rpresModel.iddef_restriction.in_(list_ids_restrictions), rpresModel.estado==1).all()
            ids_rateplans_filtered = [elem_rpr.idop_rateplan for elem_rpr in data_rateplan_restriction]

            data = [rateplan_elem for rateplan_elem in data if rateplan_elem.idop_rateplan in ids_rateplans_filtered]
        else:
            data_rateplan_restriction = []

        #Se valida el valor "lead_time" con la fecha de booking
        if validate_lead_time:
            new_data_list = []
            today = datetime.utcnow().date()
            for data_index, data_value in enumerate(data):
                date_booking_limit = date_start - timedelta(days=data_value.lead_time)
                if today <= date_booking_limit:
                    new_data_list.append(data[data_index])
            #Se sustituyen datos de variable data
            data = new_data_list

        if only_one and len(data) >= 1:
            data = data[0]

        if only_rateplan == False and (data is None or len(data_rateplan_restriction)==0):
            raise Exception(Util.t(language, "rateplan_not_found"))
        elif only_rateplan and data is None:
            raise Exception(Util.t(language, "rateplan_not_found"))

        return data

    @staticmethod
    def getPrices(property_id,rate_plan_id,room_type_id,pax_type_id,date_start,\
    date_end,order_desc=True):

        if order_desc is True:
            data = rtpModel.query.filter(and_(rtpModel.idproperty==property_id, \
            rtpModel.idrateplan==rate_plan_id, \
            rtpModel.idroom_type==room_type_id, \
            rtpModel.idpax_type==pax_type_id, rtpModel.estado==1, \
            or_(and_(rtpModel.date_start<=date_start, rtpModel.date_end>=date_end),\
            or_(rtpModel.date_start.between(date_start, date_end), \
            rtpModel.date_end.between(date_start, date_end))))).order_by(rtpModel.is_override.desc()).all()
        else:
            data = rtpModel.query.filter(and_(rtpModel.idproperty==property_id, \
            rtpModel.idrateplan==rate_plan_id, \
            rtpModel.idroom_type==room_type_id, \
            rtpModel.idpax_type==pax_type_id, rtpModel.estado==1, \
            or_(and_(rtpModel.date_start<=date_start, rtpModel.date_end>=date_end),\
            or_(rtpModel.date_start.between(date_start, date_end), \
            rtpModel.date_end.between(date_start, date_end))))).all()

        if data is None:
            raise Exception ("No se encontraron tarifas para las fechas selecionadas")

        data = sorted(data, key=lambda x: x.fecha_creacion, reverse=True)

        return data

    @staticmethod
    def getPrices_v2(property_id,rate_plan_id,room_type_id,pax_type_id,date_start,\
    date_end,overrides=True):

        if overrides is True:
            data = rtpModel.query.filter(and_(rtpModel.idproperty==property_id, \
            rtpModel.idrateplan==rate_plan_id, \
            rtpModel.idroom_type==room_type_id, \
            rtpModel.is_override == 1,\
            rtpModel.idpax_type==pax_type_id, rtpModel.estado==1, \
            or_(and_(rtpModel.date_start<=date_start, rtpModel.date_end>=date_end),\
            or_(rtpModel.date_start.between(date_start, date_end), \
            rtpModel.date_end.between(date_start, date_end))))).all()
        else:
            data = rtpModel.query.filter(and_(rtpModel.idproperty==property_id, \
            rtpModel.idrateplan==rate_plan_id, \
            rtpModel.idroom_type==room_type_id, \
            rtpModel.idpax_type==pax_type_id, rtpModel.estado==1, \
            or_(and_(rtpModel.date_start<=date_start, rtpModel.date_end>=date_end),\
            or_(rtpModel.date_start.between(date_start, date_end), \
            rtpModel.date_end.between(date_start, date_end))))).all()

        data = sorted(data, key = lambda x: (x.date_start, x.date_end))
        
        if data is None:
            raise Exception ("No se encontraron tarifas para las fechas selecionadas")

        return data


    @staticmethod
    def getCossOutConfig(property_id,sistema_id,rate_plan_id,date_start,date_end,only_crossout=False, use_booking_window=True, market=None, country=None):

        data = cocModel.query.join(sModel).join(crpModel).join(rpModel).join(rppModel, rpModel.idop_rateplan == rppModel.id_rateplan).\
        filter(and_(rppModel.id_property == property_id, \
        cocModel.id_sistema == sistema_id, \
        rpModel.idop_rateplan==rate_plan_id, cocModel.estado==1, crpModel.estado==1)).all()

        if only_crossout == False:
            # restriction_details_apply = resFuntions.getRestrictionDetails(useBooking=use_booking_window,travel_window_start=date_start.strftime("%Y-%m-%d"), \
            #     travel_window_end=date_end.strftime("%Y-%m-%d"), restriction_by=6, restriction_type=4, market_targeting=market, geo_targeting_country=country)
            obj = resFuntions2(useBooking=use_booking_window,travel_window_start=date_start.strftime("%Y-%m-%d"), \
                travel_window_end=date_end.strftime("%Y-%m-%d"), restriction_by=6, restriction_type=4, market_targeting=market, geo_targeting_country=country)
            restriction_details_apply = obj.get_restriction_details()
            list_ids_restrictions = [restriction_elem["iddef_restriction"] for restriction_elem in restriction_details_apply]

            if data is not None:
                list_ids_crossouts = [crossout_elem.idop_cross_out_config for crossout_elem in data]
            else:
                list_ids_crossouts = []

            data_crossout_restriction = crModel.query.filter(crModel.idop_crossout.in_(list_ids_crossouts), crModel.iddef_restriction.in_(list_ids_restrictions), crModel.estado==1).all()
            ids_crossouts_filtered = [elem_cor.idop_crossout for elem_cor in data_crossout_restriction]

            data = [crossout_elem for crossout_elem in data if crossout_elem.idop_cross_out_config in ids_crossouts_filtered]

            if len(data_crossout_restriction) == 0:
                is_valid = False
            else:
                is_valid = True
        else:
            is_valid = True

        if data is None:
            raise Exception ("No se encontraron porcentajes para las fechas selecionadas")
        elif is_valid == False:
            raise Exception ("No se encontraron Restrictions relacionados al Crossout")

        return data

    @staticmethod
    def getRoomTypeInfo(idproperty=None,room_type_code=None,property_name="",idroom_type=None,only_one=True):
        conditions = []

        if idproperty is not None:
            conditions.append(rtcModel.iddef_property==idproperty)

        if room_type_code is not None:
            conditions.append(rtcModel.room_code==room_type_code)

        if idroom_type is not None:
            conditions.append(rtcModel.iddef_room_type_category==idroom_type)

        if only_one:
            data = rtcModel.query.filter(and_(*conditions,rtcModel.estado==1)).first()
        else:
            data = rtcModel.query.filter(and_(*conditions,rtcModel.estado==1)).all()

        if data is None and idproperty is not None:
            raise Exception("Room Type {0:s} no encontrado para la propiedad {1:s}, favor de verificar que el tipo de habitacion exista".format(room_code,property_name))

        if data is None and idproperty is None:
            raise Exception("Room Type {0:s} no encontrado para ninguna propiedad {1:s}, favor de verificar que el tipo de habitacion exista" + str(room_code))
        
        return data

    @staticmethod
    def getRoomTypesForRatePlan(rate_plan_id,property_id,only_firts=False,all=False):
        
        data = None

        if all == False:
            rooms = rtcModel.query.join(rtprModel, \
            rtprModel.id_room_type == rtcModel.iddef_room_type_category \
            ).join(rpModel, rpModel.idop_rateplan == rtprModel.id_rate_plan\
            ).filter(rtprModel.id_rate_plan==rate_plan_id, \
            rtcModel.iddef_property == property_id, rtprModel.estado==1 \
            ).order_by(rtcModel.room_order.asc()).all()
        else:
            rooms = rtcModel.query.join(rtprModel, \
            rtprModel.id_room_type == rtcModel.iddef_room_type_category \
            ).join(rpModel, rpModel.idop_rateplan == rtprModel.id_rate_plan\
            ).filter(rtprModel.id_rate_plan==rate_plan_id, \
            rtcModel.iddef_property == property_id, rtprModel.estado==1 \
            ).order_by(rtcModel.room_order.asc()).all()

        if rooms is not None and len(rooms) > 0:
            if only_firts:
                data = rooms[0]
            else:
                data = rooms
        else:
            raise Exception("El rate plan aun no tiene habitaciones mapeadas")

        return data
        
    @staticmethod
    def getExtraAmount(prices):
        extra = 0
    
        if prices is not None :
            for price in prices:
                if price["pax_type"] == "EXT" and price["rate_exists"]:
                    extra = price["amount_final"]
                    
        return extra
    
    @staticmethod
    def getAdultsInfo(prices):
        
        response = []
        
        if prices is not None :
            for price in prices:
                
                #obtenemos la lista de tipos de pax activos para comparar
                ctpData = ctpModel.query.filter(ctpModel.estado==1, ctpModel.type==price["pax_type"], ctpModel.group_pax==price["group_pax"]).first()
                
                if ctpData is not None and ctpData.group_pax == "ADULT":
                    data = {
                        "type":ctpData.type,
                        "paxes": ctpData.pax_number,
                        "idPax_type":ctpData.iddef_category_type_pax,
                        "amount": price["amount_final"],
                        "promo":price["promotions"]
                    }
                    response.append(data)
        
        return response
    
    @staticmethod
    def getChildsInfo(prices):
        
        response = []
        
        if prices is not None :
            for price in prices:
                
                #obtenemos la lista de tipos de pax activos para comparar
                ctpData = ctpModel.query.filter(ctpModel.estado==1, ctpModel.type==price["pax_type"], ctpModel.group_pax==price["group_pax"]).first()
                
                if ctpData is not None and ctpData.group_pax == "CHILD":
                    data = {
                        "type":ctpData.type,
                        "paxes": ctpData.pax_number,
                        "idPax_type":ctpData.iddef_category_type_pax,
                        "amount": price["amount_final"],
                        "promo":price["promotions"]
                    }
                    response.append(data)
        
        return response

    @staticmethod
    def getStandarOcupancy(idProperty,id_room_type):
        
        StandarOcupancy = 0
        
        SOData = rtcModel.query.filter(rtcModel.estado==1, rtcModel.iddef_property==idProperty, rtcModel.iddef_room_type_category==id_room_type).first()
        
        if SOData is not None:
            StandarOcupancy = SOData.standar_ocupancy
        
        return StandarOcupancy
    
    @staticmethod
    def getIdPaxtype(cont_adults):
        
        idType = 0
        
        ctpData = ctpModel.query.filter(ctpModel.estado==1, ctpModel.pax_number==cont_adults, ctpModel.group_pax=="ADULT").first()
        
        if ctpData is not None:
            idType = ctpData.iddef_category_type_pax
        
        return idType
    
    @staticmethod
    def getPromotionsExtra(prices):
        response = []
        
        if prices is not None:
            res = [ promo["promotions"] for promo in prices if promo["pax_type"]=="EXT" ]
            if len(res) > 0:
                response = res[0]
        
        return response

    @staticmethod
    def calculateRate(percent_discount,amount=0):

        if percent_discount == 0:
            amount_final = 0
        else:
            percent_dif = 100 - percent_discount

            amount_final = (amount * 100) / percent_dif

        return round(amount_final,0)

    @staticmethod
    def calculatepercent(amount,amout_discount):

        if amout_discount == 0:        
            percent_total = 0
        else: 
            percent_apply = (amount * 100) / amout_discount
            percent_total = 100 - percent_apply

        return int(round(percent_total))

    @staticmethod
    def format_promotions(promotions):
        data = []

        list_discounts = []        
        for promo in promotions:

            priority_weight = 0
            
            to_discount = {
                "free":[],
                "code":promo["code"],
                "abs_value":0.0,
                "per_value":0.0,
                "priority":0,
                "apply_once":False
            }

            list_free = []

            if promo["partial_aplication"]==1:
                to_discount["apply_once"]=True

            if promo["free_childs"] == 1:
                #La promocion incluye niños gratis
                #+3
                for childs in promo["free_childs_conditions"]:
                    priority_weight += 3
                    free={
                        "type":1,
                        "min":childs["age_id"],
                        "max":childs["free"],
                        "value":0
                    }
                    list_free.append(free)
            
            if promo["free_nights"] == 1:
                #La promocion incluye noches gratis
                #+4
                priority_weight += 4
                free={
                    "type":2,
                    "min":promo["free_nights_conditions"]["free"],
                    "max":promo["free_nights_conditions"]["paid"],
                    "value":promo["free_nights_conditions"]["apply_once"]
                }
                list_free.append(free)

            if promo["free_rooms"] == 1:
                #La promocion incluye cuartos gratis
                #+5
                priority_weight += 5
                free={
                    "type":3,
                    "min":promo["free_rooms_conditions"]["free"],
                    "max":promo["free_rooms_conditions"]["paid"],
                    "value":promo["free_rooms_conditions"]["apply_once"]
                }
                list_free.append(free)

            percent_discount = 1.0
            absolute_value = 0
            for discounts in promo["discounts"]:

                if discounts["format"] == 2:
                    #La promocion realiza un descuento en porcentajes
                    #+2
                    priority_weight += 2
                    percent_discount *= (1-(discounts["value"]/100))

                elif discounts["format"] == 1:
                    #La promocion realiza un descuento en valor absoluto(Dolares)
                    #+1
                    priority_weight += 1
                    absolute_value += discounts["value"]

            #to_discount["per_discount"]=(1 - percent_discount)*100
            to_discount["per_discount"]=(1 - percent_discount)
            to_discount["abs_discount"] = absolute_value
            to_discount["priority"]=priority_weight
            to_discount["free"]=list_free

            list_discounts.append(to_discount)

        list_discounts.sort(key=lambda x: x.get("priority"),reverse=True)
        data = list_discounts
        
        return data

    #Valida si la promocion aplica para la habitacion y rateplan 
    @staticmethod
    def valide_room_promotion(price,promo_room_rates):
        apply_room = False

        for item in promo_room_rates:
            if price["rateplan"] == item["rateplan"]:
                if price["room"] in item["rooms"]:
                    apply_room = True
                    break

        return apply_room
        
    
    #price: object price per day
    #promotions: list of promotions to apply
    @staticmethod
    def select_rates_promotion(price_list):

        if len(price_list) >= 1:
            price_aux = copy.deepcopy(price_list[0])
        else:
            raise Exception("Lista de precios vacia, favor de verificar")

        day_position = 0
        for price in price_aux["price_per_day"]:
            cont_position = 1
            
            while cont_position < len(price_list):
                
                if price["amount"] >= price_list[cont_position]["price_per_day"][day_position]["amount"]:
                    price["amount"] = price_list[cont_position]["price_per_day"][day_position]["amount"]
                    price["promotions"] = price_list[cont_position]["price_per_day"][day_position]["promotions"]
                    price["promotion_amount"] = price_list[cont_position]["price_per_day"][day_position]["promotion_amount"]
                    price["amount_to_pms"] = price_list[cont_position]["price_per_day"][day_position]["amount_to_pms"]
                    
                    if price_aux["apply_room_free"] == False:
                        if price_list[cont_position]["apply_room_free"] == True:
                            price_aux["apply_room_free"] = price_list[cont_position]["apply_room_free"] 
                    
                    if price_aux["timer_on"] == False:
                        if price_list[cont_position]["timer_on"] == True:
                            price_aux["timer_on"]=price_list[cont_position]["timer_on"]
                            price_aux["date_end_promotion"]=price_list[cont_position]["date_end_promotion"]
                
                cont_position += 1
            
            day_position += 1

        return price_aux
    
    @staticmethod
    def apply_promotion(prices,promotions):
        
        #Se ordenan las habitaciones segun el total de sus tarifas diarias
        prices.sort(key=lambda x: x["total"])

        data = {
            "Code_Apply":[],
            "Prices":prices,
            "Total":0.00,
            "Subtotal":0.00,
            "generate_free_room":False
        }

        list_codes = []
        for discount in promotions:
            #Apply_Discounts
            total_promotion_discount = 0
            for free in discount["free"]:
                if free["type"]==1:
                    #niños gratis
                    pivot = free["min"]
                    pivot_free = free["max"]
                    for price in prices:
                        room_apply = RatesFunctions.valide_room_promotion(price,discount["rates_rooms_avail"])
                        price_discount = 0
                        if room_apply == True:                        
                            apply_minors = 0
                            apply=False
                            if pivot != 0:
                                agcData = agcModel.query.join(agrModel,\
                                agcModel.iddef_age_code == agrModel.iddef_age_code).filter(agrModel.iddef_property==price["property"],\
                                agrModel.estado==1,agcModel.iddef_age_code==pivot).all()

                                if len(agcData) >= 1:
                                    if price["paxes"] is not None:                                    
                                        age_code = [item.code for item in agcData]
                                        for paxes in price["paxes"].keys():
                                            if paxes in age_code:
                                                if price["paxes"][paxes] >= 1:
                                                    apply = True
                                                    break
                            elif pivot == 0:
                                apply = True

                            if apply == True:    
                                room_detail = rtcModel.query.get(price["room"])
                                if room_detail.acept_chd == 1 and price["minors"]>=1:

                                    while apply_minors < pivot_free and apply_minors < price["minors"]:
                                        discount_applied = 0
                                        for price_night in price["price_per_day"]:
                                            if price_night["amount"] > 0:
                                                date_str = datetime.strftime(price_night["efective_date"],"%Y-%m-%d")
                                                if date_str in discount["apply_dates"]["dates_travel"]:
                                                
                                                    child_data = RatesFunctions.getPrices(price["property"],\
                                                    price["rateplan"],price["room"],1,\
                                                    price_night["efective_date"],price_night["efective_date"])

                                                    if len(child_data) >= 1:
                                                        discount_applied = child_data[0].amount
                                                        price_night["amount"] -= child_data[0].amount
                                                        price_night["amount"] = round(price_night["amount"],0)
                                                        price_night["amount_to_pms"] = price_night["amount"]
                                                        total_promotion_discount += discount_applied
                                                        promo_detail = {
                                                            "id_promotion":discount["idop_promotions"],
                                                            "code":discount["code"],
                                                            "value_discount":discount_applied,
                                                            "crossout":discount["percent_cross_out"]
                                                        }
                                                        price_night["promotions"] = promo_detail
                                                        price_night["promotion_amount"] = discount_applied
                                                
                                        apply_minors += 1
                                        price_discount += discount_applied

                        price["total"] = round(price["total"]-price_discount,0)

                elif free["type"]==2:
                    #noches gratis
                    pivot = free["max"]
                    pivot_free = free["min"]
                    if free["value"]==0:
                        #Se aplica varias veces
                        for price in prices:
                            room_apply = RatesFunctions.valide_room_promotion(price,discount["rates_rooms_avail"])
                            
                            if room_apply == True:
                                nigths_cont = 0
                                apply_discount = False
                                free_nights_count = 0
                                price_discount = 0
                                for price_nigth in price["price_per_day"]:
                                    date_str = datetime.strftime(price_nigth["efective_date"],"%Y-%m-%d")
                                    if date_str in discount["apply_dates"]["dates_travel"]:

                                        if apply_discount == True:
                                            #price_nigth["amount_crossout"]=price_nigth["amount"]
                                            price_discount += price_nigth["amount"]
                                            price_nigth["amount"]=0.00
                                            price_nigth["amount_to_pms"] = price_nigth["amount"]
                                            total_promotion_discount += price_nigth["amount"]
                                            promo_detail = {
                                                "id_promotion":discount["idop_promotions"],
                                                "code":discount["code"],
                                                "value_discount":price_nigth["amount"],
                                                "crossout":discount["percent_cross_out"]
                                            }
                                            price_nigth["promotions"] = promo_detail
                                            price_nigth["promotion_amount"] = price_nigth["amount"]
                                            #price_nigth["percent_discount"]=100
                                            free_nights_count += 1
                                            if free_nights_count >= pivot_free:
                                                apply_discount = False                                
                                        else:
                                            nigths_cont +=1
                                            if nigths_cont >= pivot:
                                                apply_discount = True
                                                nigths_cont = 0 
                                                free_nights_count = 0

                                price["total"] = price["total"]-price_discount
                                #price["total_crossout"] = price["total_crossout"] + price_discount
                    else:
                        #Se aplica una sola ves
                        for price in prices:
                            room_apply = RatesFunctions.valide_room_promotion(price,discount["rates_rooms_avail"])
                            if room_apply == True:
                                nigths_cont = 0
                                apply_discount = False
                                free_nights_count = 0
                                price_discount = 0
                                for price_nigth in price["price_per_day"]:
                                    date_str = datetime.strftime(price_nigth["efective_date"],"%Y-%m-%d")
                                    if date_str in discount["apply_dates"]["dates_travel"]:

                                        if apply_discount == True:
                                            #price_nigth["amount_crossout"]=price_nigth["amount"]
                                            price_discount += price_nigth["amount"]
                                            price_nigth["amount"]=0.00
                                            price_nigth["amount_to_pms"] = price_nigth["amount"]
                                            total_promotion_discount += price_nigth["amount"]
                                            promo_detail = {
                                                "id_promotion":discount["idop_promotions"],
                                                "code":discount["code"],
                                                "value_discount":price_nigth["amount"],
                                                "crossout":discount["percent_cross_out"]
                                            }
                                            price_nigth["promotions"] = promo_detail
                                            price_nigth["promotion_amount"] = price_nigth["amount"]
                                            #price_nigth["percent_discount"]=100
                                            free_nights_count += 1
                                            if free_nights_count >= pivot_free:
                                                break                              
                                        else:
                                            nigths_cont +=1
                                            if nigths_cont >= pivot:
                                                apply_discount = True
                                                nigths_cont = 0 
                                                free_nights_count = 0

                                price["total"] = price["total"]-price_discount
                                #price["total_crossout"] = price["total_crossout"] + price_discount
                            
                elif free["type"]==3:
                    #cuartos gratis
                    #Se ordenan las habitaciones segun el total de sus tarifas diarias
                    #prices.sort(key=lambda x: x["total"])
                    pivot = free["max"]
                    pivot_free = free["min"]
                    rooms_cont = 0
                    apply_discount = False
                    free_room_count = 0
                    if free["value"]==0:

                        cont_room = 0
                        for rooms_rates in prices:
                            room_apply_aux = RatesFunctions.valide_room_promotion(rooms_rates,\
                            discount["rates_rooms_avail"])

                            #Si la habitacion es aplicable a la promocion 2x1, se coloca la bandera
                            rooms_rates["apply_room_free"] = room_apply_aux

                            #if room_apply == True:
                            #price_day = len(price["price_per_day"])
                            if apply_discount == True:
                                room_apply = RatesFunctions.valide_room_promotion(prices[cont_room],\
                                discount["rates_rooms_avail"])

                                if room_apply == True:
                                    #data["generate_free_room"] = False
                                    #prices[cont_room]["total_crossout"]=prices[cont_room]["total"]
                                    prices[cont_room]["total"]=0.00
                                    #prices[cont_room]["apply_room_free"] = True
                                    #prices[cont_room]["total_percent_discount"]=100
                                    for price_nigth in prices[cont_room]["price_per_day"]:
                                        #price_nigth["amount_crossout"]=price_nigth["amount"]
                                        total_promotion_discount += price_nigth["amount"]
                                        promo_detail = {
                                            "id_promotion":discount["idop_promotions"],
                                            "code":discount["code"],
                                            "value_discount":price_nigth["amount"],
                                            "crossout":discount["percent_cross_out"]
                                        }
                                        price_nigth["promotions"] = promo_detail
                                        price_nigth["promotion_amount"] = price_nigth["amount"]
                                        price_nigth["amount"]=0.00
                                        price_nigth["amount_to_pms"]=price_nigth["amount"]
                                        #price_nigth["percent_discount"]=100

                                    free_room_count += 1
                                    if free_room_count >= pivot_free:
                                        apply_discount = False

                                cont_room += 1
                            else:
                                room_apply = RatesFunctions.valide_room_promotion(prices[cont_room],\
                                discount["rates_rooms_avail"])

                                if room_apply == True:                                    
                                    rooms_cont +=1
                                    #prices[cont_room]["apply_room_free"] = True
                                    if rooms_cont >= pivot:
                                        apply_discount = True
                                        rooms_cont = 0 
                                        free_room_count = 0
                                else:
                                    cont_room += 1
                    else:
                        #Se aplica una sola ves
                        cont_room = 0
                        for rooms_rates in prices:
                            #if room_apply == True:
                            #price_day = len(price["price_per_day"])
                            if apply_discount == True:
                                room_apply = RatesFunctions.valide_room_promotion(prices[cont_room],\
                                discount["rates_rooms_avail"])

                                if room_apply == True:
                                    #prices[cont_room]["apply_room_free"] = True
                                    #prices[cont_room]["total_crossout"]=prices[cont_room]["total"]
                                    prices[cont_room]["total"]=0.00
                                    #prices[cont_room]["total_percent_discount"]=100
                                    for price_nigth in prices[cont_room]["price_per_day"]:
                                        #price_nigth["amount_crossout"]=price_nigth["amount"]
                                        total_promotion_discount += price_nigth["amount"]
                                        promo_detail = {
                                            "id_promotion":discount["idop_promotions"],
                                            "code":discount["code"],
                                            "value_discount":price_nigth["amount"],
                                            "crossout":discount["percent_cross_out"]
                                        }
                                        price_nigth["promotions"] = promo_detail
                                        price_nigth["promotion_amount"] = price_nigth["amount"]
                                        price_nigth["amount"]=0.00
                                        price_nigth["amount_to_pms"] = price_nigth["amount"]
                                        #price_nigth["percent_discount"]=100

                                    free_room_count += 1
                                    if free_room_count >= pivot_free:
                                        break
                                
                                cont_room += 1
                            else:
                                room_apply = RatesFunctions.valide_room_promotion(prices[cont_room],\
                                discount["rates_rooms_avail"])

                                if room_apply == True:
                                    rooms_cont +=1
                                    #prices[cont_room]["apply_room_free"] = True
                                    if rooms_cont >= pivot:
                                        apply_discount = True
                                        rooms_cont = 0 
                                        free_room_count = 0
                                else:
                                    cont_room += 1

            #Apply_Offers
            for price in prices:
                room_apply = RatesFunctions.valide_room_promotion(price,discount["rates_rooms_avail"])
                
                if room_apply == True:
                    dif_total = 0
                    if discount["per_discount"]>0.0:
                        for price_item in price["price_per_day"]:
                            date_str = datetime.strftime(price_item["efective_date"],"%Y-%m-%d")
                            if date_str in discount["apply_dates"]["dates_travel"]:
                                if price_item["amount"]>0:
                                    aux = price_item["amount"]
                                    price_discount=price_item["amount"]-(price_item["amount"]*discount["per_discount"])
                                    price_item["amount"]=round(price_discount,0)
                                    price_item["amount_to_pms"] = price_item["amount"]
                                    dif = aux - price_item["amount"]
                                    total_promotion_discount += dif
                                    promo_detail = {
                                        "id_promotion":discount["idop_promotions"],
                                        "code":discount["code"],
                                        "value_discount":dif,
                                        "crossout":discount["percent_cross_out"]
                                    }
                                    price_item["promotion_amount"] = dif
                                    price_item["promotions"] = promo_detail
                                    #price_item["amount_crossout"]=round(price_item["amount_crossout"]+dif,2)
                                    dif_total += dif
                    #price["total"] = round(price["total"]-dif_total,0)
                    #price["total_crossout"] = round(price["total_crossout"] + dif_total,2)

                    if discount["abs_discount"]>0.0:
                        for price_item in prices["price_per_day"]:
                            date_str = datetime.strftime(price_item["efective_date"],"%Y-%m-%d")
                            if date_str in discount["apply_dates"]["dates_travel"]:
                                #price_item["amount_crossout"] += round(price_item["amount"],2)
                                if price_item["amount"]>0:
                                    total_promotion_discount += discount["abs_discount"]
                                    promo_detail = {
                                        "id_promotion":discount["idop_promotions"],
                                        "code":discount["code"],
                                        "value_discount":discount["abs_discount"],
                                        "crossout":discount["percent_cross_out"]
                                    }
                                    price_item["promotion_amount"] = discount["abs_discount"]
                                    price_item["promotions"] = promo_detail
                                    price_item["amount"]=round(price_item["total"]-discount["abs_discount"],0)
                                    price_item["amount_to_pms"] = price_item["amount"]

            if discount["timer_config"]["timer"] == 1:
                if discount["apply_dates"]["dates_booking"] != "1900-01-01":
                    
                    date_apply_str = discount["apply_dates"]["dates_booking"]+" "+discount["apply_dates"]["times_booking"]+":00"
                    date_end_bookin = datetime.strptime(date_apply_str,"%Y-%m-%d %H:%M:%S")
                    
                    date_offset_str = str(discount["timer_config"]["days_offset"])+" "+discount["timer_config"]["time_offset"]
                    date_offset = datetime.strptime(date_offset_str,"%d %H:%M:%S")
                    
                    date_offset_1 = timedelta(days = date_offset.day, \
                    hours = date_offset.hour, minutes = date_offset.minute, \
                    seconds = date_offset.second)
                    
                    date_now = datetime.now()
                    dif_date = date_end_bookin - date_now

                    if dif_date <= date_offset_1:
                        for price in prices:
                            room_apply = RatesFunctions.valide_room_promotion(price,discount["rates_rooms_avail"])
                            if room_apply == True:
                                price["timer_on"] = True
                                price["date_end_promotion"] = date_end_bookin

        totales = RatesFunctions.calcualte_total_rates(prices)

        #calculate amount promotion night
        # for price in prices:
        #     for price_nigth in price["price_per_day"]:
        #         price_nigth["promotion_amount"] = round(price_nigth["amount_crossout"] - price_nigth["amount"],0)
        
        data["Code_Apply"]=list_codes
        data["Prices"]=prices
        data["Total"]=totales["total"]
        data["Subtotal"]=totales["subtotal"]

        return data

    @staticmethod
    def format_vauchers(promocode_data):
        to_discount = {
            "code":"",
            "text_only":False,
            "text":"",
            "abs_value":0.0,
            "per_value":0.0,
            "type_amount":0,
            "currency":"USD"
        }

        try:

            to_discount["code"]=promocode_data["code"]

            if promocode_data["iddef_promo_code_discount_type"] == 2:
                to_discount["text_only"] = True
                to_discount["text"] = promocode_data["description"]
            elif promocode_data["iddef_promo_code_discount_type"] == 1:
                if promocode_data["iddef_promo_code_type_amount"] == 4:
                    to_discount["per_value"]=promocode_data["value_discount"]
                    to_discount["type_amount"] = promocode_data["iddef_promo_code_type_amount"]
                else:
                    to_discount["abs_value"] = promocode_data["value_discount"]
                    to_discount["currency"] = promocode_data["currency_code"]
                    to_discount["type_amount"] = promocode_data["iddef_promo_code_type_amount"]
        
        except Exception as format_error:
            pass

        return to_discount

    @staticmethod
    def calcualte_total_rates(price_list):
        data={
            "total":0.00,
            "subtotal":0.00
        }
        
        total = 0.00
        subtotal = 0.00
        for price in price_list:
            new_total = 0
            new_total_crossout = 0
            for price_night in price["price_per_day"]:
                new_total += price_night["amount"]
                new_total_crossout += price_night["amount_crossout"]
            
            price["total"] = round(new_total,0)
            price["total_crossout"] = round(new_total_crossout,0)

            total += price["total"]
            subtotal += price["total_crossout"]

        data["total"]= round(total,0)
        data["subtotal"]= round(subtotal,0)

        return data

    @staticmethod
    def calcualte_total(price):
        data={
            "total":0.00,
            "subtotal":0.00
        }
        
        new_total = 0
        new_total_crossout = 0
        for price_night in price["price_per_day"]:
            new_total += price_night["amount"]
            new_total_crossout += price_night["amount_crossout"]
        
        price["total"] = round(new_total,0)
        price["total_crossout"] = round(new_total_crossout,0)

        data["total"]= round(price["total"],0)
        data["subtotal"]= round(price["total_crossout"],0)

        return data

    @staticmethod
    def convert_to_currency(currency_select,currency_vaucher,value_vaucher,date_now):
        to_usd_amount = 1
        exange_amount = 1
        currency_vaucher = currency_vaucher.upper()
        currency_select = currency_select.upper()

        try:
            if currency_vaucher != currency_select:
                Exange_apply = True
                if currency_vaucher != "USD":
                    exangeDataMx = funtionsExchange.get_exchange_rate_date(date_now,currency_vaucher)
                    to_usd_amount = round(exangeDataMx.amount,2)

                if currency_select != "USD":
                    exangeData = funtionsExchange.get_exchange_rate_date(date_now,currency_select)
                    exange_amount = round(exangeData.amount,2)
                
            if Exange_apply == True:
                value_vaucher = round(value_vaucher / to_usd_amount,2)
                value_vaucher = round(value_vaucher * exange_amount,2)

        except Exception as error:
            pass
        
        return value_vaucher
    
    @staticmethod
    def apply_vauchers(prices,vaucher,currency_code,date_totay):
        data = {
            "Vaucher_Apply":"",
            "Prices":[],
            "Total":0.00,
            "Subtotal":0.00,
            "vaucher_applied":False,
            "Text_Vaucher":""
        }

        totales = RatesFunctions.calcualte_total_rates(prices)

        total = totales["total"]
        subtotal = totales["subtotal"]
        total_vaucher_discount = 0

        if vaucher is not None:

            data["Vaucher_Apply"]=vaucher["code"]

            if vaucher["text_only"]== True:
                data["Text_Vaucher"] = vaucher["text"]
                data["vaucher_applied"] = True

                for price in prices:
                    price["vaucher_applied"] = True

            else:
                vaucher_value = RatesFunctions.convert_to_currency(currency_code,\
                vaucher["currency"],vaucher["abs_value"],date_totay)

                total_rooms = len(prices)
                total_rooms_cont = 0
                total_after = 0
                for price in prices:
                    total_nigth = price["nights"]
                    cont_nigth = 0
                    discount_room = 0
                    for rateplan_vaucher in vaucher["rateplans"]:
                        if price["property"] == rateplan_vaucher["id_property"]:
                            if price["rateplan"] == rateplan_vaucher["id_rateplan"]:
                                if price["room"] in rateplan_vaucher["id_rooms"]:
                                    price["vaucher_applied"] = True
                                    total_rooms_cont += 1
                                    for price_item in price["price_per_day"]:
                                        date_str = datetime.strftime(price_item["efective_date"],"%Y-%m-%d")
                                        if date_str in vaucher["valid_dates"]:
                                            cont_nigth += 1
                                            if vaucher["type_amount"]==3:
                                                #Per night 
                                                #Se resta a cada noche de cada habitacion
                                                if vaucher_value > price_item["amount"]:
                                                    vaucher_value = price_item["amount"]
                                                total_vaucher_discount += vaucher_value
                                                price_item["amount"] -= vaucher_value
                                                discount_room += vaucher_value
                                                price_item["amount"] = round(price["amount"],0)
                                                price_item["amount_to_pms"] = price_item["amount"]
                                                price_item["vaucher_discount"]=vaucher_value
                                                data["vaucher_applied"] = True

                                            elif vaucher["type_amount"]==4:
                                                #Percent 
                                                #Se aplica un porcentaje a cada noche 
                                                #de cada habitacion
                                                amount_discount = round(price_item["amount"]*(vaucher["per_value"]/100),2)
                                                if amount_discount > price_item["amount"]:
                                                    amount_discount = price_item["amount"]
                                                total_vaucher_discount += amount_discount
                                                price_item["amount"] -= amount_discount
                                                discount_room += amount_discount
                                                price_item["amount"] = round(price_item["amount"],0)
                                                price_item["amount_to_pms"] = price_item["amount"]
                                                price_item["vaucher_discount"]=amount_discount
                                                data["vaucher_applied"] = True

                                    totalroom = RatesFunctions.calcualte_total(price)
                                    price["total"] = totalroom["total"]
                                    price["discount_room"] = discount_room


                    if vaucher["type_amount"]==2 and cont_nigth == total_nigth:
                        #Per room, se resta al total de cada habitacion
                        price["vaucher_applied"] = True
                        if vaucher_value > price["total"]:
                            vaucher_value = price["total"]
                        total_vaucher_discount += vaucher_value
                        price["total"] -= vaucher_value
                        price["discount_room"] = vaucher_value
                        price["total"] = round(price["total"],0)
                        total_after += price["total"]

                        vaucher_per_day = vaucher_value/total_nigth
                        for price_item in price["price_per_day"]:
                            price_item["amount_to_pms"] = round(price_item["amount"] - vaucher_per_day,2)
                            price_item["vaucher_discount"]= vaucher_per_day
                        data["vaucher_applied"] = True
                    else:
                        total_after += price["total"]

                totales["total"] = total_after
                
                if vaucher["type_amount"]==1 and total_rooms_cont == total_rooms:
                    vaucher_value /= total_rooms
                    #Per stay, se resta una parte igual al total de cada habitacion 
                    #solo si todas las habitaciones son compatibles con el vaucher
                    total_amount = 0
                    for price in prices:
                        price["vaucher_applied"] = True
                        if vaucher_value > price["total"]:
                            vaucher_value = price["total"]
                        total_vaucher_discount += vaucher_value
                        price["total"] -= vaucher_value
                        price["discount_room"] = vaucher_value
                        price["total"] = round(price["total"],0)
                        total_amount += price["total"]
                        vaucher_per_day = vaucher_value/total_nigth
                        for price_item in price["price_per_day"]:
                            price_item["amount_to_pms"] = round(price_item["amount"] - vaucher_per_day,2)
                            price_item["vaucher_discount"]= vaucher_per_day
                        data["vaucher_applied"] = True

                    totales["total"] = total_amount
        
            #totales = RatesFunctions.calcualte_total_rates(prices)

        data["Prices"]=prices
        data["Total"]=round(totales["total"],0)
        data["Subtotal"]=round(total_vaucher_discount,0)
        
        return data

    @staticmethod
    def get_price_with_promotions(hotel_code, market_code, date_start, date_end,\
    currency_code, lang_code, rooms_info, vaucher_code="", booking_window_use=True):

        data = {
            "error":False,
            "msg":"Success",
            "Promotion_Apply":[],
            "Vaucher_Apply":"",
            "Vuaucher_error_txt":"",
            "Promotion_error_txt":[],
            "Prices":[],
            "Total":0.0,
            "Text":"",
            "tax_total":0,
            "vaucher_applied":False
        }

        if rooms_info is None:
            raise Exception("Informacion de habitacion no encontrada, favor de validar")

        try:

            property_info = RatesFunctions.getHotelInfo(hotel_code)

            rateplan_list = []
            rooms_list = []
            
            #Obtenemos las tarifas por cada habitacion de la reserva
            rates_list = []
            for rooms in rooms_info:

                rates_room = None

                #Tarifas por dia
                try:

                    #Hacemos una lista de rateplans y habitaciones
                    rateplan_list.append(rooms["idop_rate_plan"])
                    rooms_list.append(rooms["iddef_room_type"])

                    #Obtenemos las tarifas para esta habitacion
                    rates_room = RatesFunctions.getPricePerDay(property_info.iddef_property,\
                    rooms["iddef_room_type"],rooms["idop_rate_plan"],date_start,date_end,\
                    currency=currency_code,use_booking_window=booking_window_use,\
                    pax_room=rooms["pax"])

                    rates_room["key_room"]=rooms["key_room"]

                    rates_list.append(copy.deepcopy(rates_room))

                except Exception as rtc_error:
                    data["msg"] = str(rtc_error)
                
            #Aplicamos promociones
            promo_error_list = []
            try:
                #obtenemos las promociones aplicables
                promotions = RatesFunctions.get_promotions_by_booking(date_start=date_start, 
                date_end=date_end, market=market_code, lang_code=lang_code, \
                hotel=hotel_code,total_rooms=rooms_info)

                # rate_list_promotion =[]
                # rate_list_promotion.append(rates_room)

                rate_list_aux = []
                for promo in promotions:
                    rate_list_promotion = copy.deepcopy(rates_list)
                    promo_list = []
                    promo_list.append(promo)

                    aux_rate = RatesFunctions.apply_promotion(rate_list_promotion,\
                    promo_list)

                    rate_list_aux.append(copy.deepcopy(aux_rate["Prices"]))
                
                cont_room = 0
                list_end = []
                generate_vaucher = False
                cont_applies = 0
                room_selected = None
                cont_room_select = 0
                for room_item in rooms_info:
                    
                    room_version = []
                    for price_version in rate_list_aux:
                        room_version.append(copy.deepcopy(price_version[cont_room]))

                    rates_aux = RatesFunctions.select_rates_promotion(room_version)
                    list_end.append(copy.deepcopy(rates_aux))

                    totales_aux = RatesFunctions.calcualte_total(rates_aux)

                    if rates_aux["apply_room_free"] == True:
                        cont_applies += 1
                        if totales_aux["total"] > 0 and cont_room_select < 1:
                            room_selected = rates_aux
                            cont_room_select += 1

                    if cont_applies % 2 != 0:
                        generate_vaucher = True
                    else:
                        generate_vaucher = False
                    
                    cont_room += 1

                list_end.sort(key=lambda x: x["key_room"])
                
                rates_list = list_end

            except Exception as promo_error:
                promo_error_list.append(str(promo_error))
            
            #rates_list.append(rates_room)

            #Aplicamos los tax
            tax_error_list = []
            total_tax = 0
            try:
                # list_rate=[]
                # list_rate.append(rates_room)
                
                price_tax = RatesFunctions.get_price_with_policy_tax(date_start,\
                date_end,currency_code, rates_list)

                rates_list = price_tax["data"]
                total_tax = price_tax["total_tax"]

            except Exception as tax_error:
                tax_error_list.append(str(tax_error))
                
            
            price_total = RatesFunctions.calcualte_total_rates(rates_list)

            market_info = RatesFunctions.getMarketInfo(market_code,lang_code)
            market_id = market_info.iddef_market_segment

            rates_list = RatesFunctions.apply_crossout_list(rates_list,\
            market_id,market_code,True)

            price_total = RatesFunctions.calcualte_total_rates(rates_list)
                
            date_now = datetime.now().date()

            data_2 = {
                "codes":"",
                "text":"",
                "total":price_total["total"],
                "subtotal":price_total["subtotal"],
                "rates":rates_list,
                "error":False,
                "msg":"Promo Code Apply",
                "vaucher_applied":False
            }
            try:
                
                #Validar el vaucher
                # vauchers = vauchersFunctions.getValidatePromoCode(vaucher_code,\
                # property_code=hotel_code,travel_window_start=date_start,\
                # travel_window_end=date_end,rateplans=rateplan_list,rooms=rooms_list,\
                # market=market_id,lang_code=lang_code,min_booking_amount=price_total["total"])
                vauchers = vauchersFunctions.getValidatePromoCode(vaucher_code,\
                property_code=hotel_code,travel_window_start=date_start,\
                travel_window_end=date_end,rateplans=rateplan_list,rooms=rooms_list,\
                market=market_id,lang_code=lang_code)

                #Formatear los vauchers
                #vaucher_data = RatesFunctions.format_vauchers(vauchers)

                #Aplicamos el vaucher
                vaucher_applied = RatesFunctions.apply_vauchers(rates_list,vauchers,\
                currency_code,date_now)

                data_2["codes"] = vaucher_applied["Vaucher_Apply"]
                data_2["text"]=vaucher_applied["Text_Vaucher"]
                data_2["total"]=vaucher_applied["Total"]
                data_2["subtotal"]=vaucher_applied["Subtotal"]
                data_2["vaucher_applied"]=vaucher_applied["vaucher_applied"]
            
            except Exception as vaucher_error:
                data_2["error"]=True
                data_2["msg"]=str(vaucher_error)
            

            if data_2["error"] == False:
                data["Vaucher_Apply"] = data_2["codes"]
                data["Text"]=data_2["text"]


            data["vaucher_applied"]=data_2["vaucher_applied"]
            data["Prices"] = data_2["rates"]
            
            # data["Prices"] = RatesFunctions.apply_crossout_list(data["Prices"],\
            # market_id,market_code,True)

            # totales = RatesFunctions.calcualte_total_rates(data["Prices"])

            data["Total"]=data_2["total"]
            data["Subtotal"]=data_2["subtotal"]
            data["Vuaucher_error_txt"]=data_2["msg"]
            data["Promotion_error_txt"]=promo_error_list
            data["total_tax"]=total_tax

        except Exception as error:
            #print(error)
            data["msg"]=str(error)
            data["error"]=True

        return data
    
    @staticmethod
    def format_policy_tax(data_tax):
        objt = {
            "apply_dates_range":False,
            "apply_maximun":False,
            "amount_tax":0.0,
            "percent_tax":1
        }
        currency_policy_tax = data_tax["currency_code"]
        objt["currency_policy_tax"] = currency_policy_tax.upper()
        objt["id_category_group"] = data_tax["policy_tax_groups"][0]["iddef_policy_tax_base"]
        amount_tax = float(data_tax["policy_tax_groups"][0]["amount"])
        if data_tax["policy_tax_groups"][0]["use_dates_range"] == 1:
            objt["apply_dates_range"] = True
            objt["dates_ranges"] = data_tax["policy_tax_groups"][0]["date_ranges"]
        if data_tax["policy_tax_groups"][0]["use_maximum_amount"] == 1:
            objt["apply_maximun"] = True
            max_tax = float(data_tax["policy_tax_groups"][0]["max_amount"])
            objt["max_tax"] = round(max_tax,2)
        if objt["id_category_group"] == 2:
            objt["percent_tax"] = int(round(amount_tax,0))
            if objt["percent_tax"] == 0:
                objt["percent_tax"] = 1
        else:
            objt["amount_tax"] = amount_tax

        return objt
    
    @staticmethod
    def apply_tax(prices, tax, currency):
        data = prices
        """ data = {
            "property":prices["property"],
            "room":prices["room"],
            "rateplan":prices["rateplan"],
            "adults":prices["adults"],
            "minors":prices["minors"],
            "nights":prices["nights"],
            "total": prices["total"],
            "total_crossout": prices["total_crossout"],
            "price_per_day":prices["price_per_day"],
            "total_percent_discount":prices["total_percent_discount"],
            "total_tax":0
        } """
        data["total_tax"] = 0
        
        date_today = datetime.today().date()
        amount_tax = 0.0
        if tax["id_category_group"] != 2:
            Exange_apply_tax, to_usd_amount_tax, exange_amount_tax = False, 1, 1
            currency_policy_tax = tax["currency_policy_tax"]
            amount_tax = tax["amount_tax"]
            if currency_policy_tax != currency:
                Exange_apply_tax = True
                if currency_policy_tax != "USD":
                    #equivalencia a dolares
                    exangeTaxMx = funtionsExchange.get_exchange_rate_date(date_today,currency_policy_tax)
                    to_usd_amount_tax = round(exangeTaxMx.amount,2)
                if currency != "USD":
                    #equivalencia a tipo de cambio solicitado
                    exangeTax = funtionsExchange.get_exchange_rate_date(date_today,currency)
                    exange_amount_tax = round(exangeTax.amount,2)

            #Si se necesita hacer alguna conversion para tax
            if Exange_apply_tax == True:
                #Primero convertimos a dolares
                amount_tax = round(amount_tax / to_usd_amount_tax,2)
                #De dolares convertimos al tipo de cambio solicitado
                amount_tax = round(amount_tax * exange_amount_tax,2)

        new_price_per_day, total_amount, total_tax = [], 0.0, 0.0
        for itm_nigth in prices["price_per_day"]:
            #validar si aplica maximun
            band_max = False
            if tax["apply_maximun"] == True:
                if itm_nigth["amount"] <= tax["max_tax"]:
                    band_max = True
            #validar si aplica por rango de fecha
            band_apply = False
            if tax["apply_dates_range"] == True:
                for date in tax["dates_ranges"]:
                    if date["start"] >= itm_nigth["efective_date"] and date["end"] <= itm_nigth["efective_date"]:
                        band_apply = True
            if tax["id_category_group"] == 1 or tax["id_category_group"] == 4:
                if tax["apply_dates_range"] == True and band_apply == True:
                    if tax["apply_maximun"] == True and band_max == True:
                        itm_nigth["amount"] = round(itm_nigth["amount"] + amount_tax,0)
                    elif tax["apply_maximun"] == False:
                        itm_nigth["amount"] = round(itm_nigth["amount"] + amount_tax,0)
                elif tax["apply_dates_range"] == False:
                    if tax["apply_maximun"] == True and band_max == True:
                        itm_nigth["amount"] = round(itm_nigth["amount"] + amount_tax,0)
                    elif tax["apply_maximun"] == False:
                        itm_nigth["amount"] = round(itm_nigth["amount"] + amount_tax,0)
            if tax["id_category_group"] == 2:
                amount_tax = (itm_nigth["amount"] * tax["percent_tax"]) / 100
                amount_tax = round(amount_tax,2)
                if tax["apply_dates_range"] == True and band_apply == True:
                    if tax["apply_maximun"] == True and band_max == True:
                        itm_nigth["amount"] = round(itm_nigth["amount"] + amount_tax,0)
                    elif tax["apply_maximun"] == False:
                        itm_nigth["amount"] = round(itm_nigth["amount"] + amount_tax,0)
                elif tax["apply_dates_range"] == False:
                    if tax["apply_maximun"] == True and band_max == True:
                        itm_nigth["amount"] = round(itm_nigth["amount"] + amount_tax,0)
                    elif tax["apply_maximun"] == False:
                        itm_nigth["amount"] = round(itm_nigth["amount"] + amount_tax,0)
            #price = itm_nigth["amount_crossout"] + itm_nigth["promotion_amount"]
            itm_nigth["country_fee"] = round(amount_tax,0) #round(itm_nigth["amount"] - price,2)
            new_price_per_day.append(itm_nigth)
            total_amount += itm_nigth["amount"]
            total_tax += itm_nigth["country_fee"]
            itm_nigth["amount_to_pms"] = itm_nigth["amount"]
        data["price_per_day"] = new_price_per_day
        
        #validar si aplica maximun
        band_max_total = False
        if tax["apply_maximun"] == True:
            if prices["total"] <= tax["max_tax"]:
                band_max_total = True
        if tax["id_category_group"] == 3 or tax["id_category_group"] == 5:
            if tax["apply_dates_range"] == True and band_apply == True:
                if tax["apply_maximun"] == True and band_max_total == True:
                    total_amount = round(prices["total"] + amount_tax,0)
                elif tax["apply_maximun"] == False:
                    total_amount = round(prices["total"] + amount_tax,0)
            elif tax["apply_dates_range"] == False:
                if tax["apply_maximun"] == True and band_max_total == True:
                    total_amount = round(prices["total"] + amount_tax,0)
                elif tax["apply_maximun"] == False:
                    total_amount = round(prices["total"] + amount_tax,0)
        if total_amount > 0:
            data["total"] = round(total_amount,0)
            data["total_tax"] = round(total_tax,0)
        else:
            data["total"] = round(prices["total"],0)
            data["total_tax"] = round(data["total"] - amount_tax,0)

        

        return data


    @staticmethod
    def get_price_with_policy_tax(date_start, date_end, currency_code, rooms_rate):
        
        total_tax = 0

        result = {
            "error":False,
            "msg":"Success",
            "total_tax":total_tax,
            "data":rooms_rate
        }

        if rooms_rate is None:
            raise Exception("Informacion de rates de habitaciones no encontrada, favor de validar")

        try:
            rateplan_list = []
            #recorremos información de rates
            for itm_room in rooms_rate:
                #obtenemos informacion de tax
                dataTaxs = funtionsPolicy.getPolicyTaxes(itm_room["rateplan"], date_start.strftime("%Y-%m-%d"),\
                date_end.strftime("%Y-%m-%d"),isFormat=False)
                #formatear informacion
                if len(dataTaxs) > 0:
                    dataTax = RatesFunctions.format_policy_tax(dataTaxs)
                    #aplicar metodo
                    try:
                        data_apply_tax = RatesFunctions.apply_tax(itm_room, dataTax, currency_code)
                        total_tax += data_apply_tax["total_tax"]
                        rateplan_list.append(data_apply_tax)
                        
                    except Exception as errTax:
                        result["msg"]=str(errTax)
                        result["error"]=True
                        rateplan_list.append(itm_room)
                else:
                    rateplan_list.append(itm_room)

            result["total_tax"] = total_tax
            result["data"] = rateplan_list
        except Exception as error:
            result["msg"]=str(error)
            result["error"]=True
            result["data"] = rooms_rate

        return result

    @staticmethod
    def apply_crossout_list(price_list,marketid,country_code,use_booking_window):

        for price in price_list:
            total_crossout = 0
            for price_night in price["price_per_day"]:

                percent_discount = 0
                try:

                    if price_night["promotions"] is not None:
                        percent_discount = price_night["promotions"]["crossout"] 

                    if percent_discount <= 0:
                        crossout_detail = RatesFunctions.getCossOutConfig(price["property"],1,\
                        price["rateplan"],price_night["efective_date"],price_night["efective_date"],\
                        False,use_booking_window, market=marketid, country=country_code)

                        if crossout_detail is not None and len(crossout_detail) > 0:
                            percent_discount = int(round(crossout_detail[0].percent,0))

                except Exception as crossEx:
                    pass

                if percent_discount > 0:
                    amount_crossout = RatesFunctions.calculateRate(percent_discount,price_night["amount"])
                    price_night["amount_crossout"] = round(amount_crossout,0)
                    price_night["percent_discount"] = int(round(percent_discount,0))
                    total_crossout += amount_crossout

            if total_crossout <= 0:
                total_crossout = price["total"]

            total_percent_discount = RatesFunctions.calculatepercent(price["total"],total_crossout)
            price["total_percent_discount"] = round(total_percent_discount,0)
            price["total_crossout"]=round(total_crossout,0)
                    
        return price_list

    
    @staticmethod
    def getPricePerDay(idProperty,idRoom,idRateplan,checkin_date,checkout_date,\
    adults=0,childs=0,currency=None,use_booking_window=True,market=None,\
    country=None,pax_room=None,apply_crossout=False,show_cero=False,spp=True):

        if pax_room is not None:

            adults=0
            childs=0
            
            agcData = agcModel.query.join(agrModel,\
            agcModel.iddef_age_code == agrModel.iddef_age_code).filter(agrModel.iddef_property==idProperty,\
            agrModel.estado==1).all()

            age_code = [item.code for item in agcData]

            for paxes in pax_room.keys():
                if paxes in age_code:
                    if paxes.lower() == "adults":
                        adults += pax_room[paxes]
                    elif paxes.lower() != "infants":
                        childs += pax_room[paxes]

        adt_aux = adults
        chd_aux = childs
        # rtcData = rtcModel.query.get(idRoom)
        # if childs >=1:
        #     if rtcData.acept_chd == 1:
        #         while adults < rtcData.single_parent_policy and childs > 0:
        #             adults += 1
        #             childs -= 1
        
        price_per_day=[]
        date_today = datetime.today().date()
        #obtenemos el currency code del rateplan
        data_rateplan =  rpModel.query.get(idRateplan) #RatesFunctions.getRateplanInfo(rateplanId=idRateplan,property_id=idProperty)
        currency_rateplan = data_rateplan.currency_code
        currency_rateplan = currency_rateplan.upper()

        if currency is None:
            #utilizamos el currency por defecto
            currency = currency_rateplan
        
        currency = currency.upper()
        
        #Verificamos el tipo de cambimo solicitado sea diferente a su base
        Exange_apply = False
        to_usd_amount = 1
        exange_amount = 1
        exange_amount_tag = 1
        if currency != currency_rateplan:
            Exange_apply = True
            #Si el tipo de cambio del rate plan esta en pesos y se solicita en un tipo de cambio
            #diferente a dolares, es necesario convertir de pesos a dolares primero
            #Y despues de dolares al tipo de cambio solicitado
            if currency_rateplan != "USD":
                #Siempre vamos a converir a dolares primero
                exangeDataMx = funtionsExchange.get_exchange_rate_date(date_today,currency_rateplan)
                to_usd_amount = round(exangeDataMx.amount,2)

            if currency != "USD":
                exangeData = funtionsExchange.get_exchange_rate_date(date_today,currency)
                exange_amount = round(exangeData.amount,2)
        
        if currency == "MXN":
            exangeaux = funtionsExchange.get_exchange_rate_date(date_today,"MXN")
            exange_amount_tag = round(exangeaux.amount,2)
        else:
            exange_amount_tag = exange_amount

        #obtenemos el id de adultos
        idAdultos= RatesFunctions.getIdPaxtype(adults)
        #Obtenemos el id de los menores
        idMenores=1

        if isinstance(checkin_date,str):
            checkin_date = datetime.strptime(checkin_date,'%Y-%m-%d').date()
        if isinstance(checkout_date,str):
            checkout_date = datetime.strptime(checkout_date,'%Y-%m-%d').date()

        nigths = checkout_date - checkin_date
        count = 0
        efective_date = checkin_date
        total_amount = 0
        total_amount_cross = 0
        while count < nigths.days :

            percent_discount = 0
            adult_amount = 0
            adult_amount_cross = 0
            childs_amount = 0
            childs_amount_cross = 0
            total_rate = 0

            #Buscamos el crossout que aplica para este dia si se solicita
            if apply_crossout == True:
                try:
                    crossout_detail = RatesFunctions.getCossOutConfig(idProperty,1,\
                    idRateplan,efective_date,efective_date,False,use_booking_window, market=market, country=country)

                    if crossout_detail is not None and len(crossout_detail) > 0:
                        percent_discount = int(round(crossout_detail[0].percent,0))

                except Exception as crossEx:
                    pass

            #Buscamos las tarifas para los pax indicados
            apply_ssp = False
            try:

                #Buscamos tarifas para adultos
                adults_price = RatesFunctions.getPrices(idProperty,idRateplan,idRoom,\
                idAdultos,efective_date,efective_date)

                if len(adults_price) > 0:
                    adult_amount = round(adults_price[0].amount,2)
                    if show_cero == False and adult_amount <= 0:
                        raise Exception("Tarifa de adulto no puede ser 0")

                    #Si se necesita hacer alguna conversion
                    if Exange_apply == True:
                        #Primero convertimos a dolares
                        adult_amount = round(adult_amount / to_usd_amount,2)

                        #De dolares convertimos al tipo de cambio solicitado
                        adult_amount = round(adult_amount * exange_amount,2)
                else:
                    if childs <= 0:                        
                        raise Exception("Tarifa no encontrada de adultos no encontrada")

                apply_ssp = False
                #Buscamos tarifa para menores si se necesita
                if childs > 0:
                    childs_price = RatesFunctions.getPrices(idProperty,idRateplan,idRoom,\
                    idMenores,efective_date,efective_date)

                    if len(childs_price) > 0:
                        
                        childs_amount1 = childs * childs_price[0].amount

                        if childs_price[0].amount > 0 and spp == True:
                            get_rate = Search()
                            
                            childs_amount1 =get_rate.apply_single_parent_policy(adults,childs,\
                            childs_price[0].amount,idProperty,idRoom,idRateplan,efective_date)

                            apply_ssp = True

                        childs_amount = round(childs_amount1,2)

                        #Si se necesita hacer alguna conversion
                        if Exange_apply == True:
                            #Primero convertimos a dolares
                            childs_amount = round(childs_amount / to_usd_amount,2)

                            #De dolares convertimos al tipo de cambio solicitado
                            childs_amount = round(childs_amount * exange_amount,2)
                    else:
                        raise Exception("Tarifa no encontrada de menores no encontrada")

                if apply_ssp:
                    total_rate = round(childs_amount,2)
                else:
                    total_rate = round(adult_amount + childs_amount,2)

                if total_rate <= 0 and show_cero == False:
                    raise Exception("La tarifa diaria no puede ser 0 o menor")
            
            except Exception as rate_error:
                #print(str(rate_error))
                if show_cero == False:
                    total_amount=0
                    break
            
            if apply_ssp:
                total_rate = round(childs_amount,2)
            else:
                total_rate = round(adult_amount + childs_amount,2)
            
            total_rate_cross = 0
            if percent_discount > 0:
                adult_amount_cross = RatesFunctions.calculateRate(percent_discount,adult_amount)
                childs_amount_cross = RatesFunctions.calculateRate(percent_discount,childs_amount)
                total_rate_cross = round(childs_amount_cross+adult_amount_cross,2)
            else:
                total_rate_cross = round(childs_amount+adult_amount,2)

            total_amount += total_rate
            total_amount_cross += total_rate_cross

            price_detail = {
                "night":(count+1),
                "amount": round(total_rate,0),
                "amount_crossout": round(total_rate_cross,0),
                "percent_discount": percent_discount,
                "efective_date": efective_date,
                "promotions":None,
                "amount_to_pms":round(total_rate,0),
                "promotion_amount": 0.0,
                "country_fee": 0.0,
                "vaucher_discount":0.0
            }

            price_per_day.append(price_detail)

            count += 1
            efective_date = efective_date + dates.timedelta(days=1)

        #EndWhile

        total_percent_discount = RatesFunctions.calculatepercent(total_amount,total_amount_cross)

        data = {
            "apply_room_free":False,
            "property":idProperty,
            "room":idRoom,
            "rateplan":idRateplan,
            "paxes":pax_room,
            "adults":adt_aux,
            "minors":chd_aux,
            "nights":count,
            "timer_on":False,
            "vaucher_applied":False,
            "date_end_promotion": datetime(1990,1,1,00,00,00),
            "total": round(total_amount,0),
            "total_crossout": round(total_amount_cross,0),
            "exange_amount":exange_amount_tag,
            "price_per_day":price_per_day,
            "total_percent_discount":int(round(total_percent_discount))
        }

        return data

    @staticmethod
    def getPricePerDay_v2(idProperty,idRoom,idRateplan,checkin_date,checkout_date,\
    adults=0,childs=0,currency=None,use_booking_window=True,market=None,\
    country=None,pax_room=None,apply_crossout=False,show_cero=False):

        if pax_room is not None:

            adults=0
            childs=0
            
            agcData = agcModel.query.join(agrModel,\
            agcModel.iddef_age_code == agrModel.iddef_age_code).filter(agrModel.iddef_property==idProperty,\
            agrModel.estado==1).all()

            age_code = [item.code for item in agcData]

            for paxes in pax_room.keys():
                if paxes in age_code:
                    if paxes.lower() == "adults":
                        adults += pax_room[paxes]
                    elif paxes.lower() != "infants":
                        childs += pax_room[paxes]

        
        price_per_day=[]
        date_today = datetime.today().date()
        #obtenemos el currency code del rateplan
        data_rateplan =  rpModel.query.get(idRateplan) #RatesFunctions.getRateplanInfo(rateplanId=idRateplan,property_id=idProperty)
        currency_rateplan = data_rateplan.currency_code
        currency_rateplan = currency_rateplan.upper()

        if currency is None:
            #utilizamos el currency por defecto
            currency = currency_rateplan
        
        currency = currency.upper()
        
        #Verificamos el tipo de cambimo solicitado sea diferente a su base
        Exange_apply = False
        to_usd_amount = 1
        exange_amount = 1
        exange_amount_tag = 1
        if currency != currency_rateplan:
            Exange_apply = True
            #Si el tipo de cambio del rate plan esta en pesos y se solicita en un tipo de cambio
            #diferente a dolares, es necesario convertir de pesos a dolares primero
            #Y despues de dolares al tipo de cambio solicitado
            if currency_rateplan != "USD":
                #Siempre vamos a converir a dolares primero
                exangeDataMx = funtionsExchange.get_exchange_rate_date(date_today,currency_rateplan)
                to_usd_amount = round(exangeDataMx.amount,2)

            if currency != "USD":
                exangeData = funtionsExchange.get_exchange_rate_date(date_today,currency)
                exange_amount = round(exangeData.amount,2)
        
        if currency == "MXN":
            exangeaux = funtionsExchange.get_exchange_rate_date(date_today,"MXN")
            exange_amount_tag = round(exangeaux.amount,2)
        else:
            exange_amount_tag = exange_amount

        #obtenemos el id de adultos
        idAdultos= RatesFunctions.getIdPaxtype(adults)
        #Obtenemos el id de los menores
        idMenores=1

        if isinstance(checkin_date,str):
            checkin_date = datetime.strptime(checkin_date,'%Y-%m-%d').date()
        if isinstance(checkout_date,str):
            checkout_date = datetime.strptime(checkout_date,'%Y-%m-%d').date()

        nigths = checkout_date - checkin_date
        count = 0
        efective_date = checkin_date
        total_amount = 0
        total_amount_cross = 0
        adults_price = 0
        childs_price = 0

        adults_prices = RatesFunctions.getPrices_v2(idProperty,idRateplan,idRoom,\
        idAdultos,checkin_date,checkout_date,overrides=False)

        if childs > 0:
            childs_prices = RatesFunctions.getPrices_v2(idProperty,idRateplan,idRoom,\
            idMenores,checkin_date,checkout_date,overrides=False)

        position_rate = 0
        while count < nigths.days :
            if len(adults_prices) > 0:
                days_rate = adults_prices[position_rate].date_end - adults_prices[position_rate].date_start
                for item in range(days_rate.days+1):
                    
                    if efective_date >= checkout_date:
                        break

                    amount = round(adults_prices[position_rate].amount,2)
                    #Si se necesita hacer alguna conversion
                    if Exange_apply == True:
                        #Primero convertimos a dolares
                        amount = round(amount / to_usd_amount,2)

                        #De dolares convertimos al tipo de cambio solicitado
                        amount = round(amount * exange_amount,2)
                    
                    price_detail = {
                        "night":(count+1),
                        "amount": round(amount,0),
                        "amount_crossout": 0.0,
                        "percent_discount": 0,
                        "efective_date": efective_date,
                        "promotions":None,
                        "amount_to_pms":round(amount,0),
                        "promotion_amount": 0.0,
                        "country_fee": 0.0,
                        "vaucher_discount":0.0
                    }

                    price_per_day.append(price_detail)

                    count += 1
                    efective_date = efective_date + dates.timedelta(days=1)
                
                position_rate += 1
            else:
                count = nigths.days

        if childs > 0:
            for day in price_per_day:
                for chd_pr in childs_prices:
                    if chd_pr.date_start <= day["efective_date"] \
                    and chd_pr.date_end >= day["efective_date"]:

                        amount = chd_pr.amount
                        #Si se necesita hacer alguna conversion
                        if Exange_apply == True:
                            #Primero convertimos a dolares
                            amount = round(amount / to_usd_amount,2)

                            #De dolares convertimos al tipo de cambio solicitado
                            amount = round(amount * exange_amount,2)
                        
                        day["amount"] += amount
                        day["amount"] = round(day["amount"],0)
                        day["amount_to_pms"] += amount
                        day["amount_to_pms"] = round(day["amount_to_pms"],0)

                        break

        
        data = {
            "apply_room_free":False,
            "property":idProperty,
            "room":idRoom,
            "rateplan":idRateplan,
            "paxes":pax_room,
            "adults":adults,
            "minors":childs,
            "nights":count,
            "timer_on":False,
            "vaucher_applied":False,
            "date_end_promotion": datetime(1990,1,1,00,00,00),
            "total": 0.00,
            "total_crossout": 0,
            "exange_amount":exange_amount_tag,
            "price_per_day":price_per_day,
            "total_percent_discount":0
        }

        totales = RatesFunctions.calcualte_total(data)
        data["total"] = totales["total"]

        return data
    
    @staticmethod
    def getFakePricePerDay(idProperty,idRoom,idRateplan,checkin_date,checkout_date,\
    adults,childs,currency=None,use_booking_window=True,market=None,country=None):
        
        if isinstance(checkin_date,str):
            checkin_date = datetime.strptime(checkin_date,'%Y-%m-%d').date()
        if isinstance(checkout_date,str):
            checkout_date = datetime.strptime(checkout_date,'%Y-%m-%d').date()
        
        nigths = checkout_date - checkin_date
        count = 0
        efective_date = checkin_date
        total_amount = 0
        total_amount_cross = 0
        total_percent_discount = 0
        price_per_day=[]
        date_today = datetime.today().date()

        while count < nigths.days:
            price_detail = {
                "night":(count+1),
                "amount": round(0,2),
                "amount_crossout": round(0,2),
                "percent_discount": 0,
                "efective_date": efective_date
            }

            price_per_day.append(price_detail)
            
            count += 1
            efective_date = efective_date + dates.timedelta(days=1)

        data = {
            "property":idProperty,
            "room":idRoom,
            "rateplan":idRateplan,
            "adults":adults,
            "minors":childs,
            "nights":count,
            "total": round(total_amount,2),
            "total_crossout": round(total_amount_cross,2),
            "price_per_day":price_per_day,
            "total_percent_discount":int(round(0))
        }
        
        return data
    
    @staticmethod
    def getTextLangInfo(table_name,attribute,lang_code,id_relation):
        text = None
        data = TextLModel.query.filter(TextLModel.estado==1, \
        TextLModel.table_name==table_name, \
        TextLModel.attribute==attribute, \
        TextLModel.lang_code==lang_code, \
        TextLModel.id_relation==id_relation).first()

        if data is not None:
            text = data

        return text

    #Metodo para obtener book_promotion
    @staticmethod
    def get_book_promotion(id_book=None,id_promotion=None,isAll=True,count=True):
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
    
    #Metodo para obtener promotions para reserva
    @staticmethod
    def get_promotions_by_booking(date_start=None,date_end=None,market=None,\
    hotel=None,lang_code=None,total_rooms=None,include_free_room=True,\
    id_rateplan=None, id_room=None,data_restrictions=None):
        data = []
        totalRooms = 0
        booking_date = datetime.now().date()
        booking_time = datetime.now().time()
        #Obtenemos informacion del lenguaje seleccionado
        if lang_code == None:
            lang_code = "EN"
        #Obtenemos informacion de los cuartos seleccionados
        if total_rooms is None:
            totalRooms = 1
            if id_rateplan is not None:
                id_rateplan = [id_rateplan]
            else:
                raise Exception(Util.t(lang_code, "rateplan_not_found"))

            if id_room is None:
                raise Exception(Util.t(lang_code, "room_not_found"))
        else:
            id_rateplan = [rateplan_elem["idop_rate_plan"] for rateplan_elem in total_rooms]
            id_room = [room_elem["iddef_room_type"] for room_elem in total_rooms]
            totalRooms = len(total_rooms)
        #Obtenemos informacion del mercado seleccionado
        if market == None:
            market = "CR"
        msData = RatesFunctions.getMarketInfo(market,lang_code)
        id_market = msData.iddef_market_segment
        #Obtenemos informacion de la propiedad seleccionado
        if hotel != None:
            hotel = RatesFunctions.getHotelInfo(hotel)
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
        # data_restrictions = resFuntions.getRestrictionDetails(travel_window_start=date_start, \
        # travel_window_end=date_end, restriction_by=7, restriction_type=4, market_targeting=id_market)
        obj = resFuntions2(travel_window_start=date_start, \
        travel_window_end=date_end, restriction_by=7, restriction_type=4, market_targeting=id_market)
        data_restrictions = obj.get_restriction_details()
        if len(data_restrictions) > 0:
            #se valida restriccioness
            ids_restrictions = RatesFunctions.validate_restrictions(data_restrictions,date_start,date_end,booking_date,include_free_room)
            #Se obtine informacion de las promociones respecto a restricciones
            id_room = ''+str(id_room)+''
            data_pro_rest = PResModel.query.filter(ProModel.estado==1,\
            PResModel.id_restriction.in_(ids_restrictions)).all()
            if len(data_pro_rest) > 0:

                ids_promotions = [promotion_elem.id_promotion for promotion_elem in data_pro_rest]

                #se obtiene promociones respecto a ratepla, cuarto, propiedad
                data_pro_rate = PRModel.query.filter(PRModel.id_promotion.in_(ids_promotions),\
                PRModel.id_property==id_property,PRModel.id_rateplan.in_(id_rateplan),\
                func.json_contains(PRModel.rate_plan_rooms,id_room),PRModel.estado==1).all()

                if len(data_pro_rate) > 0:
                    ids_promotion = [promotion_ele.id_promotion for promotion_ele in data_pro_rate]
                    
                    #Validacion nigth
                    dataPromotions = RatesFunctions.get_promotions(ids_promotion=ids_promotion,\
                    totalNigths=totalNigths,totalRooms=totalRooms)

                    if len(dataPromotions) > 0:
                        list_discounts = []
                        for itx in dataPromotions:
                            bandLength, bandLimitSales, bandDiscount, bandFreeRooms = True, False, True, True
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
                                #Obtenemos informacion de book_promotion
                                total_book = RatesFunctions.get_book_promotion(id_promotion=itx["idop_promotions"])
                                if int(total_book) > 0:
                                    if total_book < itx["limit_sales_count"]:
                                        bandLimitSales = True
                                else:
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
                            if include_free_room == False:
                                bandFreeRooms = False
                                if itx["free_rooms"]==0:
                                    bandFreeRooms = True
                            if bandLength == True and bandLimitSales == True and bandDiscount == True and bandFreeRooms==True:
                                rateplan_list = [ \
                                { "rateplan":promotion_ele.id_rateplan,
                                "rooms":promotion_ele.rate_plan_rooms }\
                                for promotion_ele in data_pro_rate \
                                if promotion_ele.id_property == id_property\
                                if promotion_ele.id_promotion == itx["idop_promotions"]]
                                priority_weight, band_free_room = 0, False
                                list_free = []
                                to_discount = {
                                    "rates_rooms_avail": rateplan_list,
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
                                if itx["free_rooms"] == 1:
                                    band_free_room = True
                                filter_restriction = list(filter(lambda elem_r: elem_r.id_promotion == itx["idop_promotions"], data_pro_rest))
                                inf_restriction = list(filter(lambda elem_r: elem_r['iddef_restriction'] == filter_restriction[0].id_restriction, data_restrictions))
                                to_discount["booking_window_dates"] = inf_restriction[0]["booking_window_dates"]
                                to_discount["travel_window"] = inf_restriction[0]["travel_window"]
                                inf_validate_dates = RatesFunctions.get_list_range(inf_restriction[0]["travel_window"],inf_restriction[0]["travel_window_option"],date_start,date_end)
                                to_discount["apply_dates"]["dates_travel"] = sorted(set(inf_validate_dates))
                                if int(inf_restriction[0]["booking_window_option"]) == 1:
                                    for itm_date in inf_restriction[0]["booking_window_dates"]:
                                        if booking_date <= itm_date["end_date"]:
                                            to_discount["apply_dates"]["dates_booking"] = itm_date["end_date"]
                                    if len(inf_restriction[0]["booking_window_times"]) > 0:
                                        for itm_date in inf_restriction[0]["booking_window_times"]:
                                            if booking_time.strftime("%H-%M") <= itm_date["end_time"]:
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
                                if band_free_room == True:
                                    id_restriction_apply = RatesFunctions.validate_restrictions(inf_restriction,date_start,date_end,booking_date,include_free_room,band_free_room)
                                    if len(id_restriction_apply) > 0:
                                        list_discounts.append(to_discount)
                                else:
                                    list_discounts.append(to_discount)
                        list_discounts.sort(key=lambda x: x.get("priority"),reverse=True)
                        data = list_discounts
        return data
    
    @staticmethod
    def range_dates_booking(date_start,date_end):
        for n in range(int ((date_end - date_start).days+1)):
            yield date_start + dates.timedelta(days=n)

    @staticmethod
    def get_list_range(data_dates,option,date_start,date_end):
        if isinstance(date_start,str):
            date_start = datetime.strptime(date_start,'%Y-%m-%d').date()
        if isinstance(date_end,str):
            date_end = datetime.strptime(date_end,'%Y-%m-%d').date()
        list_dates = []
        for itm_date in RatesFunctions.range_dates_booking(date_start,date_end):
            for travel_window in data_dates:
                if int(option) == 0:
                    list_dates.append(itm_date.strftime("%Y-%m-%d"))
                elif int(option) == 1:
                    if itm_date.strftime("%Y-%m-%d") >= travel_window["start_date"] and itm_date.strftime("%Y-%m-%d") <= travel_window["end_date"]:
                        list_dates.append(itm_date.strftime("%Y-%m-%d"))
                elif int(option) == 2:
                    if itm_date.strftime("%Y-%m-%d") < travel_window["start_date"] or itm_date.strftime("%Y-%m-%d") > travel_window["end_date"]:
                        list_dates.append(itm_date.strftime("%Y-%m-%d"))

        return list_dates

    @staticmethod
    def validate_restrictions(data_restrictions,date_start,date_end,booking_date,include_free_room,band_free_room=False):
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
    
    @staticmethod
    def get_promotions(ids_promotion=None,totalNigths=None,totalRooms=None, code=None):
        schema = ProModelSchema(exclude=Util.get_default_excludes())
        result, conditions = [], []
        conditionsOr, conditionsOr2, conditionsOr3 = [], [], []
        conditionsAnd, conditionsAnd2, conditionsAnd22,\
        conditionsAnd23, conditionsAnd24, conditionsAnd25 = [], [], [], [], [], []
        if ids_promotion is not None:
            conditions.append(ProModel.idop_promotions.in_(ids_promotion))
        if code is not None:
            conditions.append(ProModel.code == code)
        if totalNigths is not None:
            conditionsAnd.append(ProModel.free_nights==0)
            conditionsOr.append(and_(*conditionsAnd))
            conditionsAnd2.append(ProModel.free_nights==1)
            conditionsAnd2.append(func.json_extract(ProModel.free_nights_conditions, '$.paid') <= totalNigths)
            conditionsOr.append(and_(*conditionsAnd2))
            conditions.append(or_(*conditionsOr))
        if totalRooms is not None:
            conditionsAnd22.append(ProModel.free_rooms==0)
            conditionsOr2.append(and_(*conditionsAnd22))
            conditionsAnd23.append(ProModel.free_rooms==1)
            conditionsAnd23.append(func.json_extract(ProModel.free_rooms_conditions, '$.paid') <= totalRooms)
            conditionsOr2.append(and_(*conditionsAnd23))
            conditions.append(or_(*conditionsOr2))
        data_promotions = ProModel.query.filter(and_(*conditions,ProModel.estado==1)).all()
        if len(data_promotions) > 0:
            result = schema.dump(data_promotions, many=True)

        return result
    
    @staticmethod
    def pushRates(data):
        url= 'https://wireclever.web.palace-resorts.local/api/CleverInterface/TestData'
        dataSend= {
            "hotel":data["hotel"],
            "date_start":data["date_start"],
            "date_end": data["date_end"],
            "rate_plan_clever": data["rate_plan_clever"],
            "rate_plan_channel": data["rate_plan_channel"],
            "include_promotion": data["include_promotion"],
            "date_start_promotions":data["date_start_promotions"],
            "refundable":data["refundable"]
        }
        #JSONData = json.dumps(dataSend)

        consumeApi = requests.post(url, verify=False,  json=dataSend)
        res =   consumeApi.text()
       
        return res
    
    #Metodo para obtener book_promo_code
    @staticmethod
    def get_book_promo_code(id_book=None,promo_code=None,isAll=True,count=True):
        conditions = []

        if id_book is not None:
            conditions.append(bpcModel.idbook_hotel==id_book)
        if promo_code is not None:
            conditions.append(bpcModel.promo_code==promo_code)
        if isAll:
            if count:
                data_promo_code = bpcModel.query.filter(and_(*conditions,bpcModel.estado==1)).count()
            else:
                data_promo_code = bpcModel.query.filter(and_(*conditions,bpcModel.estado==1)).all()
        else:
            data_promo_code = bpcModel.query.filter(and_(*conditions,bpcModel.estado==1)).first()

        return data_promo_code

    #Metodo para obtener promocode por reserva
    @staticmethod
    def getPromoCode(promocode=None, hotel=None, rateplan=None,\
    room=None, date_start=None, date_end=None, market=None, country=None,\
    total_pax=None, total_room=None, total_amount=None, useStay=True, lang_code="EN"):
        result = []
        schema = GetPMModelSchema(exclude=Util.get_default_excludes())
        condition = []
        conditionsOr0, conditionsAnd02 = [], []
        conditionsOr1, conditionsOr2 = [], []
        conditionsOr3, conditionsAnd31 = [], []
        conditionsOr4, conditionsAnd41 = [], []
        conditionsOr5, conditionsAnd51 = [], []

        booking_window_date = datetime.today().strftime('%Y-%m-%d')
        booking_window_time = datetime.now().strftime('%H:%M')
        total_nigths, id_property, id_market = None, None, None

        if date_start is not None and date_end:
            total_nigths = date_end - date_start
            total_nigths = total_nigths.days
        if market is not None:
            msData = RatesFunctions.getMarketInfo(market,lang_code)
            id_market = msData.iddef_market_segment
        if hotel is not None:
            inf_hotel = RatesFunctions.getHotelInfo(hotel)
            id_property = inf_hotel.iddef_property
        if room is not None:
            list_room = []
            for x in room:
                data_room = rtcModel.query.get(x)
                code_room = str(data_room.room_code)
                list_room.append(code_room)

        #filtrado
        if promocode is not None:
            condition.append(pcModel.code==promocode)
        if id_property is not None:
            condition.append(pcrpModel.iddef_property==id_property)
        if rateplan is not None:
            condition.append(pcrpModel.idop_rateplan.in_(rateplan))
        if total_amount is not None:
            conditionsOr0.append(pcModel.min_booking_amount_option==1)
            conditionsAnd02.append(pcModel.min_booking_amount_option==2)
            conditionsAnd02.append(pcModel.min_booking_value<=total_amount)
            conditionsOr0.append(and_(*conditionsAnd02))
            condition.append(or_(*conditionsOr0))
        if useStay:
            conditionsOr1.append(pcModel.stay_dates_option==1)
            conditionsOr1.append(pcModel.stay_dates_option==2)
            conditionsOr1.append(pcModel.stay_dates_option==3)
            condition.append(or_(*conditionsOr1))
        if total_nigths is not None:
            conditionsOr4.append(pcModel.min_LOS_option==1)
            conditionsAnd41.append(pcModel.min_LOS_option==2)
            conditionsAnd41.append(pcModel.min_LOS_value<=total_nigths)
            conditionsOr4.append(and_(*conditionsAnd41))
            condition.append(or_(*conditionsOr4))
        if date_start is not None and date_end is not None:
            conditionsOr2.append(pcModel.booking_dates_option==1)
            conditionsOr2.append(pcModel.booking_dates_option==2)
            conditionsOr2.append(pcModel.booking_dates_option==3)
            condition.append(or_(*conditionsOr2))
        if id_market is not None:
            id_market = '['+str(id_market)+']'
            ids_market = ''+id_market+''
            conditionsOr3.append(pctcModel.market_option==0)
            conditionsOr3.append(pctcModel.market_option==1)
            conditionsAnd31.append(pctcModel.market_option==2)
            conditionsAnd31.append(func.json_contains(pctcModel.market_targeting,ids_market))
            conditionsOr3.append(and_(*conditionsAnd31))
            condition.append(or_(*conditionsOr3))
        if country is not None:
            country = ''+country+''
            conditionsOr5.append(pctcModel.country_option==0)
            conditionsOr5.append(pctcModel.country_option==1)
            conditionsAnd51.append(pctcModel.country_option==2)
            conditionsAnd51.append(func.json_contains(pctcModel.country_targeting,country))
            conditionsOr5.append(and_(*conditionsAnd51))
            condition.append(or_(*conditionsOr5))

        #consulta
        data = pcModel.query\
        .join(pcrpModel, and_(pcModel.iddef_promo_code == pcrpModel.iddef_promo_code, pcrpModel.estado == 1))\
        .join(pctcModel, and_(pcModel.iddef_promo_code == pctcModel.iddef_promo_code, pctcModel.estado ==1))\
        .with_entities(pcModel.iddef_promo_code, pcModel.iddef_promo_code_discount_type,\
        pcModel.name, pcModel.code, pcModel.value_discount,\
        pcModel.iddef_promo_code_type_amount, pcModel.currency_code,\
        pcModel.global_sales_limit_option, pcModel.global_sales_limit_value,\
        pcModel.maximum_nights_option, pcModel.maximum_nights_value,\
        pcrpModel.rooms_rateplan, pctcModel.market_option,\
        pcModel.booking_dates_option, pcModel.booking_dates, pcModel.booking_times,\
        pcModel.stay_dates_option, pcModel.stay_dates, pctcModel.market_targeting)\
        .filter(and_(*condition,pcModel.estado==1)).group_by(pcModel.code)
        promoDataJson = schema.dump(data, many = True)

        date_start = date_start.strftime("%Y-%m-%d")
        date_end = date_end.strftime("%Y-%m-%d")
        booking_window_date = dates.datetime.strptime(booking_window_date, '%Y-%m-%d')
        booking_window_time = dates.datetime.strptime(booking_window_time, '%H:%M')
        #validacion market option 2
        if len(promoDataJson) > 0:
            for item in promoDataJson:
                band_market, band_country , band_room, band_limit, band_night, band_stay, band_stay_time, band_travel = True, True, True, True, True, True, True, True
                #validacion market
                if market is not None:
                    if item['market_option'] == 3:
                        if len(item['market_targeting']) > 0:
                            band_market = False
                            for y in item['market_targeting']:
                                if str(y) not in id_market:
                                    band_market = True
                #validacion country
                if country is not None:
                    if item['country_option'] == 3:
                        if len(item['country_targeting']) > 0:
                            band_country = False
                            for y in item['country_targeting']:
                                if str(y) not in country:
                                    band_country = True
                #validacion room
                if room is not None:
                    if len(item['rooms_rateplan']) > 0:
                        band_room = False
                        for x in item['rooms_rateplan']:
                            if x in list_room:
                                band_room = True
                #validacion global sales limit
                if item['global_sales_limit_option'] == 2:
                    band_limit = False
                    total_book = RatesFunctions.get_book_promo_code(promo_code=item["code"])
                    if int(total_book) >0:
                        if total_book < item["global_sales_limit_value"]:
                            band_limit = True
                    else:
                        band_limit = True
                #validacion maximun nigths
                if total_nigths is not None:
                    if item['maximum_nights_option'] == 2:
                        band_night = False
                        if total_nigths <= item["maximum_nights_value"]:
                            band_night = True
                if useStay:
                    #validacion booking dates
                    band_stay = False
                    if item['booking_dates_option'] == 1:
                        band_stay = True
                    elif item['booking_dates_option'] == 2:
                        for booking_date in item["booking_dates"]:
                            booking_date_start = dates.datetime.strptime(booking_date["start_date"], '%Y-%m-%d')
                            booking_date_end = dates.datetime.strptime(booking_date["end_date"], '%Y-%m-%d')
                            if booking_date_start <= booking_window_date and booking_window_date <= booking_date_end:
                                band_stay = True
                    elif item['booking_dates_option'] == 3:
                        band_stay = True
                        for booking_date in item["booking_dates"]:
                            booking_date_start = dates.datetime.strptime(booking_date["start_date"], '%Y-%m-%d')
                            booking_date_end = dates.datetime.strptime(booking_date["end_date"], '%Y-%m-%d')
                            if booking_date_start <= booking_window_date and booking_window_date <= booking_date_end:
                                band_stay = False
                    #validacion booking dates time
                    band_stay_time = True
                    if len(item["booking_times"])>0:
                        band_stay_time = False
                        if item["booking_dates_option"] == 1:
                            band_stay_time = True
                        elif item["booking_dates_option"] == 2:
                            for booking_date in item["booking_times"]:
                                booking_date_start_time = dates.datetime.strptime(booking_date["start_time"], '%H:%M')
                                booking_date_end_time = dates.datetime.strptime(booking_date["end_time"], '%H:%M')
                                if booking_date_start_time <= booking_window_time and booking_window_time <= booking_date_end_time:
                                    band_stay_time = True
                        elif item["booking_dates_optio"] == 3:
                            band_stay_time = True
                            for booking_date in item["booking_times"]:
                                booking_date_start_time = dates.datetime.strptime(booking_date["start_time"], '%H:%M')
                                booking_date_end_time = dates.datetime.strptime(booking_date["end_time"], '%H:%M')
                                if booking_date_start_time <= booking_window_time and booking_window_time <= booking_date_end_time:
                                    band_stay_time = False
                #validacion travel
                if date_start is not None and date_end is not None:
                    band_travel = False
                    if item['stay_dates_option'] == 1:
                        band_travel = True
                    elif item['stay_dates_option'] == 2:
                        for stay_date in item["stay_dates"]:
                            stay_date_start = stay_date["start_date"]
                            stay_date_end = stay_date["end_date"]
                            if ((stay_date_start <= date_start and stay_date_end >= date_end) 
                            or (stay_date_start >= date_start and stay_date_end <= date_end) 
                            or (stay_date_start > date_start and stay_date_end > date_end 
                                and stay_date_start <= date_end and stay_date_end >= date_start) 
                            or (stay_date_start <= date_start and stay_date_end < date_end 
                                and stay_date_start < date_end and stay_date_end >= date_start)):
                                band_travel = True
                    elif item['stay_dates_option'] == 3:
                        for stay_date in item["stay_dates"]:
                            stay_date_start = stay_date["start_date"]
                            stay_date_end = stay_date["end_date"]
                            if ((stay_date_start < date_start and stay_date_end < date_end) 
                            or (stay_date_start > date_start and stay_date_end > date_end) 
                            or (stay_date_start > date_start and stay_date_end < date_end)):
                                band_travel = True

                if band_market == True and band_country == True and band_room == True and band_limit == True and band_night == True and band_stay == True and band_stay_time == True and band_travel == True:
                    in_text, value, discount_type, description = True, 0, "", ""
                    result_description = TextLModel.query\
                    .filter(TextLModel.table_name=="def_promo_code", TextLModel.attribute=="description", TextLModel.lang_code==lang_code,
                        TextLModel.id_relation==item["iddef_promo_code"], TextLModel.estado==1).first()
                    if result_description is not None:
                        description = result_description.text
                    if item["iddef_promo_code_type_amount"] != 0:
                        in_text = False
                        value = item["value_discount"]
                        data_amount = pctaModel.query.get(item["iddef_promo_code_type_amount"])
                        discount_type = data_amount.name
                    data_promocode = {
                        "iddef_promo_code": item["iddef_promo_code"],
                        "promo_code": item["code"],
                        "name": item["name"],
                        "in_text": in_text,
                        "value": value,
                        "voucher_discount_type": discount_type,
                        "description": description
                    }
                    result.append(data_promocode)
            
        return result
    
    @staticmethod
    def getPolicyDataByRatePlan(id_rate_plan, booking_start_date):
        """
            Find and return policies by rateplan ID and booking start date.

            :param id_rate_plan ID rateplan
            :param booking_start_date Booking start date

            :return Dict the follow policies:
                cancel_policy_detail Instance of models.policy_cancellation_detail.PolicyCancellationDetail
                guarantee_policy Instance of models.policy.Policy
                tax_policy Instance of models.policy.Policy
        """
        data = {}
        cancel_policy_detail = None
        guarantee_policy = None
        tax_policy = None

        if isinstance(booking_start_date,str):
            date_str = booking_start_date
        else:
            date_str = datetime.strftime(booking_start_date,'%Y-%m-%d')        
        
        cancel_policy_detail_aux = funtionsPolicy.getPolicyCancel(id_rate_plan,date_str,date_str)
        if cancel_policy_detail_aux != {}:
            cancel_policy_detail = {
                "id_policy":cancel_policy_detail_aux["iddef_policy"],
                "policy_code":cancel_policy_detail_aux["policy_code"]
            }

        guarantee_policy_aux = funtionsPolicy.getPolicyGuarantee(id_rate_plan,date_str,date_str)
        if guarantee_policy_aux != {}:
            guarantee_policy = {
                "id_policy":guarantee_policy_aux["iddef_policy"],
                "policy_code":guarantee_policy_aux["policy_code"]
            }

        tax_policy_aux = funtionsPolicy.getPolicyTaxes(id_rate_plan,date_str,date_str)
        if tax_policy_aux != {}:
            tax_policy = {
                "id_policy":tax_policy_aux["iddef_policy"],
                "policy_code":tax_policy_aux["policy_code"]
            }

        data = {
            "cancel_policy_detail": cancel_policy_detail,
            "guarantee_policy": guarantee_policy,
            "tax_policy": tax_policy
        }

        return data