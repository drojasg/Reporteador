from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from datetime import date, datetime, timedelta
from sqlalchemy.sql.expression import and_
from models.book_customer import BookCustomer as bcModel,BookCustomerModifySchema as bcSchema
from models.book_customer_hotel import BookCustomerHotel as bchModel
from models.book_hotel import BookHotel as bhModel
from models.book_address import BookAddress as badModel

class BookCustomerModify(Resource):
    #api-internal-booking-customer-post
    def get(self,idbooking):

        try:
            schema = bcSchema()

            bcData = bcModel.query.join(bchModel,bcModel.idbook_customer==bchModel.idbook_customer)\
            .join(bhModel,bhModel.idbook_hotel==bchModel.idbook_hotel)\
            .join(badModel, badModel.idbook_customer==bcModel.idbook_customer)\
            .filter(bhModel.idbook_hotel==idbooking,bchModel.estado==1,\
            bcModel.estado==1,badModel.estado==1,bhModel.estado==1).first()

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(bcData)
            }

        except ValidationError as error:
            #db.session.rollback()
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