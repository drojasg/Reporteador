from sqlalchemy import and_
from models.room_type_category import RoomTypeCategory as rtcModel

class Room_Type_Helper():

    def get_room_type(self,idproperty=None,room_type_code=None,property_name="",\
        idroom_type=None,only_one=True,only_of_the_house=True):

        conditions = []

        if idproperty is not None:
            conditions.append(rtcModel.iddef_property==idproperty)

        if room_type_code is not None:
            conditions.append(rtcModel.room_code==room_type_code)

        if idroom_type is not None:
            conditions.append(rtcModel.iddef_room_type_category==idroom_type)

        if only_of_the_house == True:
            conditions.append(rtcModel.is_room_of_house==1)
            only_one = True
        # else:
        #     conditions.append(rtcModel.is_room_of_house==0)

        if only_one:
            data = rtcModel.query.filter(and_(*conditions,rtcModel.estado==1)).first()
        else:
            data = rtcModel.query.filter(and_(*conditions,rtcModel.estado==1)).all()

        if data is None and idproperty is not None:
            raise Exception("Room Type {0:s} no encontrado para la propiedad {1:s}, favor de verificar que el tipo de habitacion exista".format(room_code,property_name))

        if data is None and idproperty is None:
            raise Exception("Room Type {0:s} no encontrado para ninguna propiedad {1:s}, favor de verificar que el tipo de habitacion exista" + str(room_code))
        
        return data