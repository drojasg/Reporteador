from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from sqlalchemy import or_, and_
from models.room_type_category import RoomTypeCategorySchema as ModelSchema, \
GetRoomTypeCategorySchema as GetModelSchema, RoomTypeCategory as Model, \
CreateRoomtypeSchema as createSchema, RoomTypeCategorySchemaLangs as RoomsDetailSchema, \
RoomTypeCategoryToSelect as RoomSingle, GetRoomTypeCategoryListSchema, \
PublicRoomsDetailsRq as PublicRoomDetailSchema, RoomDetailRqSchema as RoomDetailrq,\
GetRoomTypeCategoryPropertySchema as GetPRTCModelSchema, RoomTypeCategoryRoomCodeSchema
from models.amenity import Amenity as amModel, AmenitySchema as amSchema
from models.room_amenity import RoomAmenity as raModel, RoomAmenitySchema as raSchema
from models.text_lang import TextLang as txModel, TextLangSchema as txSchema, GetTextLangSchema as getTxSchema
from common.util import Util
from sqlalchemy import or_, and_
from resources.rates.RatesHelper import RatesFunctions as functions
from resources.media.MediaHelper import MediaFunctions as medFunctions
from resources.room_amenity import RoomAmenityDescriptions as ameFunctions,  ListRoomAmenity
from models.media import publicGetListMedia as mediaSchema
from models.property import Property as prModel
from models.age_code import AgeCode as agcModel
from models.rateplan import RatePlanSchema, GetRatePlanSchema, GetPublicRatePlanSchema, RatePlan as rpModel, PostRatePlanSchema, RatePlanIdSchema, RatePlanEstadoSchema, GetDataRatePlan2Schema as GetDRPModelSchema
from models.rateplan_property import RatePlanProperty as RateplanPropertyModel
from models.rate_plan_rooms import RatePlanRooms as RateplanRoomModel
from common.public_auth import PublicAuth
from resources.restriction.restricctionHelper import RestricctionFunction as resFunction
from resources.inventory.inventory import Inventory as availFunction
from resources.booking.rates_services import RatesService
from resources.booking.wire_request import WireRequest
import datetime

class RoomTypeCategory(Resource):
    #api-room-type-category-get-by-id
    # @base.access_middleware
    def get(self, id):
        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = Model.query.get(id)

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
                    "data": schema.dump(data)
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

    #api-room-type-category-put
    # @base.access_middleware
    def put(self, id):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = GetModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            model = Model.query.get(id)

            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            
            if model is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }
            if request.json.get("iddef_property") != None:
                model.iddef_property = data["iddef_property"]
            if request.json.get("iddef_room_class") != None:
                model.iddef_room_class = data["iddef_room_class"]
            if request.json.get("room_description") != None:
                model.room_description = data["room_description"]
            if request.json.get("room_code") != None:
                model.room_code = data["room_code"]
            if request.json.get("max_adt") != None:
                model.max_adt = data["max_adt"]
            if request.json.get("max_chd") != None:
                model.max_chd = data["max_chd"]
            if request.json.get("acept_chd") != None:
                model.acept_chd = data["acept_chd"]
            if request.json.get("estado") != None:
                model.estado = data["estado"]
            model.usuario_ultima_modificacion = user_name
            db.session.commit()
            #Agregar campos faltantes para insertar en la db

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(model)
            }
        except ValidationError as error:
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data": {}
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

    #api-room-type-category-delete
    # @base.access_middleware
    def delete(self, id):
        response = {}
        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())
            model = Model.query.get(id)

            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            if model is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }

            model.estado = 0
            model.usuario_ultima_modificacion = user_name
            db.session.commit()

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(model)
            }
        except ValidationError as error:
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data": {}
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

    #api-room-type-category-post
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)            
            model = Model()

            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            
            model.iddef_property = data["iddef_property"]
            model.iddef_room_class = data["iddef_room_class"]
            model.room_description = data["room_description"]
            model.room_code = data["room_code"]
            model.max_adt = data["max_adt"]
            model.max_chd = data["max_chd"]
            model.acept_chd = data["acept_chd"]
            model.estado = 1
            model.usuario_creacion = user_name
            db.session.add(model)
            db.session.commit()
            #Agregar campos faltantes para insertar en la db

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(model)
            }
        except ValidationError as error:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data" : {}
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data" : {}
            }
        
        return response

