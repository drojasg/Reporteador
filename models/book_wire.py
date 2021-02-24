from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util

class CompanyField(ma.Schema):
    CompanyTypeField = fields.Integer(default=2,required=True)
    CompanyIDField = fields.String(default="",required=True)

class ProfileIDsField(ma.Schema):

    ValueField = fields.Integer(default=1,required=True)
    typeField =  fields.Integer(default=1,required=True)


class ProfilesField(ma.Schema):

    ProfileIDsField = fields.List(fields.Nested(ProfileIDsField),default=None,required=True)
    ItemField = fields.Nested(CompanyField,default=None, required=True)
    languageCodeField = fields.String(default="E",required=True)

class ResGuestsField(ma.Schema):
    
    ProfilesField = fields.List(fields.Nested(ProfilesField),default=None,required=True)

class GuaranteeTravelAgentField(ma.Schema):

    sourceField = fields.String(default="0",required=True)
    typeField = fields.Integer(default=1,required=True)

class GuaranteesAcceptedField(ma.Schema):

    GuaranteeTravelAgentField = fields.Nested(GuaranteeTravelAgentField,default=None,required=True)


class GuaranteeField(ma.Schema):

    GuaranteesAcceptedField = fields.List(fields.Nested(GuaranteesAcceptedField),default=None,required=True)
    guaranteeTypeField = fields.String(default="CIA",required=True)

class GuestCountField(ma.Schema):

    ageFieldSpecified = fields.Boolean(default=True,required=True)
    ageField = fields.Integer()
    ageQualifyingCodeField = fields.String(default="ADULT",required=True)
    ageQualifyingCodeFieldSpecified = fields.Boolean(default=True,required=True)
    countField = fields.Integer(default=1,required=True)
    countFieldSpecified = fields.Boolean(default=True,required=True)

class GuestCountsField(ma.Schema):

    GuestCountField = fields.List(fields.Nested(GuestCountField),default=None,required=True)

class HotelReferenceField(ma.Schema):

    chainCodeField = fields.String(default="CHA",required=True)
    hotelCodeField = fields.String(default="",required=True)

class ItemsField(ma.Schema):

    valueField = fields.String(default="",required=True)

class CommentsField(ma.Schema):

    CommentTypeField = fields.String(default="RESERVATION",required=True)
    guestViewableField = fields.Boolean(default=True,required=True)
    guestViewableFieldSpecified = fields.Boolean(default=True,required=True)
    itemsField = fields.List(fields.Nested(ItemsField),default=None,required=True)
    ItemsElementNameField = fields.List(fields.Integer(),default=None,required=True)

class RatePlansField(ma.Schema):

    ratePlanCodeField = fields.String(default="",required=True)

class BaseField(ma.Schema):

    #currencyCodeField = fields.String(default="USD",required=True)
    currencyTextField = fields.String(default="",required=True)
    valueField = fields.Float(default=0,required=True)

class RatesField(ma.Schema):

    baseField = fields.Nested(BaseField,default=None,required=True)
    effectiveDateField = fields.Date("%Y-%m-%d",default=datetime.now(),required=True)
    effectiveDateFieldSpecified = fields.Boolean(default=True,required=True)
    rateOccurrenceField = fields.String(default="DAILY",required=True)

class RoomRatesField(ma.Schema):

    effectiveDateField = fields.Date("%Y-%m-%d",default=datetime.now(),required=True)
    effectiveDateFieldSpecified = fields.Boolean(default=True,required=True)
    ratePlanCodeField = fields.String(default="",required=True)
    ratesField = fields.List(fields.Nested(RatesField),default=None,required=True)
    roomTypeCodeField = fields.String(default="",required=True)

class RoomTypesField(ma.Schema):

    invBlockCodeField = fields.String(default="",required=True)
    numberOfUnitsField = fields.Integer(default=1,required=True)
    numberOfUnitsSpecifiedField = fields.Boolean(default=True,required=True)
    roomTypeCodeField = fields.String(default="",required=True)

class TimeSpanField(ma.Schema):

    ItemField = fields.Date("%Y-%m-%d",default=datetime.now(),required=True)
    StartDateField = fields.Date("%Y-%m-%d",default=datetime.now(),required=True)

class RoomStaysField(ma.Schema):

    GuaranteeField = fields.Nested(GuaranteeField,default=None,required=True)
    GuestCountsField = fields.Nested(GuestCountsField,default=None,required=True)
    HotelReferenceField = fields.Nested(HotelReferenceField,default=None,required=True)
    CommentsField = fields.List(fields.Nested(CommentsField),default=None,required=True)
    RatePlansField = fields.List(fields.Nested(RatePlansField),default=None,required=True)
    RoomRatesField = fields.List(fields.Nested(RoomRatesField),default=None,required=True)
    RoomTypesField = fields.List(fields.Nested(RoomTypesField),default=None,required=True)
    TimeSpanField = fields.Nested(TimeSpanField,default=None,required=True)

class UserDefinedValuesField(ma.Schema):

    valueNameField = fields.String(default=None,allow_none=True,required=True)
    itemField = fields.String(default=None,allow_none=True,required=True)

class ExternalSystemNumberField(ma.Schema):

    ReferenceNumberField = fields.String(default=None,allow_none=True,required=True)
    LegNumberField = fields.String(default=None,allow_none=True,required=True)
    ReferenceTypeField = fields.String(default=None,allow_none=True,required=True)

class UniqueIDListField(ma.Schema):
    
    typeField = fields.String(default=None,allow_none=True,required=True)
    valueField = fields.String(default=None,allow_none=True,required=True)

class HotelReservationField(ma.Schema):

    marketSegmentField = fields.String(default="WBPR",required=True)
    ResGuestsField = fields.List(fields.Nested(ResGuestsField),default=None,required=True)
    RoomStaysField = fields.List(fields.Nested(RoomStaysField),default=None,required=True)
    UniqueIDListField = fields.List(fields.Nested(UniqueIDListField),default=None,required=True)
    UserDefinedValuesField = fields.List(fields.Nested(UserDefinedValuesField),default=None,required=True)

class Wire_Request(ma.Schema):

    HotelReservationField = fields.Nested(HotelReservationField,default=None,required=True)
    ExternalSystemNumberField = fields.Nested(ExternalSystemNumberField,default=None,required=True)
    xsn = fields.String(default=None,allow_none=True,required=True)