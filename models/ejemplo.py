from config import db, ma
import json

class create_dict(dict0):
    def __init__(self):
        self = dict()

    def add(self, key, value):
        self[key] = value

mydict = create_dict()
query = """select book_hotel.idbook_hotel, 
book_hotel.code_reservation,
book_hotel.iddef_property,
def_property.short_name as "Hotel Name",
def_property.trade_name,
def_property.property_code as "Hotel Code",  
book_hotel.from_date,
book_hotel.to_date,
book_hotel.nights,
book_hotel.adults,
book_hotel.child,
book_hotel.total_rooms,
book_hotel.iddef_market_segment,
def_market_segment.code,
def_market_segment.currency_code,
def_market_segment.description as "Market Description",
book_hotel.iddef_country,rom config import db, ma
def_currency.currency_code,
def_currency.description as "Currency description",
def_language.iddef_language,
def_language.lang_code,
def_language.description as "Language description",
book_hotel.exchange_rate,
book_hotel.promo_amount,
book_hotel.discount_percent,
book_hotel.discount_amount,
book_hotel.total_gross,
book_hotel.fee_amount,
book_hotel.country_fee,
book_hotel.amount_pending_payment,
book_hotel.amount_paid,
book_hotel.total,
book_hotel.promotion_amount,
book_hotel.last_refund_amount,
book_hotel.idbook_status,
book_status.name as "Status name",
book_status.code as "Status code",
book_status.description as "Status code",
book_hotel.device_request,
book_hotel.expiry_date,
book_hotel.cancelation_date,
book_hotel.modification_date_booking,
book_hotel.estado,
book_hotel.usuario_creacion,
book_hotel.fecha_creacion,
book_hotel.usuario_ultima_modificacion,
book_hotel.fecha_ultima_modificacion

from book_hotel 

inner join def_property on book_hotel.iddef_property = def_property.iddef_property 
inner join def_market_segment on book_hotel.iddef_market_segment = def_market_segment.iddef_market_segment
inner join def_country on book_hotel.iddef_country = def_country.iddef_country
inner join def_channel on book_hotel.iddef_channel = def_channel.iddef_channel
inner join def_currency on book_hotel.iddef_currency  = def_currency.iddef_currency
inner join def_language on book_hotel.iddef_language = def_language.iddef_language
inner join book_status on book_hotel.idbook_status = book_status.idbook_status

where book_hotel.estado=1;"""
cursor = db.cursor()
cursor.execute(query)
result = cursor.fetchall()

for row in result: 
    mydict.add(row[0],({"idop_sistemas":row[1],"nombre":row[2],"estado":row[3],"usuario_creacion":row[4],"fecha_creacion":row[5],"usuario_ultima_modificacion"}:row[6],"fecha_ultima_modificacion":row[7]))