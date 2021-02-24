from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from config import base
from datetime import date, datetime, timedelta
from sqlalchemy.sql.expression import and_
from models.book_hotel import BookHotel as bhModel
from models.book_hotel_room import BookHotelRoom as bhrModel, BookModifyRoomSchema as bhrSchema
from resources.restriction.restricctionHelper import RestricctionFunction as resFunction
from resources.inventory.inventory import Inventory as availFunction
from common.public_auth import PublicAuth
from resources.rates.RatesHelper import RatesFunctions as functions
from resources.media.MediaHelper import MediaFunctions as medFunctions
from resources.room_amenity import RoomAmenityDescriptions as ameFunctions,  ListRoomAmenity
from models.media import publicGetListMedia as mediaSchema
from models.property import Property as prModel
from models.age_code import AgeCode as agcModel
from models.room_type_category import RoomTypeCategorySchema as ModelSchema, \
GetRoomTypeCategorySchema as GetModelSchema, RoomTypeCategory as Model,\
PublicRoomsDetailsRq as PublicRoomDetailSchema, RoomDetailRqSchema as RoomDetailrq

class BookRoomsModify(Resource):
    #api-internal-booking-rooms-post
    def get(self,idbooking):

        try:
            schema = bhrSchema()

            data = bhrModel.query.join(bhModel,bhModel.idbook_hotel==bhrModel.idbook_hotel)\
            .filter(bhModel.idbook_hotel==idbooking, bhrModel.estado==1,bhModel.estado==1).all()

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(data,many=True)
            }

        except ValidationError as error:
            #db.session.rollback()
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

    #@base.access_middleware
    def post(self):

        response = {}

        try:

            requestData = request.get_json(force=True)
            schema = PublicRoomDetailSchema()
            data = schema.load(requestData)
            market = data["market"]
            language = data["lang_code"]
            property_detail = functions.getHotelInfo(data["property_code"])
            propertyId = property_detail.iddef_property

            property_media = medFunctions.GetMediaProperty(idProperty=propertyId,\
            MediaType=1,only_one=False)

            adultos = 0
            menores = 0
            contains_childs = False
            totalPax = 0
            get_pax = False
            if request.json.get("pax") is not None:
                get_pax = True
                #Esto depende de la tabla
                agcData = agcModel.query.filter(agcModel.estado==1).all()

                age_code = [item.code for item in agcData]

                for paxes in data["pax"].keys():
                    if paxes in age_code:
                        if paxes.lower() == "adults":
                            adultos += data["pax"][paxes]
                        else:
                            menores += data["pax"][paxes]

                if menores > 0:
                    contains_childs = True

                totalPax = adultos + menores
            

            if request.json.get("rooms") is None:

                if get_pax == False:
                    raise Exception("No se puede obtener informacion de cuartos, necesita los seleccionar los pax para el viaje")

                list_rooms=[]
                roomsByProperty = Model.query.filter(Model.iddef_property==propertyId,\
                Model.estado==1).all()
                if len(roomsByProperty) > 0:
                    for roomItem in roomsByProperty:
                        list_rooms.append(roomItem.iddef_room_type_category)
                    data["rooms"]=list_rooms

            rooms_detail = []

            roomSchema = RoomDetailrq()
            for itemRq in data["rooms"]:

                try:
                    msj = ""
                    roomInfo = Model.query.get(itemRq)

                    try:

                        # close_info = resFunction.getCloseDatesOperaRestriction(data["date_start"],\
                        # data["date_end"],propertyId,itemRq,[])
                        # print(close_info)
                        date_end_checkout = data["date_end"] - datetime.timedelta(days=1)

                        close_room_info = resFunction.getOperaRestrictions(id_restriction_type=[1],\
                        id_restriction_by=3,id_room_type=itemRq,id_property=roomInfo.iddef_property,\
                        date_start=data["date_start"], date_end=date_end_checkout,estado=1)

                        if len(close_room_info) >= 1:
                            raise Exception("La habitacion no esta disponible para las fechas seleccionadas")

                        min_room_info = resFunction.getOperaRestrictions(id_restriction_by=3,\
                        id_restriction_type=[2],id_room_type=itemRq,\
                        id_property=roomInfo.iddef_property,date_start=data["date_start"],\
                        date_end=date_end_checkout,estado=1)

                        if len(min_room_info) >= 1:
                            total_lenght = data["date_end"]-data["date_start"]
                            if total_lenght.days < min_room_info[0].value:
                                raise Exception("Estancia minima de "+str(min_room_info[0].value)+" noches necesaria")

                        max_room_info = resFunction.getOperaRestrictions(id_restriction_by=3,\
                        id_restriction_type=[3],id_room_type=itemRq,\
                        id_property=roomInfo.iddef_property,date_start=data["date_start"],\
                        date_end=date_end_checkout,estado=1)

                        if len(max_room_info) >= 1:
                            total_lenght = data["date_end"]-data["date_start"]
                            if total_lenght.days > max_room_info[0].value:
                                raise Exception("Estancia maxima de "+str(max_room_info[0].value)+" noches necesaria")

                        avail_data = availFunction.get_disponibilidad(date_start=data["date_start"],\
                        date_end=date_end_checkout,room_code=roomInfo.room_code,only_one=False,\
                        id_property=roomInfo.iddef_property)

                        if avail_data is not None:
                            #total_lenght = data["date_end"]-data["date_start"]
                            for avail_dates in avail_data:
                                if avail_dates.avail_rooms <= 0:
                                    raise Exception("No hay disponibilidad suficiente para uan fecha seleccionada")
                                    #print(avail_data)
                        else:
                            raise Exception("Habitacion sin disponibilidad suficiente")
                        
                        if get_pax == True:
                            if contains_childs == True and bool(roomInfo.acept_chd) == False:
                                raise Exception("La habitacion no permite menores")

                            if roomInfo.max_adt < adultos:
                                raise Exception("La habitacion no soporta mas de "+roomInfo.max_adt+" adultos")

                            if roomInfo.max_chd < menores:
                                raise Exception("La habitacion no soporta mas de "+roomInfo.max_chd+" mas")

                            if roomInfo.min_adt > adultos:
                                raise Exception("La habitacion necesita almenos "+roomInfo.min_adt+" adultos")

                            if roomInfo.min_ocupancy > totalPax:
                                raise Exception("La habitacion necesita almenos "+roomInfo.min_ocupancy+" ocupantes")

                            if roomInfo.max_ocupancy < totalPax:
                                raise Exception("La habitacion soporta maximo "+roomInfo.max_ocupancy+" ocupantes")

                    except Exception as validatioError:
                            roomInfo.estado = 0
                            msj = str(validatioError)

                    market_code = ["US","CA"]
                    equival_ft = 10.764
                    if market in (market_code):
                        area = roomInfo.area
                        unit = roomInfo.area_unit
                        if roomInfo.area_unit == 2: #convertir a ft2
                            area = roomInfo.area * equival_ft
                            unit = 1
                    else:
                        area = roomInfo.area
                        unit = roomInfo.area_unit
                        if roomInfo.area_unit == 1: #convertir a mt2
                            area = roomInfo.area / equival_ft
                            unit = 2
                    roomInfo.area = round(area,2)
                    roomInfo.area_unit = unit

                    roomDump = roomSchema.dump(roomInfo)

                    roomDump["msg"] = msj

                    roomName = functions.getTextLangInfo("def_room_type_category","room_name",\
                    language,itemRq)
                    if roomName is not None:
                        roomDump["room_description"] = roomName.text
                    else:
                        roomDump["room_description"] = ""
                    
                    roomDescription = functions.getTextLangInfo("def_room_type_category",\
                    "room_description",language,itemRq)
                    if roomDescription is not None:
                        roomDump["description"] = roomDescription.text
                    else:
                        roomDump["description"] = ""
                    
                    media = medFunctions.GetMediaRoom(idRoom=itemRq,only_one=False)
                    schema2 = mediaSchema(many=True)
                    mediaDump = schema2.dump(media)
                    roomDump["room_media"] = mediaDump
                    amenities = ameFunctions.get_amenities_by_room_type_lang(itemRq,language)
                    roomDump["room_amenities"] = amenities
                    rooms_detail.append(roomDump)

                except Exception as roomError:
                    pass

            data = {
                "property_media":property_media,
                "rooms_detail":rooms_detail
            }

            dataDump = schema.dump(data)
            
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": rooms_detail
            }

        except ValidationError as error:
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data": {}
            }
        except Exception as ex:
            response = {
                "Code": 500,
                "Msg": str(ex),
                "Error": True,
                "data": {}
            }

        return response
