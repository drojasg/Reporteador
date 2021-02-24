from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
from models.promotions import Promotions, PromotionsSchema
#from models.book_hotel import BookHotel, BookHotelSchema
#from models.book_hotel_room import BookHotelRoom, BookHotelRoomSchema

class BookPromotion(db.Model):
    __tablename__ = "book_promotion"

    idbook_promotion = db.Column(db.Integer, primary_key=True)
    idbook_hotel = db.Column(db.Integer,db.ForeignKey("book_hotel.idbook_hotel"), nullable=False)
    #book_hotel_promotion = db.relationship('BookHotel', backref=db.backref('book_promotion', lazy='dynamic'))
    #idbook_hotel_room = db.Column(db.Integer,db.ForeignKey("book_hotel_room.idbook_hotel_room"), nullable=False)
    #idop_promotions = db.Column(db.Integer)
    idop_promotions = db.Column(db.Integer,db.ForeignKey("op_promotions.idop_promotions"), nullable=False)
    promotion = db.relationship('Promotions', backref="promotion", lazy="joined", 
        primaryjoin="and_(Promotions.idop_promotions == BookPromotion.idop_promotions, Promotions.estado == 1)")
    #promotion_book_ht = db.relationship('Promotions', backref=db.backref('book_promotion', lazy='dynamic'))
    #amount = db.Column(db.Float, nullable=False)
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class BookPromotionSchema(ma.Schema):    
    idbook_promotion = fields.Integer()
    idbook_hotel = fields.Integer()
    #idbook_hotel_room = fields.Integer()
    idop_promotions = fields.Integer()
    #amount = fields.Float()
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")