class RoomTypeCategoryListSearch(Resource):
    #api-room-type-category-get-all
    # @base.access_middleware
    def get(self):
        try:
            isAll = request.args.get("all")
            propertyId = request.args.get("property")
            properties = request.args.get("properties")

            data = Model()

            conditions = []

            conditions.append(Model.estado == 1)

            txSchema = getTxSchema()

            if isAll is not None:
                #data = Model.query.all()
                conditions.pop()

            if properties is not None:
                listProperty = properties.split(",")
                conditions.append(Model.iddef_property.in_(listProperty))

            if propertyId is not None:
                conditions.append(Model.iddef_property == propertyId)

            if len(conditions) >= 1:
                data = Model.query.filter(and_(*conditions)\
                ).order_by(Model.room_order.asc()).all()
            else:
                data = Model.query.order_by(Model.iddef_property.asc(),\
                Model.room_order.asc()).all()

            schema = RoomsDetailSchema(exclude=Util.get_default_excludes(), many=True)

            dataDump = schema.dump(data)

            if data is not None:
                
                for dataItem in dataDump:

                    textName = []
                    textDesc = []

                    
                    txtRoom_name = txModel.query.filter(\
                    txModel.table_name=="def_room_type_category", \
                    txModel.attribute == "room_name", \
                    txModel.id_relation == dataItem["iddef_room_type_category"], \
                    txModel.estado == 1)
                    
                    if txtRoom_name is not None:
                        for txItem in txtRoom_name:
                            
                            textName.append(txSchema.dump(txItem))

                    dataItem["room_description"] = textName

                    txtRom_desc = txModel.query.filter(\
                    txModel.table_name=="def_room_type_category", \
                    txModel.attribute == "room_description", \
                    txModel.id_relation == dataItem["iddef_room_type_category"], \
                    txModel.estado == 1)

                    if txtRom_desc is not None:
                        for txItem in txtRom_desc:
                            textDesc.append(txSchema.dump(txItem))

                    dataItem["description"] = textDesc

            if dataDump is None:
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
                    "data": dataDump
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

    #api-room-type_category-post-list
    # @base.access_middleware
    def post(self):
        response = {}

        try:

            request_json = request.get_json(force=True)
            model = Model()

            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            schema = createSchema()

            dataLoad = schema.load(request_json)
            #user_data = base.get_token_data()
            #user_name = user_data['user']['username']

            lastRoom_Order = Model.query.filter(Model.iddef_property == dataLoad["iddef_property"],\
            Model.estado == 1).order_by(Model.room_order.desc())

            if lastRoom_Order is not None:
                for item in lastRoom_Order:
                    if item.room_order == dataLoad["room_order"] and item.room_order > 0:
                        raise Exception("El numero de orden que intenta asignarse ya existe, porfavor verifique")

            model_property = prModel.query.get(dataLoad["iddef_property"])
            rates_service = RatesService()
            info_room_opera = rates_service.getOperaRoomCode(property_code=model_property.property_code, room_category_clever_code=dataLoad["room_code"],
                username = user_name)
            if info_room_opera["error"] == False and info_room_opera["data"] and info_room_opera["data"]["target_value"] not in (None, ""):
                room_code_opera = info_room_opera["data"]["target_value"]
            else:
                room_code_opera = dataLoad["room_code"]

            max_ocupancy_pms = 0
            is_room_of_house = 0
            
            detail_room_pms = rates_service.getOperaRoomInfo(model_property.property_code, \
                dataLoad["room_code"],user_name)

            if detail_room_pms["error"]==False:
                max_ocupancy_pms = detail_room_pms["data"]["max_ocupancy"]
                is_room_of_house = 1 if detail_room_pms["data"]["type_ro"] == "ROH" else 0

            estado = 1
            if request.json.get("estado") is not None:
                estado = dataLoad["estado"]

            description_txt_default = ""
            for description in dataLoad["names"]:
                if description["lang_code"].upper() == "EN":
                    description_txt_default = description["text"]
            
            model.iddef_property = dataLoad["iddef_property"]
            model.room_description = description_txt_default
            model.room_code = dataLoad["room_code"]
            model.room_code_opera = room_code_opera
            model.max_ocupancy_pms = max_ocupancy_pms
            model.is_room_of_house = is_room_of_house
            model.max_adt = dataLoad["max_adt"]
            model.max_chd = dataLoad["max_chd"]
            model.acept_chd = dataLoad["acept_chd"]
            if model.acept_chd == 1:
                if model.max_adt == 0:
                    model.single_parent_policy = 0
                else:
                    if dataLoad["single_parent_policy"] > model.max_adt:
                        raise Exception("Error is single_parent_policy:"+ str(dataLoad["single_parent_policy"]) +" > max_adt:" +str(model.max_adt))
                    else:
                        model.single_parent_policy = dataLoad["single_parent_policy"]
            model.smoking = dataLoad["smoking"]
            model.min_adt = dataLoad["min_adt"]
            model.min_chd = dataLoad["min_chd"]
            model.standar_ocupancy = dataLoad["standar_ocupancy"]
            model.area = dataLoad["area"]
            model.area_unit = dataLoad["area_unit"]
            model.max_ocupancy = dataLoad["max_ocupancy"]
            model.min_ocupancy = dataLoad["min_ocupancy"]
            model.room_order = dataLoad["room_order"]
            model.market_option = dataLoad["market_option"]
            model.market_targeting = dataLoad["market_targeting"]
            model.estado = estado
            model.usuario_creacion = user_name
            db.session.add(model)
            db.session.commit()
            #Agregar campos faltantes para insertar en la db

            if model.iddef_room_type_category > 0:

                for description in dataLoad["description"]:
                    textModel = txModel()
                    textModel.lang_code = description["lang_code"]
                    textModel.text = description["text"]
                    textModel.table_name = "def_room_type_category"
                    textModel.id_relation = model.iddef_room_type_category
                    textModel.attribute = "room_description"
                    textModel.estado = 1
                    textModel.usuario_creacion = user_name
                    db.session.add(textModel)
                    db.session.commit()
                
                for texts in dataLoad["names"]:
                    textModel = txModel()
                    textModel.lang_code = texts["lang_code"]
                    textModel.text = texts["text"]
                    textModel.table_name = "def_room_type_category"
                    textModel.id_relation = model.iddef_room_type_category
                    textModel.attribute = "room_name"
                    textModel.estado = 1
                    textModel.usuario_creacion = user_name
                    db.session.add(textModel)
                    db.session.commit()

                for amenities in dataLoad["amenities"]:
                    if amenities["estado"] == 1:
                        gotAmenity = amModel.query.filter(amModel.name == amenities["nombre"]).first()
                        amSchemaRes = amSchema(exclude=Util.get_default_excludes())
                        amenitiItem = amSchemaRes.dump(gotAmenity)
                        arModel = raModel()
                        arModel.iddef_amenity = amenitiItem["iddef_amenity"]
                        arModel.iddef_room_type_category = model.iddef_room_type_category
                        arModel.is_priority = amenities["is_priority"]
                        arModel.usuario_creacion = user_name
                        arModel.estado = 1
                        db.session.add(arModel)
                        db.session.commit()

            else:
                db.session.rollback()
                response = {
                    "Code": 500,
                    "Msg": "no se pudo crear el room type especificado",
                    "Error": True,
                    "data" : {}
                }

            rtSchema = ModelSchema(exclude=Util.get_default_excludes())

            dumpRoom = rtSchema.dump(model)

            amenitiesGet = ListRoomAmenity.get(self,dumpRoom["iddef_property"],dumpRoom["iddef_room_type_category"])
            resDump = {
                "room":dumpRoom,
                "amenities":amenitiesGet["data"]
            }

            response = {
                "Code":200,
                "Msg":"Success",
                "Error":False,
                "data": resDump
            }

        except ValidationError as error:
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data": {}
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data" : {}
            }

        return response

    #api-room-type_category-put-list
    # @base.access_middleware
    def put(self,roomtype):
        response = {}

        try:

            request_json = request.get_json(force=True)
            model = Model()
            rates_service = RatesService()

            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            data = model.query.get(roomtype)

            schema = createSchema()

            dataLoad = schema.load(request_json)
            # user_data = base.get_token_data()
            # user_name = user_data['user']['username']

            model_property = prModel.query.get(dataLoad["iddef_property"])

            if data.room_order != dataLoad["room_order"]:
                lastRoom_Order = Model.query.filter(Model.iddef_property == dataLoad["iddef_property"],\
                Model.estado == 1).order_by(Model.room_order.desc())

                if lastRoom_Order is not None:
                    for item in lastRoom_Order:
                        if item.room_order == dataLoad["room_order"] and item.room_order > 0:
                            raise Exception("El numero de orden que intenta asignarse ya existe, porfavor verifique")

            if data.room_code != dataLoad["room_code"] or data.room_code_opera=="":
                #model_property = prModel.query.get(dataLoad["iddef_property"])
                #rates_service = RatesService()
                info_room_opera = rates_service.getOperaRoomCode(property_code=model_property.property_code, room_category_clever_code=dataLoad["room_code"],
                    username = user_name)
                if info_room_opera["error"] == False and info_room_opera["data"] and info_room_opera["data"]["target_value"] not in (None, ""):
                    room_code_opera = info_room_opera["data"]["target_value"]
                else:
                    room_code_opera = dataLoad["room_code"]
            else:
                room_code_opera = data.room_code_opera

            
            max_ocupancy_pms = data.max_ocupancy_pms
            is_room_of_house = data.is_room_of_house

            detail_room_pms = rates_service.getOperaRoomInfo(model_property.property_code, \
                dataLoad["room_code"],user_name)

            if detail_room_pms["error"]==False:
                max_ocupancy_pms = detail_room_pms["data"]["max_ocupancy"]
                is_room_of_house = 1 if detail_room_pms["data"]["type_ro"] == "ROH" else 0

            estado = 1
            if request.json.get("estado") is not None:
                estado = dataLoad["estado"]

            description_txt_default = ""
            for description in dataLoad["names"]:
                if description["lang_code"].upper() == "EN":
                    description_txt_default = description["text"]
            
            data.iddef_property = dataLoad["iddef_property"]
            data.room_description = description_txt_default
            data.room_code = dataLoad["room_code"]
            data.max_ocupancy_pms = max_ocupancy_pms
            data.room_code_opera = room_code_opera
            data.is_room_of_house = is_room_of_house
            data.max_adt = dataLoad["max_adt"]
            data.max_chd = dataLoad["max_chd"]
            data.acept_chd = dataLoad["acept_chd"]
            if data.acept_chd == 1:
                if model.max_adt == 0:
                    model.single_parent_policy = 0
                else:
                    if dataLoad["single_parent_policy"] > data.max_adt:
                        raise Exception("Error is single_parent_policy:"+ str(dataLoad["single_parent_policy"]) +" > max_adt:" +str(data.max_adt))
                    else:
                        data.single_parent_policy = dataLoad["single_parent_policy"]
            data.smoking = dataLoad["smoking"]
            data.min_adt = dataLoad["min_adt"]
            data.min_chd = dataLoad["min_chd"]
            data.standar_ocupancy = dataLoad["standar_ocupancy"]
            data.area = dataLoad["area"]
            data.area_unit = dataLoad["area_unit"]
            data.max_ocupancy = dataLoad["max_ocupancy"]
            data.min_ocupancy = dataLoad["min_ocupancy"]
            data.room_order = dataLoad["room_order"]
            data.market_option = dataLoad["market_option"]
            data.market_targeting = dataLoad["market_targeting"]
            data.estado = estado
            data.usuario_ultima_modificacion = user_name
            db.session.flush()
            #Agregar campos faltantes para insertar en la db

            for texts in dataLoad["names"]:
                textModel = txModel()
                textName = textModel.query.filter(txModel.estado==1,\
                txModel.id_relation==roomtype,\
                txModel.table_name=="def_room_type_category",\
                txModel.lang_code==texts["lang_code"], \
                txModel.attribute=="room_name").first()
                
                if textName is not None:
                    textName.lang_code = texts["lang_code"]
                    textName.text = texts["text"]
                    textName.table_name = "def_room_type_category"
                    textName.id_relation = roomtype
                    textName.attribute = "room_name"
                    textName.estado = 1
                    textName.usuario_ultima_modificacion = user_name
                    db.session.flush()
                else:
                    textModel.lang_code = texts["lang_code"]
                    textModel.text = texts["text"]
                    textModel.table_name = "def_room_type_category"
                    textModel.id_relation = roomtype
                    textModel.attribute = "room_name"
                    textModel.estado = 1
                    textModel.usuario_creacion = user_name
                    db.session.add(textModel)
                    db.session.commit()

            for description in dataLoad["description"]:
                textModel = txModel()
                textData = textModel.query.filter(txModel.estado==1,\
                txModel.id_relation==roomtype,\
                txModel.table_name=="def_room_type_category",\
                txModel.lang_code==description["lang_code"], \
                txModel.attribute=="room_description").first()

                if textData is not None:
                    textData.lang_code = description["lang_code"]
                    textData.text = description["text"]
                    textData.table_name = "def_room_type_category"
                    textData.id_relation = roomtype
                    textData.attribute = "room_description"
                    textData.estado = 1
                    textData.usuario_ultima_modificacion = user_name
                    db.session.flush()
                else:
                    textModel.lang_code = description["lang_code"]
                    textModel.text = description["text"]
                    textModel.table_name = "def_room_type_category"
                    textModel.id_relation = roomtype
                    textModel.attribute = "room_description"
                    textModel.estado = 1
                    textModel.usuario_creacion = user_name
                    db.session.add(textModel)
                    db.session.commit()

            #desactivar amenidades
            dataAmenity = raModel.query.filter_by(iddef_room_type_category=roomtype).all()
            if len(dataAmenity) > 0:
                for x in dataAmenity:
                    updateRA = raModel.query.get(x.iddef_room_amenity)
                    updateRA.estado = 0
                    db.session.commit()

            #Actualizar amenidades a activas
            for amenities in dataLoad["amenities"]:
                gotAmenity = amModel.query.filter(amModel.estado==1, \
                amModel.name == amenities["nombre"]).first()

                arModel = raModel()
                amenity = raModel.query.filter(raModel.iddef_amenity==gotAmenity.iddef_amenity, raModel.iddef_room_type_category==roomtype).first()

                if amenity is not None:
                    amenity.is_priority = amenities["is_priority"]
                    amenity.estado = amenities["estado"]
                    amenity.usuario_ultima_modificacion = user_name
                    db.session.commit()
                else:
                    arModel.iddef_amenity = gotAmenity.iddef_amenity
                    arModel.iddef_room_type_category = data.iddef_room_type_category
                    arModel.is_priority = amenities["is_priority"]
                    arModel.usuario_creacion = user_name
                    arModel.estado = 1
                    db.session.add(arModel)
                    db.session.commit()

                
            rtSchema = ModelSchema(exclude=Util.get_default_excludes())

            dumpRoom = rtSchema.dump(data)

            amenitiesGet = ListRoomAmenity.get(self,dumpRoom["iddef_property"],dumpRoom["iddef_room_type_category"])

            resDump = {
                "room":dumpRoom,
                "amenities":amenitiesGet["data"]
            }

            response = {
                "Code":200,
                "Msg":"Success",
                "Error":False,
                "data": resDump
            }

        except ValidationError as error:
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data": {}
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data" : {}
            }

        return response

