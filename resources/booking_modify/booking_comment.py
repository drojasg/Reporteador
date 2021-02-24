from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from datetime import date, datetime, timedelta
from sqlalchemy.sql.expression import and_

from config import db, base
from models.book_hotel import BookHotelBaseSchema as ModelBaseSchema, BookHotel
from common.util import Util
   
class BookingCommentModify(Resource):
    #api-internal-booking-comment-get
    #@base.access_middleware
    def get(self, idbooking):
        response = {}
        try:
            
            schema = ModelBaseSchema()

            data = []

            book_hotel = BookHotel.query.\
                filter(BookHotel.idbook_hotel == idbooking, BookHotel.estado == 1).first()

            if len(book_hotel.comments) > 0:
                for comment in book_hotel.comments:
                    if comment.estado ==1:
                        data_comment = {
                            "idbook_hotel_comment": comment.idbook_hotel_comment,
                            "text": comment.text,
                            "visible_to_guest": comment.visible_to_guest,
                            "source": comment.source,
                            "estado": comment.estado
                        }
                        data.append(data_comment)
                

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