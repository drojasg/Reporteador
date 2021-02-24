from models.age_code import AgeCode as agcModel
from models.age_range import AgeRange as agrModel

class age_helper():

    #Obtiene los codigos de edad segun una propiedad
    def get_age_code_avail_by_property(self,idproperty):

        agcData = agcModel.query.join(agrModel,\
        agcModel.iddef_age_code == agrModel.iddef_age_code)\
        .filter(agrModel.iddef_property==idproperty,\
        agrModel.estado==1).all()

        return [item.code for item in agcData]

    def get_age_code_avail_data_by_property(self,idproperty):

        agcData = agcModel.query.join(agrModel,\
        agcModel.iddef_age_code == agrModel.iddef_age_code)\
        .filter(agrModel.iddef_property==idproperty,\
        agrModel.estado==1).all()

        return agcData

    def get_age_range_avail_by_property(self,idproperty):

        agrData = agrModel.query.join(agcModel,\
        agcModel.iddef_age_code==agrModel.iddef_age_code)\
        .filter(agrModel.iddef_property==idproperty,agrModel.estado==1).all()

        return agrData

    def get_age_codes_property_valid(self,property_id,agc_id):

        agcdata = agcModel.query.join(agrModel,\
        agrModel.iddef_age_code==agcModel.iddef_age_code)\
        .filter(agrModel.estado==1,agrModel.iddef_property==property_id,\
        agcModel.iddef_age_code==agc_id).all()

        return agcdata