class RoomTypeCategorySingle(Resource):
    # @base.access_middleware
    def get(self):
        try:
            
            isAll = request.args.get("all")
            properties = request.args.get("properties")

            conditions = []

            conditions.append(Model.estado == 1)

            if isAll is not None:
                #data = Model.query.all()
                conditions.pop()

            if properties is not None:
                listProperty = properties.split(",")
                conditions.append(Model.iddef_property.in_(listProperty))

            if len(conditions) >= 1:
                data = Model.query.filter(and_(*conditions)\
                ).order_by(Model.iddef_property, Model.room_order.asc()).all()
            else:
                data = Model.query.order_by(Model.iddef_property.asc(),\
                Model.room_order.asc()).all()

            schema = RoomSingle(exclude=Util.get_default_excludes(),many=True)
            txSchema = getTxSchema()

            dataDump = schema.dump(data)

            if data is not None:
                
                for dataItem in dataDump:

                    

                    prData = prModel.query.get(dataItem["iddef_property"])

                    if prData is not None:
                        dataItem["property_code"] = prData.property_code
                    else:
                        dataItem["property_code"] = None

                    textName = []

                    

                    txtRoom_name = txModel.query.filter(\
                    txModel.table_name=="def_room_type_category", \
                    txModel.attribute == "room_name", \
                    txModel.id_relation == dataItem["iddef_room_type_category"], \
                    txModel.estado == 1)
                    
                    if txtRoom_name is not None:
                        for txItem in txtRoom_name:
                            textName.append(txSchema.dump(txItem))

                    dataItem["room_name"] = textName

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
                    "data": dataDump
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

