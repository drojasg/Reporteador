from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db,base
from models.inventory import InventorySchema as ModelSchema, SaveInventorySchema as SaveModelSchema, Inventory as Model
from common.util import Util
from resources.rates.RatesHelper import RatesFunctions as functions
from sqlalchemy import or_, and_
from datetime import datetime
import datetime as dates
#from common.custom_log_response import CustomLogResponse

class Inventory(Resource):
    #api-inventory-get-by-id
    @base.access_middleware
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

    #api-inventory-put
    # @base.access_middleware
    def put(self, id):
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

    #api-inventory-post
    #@CustomLogResponse.save
    def post(self):
        response = {}
        try:
            
            json_data = request.get_json(force=True)
            schema_load = SaveModelSchema()
            data = schema_load.load(json_data)
            #user_data = base.get_token_data()
            #user_name = user_data['user']['username']
            user_name = "Clever Oxi"
            hotel_code = data["hotel_code"]
            hotel = functions.getHotelInfo(hotel_code)
            id_property = hotel.iddef_property
            result = {}
            data_room = []
            for item in data["rooms"]:
                fecha = item["date"]
                room = []
                item_result = {}
                for itemRoom in item["rooms"]:
                    #Validar que no sea valor negativo
                    if itemRoom["count"] < 0:
                        ms = "Error is not allowed negative values: " + str(itemRoom["count"])
                        response_room = {
                                "Code":500,
                                "Msg": ms,
                                "Error":True,
                                "data": {}
                            }
                        room.append(response_room)
                    #Validar si el codigo de cuarto existe en la propiedad
                    try:
                        dataRoom = functions.getRoomTypeInfo(idproperty=id_property,room_type_code=itemRoom["room_code"])
                        if dataRoom is not None:
                            id_room = dataRoom.iddef_room_type_category
                            #Validar si existe registro en inventory
                            dataInventory = Model.query.filter_by(estado=1, idProperty=id_property, idRoom_type_category=id_room, efective_date=fecha).first()
                            if dataInventory is None:
                                #Agregar registro
                                inventory = self.create_inventory(id_room,itemRoom["count"],fecha,id_property)
                            else:
                                #Actualizar registro
                                inventory = self.update_inventory(dataInventory,id_room,itemRoom["count"],fecha,id_property)  
                        response_room = {
                            "Code": 200,
                            "Msg": "Success",
                            "Error": False,
                            "data": inventory
                        }    
                        room.append(response_room)                       
                    except Exception as e:
                        ms = "Room no encontrado para la propiedad, favor de verificar: " + itemRoom["room_code"].upper()
                        response_room = {
                            "Code": 500,
                            "Msg": str(ms),
                            "Error": True,
                            "data": {}
                        }
                        room.append(response_room)
                fecha = fecha.strftime('%m-%d-%Y')
                item_result["date"] = fecha
                item_result["rooms"] = room
                data_room.append(item_result)
            result["hotel_code"] = hotel_code
            result["rooms"] = data_room

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": result
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
        
    
    @staticmethod
    def create_inventory(id_room,avail_rooms,efective_date,id_property):
        try: 
            schema = ModelSchema(exclude=Util.get_default_excludes())
            #user_data = base.get_token_data()
            user_name = "Clever Oxi"
            data = None
            Data = Model()
            Data.idRoom_type_category = id_room
            Data.avail_rooms = avail_rooms
            Data.efective_date = efective_date
            Data.idProperty = id_property
            Data.estado = 1
            Data.usuario_creacion = user_name
            db.session.add(Data)
            db.session.commit()
            data = schema.dump(Data)

        except Exception as ex:
            raise Exception("Error al crear inventario "+str(ex))

        return data
    
    @staticmethod
    def update_inventory(model,id_room,avail_rooms,efective_date,id_property):
        try: 
            schema = ModelSchema(exclude=Util.get_default_excludes())
            #user_data = base.get_token_data()
            user_name = "Clever Oxi"
            data = None
            model.idRoom_type_category = id_room
            model.avail_rooms = avail_rooms
            model.efective_date = efective_date
            model.idProperty = id_property
            model.usuario_ultima_modificacion = user_name
            db.session.commit()
            data = schema.dump(model)

        except Exception as ex:
            raise Exception("Error al actualizar inventario "+str(ex))

        return data
    
    @staticmethod
    def get_disponibilidad(room_code=None,date_start=None,date_end=None,id_property=None,only_one=True,Noffset=None,Nolimit=None):

        if room_code is None and id_property is None:
            raise Exception("Se necesita el codigo de la habitacion / propiedad")

        if date_start is None:
            today = datetime.today().date()
            date_start = today + dates.timedelta(days=15)
            
        if date_end is None:
            date_end = date_start + dates.timedelta(days=5)
        
        if Noffset is None and Nolimit is None:
            Noffset = 1
            Nolimit = 100

        #Buscar cuartos
        if only_one == True:
            
            try:

                if id_property is not None and room_code is None:
                    dataRoom = functions.getRoomTypeInfo(idproperty=id_property,only_one=True)
                    if dataRoom is not None:
                        id_room = dataRoom.iddef_room_type_category
                        data_stock = Inventory.get_inventory(id_room=id_room,date_start=date_start,date_end=date_end,id_property=id_property,only_one=True)

                elif id_property is not None and room_code is not None:
                    dataRoom = functions.getRoomTypeInfo(idproperty=id_property,room_type_code=room_code,only_one=True)
                    if dataRoom is not None:
                        id_room = dataRoom.iddef_room_type_category
                        data_stock = Inventory.get_inventory(id_room=id_room,date_start=date_start,date_end=date_end,id_property=id_property,only_one=True)
                else:
                    dataRoom = functions.getRoomTypeInfo(room_type_code=room_code,only_one=True)
                    if dataRoom is not None:
                        id_room = dataRoom.iddef_room_type_category
                        data_stock = Inventory.get_inventory(id_room=id_room,date_start=date_start,date_end=date_end,only_one=True)
            except Exception as exceptio:
                raise Exception ("Error: "+str(exceptio))
        else:
            
            try:

                if id_property is not None and room_code is None:
                    dataRoom = functions.getRoomTypeInfo(idproperty=id_property,only_one=False)
                    listItemsRoom = []
                    if len(dataRoom) > 0:
                        for item_room in dataRoom:
                            id_room = item_room.iddef_room_type_category
                            listItemsRoom.append(id_room)
                        data_stock = Inventory.get_inventory(listRoom=listItemsRoom,date_start=date_start,date_end=date_end,id_property=id_property,only_one=False)

                elif id_property is not None and room_code is not None:
                    dataRoom = functions.getRoomTypeInfo(idproperty=id_property,room_type_code=room_code,only_one=True)
                    if dataRoom is not None:
                        id_room = dataRoom.iddef_room_type_category
                        data_stock = Inventory.get_inventory(id_room=id_room,date_start=date_start,date_end=date_end,id_property=id_property,only_one=False)
                else:
                    listItemsRoom = []
                    dataRoom = functions.getRoomTypeInfo(room_type_code=room_code,only_one=False)
                    if len(dataRoom) > 0:
                        for item_room in dataRoom:
                            id_room = item_room.iddef_room_type_category
                            listItemsRoom.append(id_room)
                        data_stock = Inventory.get_inventory(listRoom=listItemsRoom,date_start=date_start,date_end=date_end,only_one=False)
            except Exception as exceptio:
                raise Exception ("Error: "+str(exceptio))

        return data_stock
    
    #Depurar metodo
    @staticmethod
    def manage_inventory(roomid,date_start,date_end,propertyid,rooms_count=1,add_to_inventory=False):
        status = False

        try:

            inventory_item = Inventory.get_inventory(id_room=roomid,\
            date_start=date_start,date_end=date_end, id_property=propertyid,only_one=True)

            if inventory_item is not None:
                if add_to_inventory == True:    
                    inventory_item.avail_rooms += rooms_count
                    inventory_item.usuario_ultima_modificacion = "Admin"
                else:
                    inventory_item.avail_rooms -= rooms_count
                    inventory_item.usuario_ultima_modificacion = "Admin"

                db.session.commit()
                status = True


        except Exception as error:
            pass

        return status

    
    @staticmethod
    def get_inventory(id_room=None,listRoom=None,date_start=None,date_end=None,id_property=None,only_one=True,Noffset=None,Nolimit=None):
        #Validar datos para filtrar
        conditions = []

        if id_room is not None:
            conditions.append(Model.idRoom_type_category==id_room)

        if listRoom is not None:
            if len(listRoom) > 0:
                conditions.append(Model.idRoom_type_category.in_(listRoom))
        
        if id_property is not None:
            conditions.append(Model.idProperty==id_property)
        
        if date_start is not None and date_end is not None:
            conditions.append(Model.efective_date.between(date_start,date_end))
        
        if date_start is not None and date_end is None:
            conditions.append(Model.efective_date==date_start)
        
        if only_one == True:
            data = Model.query.filter(and_(*conditions,Model.estado==1)).first()
        else:
            if Nolimit is not None and Noffset is not None:
                data = Model.query.filter(and_(*conditions,Model.estado==1)).offset(Noffset).limit(Nolimit).all()
            else:
                data = Model.query.filter(and_(*conditions,Model.estado==1)).all()
            
        return data
        

class InventoryListSearch(Resource):
    #api-inventory-get-all
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