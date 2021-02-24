from config import db, base
from models.terms_and_conditions import TermsAndConditionsSchema as ModelSchema, TermsAndConditionsRefSchema as ModelRefSchema, TermsAndConditions as Model
from models.brand import BrandSchema as BrandModelSchema, Brand as BrandModel
from models.property import Property

class TermsAndConditionsService():
    @staticmethod
    def get_terms_and_conditions_by_brand(brand_code):
        """
            Get terms and conditions by brand code
            param: brand_code Brand code to search data

            return: TermsAndConditions model
        """
        brand = BrandModel.query.filter(BrandModel.code == brand_code, BrandModel.estado == 1).first()
        if not brand:
            return None

        terms_cond = Model.query.filter(Model.iddef_brand == brand.iddef_brand, Model.estado == 1).first()

        return terms_cond
    
    @staticmethod
    def get_terms_and_conditions_by_property(property_code):
        """
            Get terms and conditions by property code
            param: property_code Property code to search data

            return: TermsAndConditions model
        """
        property = Property.query.filter(Property.property_code == property_code, Property.estado == 1).first()

        if not property:
            return None

        terms_cond = Model.query.filter(Model.iddef_brand == property.iddef_brand, Model.estado == 1).first()

        return terms_cond

    @staticmethod
    def get_all_terms_and_conditions():
        """
            Get all terms and conditions

            return: TermsAndConditions model list
        """
        terms_cond = Model.query.filter(Model.estado == 1).all()

        return terms_cond
    