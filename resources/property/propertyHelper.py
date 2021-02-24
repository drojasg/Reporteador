from config import db, base
from models.property import Property as pModel, GetSearchEmailsSchema as eModelSchema

class FilterProperty():

    #filter code
    def getHotelInfo(self,property_code):

        data = pModel.query.filter(pModel.estado == 1, \
        pModel.property_code == property_code).first()

        if data is None:
            raise Exception('Codigo de propiedad invalido, favor de verificar el codigo {0:s}'.format(property_code))

        return data