class RoomTypeForPropertyToRatePlan(Resource):
    # @base.access_middleware
    def get(self, propertyId, rateplanId):

        response = {}

        try:

            schema = ModelSchema(exclude=Util.get_default_excludes())
            dataResponse = []

            data = Model.query.filter(Model.iddef_property==propertyId, \
            Model.estado ==1)

            rooms_in_rate_plan = []
            if rateplanId != 0:

                try:

                    rooms_for_rate_plan = functions.getRoomTypesForRatePlan(rate_plan_id=rateplanId,\
                    property_id=propertyId)

                    rooms_in_rate_plan = [item.iddef_room_type_category for item in rooms_for_rate_plan]
                    
                except Exception as rooms_rates_ex:
                    pass

            for room in data:

                roomId = room.iddef_room_type_category

                room_name = functions.getTextLangInfo("def_room_type_category",\
                "room_name","en",roomId)

                room.room_description = room_name.text

                if len(rooms_in_rate_plan) > 0:
                    if roomId not in rooms_in_rate_plan:
                        room.estado = 0
                else:
                    room.estado = 0

                dataResponse.append(schema.dump(room))

            response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": dataResponse
                }

        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

class RoomTypesRateplan(Resource):
    #api-room-type-category-rateplan-get-all
    # @base.access_middleware
    def get(self,id_property, id_rateplan):

        response = {}

        try:

            schema = ModelSchema(exclude=Util.get_default_excludes(),many=True)

            data = functions.getRoomTypesForRatePlan(rate_plan_id=id_rateplan,\
            property_id=id_property)

            cont_data = 0
            total_data = len(data)
            while cont_data < total_data :

                room_name = functions.getTextLangInfo("def_room_type_category",\
                "room_name","en",data[cont_data].iddef_room_type_category)

                if room_name is not None:
                    data[cont_data].room_description = room_name.text

                cont_data += 1

            response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": schema.dump(data)
                }

        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

