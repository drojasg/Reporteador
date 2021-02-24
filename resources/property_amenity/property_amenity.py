from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.property_amenity import PropertyAmenitySchema as ModelSchema, GetPropertyAmenitySchema as GetModelSchema, PutPropertyAmenitySchema as PutModelSchema, SearchPropertyAmenitySchema as SearchModelSchema, PropertyAmenity as Model, PropertyAmenityDescription
from models.amenity_group import AmenityGroup as AmenGruModel
from models.amenity_type import AmenityType as AmenTypeModel
from models.amenity import Amenity as AmenModel, GetIdAmenitySchema as GetIdAmenModelSchema, IdAmenitySchema as IdAmenModelSchema, GetAmenitySchema as GetListAmenitySchema
from models.text_lang import TextLang, GetTextLangSchema
from common.util import Util
from sqlalchemy.sql.expression import and_
from common.public_auth import PublicAuth

class PropertyAmenity(Resource):
    #api-property-amenity-get-by-id
    #Administrativo
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

    #api-property-amenity-put
    #Administrativo
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
            if request.json.get("iddef_property") != None:
                model.iddef_property = data["iddef_property"]
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

    #api-property-amenity-delete
    #Administrativo
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

    #api-property-amenity-post
    #Administrativo
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
            model.iddef_property = data["iddef_property"]
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

class PropertyAmenityListSearch(Resource):
    #api-property-amenity-get-all
    #Administrativo
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

    #api-property-amenity-put-list
    #Administrativo
    # @base.access_middleware
    def put(self, property, group):
        response = {}
        if request.is_json:
            try:
                data = request.json
                dataResponse = []
                user_data = base.get_token_data()
                user_name = user_data['user']['username']
                #Verificar que no este vacio el nodo
                if len(data["datos"]) > 0:
                    for toUpdate in data["datos"]:
                        schema = GetIdAmenModelSchema()
                        datax = schema.load(toUpdate)
                        #Busqueda de la amenidad
                        dataSearch = AmenModel.query.filter_by(description=datax["nombre"], iddef_amenity_group=group, iddef_amenity_type=1, estado=1).first()
                        if dataSearch is None:
                            response = {
                                "Code": 200,
                                "Msg": "Success",
                                "Error": False,
                                "data": {}
                            }
                        else:
                            #Buscar si existe registro de asignacion
                            schema2 = PutModelSchema()
                            dataUpdate = Model.query.filter_by(iddef_amenity=dataSearch.iddef_amenity, iddef_property=property).first()
                            #Actualizar o crear registro de asignacion
                            if dataUpdate is None:
                                model = Model()
                                model.iddef_amenity = dataSearch.iddef_amenity
                                model.iddef_property = property
                                model.is_priority = datax["is_priority"]
                                model.estado = datax["estado"]
                                model.usuario_creacion = user_name
                                db.session.add(model)
                                db.session.commit()
                                dataResponse.append(model)
                            else:
                                dataUpdate.is_priority = datax["is_priority"]
                                dataUpdate.estado = datax["estado"]
                                dataUpdate.usuario_ultima_modificacion = user_name
                                db.session.commit()
                                dataResponse.append(dataUpdate)
                            response = {
                                "Code": 200,
                                "Msg": "Success",
                                "Error": False,
                                "data": schema2.dump(dataResponse,many=True)
                            }
            except ValidationError as Error:
                response = {
                    "Code":500,
                    "Msg": Error.messages,
                    "Error":True,
                    "data": {}
                }
            except Exception as e:
                #

                response = {
                    "Code":500,
                    "Msg":str(e),
                    "Error":True,
                    "data":{}
                }
        else:
            response = {
                "Code":500,
                "Msg":"INVALID REQUEST",
                "Error":True,
                "data": {}
            }

        return response

