from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from config import db, base
from models.rates import RatesSchema
from models.market_segment import MarketSegment as mkModel
from models.rateplan import RatePlan as rpModel, RatePlanSchema as rtSchema
from models.rateplan_prices import RatePlanPrices as rtpModel, RatePlanPricesSchema as rtpSchema
from models.room_type_category import RoomTypeCategory as rtcModel, RoomTypeCategorySchema as rtcSchema
from models.rate_plan_rooms import RatePlanRooms as rtprModel, RatePlanRoomsSchema as rtprSchema
from models.property import Property as prModel, PropertySchema as prSchema
from models.category_type_pax import CategoryTypePax as ctpModel, CategoryTypePaxSchema as ctpSchema
from models.rates_promotions import RatesPromotions as rpprModel, RatesPromotionsSchema as rpprSchema
from common.util import Util
from operator import itemgetter
from sqlalchemy import or_, and_
import datetime
from resources.rates.RatesHelper import RatesFunctions as funtions
from common.public_auth import PublicAuth
#from common.custom_log_response import CustomLogResponse

class operations():

    @staticmethod
    def update_rate_code_base_rateplan(id_rateplan,rate_base_code):
        ratePlan_data = rpModel.query.get(id_rateplan)

        ratePlan_data.rate_code_base = rate_base_code

        db.session.commit()
    
    @staticmethod
    def createPromotions(promotions, rtpData, user_name="admin"):
        
        response = []
                
        try:
            schema = rpprSchema(exclude=Util.get_default_excludes())
            for promotion in promotions:
                
                try:
                    rpprAux = rpprModel.query.filter(rpprModel.travel_win_start==promotion["travel_begin"], \
                    rpprModel.booking_win_end==promotion["travel_end"], rpprModel.estado==1, \
                    rpprModel.idpax_type == rtpData.idpax_type, \
                    rpprModel.idproperty == rtpData.idproperty, \
                    rpprModel.idrate_plan == rtpData.idrateplan, \
                    rpprModel.idroom_type_category == rtpData.idroom_type, \
                    rpprModel.promotion_code == promotion["promotion_code"] ).first()
                    
                    if rpprAux is not None:
                        #Si existe un registro actualizamos el valor y el factor unicamente
                        rpprAux.value = promotion["amount_promotion"]
                        rpprAux.factor_type = promotion["idrate_factor_type"]
                        rpprAux.usuario_ultima_modificacion = user_name
                        
                        db.session.commit()
                        
                        data = schema.dump(rpprAux)
                        
                    else:
                        #Si no existe un registro lo creamos
                        rpprData = rpprModel()
                        rpprData.promotion_code = promotion["promotion_code"]
                        rpprData.idproperty = rtpData.idproperty
                        rpprData.idrate_plan = rtpData.idrateplan
                        rpprData.idroom_type_category = rtpData.idroom_type
                        rpprData.idpax_type = rtpData.idpax_type
                        rpprData.factor_type = promotion["idrate_factor_type"]
                        rpprData.value = promotion["amount_promotion"]
                        rpprData.booking_win_start = rtpData.date_start
                        rpprData.booking_win_end = rtpData.date_end
                        rpprData.travel_win_start = promotion["travel_begin"]
                        rpprData.travel_win_end = promotion["travel_end"]
                        rpprData.estado = 1
                        rpprData.usuario_creacion = user_name
                        db.session.add(rpprData)
                        db.session.commit()
                        
                        data = schema.dump(rpprData)
                        
                except Exception as ex:
                    data = None
                    raise Exception("Error al crear/actualizar la promocion {0:s}".format(str(ex)))
                
                response.append(data)
            
        except Exception as err:
            raise Exception(str(err))
        
        return response
    
    @staticmethod
    def createRate(rtpData, user_name="admin"):
        
        schema = rtpSchema(exclude=Util.get_default_excludes())
        
        data = None
        
        try:
            
            #Verificamos si existe o no un registro con estos datos
            rtpAux = rtpModel.query.filter(rtpModel.estado == 1, \
            and_(or_
            (and_(rtpModel.date_start <= rtpData.date_start,\
            rtpModel.date_end >= rtpData.date_end),\
            and_(rtpModel.date_start >= rtpData.date_start,\
            rtpModel.date_end <= rtpData.date_end),
            and_(rtpModel.date_start <= rtpData.date_start,\
            rtpModel.date_end <= rtpData.date_end, rtpModel.date_end >= rtpData.date_start))),
            rtpModel.idpax_type == rtpData.idpax_type, \
            rtpModel.idproperty == rtpData.idproperty, \
            rtpModel.idrateplan == rtpData.idrateplan, \
            rtpModel.idroom_type == rtpData.idroom_type,
            rtpModel.is_override == 0).all()


            # cont = 0
            # rows_afected = []
            # while cont < len(rtpAux):

            #     row = {
            #         "date_start": rtpAux[cont].date_start,
            #         "date_end":rtpAux[cont].date_end,
            #         "amount":rtpAux[cont].amount,
            #         "position":cont
            #     }

            #     rows_afected.append(row)

            #     rtpAux[cont].estado = 0
            #     rtpAux[cont].usuario_ultima_modificacion = user_name
            #     db.session.commit()
            #     cont += 1


            date_end_before = rtpData.date_start - datetime.timedelta(days=1)
            date_start_after = rtpData.date_end + datetime.timedelta(days=1)

            #Creamos nuevos registros
            for item_afect in rtpAux:
                date_start = item_afect.date_start
                date_end = item_afect.date_end

                # item_afect.estado = 0
                # item_afect.usuario_ultima_modificacion = user_name
                # db.session.commit()
                db.session.delete(item_afect)

                if date_start < rtpData.date_start and date_end > rtpData.date_end:

                    new_rtp_before = rtpModel()
                    new_rtp_before.is_override = 0
                    new_rtp_before.estado = 1
                    new_rtp_before.usuario_creacion = user_name
                    new_rtp_before.date_start = date_start
                    new_rtp_before.idpax_type = rtpData.idpax_type
                    new_rtp_before.idproperty = rtpData.idproperty
                    new_rtp_before.idroom_type = rtpData.idroom_type
                    new_rtp_before.idrateplan = rtpData.idrateplan
                    new_rtp_before.amount = item_afect.amount
                    new_rtp_before.date_end = date_end_before
                    db.session.add(new_rtp_before)

                    new_rtp_after = rtpModel()
                    new_rtp_after.is_override = 0
                    new_rtp_after.estado = 1
                    new_rtp_after.usuario_creacion = user_name
                    new_rtp_after.date_start = date_start_after
                    new_rtp_after.idpax_type = rtpData.idpax_type
                    new_rtp_after.idproperty = rtpData.idproperty
                    new_rtp_after.idroom_type = rtpData.idroom_type
                    new_rtp_after.idrateplan = rtpData.idrateplan
                    new_rtp_after.amount = item_afect.amount
                    new_rtp_after.date_end = date_end
                    db.session.add(new_rtp_after)

                elif date_end > rtpData.date_end and date_start >= rtpData.date_start:

                    new_rtp = rtpModel()
                    new_rtp.is_override = 0
                    new_rtp.estado = 1
                    new_rtp.usuario_creacion = user_name
                    new_rtp.date_start = date_start_after
                    new_rtp.idpax_type = rtpData.idpax_type
                    new_rtp.idproperty = rtpData.idproperty
                    new_rtp.idroom_type = rtpData.idroom_type
                    new_rtp.idrateplan = rtpData.idrateplan
                    new_rtp.amount = item_afect.amount
                    new_rtp.date_end = date_end
                    db.session.add(new_rtp)
                
                elif date_start < rtpData.date_start and date_end <= rtpData.date_end:
                    #Creamos un registro para las fechas anteriores
                    new_rtp = rtpModel()
                    new_rtp.is_override = 0
                    new_rtp.estado = 1
                    new_rtp.usuario_creacion = user_name
                    new_rtp.date_start = date_start
                    new_rtp.idpax_type = rtpData.idpax_type
                    new_rtp.idproperty = rtpData.idproperty
                    new_rtp.idroom_type = rtpData.idroom_type
                    new_rtp.idrateplan = rtpData.idrateplan
                    new_rtp.amount = item_afect.amount
                    new_rtp.date_end = date_end_before
                    db.session.add(new_rtp)

            rtpDataAux = rtpModel()
        
            rtpDataAux.idproperty = rtpData.idproperty
            rtpDataAux.idrateplan = rtpData.idrateplan
            rtpDataAux.idroom_type = rtpData.idroom_type
            rtpDataAux.idpax_type = rtpData.idpax_type
            rtpDataAux.amount = rtpData.amount
            rtpDataAux.date_start = rtpData.date_start
            rtpDataAux.date_end = rtpData.date_end
            rtpDataAux.estado = rtpData.estado
            rtpDataAux.is_override = 0
            rtpDataAux.estado = 1
            rtpDataAux.usuario_creacion = rtpData.usuario_creacion
            
            db.session.add(rtpDataAux)
            db.session.commit()
    
            data = schema.dump(rtpDataAux)
            
        except Exception as ex:
            #data = None
            db.session.rollback()
            raise Exception("Error al crear/actualizar la tarifa "+str(ex))
        
        return data
    
    @staticmethod
    def create(rates, rtpData, maxAdult, includeChilds, user_name="admin"):
        
        response = []
        wrg=[]
        
        try:
            rtpData.date_start = rates["date_from"]
            rtpData.date_end = rates["date_to"]
            
            #Extraemos el valor del pax extra
            amoutExtra = funtions.getExtraAmount(rates["prices"])
            
            #Extraemos la informacion para los pax adultos
            adults = funtions.getAdultsInfo(rates["prices"])
            adultsRates = len(adults)
            
            #Extraemos la informacion para los pax menores
            childs = funtions.getChildsInfo(rates["prices"])
            childsRates = len(childs)
            
            #Extraemos las promociones aplicables a los pax extras
            #extrasPromotion = funtions.getPromotionsExtra(rates["prices"])
            
            cont = 0
            #Recorremos el total de pax adultos y calculamos los registros necesarios
            while cont < maxAdult:
                
                try:
                    
                    cont = cont + 1
                    
                    #Verificamos los paxes
                    if  cont > adultsRates:
                        #Si el contador es mayor al numero de rates de adultos recibidos se calcula la tarifa
                        ##Se calcula la tarifa (ultima tarifa de adulto recibida + ((cont-total de tarifas recibidas)*tarifa extra))
                        amount = adults[adultsRates-1]["amount"]+((cont-adultsRates)*amoutExtra)
                        idPaxType = funtions.getIdPaxtype(cont)
                        
                        #Seleccionamos las promociones
                        #promos=extrasPromotion
                    else:
                        #Si el contador es menor al numero de rates de adultos recibidos se toman los valores recibidos
                        amount = adults[cont-1]["amount"]
                        idPaxType = adults[cont-1]["idPax_type"]
                        
                        #Seleccionamos las promociones
                        #promos=adults[cont-1]["promo"]
                        
                    #Se setean los valores a insertar
                    rtpData.amount = amount
                    rtpData.idpax_type = idPaxType
                    
                    #Creamos/Actualizamos el registro
                    register = operations.createRate(rtpData, user_name)
                    
                    status = False
                    if register is not None:
                        status = True
                    
                    wrgPx=[]
                    # #Si existen promociones para el pax actual se intentaran registrar en la db
                    # if len(promos) > 0:
                    #     try:
                    #         #Creamos/Actualizamos las respectivas promociones
                    #         promotionsRe = operations.createPromotions(promos,rtpData, user_name)
                            
                    #         #Verificamos si todas las promociones se cargaron con exito
                    #         promosCount = 0
                    #         for itemPromotion in promotionsRe:
                            
                    #             if itemPromotion is None:
                    #                 wrgPx.append("Error al crear/actualizar la promocion {0:s} para el registro actual".format( \
                    #                     promos[promosCount]["promotion_code"]))
                                
                    #             promosCount = promosCount + 1
                                    
                    #     except Exception as promoError:
                    #         wrgPx.append("Error al intentar crear promociones, Error:"+str(promoError))
                        
                    data={
                        "msg":"Tarifa actualizada con exito",
                        "paxes":cont,
                        "group":"Adult",
                        "wrgs":wrgPx,
                        "amount":str(amount),
                        "status":status
                    }
                    response.append(data)
                    
                except Exception as exc:
                    data={
                        "msg":str(exc),
                        "paxes":cont,
                        "group":"Adult",
                        "amount":None,
                        "wrgs":wrg,
                        "status":False
                    }
                    response.append(data)                
                
            if includeChilds: 
                #Recorremos las tarifas para menores recibidas
                chCount = 0
                for childItem in childs:
                    chCount = chCount + 1                    
                    try:
                        rtpData.idpax_type = childItem["idPax_type"]
                        amount = childItem["amount"]
                        rtpData.amount = amount
                        
                        #Creamos/Actualizamos un registro para los menores
                        register = operations.createRate(rtpData, user_name)
                        
                        childStatus = False
                        if register is not None:
                            childStatus = True
                        
                        wrgChd = []
                        #Creamos las promociones
                        # if len(childItem["promo"]) > 0:
                            
                        #     promotionsRe = operations.createPromotions(childItem["promo"],rtpData, user_name)
                            
                        #     #Verificamos si todas las promociones se cargaron con exito
                        #     promosCount = 0
                        #     for itemPromotion in promotionsRe:
                            
                        #         if itemPromotion is None:
                        #             wrgChd.append("Error al crear/actualizar la promocion {0:s} para el registro actual".format( \
                        #                 childItem["promo"][promosCount]["promotion_code"]))
                                
                        #         promosCount = promosCount + 1
                                
                        
                        if register is not None:
                            data={
                                "msg":"Tarifa actualizada con exito",
                                "paxes":chCount,
                                "group":"Child",
                                "amount":str(amount),
                                "wrgs":wrgChd,
                                "status":True
                            }
                            response.append(data)
                        
                    except Exception as ex:
                        data={
                            "msg":"Tarifa actualizada con exito",
                            "paxes":chCount,
                            "group":"Child",
                            "amount": str(amount),
                            "wrgs":wrg,
                            "status":True
                        }
                        response.append(data)
                    
        except Exception as ex:
            data={
                "msg":"Tarifa actualizada con exito",
                "paxes":None,
                "group":None,
                "amount":None,
                "wrgs":wrg,
                "status":False
            }
            response.append(data)
            
        return response

