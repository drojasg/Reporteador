import datetime

class Utilities():
    def format_dates_apply(self,date_start,date_end):
        dates = []

        for n in range(int ((date_end - date_start).days+1)):
            dates.append(date_start + datetime.timedelta(days=n))

        return dates

    #Por defecto ordena de menor a mayor
    def sort_dict(self,obj_list,key_sort,asc=True):

        return sorted(obj_list, key = lambda i: (i[key_sort] is None, i[key_sort]),reverse=asc)

    def get_valid_dates(self,date):
        valid_date = date

        if isinstance(date,str):
            valid_date = datetime.datetime.strptime(date,'%Y-%m-%d').date()

        return valid_date

    def get_valid_dates_str(self,date):
        valid_date = date

        if isinstance(date,datetime.date):
            valid_date = datetime.datetime.strftime(date,"%Y-%m-%d")

        return valid_date
    def check_field_exists_data(self,data,field):
        return any(field in data_elem for data_elem in data)

    def check_field_exists_schema(self,schema,field):
        return field in schema.fields
