from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db,base
from models.room_type_category import RoomTypeCategory as RtModel, RoomTypeCategorySchema as RtSchema
from models.amenity import Amenity as AmModel, AmenitySchema as AmSchema, GetAmenitySchema as GetListAmenitySchema
from models.property import Property as PrModel, PropertySchema as PrSchema
from models.amenity_group import AmenityGroup as AmgModel, AmenityGroupSchema as AmgSchema
from models.amenity_type import AmenityType as AmtModel, AmenityTypeSchema as AmtSchema
from models.room_amenity import RoomAmenitySchema as ModelSchema, GetRoomAmenitySchema as GetModelSchema, RoomAmenity as Model, RoomAmenityDescription
from models.room_amenity import GetRoomAmenityDumpSchema as dumpSchema
from models.text_lang import TextLang, GetTextLangSchema
from common.util import Util
from sqlalchemy.sql.expression import and_


class RoomAmenity(Resource):
    #api-room-amenity-get-by-id
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

    #api-room-amenity-put
    # @base.access_middleware
    def put(self, id):
        response = {}
        try:
            json_data = request.json
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
            if request.json.get("iddef_amenity") != None:
                model.iddef_amenity = data["iddef_amenity"]
            if request.json.get("iddef_room_type_category") != None:
                model.iddef_room_type_category = data["iddef_room_type_category"]
            if request.json.get("estado") != None:
                model.estado = data["estado"]
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

    #api-room-amenity-delete
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

    #api-room-amenity-post
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.json
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)            
            model = Model()
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            
            model.iddef_amenity = data["iddef_amenity"]
            model.iddef_room_type_category = data["iddef_room_type_category"]
            model.estado = 1
            model.usuario_creacion = user_name
            db.session.add(model)
            db.session.commit()

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

class RoomAmenityListSearch(Resource):
    #api-room-amenity-get-all
    # @base.access_middleware
    def get(self):
        try:
            isAll = request.args.get("all")

            data = Model()

            if isAll is not None:
                data = Model.query.all()
            else:
                data = Model.query.filter(Model.estado==1)

            schema = ModelSchema(exclude=Util.get_default_excludes(), many=True)

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

class ListRoomAmenity(Resource):
    #api-room-amenity-get-parameters
    # @base.access_middleware
    def get(self,idProperty,idRoom):
        
        response = {}

        try:
            
            data = Model.query.join(AmModel, \
            Model.iddef_amenity == AmModel.iddef_amenity).join(RtModel, \
            RtModel.iddef_room_type_category == Model.iddef_room_type_category).join( \
            PrModel, RtModel.iddef_property == PrModel.iddef_property).join(AmgModel, \
            AmModel.iddef_amenity_group == AmgModel.iddef_amenity_group).join(AmtModel, \
            AmModel.iddef_amenity_type == AmtModel.iddef_amenity_type).filter( \
            Model.iddef_room_type_category == idRoom, \
            PrModel.iddef_property == idProperty, AmtModel.iddef_amenity_type == 2, \
            Model.estado==1).all()
            
            dataAmenities = AmModel.query.filter(AmModel.iddef_amenity_type == 2, \
            AmModel.estado == 1).order_by(AmModel.iddef_amenity_group.asc())

            dataResponse = []
            aux = 0
            lastName = ""
            items = []

            schemaAm = GetListAmenitySchema(exclude=Util.get_default_excludes())
            schemaAmRom = GetModelSchema(exclude=Util.get_default_excludes())

            totalRegistros = len(schemaAm.dump(dataAmenities,many=True))

            cont = 0

            for amenities in dataAmenities:

                cont = cont +1

                if aux == 0:
                    aux = amenities.iddef_amenity_group

                pivot = amenities.iddef_amenity_group
                
                amRes = schemaAm.dump(amenities)
                amRes["estado"]=0
                amRes["is_priority"] = 0
                for addedAm in data:
                    amAdded = schemaAm.dump(addedAm.amenity)
                    #Se agrega a esquema ameniti room
                    is_priority = schemaAmRom.dump(addedAm)
                    if amRes["iddef_amenity"] == amAdded["iddef_amenity"]:
                        amRes["estado"]=1
                        if is_priority['is_priority'] == 1:
                            amRes['is_priority']=1

                if pivot == aux:
                    items.append(amRes)
                    lastName = amenities.amenity_group.name
                else:
                    itemCopy = items.copy()
                    item = {

                        "group":lastName,
                        "idGroup":aux,
                        "items":itemCopy
                    }
                    dataResponse.append(item)
                    items.clear()
                    items.append(amRes)
                    aux = pivot

                if cont == totalRegistros:
                    item = {

                        "group":lastName,
                        "idGroup":aux,
                        "items":items
                    }
                    dataResponse.append(item)

            response = {
                "Code":200,
                "Msg":"Success",
                "Error":False,
                "data":dataResponse
            }

        except Exception as e:
            response = {
                "Code":500,
                "Msg":str(e),
                "Error":True,
                "data":{}
            }

        return response