class Rates_Detail(Resource):
    #api-public-push-rates-post
    #@PublicAuth.access_middleware
    #@CustomLogResponse.save
    def post(self):
        response = {}

        try:
            
            json_data = request.json
            
            schema = RatesSchema()
            
            schemaResult = rtpSchema(exclude=Util.get_default_excludes())

            data = schema.load(json_data)
            #get api-key data
            #credential_data = PublicAuth.get_credential_data()
            #user_name = credential_data.iddef_credentials
            user_name = "Clever Layers"
            
            rtpData = rtpModel()
            
            rtpData.estado = 1
            rtpData.usuario_creacion = user_name
            
            #Obtenemos el id de la propiedad
            prData = funtions.getHotelInfo(data["hotel"])
            rtpData.idproperty = prData.iddef_property

            #Obtenemos el id del rate plan
            #rpData = rpModel.query.filter(rpModel.estado==1, rpModel.code==data["rate_plan"], rpModel.idProperty==prData.iddef_property).first()
            rpData = funtions.getRateplanInfo(rate_code=data["rate_plan"],\
            property_id=rtpData.idproperty,only_rateplan=True,validate_estado=False)
            rtpData.idrateplan = rpData.idop_rateplan

            operations.update_rate_code_base_rateplan(rpData.idop_rateplan,data["rate_base_code"])

            if rpData.currency_code.upper() != data["currency_code"].upper():
                raise Exception("Rate Plan moneda no compatible, {0} to {1}".format(data["currency_code"].upper(),rpData.currency_code.upper()))
            
            #Obtenemos el id del tipo de habitacion
            rtcData = funtions.getRoomTypeInfo(idproperty=rtpData.idproperty,\
            room_type_code=data["room_type_category"], property_name=prData.property_code)
            rtpData.idroom_type = rtcData.iddef_room_type_category

            #if rtcData is not None:
            #    rtpData.idroom_type = rtcData.iddef_room_type_category
            #else:
            #    raise Exception("Room Type {0:s} no encontrado para la propiedad {1:s}, favor de verificar que el tipo de habitacion exista".format(data["room_type_category"],prData.property_code))
            
            #Verificamos que la habitacion exista para este rate plan
            rtprData = rtprModel.query.filter(rtprModel.estado==1, rtprModel.id_rate_plan==rpData.idop_rateplan, \
            rtprModel.id_room_type==rtcData.iddef_room_type_category).first()
            
            if rtprData is not None:
                pass
            else:
                raise Exception("Habitacion {0:s} no esta mapeada con el Rate Plan {1:s}".format(rtcData.room_code,rpData.code))
            
            #maxAdult = data["max_ocupancy"]
            maxAdult = rtcData.max_ocupancy
            maxChild = data["max_children"]
            includeChilds = data["include_kids"]
            
            msgs = []
            
            for rates in data["rates"]:
                
                try:
                    
                    dataAux = operations.create(rates,rtpData, maxAdult, includeChilds, user_name)
                    data = {
                        "Room_type_category":rtcData.room_code,
                        "Rate_Plan_Code":rpData.code,
                        "Date_start":str(rates["date_from"]),
                        "Date_end":str(rates["date_to"]),
                        "Items":dataAux,
                        "Msg":"Success"
                    }
                    msgs.append(data)
                    
                except Exception as ex:
                    msg = "Error al actualizar las tarifas para la habitacion {0:s} en el rate plan {1:s}  \
                    en las fechas del {2:s} hasta el {3:s}".format(rtcData.room_code, rpData.code, \
                    rates["date_from"],rates["date_to"])
                    data = {
                        "Room_type_category":rtcData.room_code,
                        "Rate_Plan_Code":rpData.code,
                        "Date_start":str(rates["date_from"]),
                        "Date_end":str(rates["date_to"]),
                        "Items":dataAux,
                        "Msg":msg
                    }
                    msgs.append(data)
                
            response = {
                "code":200,
                "error":False,
                "msg":"Success",
                "data":msgs
            }
            
        except ValidationError as error:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data": []
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": []
            }

        return response        