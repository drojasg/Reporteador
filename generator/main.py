from config import db, app
from sqlalchemy import text
from pathlib import Path

class Main():
    models_folder = Path("models/")

    data_types_model = {
        "int": "Integer",
        "bigint": "Integer",
        "mediumint": "Integer",
        "smallint": "Integer",
        "tinyint": "Integer",
        "float": "Float",
        "double": "Decimal",
        "decimal": "Decimal",
        "date": "Date",
        "year": "Date",
        "datetime": "DateTime",
        "timestamp": "DateTime",
        "varchar": "String",
        "char": "String",
        "text": "String",
        "json": "Json",
    }

    default_values_model = {
        "fecha_creacion": "datetime.now",
        "usuario_ultima_modificacion": "",
        "fecha_ultima_modificacion": '"1900-01-01 00:00:00"',
    }
    
    def dump(self):
        table_name = "def_period_season"
        #resources_folder = Path("models/")
        model_name = str(table_name).lower() + ".py"
        #resource_folder = str(table_name).lower()
        
        model_path = self.models_folder / model_name
        #resource_path = resources_folder / resources_folder

        if Path(model_path).exists():
            app.logger.info("The model exists")
        else:
            attributes = ""
            attributes_schema = ""
            sql = "SELECT * FROM information_schema.columns WHERE table_name = '%s'" % table_name
            result = db.session.query("COLUMN_NAME", "DATA_TYPE", "COLUMN_KEY", "IS_NULLABLE",
                                      "COLUMN_DEFAULT", "CHARACTER_MAXIMUM_LENGTH").from_statement(text(sql)).all()

            for item in result:                
                attributes += "\n    " + self.getAlchemySqlAttributeFormat(item)
                attributes_schema += "\n    " + self.getSchemaAttributeFormat(item)
            
            camel_case_name = self.getCamelCaseName(table_name)
            
            self.create_model(camel_case_name, table_name, attributes, attributes_schema, model_path)
    
    def create_model(self, camel_case_name, table_name, attributes, attributes_schema, model_path):
        model_template = Path("generator/model_template.py")
        text_tmp = model_template.read_text()
        text_tmp = text_tmp.replace("$class_name$", camel_case_name)
        text_tmp = text_tmp.replace("$table_name$", '"' + table_name + '"')
        text_tmp = text_tmp.replace("$attributes$", attributes)
        text_tmp = text_tmp.replace(
            "$schema_attributes$", attributes_schema)

        new_model = Path(model_path)
        new_model.write_text(text_tmp)

    def getCamelCaseName(self, name):
        return "".join(single.title() for single in name.split("_"))

    def getAlchemySqlAttributeFormat(self, item):
        attr = item[0]
        data_type = self.data_types_model.get(item[1], "")
        data_type_format = "db."+str(data_type) if data_type != "" else ""
        primary_opt = ", primary_key=True" if item[2] == "PRI" else ""
        nullable_opt = ", nullable=False" if item[2] != "PRI" and item[3] == "NO" else ""
        onupdate_opt = ""
        default_opt = ""
        
        if (item[4] != None and item[4] != ""):
            default_value = self.default_values_model.get(item[0], str(item[4]))
            default_opt = ", default=" + default_value

        if item[0] == "fecha_ultima_modificacion":
            onupdate_opt = ", onupdate = datetime.now"
        
        attr_extra_data = primary_opt + nullable_opt + default_opt + onupdate_opt
        attr_formated = attr + \
            " = db.Column(" + data_type_format + attr_extra_data + ")"

        return attr_formated
    
    def getSchemaAttributeFormat(self, item):
        attr = item[0]
        data_type = self.data_types_model.get(item[1], "")
        data_type_format = "fields."+str(data_type) if data_type != "" else ""
        required_opt = "required=True" if (
            item[2] != "PRI" and item[3] == "NO" and item[4] == None and item[4] == "") else ""
        lenght_opt = ""
        format_opt = ""
        attr_extra_data = required_opt
        
        if (item[5] != None):
            separator = " , " if attr_extra_data != "" else ""
            lenght_opt = separator + "validate=validate.Length(max=" + str(item[5]) + ")"
            attr_extra_data += lenght_opt

        if data_type == "DateTime":
            separator = " , " if attr_extra_data != "" else ""
            format_opt = separator + '"%Y-%m-%d %H:%M:%S"'
            attr_extra_data += format_opt
        
        attr_formated = attr + " = " + data_type_format + "(" + attr_extra_data + ")"
        
        return attr_formated