class RoomTypeCategoryDefaultList(Resource):
    # @base.access_middleware
    def get(self):
        try:
            lang_code = request.args.get("lang_code", "EN")

            schema = GetRoomTypeCategoryListSchema()
            data = Model.query\
            .join(txModel, and_(txModel.id_relation == Model.iddef_room_type_category))\
            .add_columns(Model.iddef_room_type_category, Model.room_code, (txModel.text).label("room_name"))\
            .filter(txModel.table_name == "def_room_type_category", Model.estado==1, txModel.estado==1, txModel.lang_code == lang_code, txModel.attribute == 'room_name')\
            .group_by(Model.room_code).all()

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
                    "data": schema.dump(data, many=True)
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response


class publicRoomTypeDetail(Resource):

    #api-public-room-type-category-detail-post
    #@PublicAuth.access_middleware
    def post(self):

        response = {}
        db.session.autoflush = False

        try:

            requestData = request.get_json(force=True)
            schema = PublicRoomDetailSchema()
            data = schema.load(requestData)
            market = data["market"]
            language = data["lang_code"]
            property_detail = functions.getHotelInfo(data["property_code"])
            propertyId = property_detail.iddef_property
            market_info = functions.getMarketInfo(market,language)
            idmarket = market_info.iddef_market_segment

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
                    raise Exception(Util.t(language, "restrictions_rooms_empty_pax"))

                list_rooms=[]
                if request.json.get("roomtype") is None:
                	roomsByProperty = Model.query.filter(Model.iddef_property==propertyId,\
                	Model.estado==1).all()
                else:
                	roomsByProperty = Model.query.filter(Model.iddef_property==propertyId, Model.room_code==data["roomtype"],\
                	Model.estado==1).all()
                if len(roomsByProperty) > 0:
                    for roomItem in roomsByProperty:
                    	if (roomItem.market_option == 0) or\
                    	(roomItem.market_option == 1 and market_info.code in roomItem.market_targeting) or\
                    	(roomItem.market_option == 2 and market_info.code not in roomItem.market_targeting):
                        	list_rooms.append(roomItem.iddef_room_type_category)
                    data["rooms"]=list_rooms

            rooms_detail = []

            roomSchema = RoomDetailrq()
            for itemRq in data["rooms"]:

                try:
                    msj = ""
                    roomInfo = Model.query.get(itemRq)

                    try:

                        date_end_checkout = data["date_end"] - datetime.timedelta(days=1)

                        """ data_rateplans = rpModel.query.join(RateplanPropertyModel,\
                        RateplanPropertyModel.id_rateplan == rpModel.idop_rateplan\
                        ).join(RateplanRoomModel,RateplanRoomModel.id_rate_plan == RateplanPropertyModel.id_rateplan\
                        ).filter(RateplanPropertyModel.estado==1,\
                        RateplanPropertyModel.id_property == propertyId,\
                        RateplanRoomModel.id_room_type == itemRq).all() """

                        data_rateplans = functions.getRateplanInfo(property_id=propertyId,\
                        date_start=data["date_start"],date_end=data["date_end"],bookin_window=True,\
                        only_one=False,market_id=idmarket,country=market,roomid=itemRq,language=language)

                        if len(data_rateplans) > 0:
                            list_rateplans = [rateplan_elem.idop_rateplan for rateplan_elem in data_rateplans]

                            #Buscamos las fechas cerradas para la habitacion
                            close_info = resFunction.getCloseDatesOperaRestriction(\
                            data["date_start"],date_end_checkout,propertyId,\
                            itemRq,list_rateplans)
                            #Validamos las fechas cerradas
                            rates_for_room = len(close_info)
                            if rates_for_room >= 1:
                                cont_rates_close = 0
                                for close in close_info:                                    
                                    for close_detail in close["dates"]:
                                        if close_detail["close"] == True:
                                            cont_rates_close += 1
                                            break

                                #Si todos los rateplans tienen por lo menos una fecha cerrada
                                if cont_rates_close == rates_for_room:
                                    raise Exception(Util.t(language, "restrictions_rooms_not_available"))

                            min_info = resFunction.getMinLosOperaRestriction(\
                            data["date_start"],date_end_checkout,propertyId,\
                            itemRq,list_rateplans)
                            if len(min_info) >= 1:
                                total_lenght = data["date_end"]-data["date_start"]
                                if min_info[0]["dates"][0]["min_los"] != 0:
                                    if total_lenght.days < min_info[0]["dates"][0]["min_los"]:
                                        raise Exception(Util.t(language, "restrictions_rooms_minimum_nights", str(min_info[0]["dates"][0]["min_los"])))

                            max_info = resFunction.getMaxLosOperaRestriction(\
                            data["date_start"],date_end_checkout,propertyId,\
                            itemRq,list_rateplans)
                            if len(max_info) >= 1:
                                total_lenght = data["date_end"]-data["date_start"]
                                if max_info[0]["dates"][0]["max_los"] != 0:
                                    if total_lenght.days > max_info[0]["dates"][0]["max_los"]:
                                        raise Exception(Util.t(language, "restrictions_rooms_maximum_nights", str(max_info[0]["dates"][0]["max_los"])))
                        
                        avail_data = availFunction.get_disponibilidad(date_start=data["date_start"],\
                        date_end=date_end_checkout,room_code=roomInfo.room_code,only_one=False,\
                        id_property=roomInfo.iddef_property)

                        if avail_data is not None:
                            #total_lenght = data["date_end"]-data["date_start"]
                            for avail_dates in avail_data:
                                if avail_dates.avail_rooms <= 0:
                                    raise Exception(Util.t(language, "restrictions_rooms_not_available_dates"))
                                    #print(avail_data)
                        else:
                            raise Exception(Util.t(language, "restrictions_rooms_not_available_enough"))
                        
                        if get_pax == True:
                            if contains_childs == True and bool(roomInfo.acept_chd) == False:
                                raise Exception(Util.t(language, "restrictions_rooms_not_allow_children"))                                

                            if roomInfo.max_adt < adultos:
                                raise Exception(Util.t(language, "restrictions_rooms_not_allow_adults", roomInfo.max_adt))

                            if roomInfo.max_chd < menores:
                                raise Exception(Util.t(language, "restrictions_rooms_not_allow_max_children", roomInfo.max_chd))

                            if roomInfo.min_adt > adultos:
                                raise Exception(Util.t(language, "restrictions_rooms_min_adults_required", roomInfo.min_adt))

                            if roomInfo.min_ocupancy > totalPax:
                                raise Exception(Util.t(language, "restrictions_rooms_min_occ_required", roomInfo.min_ocupancy))

                            if roomInfo.max_ocupancy < totalPax:
                                raise Exception(Util.t(language, "restrictions_rooms_max_occ_required", roomInfo.max_ocupancy))

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

