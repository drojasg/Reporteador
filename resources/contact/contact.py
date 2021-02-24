from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.sql import exists

from config import db, base
from models.contact import ContactSchema as ModelSchema, Contact as Model, ContactPostSchema
from models.address import Address, AddressSchema
from models.email_contact import EmailContact, EmailContactSchema
from models.contact_phone import ContactPhone, ContactPhoneSchema
from models.property import Property, GetPropertyContactsSchema
from common.util import Util
from models.media import Media, MediaSchema
from resources.reports.reportsHelper import ReportsHelper as reportsData

class Contact(Resource):
    #api-contacts-get-by-id
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

    #api-contacts-put
    # @base.access_middleware
    def put(self, id):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
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
            
            model.first_name = data["first_name"]
            model.last_name = data["last_name"]
            model.iddef_address = data["iddef_address"]
            model.iddef_contact_type = data["iddef_contact_type"]
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

    #api-contacts-delete
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

    #api-contacts-post
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

            model.first_name = data["first_name"]
            model.last_name = data["last_name"]
            model.iddef_address = data["iddef_address"]
            model.iddef_contact_type = data["iddef_contact_type"]
            model.estado = data["estado"]
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

class ContactListSearch(Resource):
    #api-contacts-get-all
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

class ContactForm(Resource):
    #api-contacts-get-form
    # @base.access_middleware
    def get(self, id, iddef_contact_type):
        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())
            property_schema = GetPropertyContactsSchema(exclude=Util.get_default_excludes())
            result = Property.query.get(id)
            result_child = None
            data = None

            if result is None:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": {}
                }
            else:
                result_data = {}
                if len(result.contacts) == 0:
                    data = None
                else:
                    property_data = property_schema.dump(result)

                    list_contacts = list(filter(lambda elem_contact: elem_contact["estado"] == 1 and elem_contact["iddef_contact_type"] == iddef_contact_type, property_data["contacts"]))

                    for index_contact, obj_contact in enumerate(list_contacts):
                        list_addresses = list(filter(lambda elem_address: elem_address["estado"] == 1, obj_contact["addresses"]))
                        list_email_contacts = list(filter(lambda elem_email_contact: elem_email_contact["estado"] == 1, obj_contact["email_contacts"]))
                        list_contact_phones = list(filter(lambda elem_contact_phone: elem_contact_phone["estado"] == 1, obj_contact["contact_phones"]))

                        list_contacts[index_contact]["addresses"] = list_addresses;
                        list_contacts[index_contact]["email_contacts"] = list_email_contacts;
                        list_contacts[index_contact]["contact_phones"] = list_contact_phones;


                    if iddef_contact_type == 2:
                        result_data = list_contacts
                        data = True
                    else:
                        if len(list_contacts) > 0:
                            result_data = list_contacts[0]
                            data = True
                        else:
                            result_data = {}
                            data = None
                            
            if data is None or result_data == {}:
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
                    "data": result_data
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

    #api-contacts-put-form
    # @base.access_middleware
    def put(self, id):
        response = {}
        try:
            
            json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            model = Model.query.get(id)
            modif_lat_long = 0

            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            
            if model is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }

            model.first_name = data["first_name"]
            model.last_name = data["last_name"]
            model.iddef_contact_type = data["iddef_contact_type"]
            model.estado = data["estado"]
            model.usuario_ultima_modificacion = user_name


            # Nota: Los modelos nuevos se agregan fuera del loop debido a que al agregar un elemento nuevo
            # dentro del for se continuaba con el elemento agregado, generando un loop infinito 
            list_models_addresses = []
            list_models_email_contacts = []
            list_models_contact_phones = []

            for address in data['addresses']:
                if(len(model.addresses) == 0):
                    model_address = Address()
                    model_address.address = address["address"]
                    model_address.latitude = address["latitude"]
                    model_address.longitude = address["longitude"]
                    model_address.country_code = address["country_code"]
                    model_address.state_code = address["state_code"]
                    model_address.zip_code = address["zip_code"]
                    model_address.city = address["city"]
                    model_address.estado = address["estado"]
                    model_address.usuario_creacion = user_name
                    list_models_addresses.append(model_address)
                    #Si aun no tiene alguna dirección se crea el mapa sin validar: 


                for id_address, value_address in enumerate(model.addresses):
                    address_index = int(address["iddef_address"]) if address["iddef_address"] else 0

                    #Validamos si hubo cambios en la latitud y longitud
                    if model.addresses[id_address].latitude != address["latitude"] or model.addresses[id_address].longitude != address["longitude"]:
                        modif_lat_long = 1
                        #map_to_bucket = reportsData.get_img_map_bucket(address["latitude"], address["longitude"])
                        

                    if(model.addresses[id_address].iddef_address == address_index):
                        model.addresses[id_address].address = address["address"]
                        model.addresses[id_address].latitude = address["latitude"]
                        model.addresses[id_address].longitude = address["longitude"]
                        model.addresses[id_address].country_code = address["country_code"]
                        model.addresses[id_address].state_code = address["state_code"]
                        model.addresses[id_address].zip_code = address["zip_code"]
                        model.addresses[id_address].city = address["city"]
                        model.addresses[id_address].estado = address["estado"]
                        model.addresses[id_address].usuario_ultima_modificacion = user_name
                    elif (address_index == 0):
                        model_address = Address()
                        model_address.address = address["address"]
                        model_address.latitude = address["latitude"]
                        model_address.longitude = address["longitude"]
                        model_address.country_code = address["country_code"]
                        model_address.state_code = address["state_code"]
                        model_address.zip_code = address["zip_code"]
                        model_address.city = address["city"]
                        model_address.estado = address["estado"]
                        model_address.usuario_creacion = user_name
                        list_models_addresses.append(model_address)
                        break

            for contact_phone in data['contact_phones']:
                if(len(model.contact_phones) == 0):
                    model_contact_phone = ContactPhone()
                    model_contact_phone.iddef_phone_type = contact_phone["iddef_phone_type"]
                    model_contact_phone.iddef_contact = contact_phone["iddef_contact"]
                    model_contact_phone.country = contact_phone["country"]
                    model_contact_phone.area = contact_phone["area"]
                    model_contact_phone.number = contact_phone["number"]
                    model_contact_phone.extension = contact_phone["extension"]
                    model_contact_phone.estado = 1
                    model_contact_phone.usuario_creacion = user_name
                    list_models_contact_phones.append(model_contact_phone)

                for id_contact_phone, value_contact_phone in enumerate(model.contact_phones):
                    contact_phone_index = int(contact_phone["iddef_contact_phone"]) if contact_phone["iddef_contact_phone"] else 0
                    if(model.contact_phones[id_contact_phone].iddef_contact_phone == contact_phone_index):
                        model.contact_phones[id_contact_phone].iddef_phone_type = contact_phone["iddef_phone_type"]
                        model.contact_phones[id_contact_phone].country = contact_phone["country"]
                        model.contact_phones[id_contact_phone].area = contact_phone["area"]
                        model.contact_phones[id_contact_phone].number = contact_phone["number"]
                        model.contact_phones[id_contact_phone].extension = contact_phone["extension"]
                        model.contact_phones[id_contact_phone].estado = contact_phone["estado"]
                        model.contact_phones[id_contact_phone].usuario_ultima_modificacion = user_name
                    elif (contact_phone_index == 0):
                        model_contact_phone = ContactPhone()
                        model_contact_phone.iddef_phone_type = contact_phone["iddef_phone_type"]
                        model_contact_phone.iddef_contact = contact_phone["iddef_contact"]
                        model_contact_phone.country = contact_phone["country"]
                        model_contact_phone.area = contact_phone["area"]
                        model_contact_phone.number = contact_phone["number"]
                        model_contact_phone.extension = contact_phone["extension"]
                        model_contact_phone.estado = 1
                        model_contact_phone.usuario_creacion = user_name
                        list_models_contact_phones.append(model_contact_phone)
                        break

            for email_contact in data['email_contacts']:
                if(len(model.email_contacts) == 0):
                    model_email_contact = EmailContact()
                    model_email_contact.email = email_contact["email"]
                    model_email_contact.notify_booking = email_contact["notify_booking"]
                    model_email_contact.email_type = email_contact["email_type"]
                    model_email_contact.estado = 1
                    model_email_contact.usuario_creacion = user_name
                    list_models_email_contacts.append(model_email_contact)
                
                for id_email_contact, value_email_contact in enumerate(model.email_contacts):
                    email_contacts_index = int(email_contact["iddef_email_contact"]) if email_contact["iddef_email_contact"] else 0
                    if(model.email_contacts[id_email_contact].iddef_email_contact == email_contacts_index):
                        model.email_contacts[id_email_contact].email = email_contact["email"]
                        model.email_contacts[id_email_contact].notify_booking = email_contact["notify_booking"]
                        model.email_contacts[id_email_contact].estado = email_contact['estado']
                        model.email_contacts[id_email_contact].usuario_ultima_modificacion = user_name
                    elif(email_contacts_index == 0):
                        model_email_contact = EmailContact()
                        model_email_contact.email = email_contact["email"]
                        model_email_contact.notify_booking = email_contact["notify_booking"]
                        model_email_contact.email_type = email_contact["email_type"]
                        model_email_contact.estado = 1
                        model_email_contact.usuario_creacion = user_name
                        list_models_email_contacts.append(model_email_contact)
                        break

            for temp_address in list_models_addresses:
                model.addresses.append(temp_address)

            for temp_email_contact in list_models_email_contacts:
                model.email_contacts.append(temp_email_contact)

            for temp_contact_phone in list_models_contact_phones:
                model.contact_phones.append(temp_contact_phone)

            #varificar si existe la imagen, si no existe insertarla
            param_exist = self.get_param_if_exists(5,data['iddef_property'])
            modelMedia = Media()

            if param_exist:
                pass
            else:
                map_to_bucket = reportsData.get_img_map_bucket(address["latitude"], address["longitude"])
                modelMedia.iddef_media_type = 5
                modelMedia.iddef_media_group = data["iddef_property"]
                modelMedia.url = map_to_bucket['objectURL']
                modelMedia.name = data["first_name"]
                modelMedia.description = data["first_name"]
                modelMedia.nombre_bucket = map_to_bucket['bucket']
                modelMedia.bucket_type = 1
                modelMedia.etag = map_to_bucket['ETag']
                modelMedia.show_icon = 0
                modelMedia.tags =  data["first_name"]
                modelMedia.estado = 1
                modelMedia.usuario_creacion = user_name
                db.session.add(modelMedia)

            #verificar si cambio latitud y longitud
            if modif_lat_long == 1: 
                
                map_to_bucket = reportsData.get_img_map_bucket(address["latitude"], address["longitude"])

                mediaSchema = MediaSchema(exclude=Util.get_default_excludes())
                modelMedia = Media()

                #param_exist = self.get_param_if_exists(5,id)

                #verificar si existe la imagen
                if param_exist:
                    data_up = Media.query.filter_by(iddef_media_type=5, iddef_media_group=data['iddef_property'], estado=1).first()
                    data_up.iddef_media_type = 5
                    data_up.iddef_media_group =data['iddef_property']
                    data_up.url = map_to_bucket['objectURL']
                    data_up.name = data["first_name"]
                    data_up.description = data["first_name"]
                    data_up.nombre_bucket = map_to_bucket['bucket']
                    data_up.bucket_type = 1
                    data_up.etag = map_to_bucket['ETag']
                    data_up.show_icon = 0
                    data_up.tags =  data["first_name"]
                    data_up.estado = 1
                    db.session.flush()
                else:
                    modelMedia.iddef_media_type = 5
                    modelMedia.iddef_media_group = data['iddef_property']
                    modelMedia.url = map_to_bucket['objectURL']
                    modelMedia.name = data["first_name"]
                    modelMedia.description = data["first_name"]
                    modelMedia.nombre_bucket = map_to_bucket['bucket']
                    modelMedia.bucket_type = 1
                    modelMedia.etag = map_to_bucket['ETag']
                    modelMedia.show_icon = 0
                    modelMedia.tags =  data["first_name"]
                    modelMedia.estado = 1
                    modelMedia.usuario_creacion = user_name
                    db.session.add(modelMedia)
            
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

    #@staticmethod
    #def insert_update_media_map(param_exist,map_to_bucket,data):

    @staticmethod
    def get_param_if_exists(media_type, media_group):

        data = db.session.query(exists().where(Media.iddef_media_type == media_type).where(Media.iddef_media_group == media_group).where(Media.estado == 1)).scalar()

        if data:
            #si ya existe el nombre del parametro regresamos True
            return True
        else:
            #si no existe entonces False
            return False

    #api-contacts-post-form
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            schema = ContactPostSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            property_model = Property.query.get(data["iddef_property"])

            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            if property_model is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }

            model = Model()
            model.first_name = data["first_name"]
            model.last_name = data["last_name"]
            model.iddef_contact_type = data["iddef_contact_type"]
            model.estado = 1
            model.usuario_creacion = user_name

            for address in data["addresses"]:
                model_address = Address()
                model_address.address = address["address"]
                model_address.latitude = address["latitude"]
                model_address.longitude = address["longitude"]
                model_address.country_code = address["country_code"]
                model_address.state_code = address["state_code"]
                model_address.zip_code = address["zip_code"]
                model_address.city = address["city"]
                model_address.estado = address["estado"]
                model_address.usuario_creacion = user_name

                map_to_bucket = reportsData.get_img_map_bucket(address["latitude"], address["longitude"])
                
                modelMedia.iddef_media_type = 5
                modelMedia.iddef_media_group = data['iddef_property']
                modelMedia.url = map_to_bucket['objectURL']
                modelMedia.name = data["first_name"]
                modelMedia.description = data["first_name"]
                modelMedia.nombre_bucket = map_to_bucket['bucket']
                modelMedia.bucket_type = 1
                modelMedia.etag = map_to_bucket['ETag']
                modelMedia.show_icon = 0
                modelMedia.tags =  data["first_name"]
                modelMedia.estado = 0
                modelMedia.usuario_creacion = user_name
                db.session.add(modelMedia)

                model.addresses.append(model_address)

            for email_contact in data["email_contacts"]:
                model_email_contact = EmailContact()
                model_email_contact.email = email_contact["email"]
                model_email_contact.notify_booking = email_contact["notify_booking"]
                model_email_contact.email_type = email_contact["email_type"]
                model_email_contact.estado = 1
                model_email_contact.usuario_creacion = user_name

                model.email_contacts.append(model_email_contact)

            for contact_phone in data["contact_phones"]:
                model_contact_phone = ContactPhone()
                model_contact_phone.iddef_phone_type = contact_phone["iddef_phone_type"]
                model_contact_phone.iddef_contact = contact_phone["iddef_contact"]
                model_contact_phone.country = contact_phone["country"]
                model_contact_phone.area = contact_phone["area"]
                model_contact_phone.number = contact_phone["number"]
                model_contact_phone.extension = contact_phone["extension"]
                model_contact_phone.estado = 1
                model_contact_phone.usuario_creacion = user_name

                model.contact_phones.append(model_contact_phone)

            property_model.contacts.append(model)

            db.session.add(property_model)
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