class RoomAmenityDescriptions(Resource):
    # @base.access_middleware
    def get(self, iddef_room_type_category, lang_code):
        response={}

        try:
            data = self.get_amenities_by_room_type_lang(iddef_room_type_category, lang_code)

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
                    "data": data
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
    def get_amenities_by_room_type_lang(iddef_room_type_category, lang_code):
    
            schema = RoomAmenityDescription(many=True)
            data = Model.query\
                .add_columns(Model.iddef_amenity, TextLang.text, TextLang.attribute, Model.is_priority, AmModel.html_icon)\
                .join (AmModel, AmModel.iddef_amenity == Model.iddef_amenity)\
                .join (TextLang, and_(TextLang.lang_code == lang_code, TextLang.estado == 1, TextLang.table_name == "def_amenity", AmModel.iddef_amenity == TextLang.id_relation))\
                .filter(and_(Model.iddef_room_type_category == iddef_room_type_category, Model.estado == 1)).all()


            if data:
                                        
                dataResult = schema.dump(data, many=True)

            else:
                data2 = Model.query\
                    .add_columns(Model.iddef_amenity, TextLang.text, TextLang.attribute, Model.is_priority, AmModel.html_icon)\
                    .join (AmModel, AmModel.iddef_amenity == Model.iddef_amenity)\
                    .join (TextLang, and_(TextLang.lang_code == "EN", TextLang.estado == 1, TextLang.table_name == "def_amenity", AmModel.iddef_amenity == TextLang.id_relation))\
                    .filter(and_(Model.iddef_room_type_category == iddef_room_type_category, Model.estado == 1)).all()
                
                dataResult = schema.dump(data2, many=True)


            #return(dataResult)
            listNames = []
            listDescriptions = [] 
            dataResponse = []

            for items in dataResult:
                aux={}
                if items["attribute"] == "name":
                    aux["iddef_amenity"] = items["iddef_amenity"]
                    aux["name"] = items["text"]
                    aux["is_priority"] = items["is_priority"]
                    aux["html_icon"] = items["html_icon"]
                    listNames.append(aux)
                else:
                    aux["iddef_amenity"] = items["iddef_amenity"]
                    aux["description"] = items["text"]
                    aux["is_priority"] = items["is_priority"]
                    aux["html_icon"] = items["html_icon"]
                    listDescriptions.append(aux)
            
            for listNam in listNames:
                listDesc = [x for x in listDescriptions\
                    if x["iddef_amenity"] == listNam["iddef_amenity"]]
                aux2 = {}
                
                if listNam["iddef_amenity"] == listDesc[0]["iddef_amenity"]:
                    aux2["iddef_amenity"] = listNam["iddef_amenity"]
                    aux2["name"] = listNam["name"]
                    aux2["description"] = listDesc[0]["description"]
                    aux2["is_priority"] = listNam["is_priority"]
                    aux2["html_icon"] = listNam["html_icon"]

                    dataResponse.append(aux2)
            
            return dataResponse