class RoomTypesProperty(Resource):
    #api-room-type-category-property-get-all
    def get(self,property_code):

        response = {}

        try:
            result = []
            schema = GetPRTCModelSchema(exclude=Util.get_default_excludes(),many=True)

            data_property = functions.getHotelInfo(property_code)
            id_property = data_property.iddef_property
            if id_property:
                data = Model.query.filter(Model.iddef_property == id_property,\
                Model.estado == 1).all()
                data_result = schema.dump(data)
                if len(data) > 0:
                    for x in data_result:
                        x["description"] = x["area_code"]["description"]
                        x["unit_code"] = x["area_code"]["unit_code"]
                        x.pop('area_code')
                        result.append(x)
            else:
                raise Exception("The property code %s invalid" % property_code)

            response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": result
                }

        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response        

class RoomTypeCategoryCodeOpera(Resource):
    #api-room-type-category-code-get
    # @base.access_middleware
    def post(self):

        response = ""

        try:
            result = {}
            requestData = request.get_json(force=True)
            schema = RoomTypeCategoryRoomCodeSchema()
            data = schema.load(requestData)

            prData = prModel.query.get(data["id_property"])

            info_room_type_category = Model.query.filter(Model.room_code==data["room_code"], 
            	Model.iddef_property==data["id_property"], Model.estado==1).first()

            if info_room_type_category is None:
            	raise Exception("Room not found")
            if info_room_type_category.room_code_opera == "":
            	raise Exception("Room Code Opera is empty")

            wire_request = WireRequest()
            result = wire_request._set_bed_tipe(info_room_type_category.room_code_opera,\
            data["adults"],data["childs"],data["room_code"],prData.property_code)

            response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": result
                }

        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": ""
            }

        return response
