from config import base, db, app
from models.book_hotel import BookHotel, BookHotelLogSchema
from datetime import date, datetime

class LogChangesHelper():
    @staticmethod
    def get_log_booking_list(code_reservation, include_active=False):

        if include_active:
            list_book_hotel = BookHotel.query.filter(BookHotel.code_reservation.like(code_reservation), BookHotel.estado.in_([1,2])).order_by(BookHotel.idbook_hotel.asc()).all()
        else:
            # Se busca estado 2 (histórico)
            list_book_hotel = BookHotel.query.filter(BookHotel.code_reservation.like(code_reservation), BookHotel.estado == 2).order_by(BookHotel.idbook_hotel.asc()).all()

        return list_book_hotel

    def format_booking_log(list_book_hotel):
        result = []
        for hotel in list_book_hotel:
            guest_name = "{} {}".format(hotel.customers[0].customer.last_name, hotel.customers[0].customer.first_name)
            codes_rooms = []
            for room_ele in hotel.rooms:
                room_code = room_ele.room_type_category.room_code
                codes_rooms.append(room_code)
            hotel_info = {
                "iddef_property": hotel.iddef_property,
                "property_code": hotel.property.property_code,
                "property_name": hotel.property.short_name,
                "idbook_hotel": hotel.idbook_hotel,
                "code_reservation": hotel.code_reservation,
                "currency_code": hotel.currency.currency_code,
                "from_date": hotel.from_date,
                "to_date": hotel.to_date,
                "status": hotel.status_item.name,
                "idbook_status": hotel.idbook_status,
                "total": hotel.total,
                "codes_rooms": codes_rooms,
                "guest_name": guest_name,
                "email": hotel.customers[0].customer.email,
                "guest_country": hotel.customers[0].customer.address.country.country_code,
                "adults": hotel.adults,
                "child": hotel.child,
                "nights": hotel.nights,
                "total": hotel.total,
                "fecha_creacion": hotel.fecha_creacion,
                "fecha_ultima_modificacion": hotel.fecha_ultima_modificacion,
                "modification_date_booking": hotel.modification_date_booking,
                "estado": hotel.estado
            }

            result.append(hotel_info)

        schema = BookHotelLogSchema(many=True)
        return schema.dump(result)

    @staticmethod
    def get_log_booking(code_reservation, include_active=False):
        list_book_hotel = LogChangesHelper.get_log_booking_list(code_reservation, include_active)

        formated_list_bookings = LogChangesHelper.format_booking_log(list_book_hotel)

        return formated_list_bookings