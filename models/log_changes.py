from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
import json

class LogChanges(db.Model):
    __tablename__ = "log_changes"

    ACTION_CREATE = 1
    ACTION_UPDATE = 2

    idlog_changes = db.Column(db.Integer, primary_key = True)
    table_name = db.Column(db.String(150), nullable = False)
    row_id = db.Column(db.Integer)
    action = db.Column(db.Integer)
    data = db.Column(db.JSON, nullable = False, default = "{}")
    username = db.Column(db.String(45), nullable = False)
    estado = db.Column(db.Integer, nullable = False)
    fecha_creacion = db.Column(db.DateTime, default = datetime.utcnow)

    def save(self, connection):
        connection.execute(
            self.__table__.insert(),
            table_name = self.table_name,
            row_id = self.row_id,
            action = self.action,
            data = self.data,
            username = self.username,
            estado = self.estado,
            fecha_creacion = datetime.now()
        )

class LogChangesSchema(ma.Schema):
    idlog_changes = fields.Integer()
    table_name = fields.String(required = True, validate = validate.Length(max = 150))
    row_id = fields.Integer()
    action = fields.Integer()
    data = fields.Method("decodeJSON") #fields.Dict() 
    username = fields.String(required = True, validate = validate.Length(max = 45))
    estado = fields.Integer()
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

    def decodeJSON(self, obj):
        self.data = json.loads(obj.data)
        return self.data