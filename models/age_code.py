from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate

class AgeCode(db.Model):
    __tablename__ = "def_age_code"

    iddef_age_code = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(25), nullable=False)
    disable_edit = db.Column(db.Integer)
    age_from = db.Column(db.Integer)
    age_to = db.Column(db.Integer)
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class AgeCodeSchema(ma.Schema):    
    iddef_age_code = fields.Integer()
    code = fields.String(required=True,validate=validate.Length(max=25))
    disable_edit = fields.Integer()
    age_from = fields.Integer()
    age_to = fields.Integer()    
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetAgeCodeSchema(ma.Schema):    
    iddef_age_code = fields.Integer()
    code = fields.String(validate=validate.Length(max=25))
    disable_edit = fields.Integer()
    age_from = fields.Integer()
    age_to = fields.Integer()    
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class age_code_public(ma.Schema):
    #detail = fields.Dict(fields.String(attribute="agc.code"),fields.Nested(age_code_detail,attribute="agc"))
    class Meta:
        ordered = True

    code = fields.String(attribute="agc.code",validate=validate.Length(max=25))
    age_min = fields.Integer(attribute="agc.age_from")
    age_max = fields.Integer(attribute="agc.age_to")
    description = fields.Method("set_description")
    text = fields.Method("set_text")

    def set_description(self,obj):
        self.description = str(str(obj["agc"].age_from)+"-"+str(obj["agc"].age_to))
        return self.description

    def set_text(self,obj):
        self.text = dict((item.lang_code,item.text) for item in obj["txt"])
        return self.text