class PublicPropertyAmenityList(Resource):
    #api-public-property-amenity-get-by-property
    #Publica
    @PublicAuth.access_middleware
    def get(self, id):
        try:
            schema = SearchModelSchema(exclude=('iddef_property_amenity','iddef_property','property','estado','usuario_creacion', 'fecha_creacion', 'usuario_ultima_modificacion', 'fecha_ultima_modificacion',), many=True)
            data = Model.query.filter(Model.iddef_property == id, Model.estado==1).all()
            property_amenity_items=schema.dump(data, many=True)
            result=[]
            for x in property_amenity_items:
                property_amenity_item=x
                property_amenity_item['html_icon']=property_amenity_item['property_amenity']['html_icon'].capitalize()
                #property_amenity_item['description']=property_amenity_item['property_amenity']['description']
                property_amenity_item['name']=property_amenity_item['property_amenity']['name'].capitalize()
                property_amenity_item.pop('property_amenity')
                result.append(property_amenity_item)

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


class PropertyGroupAmenityList(Resource):
    #api-property-amenity-get-by-params
    #Administrativo
    # @base.access_middleware
    def get(self, id, group, type):
        try:
            dataSearch = AmenModel.query.filter_by(iddef_amenity_group=group, iddef_amenity_type=type, estado=1).all()
            schema = GetListAmenitySchema(exclude=('iddef_amenity_type','iddef_amenity_group','usuario_creacion', 'fecha_creacion', 'usuario_ultima_modificacion', 'fecha_ultima_modificacion',), many=True)
            amenity_items=schema.dump(dataSearch, many=True)
            if dataSearch is None:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": {}
                }
            else:
                data = Model.query.join(AmenModel).join(AmenGruModel).join(AmenTypeModel).filter(Model.iddef_property == id, AmenGruModel.iddef_amenity_group == group, AmenTypeModel.iddef_amenity_type == type, Model.estado==1).all()
                schema2 = ModelSchema(exclude=('iddef_property_amenity','iddef_property','usuario_creacion', 'fecha_creacion', 'usuario_ultima_modificacion', 'fecha_ultima_modificacion',))
                property_amenity_items=schema2.dump(data, many=True)
                result=[]
                for x in amenity_items:
                    amenity_item=x
                    amenity_item['html_icon']
                    amenity_item['description']
                    amenity_item['name']
                    amenity_item['estado']=0
                    amenity_item['is_priority']=0
                    for y in property_amenity_items:
                        property_amenity_item=y
                        if amenity_item['iddef_amenity'] == property_amenity_item['iddef_amenity']:
                            amenity_item['estado']=1
                            if property_amenity_item['is_priority'] == 1:
                                amenity_item['is_priority']=1
                    result.append(amenity_item)

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


class PropertyAmenityDescriptions(Resource):
    #api-property-amenity-get-description
    # @base.access_middleware
    def get(self,iddef_property, lang_code):
        response = {}
        try:
            data = self.get_amenities_by_property_lang(iddef_property, lang_code)

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
    def get_amenities_by_property_lang(iddef_property, lang_code):
    
            schema = PropertyAmenityDescription(many=True)
            data = Model.query\
                .add_columns(Model.iddef_amenity, TextLang.text, TextLang.attribute, Model.is_priority, AmenModel.html_icon)\
                .join (AmenModel, AmenModel.iddef_amenity == Model.iddef_amenity)\
                .join (TextLang, and_(TextLang.lang_code == lang_code, TextLang.estado == 1, TextLang.table_name == "def_amenity", AmenModel.iddef_amenity == TextLang.id_relation))\
                .filter(and_(Model.iddef_property == iddef_property, Model.estado == 1)).all()


            if data:
                                        
                dataResult = schema.dump(data, many=True)

            else:
                data2 = Model.query\
                    .add_columns(Model.iddef_amenity, TextLang.text, TextLang.attribute, Model.is_priority, AmenModel.html_icon)\
                    .join (AmenModel, AmenModel.iddef_amenity == Model.iddef_amenity)\
                    .join (TextLang, and_(TextLang.lang_code == "EN", TextLang.estado == 1, TextLang.table_name == "def_amenity", AmenModel.iddef_amenity == TextLang.id_relation))\
                    .filter(and_(Model.iddef_property == iddef_property, Model.estado == 1))
                
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