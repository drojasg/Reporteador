from config import app, db, base
from models.book_hotel_room import BookHotelRoom as Model, BookHotelRoomSchema as ModelSchema
from marshmallow import ValidationError
from common.util import Util
from flask import Flask, request
from flask_restful import Resource

class BookHotelRoom(Resource):
    #@base.access_middleware
    def put(self):
        response:{}

        try:
            data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            #model = Model()
            arr_update = []

            for i in data:
                model = Model.query.get(i['idbook_hotel_room'])

                if model is None:
                    return {
                        "Code": 404,
                        "Msg": "The ID is not found",
                        "Error": True,
                        "data": {}
                    }
                
                model.no_show = i['no_show']
                model.usuario_ultima_modificacion = user_name
                db.session.flush()
                arr_update.append(schema.dump(model))
            
            db.session.commit()

            response = {
                "code": 200,
                "Msg": "Success",
                "Error": False,
                "data": arr_update
            }
        except ValidationError as error:
            response ={
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






