from models.config_external_services import ConfigExternalServices as ConfigServicesModel
from models.exchange_rate import ExchangeRate as ExchangeRateModel
from models.currency import Currency as CurrencyModel
from datetime import date
from config import db, app, base
import json, requests

class ExchangeRateService():
    
    def __init__(self):
        #get config data
        env = base.environment
        self.config = ConfigServicesModel.query.filter(ConfigServicesModel.code == "openex", ConfigServicesModel.estado == 1, ConfigServicesModel.env == env).first()
        self.base_url = self.config.url
        self.account_id = self.config.settings.get("account_id", "")
    
    @staticmethod
    def convert_to_currency(currency_select,currency_vaucher,value_vaucher,date_now):
        to_usd_amount = 1
        exange_amount = 1
        currency_vaucher = currency_vaucher.upper()
        currency_select = currency_select.upper()

        try:
            if currency_vaucher != currency_select:
                Exange_apply = True
                if currency_vaucher != "USD":
                    exangeDataMx = ExchangeRateService.get_exchange_rate_date(date_now,currency_vaucher)
                    to_usd_amount = round(exangeDataMx.amount,2)

                if currency_select != "USD":
                    exangeData = ExchangeRateService.get_exchange_rate_date(date_now,currency_select)
                    exange_amount = round(exangeData.amount,2)
                
            if Exange_apply == True:
                value_vaucher = value_vaucher / to_usd_amount
                value_vaucher = value_vaucher * exange_amount

        except Exception as error:
            pass
        
        return round(value_vaucher, 6)
    
    @staticmethod
    def get_exchange_rate_date(finding_date, currency_code):
        currency = CurrencyModel.query.filter(CurrencyModel.currency_code == currency_code, CurrencyModel.estado == 1).first()
        
        if currency is None:
            raise Exception("Currency code {} not exists".format(currency_code))

        exchange_rate = ExchangeRateModel.query.filter(
            ExchangeRateModel.date == finding_date, ExchangeRateModel.currency_code == currency_code, ExchangeRateModel.estado == 1).first()
        
        if exchange_rate is None:
            #if not exist a exchange rate for the finding date, so get the last one
            exchange_rate = ExchangeRateModel.query.filter(ExchangeRateModel.currency_code == currency_code, ExchangeRateModel.estado == 1)\
                .order_by(ExchangeRateModel.idop_exchange_rate.desc()).first()
        
        if currency.own_exchange_rate > 0:
            exchange_rate = ExchangeRateModel()
            exchange_rate.amount = currency.own_exchange_rate
        
        return exchange_rate
    
    def save_exchange_rate(self, search_date, username):
        """
            Save exchange rate for all currencies configured in currency table.
            The data is retrieves from external service
            param: seach_date (optional) Date to retrieve exchange rates
            param: username Username of the user execute the process

            return: Dict Data Rates
        """
        default_currency = "USD"
        response = None
        
        #get currencies
        currency_list = CurrencyModel.query.filter(CurrencyModel.estado == 1, CurrencyModel.currency_code != default_currency).all()
        
        #currencies separate by comma and call the service
        currencies = ",".join([str(item.currency_code) for item in currency_list])

        if search_date != date.today():
            response = self.get_historical_exchange_external(search_date, currencies)
        else:
            search_date = date.today()
            response = self.get_latest_exchange_external(currencies)
        
        response_list = response["rates"]

        exchange_list = ExchangeRateModel.query.filter(
            ExchangeRateModel.estado == 1, 
            ExchangeRateModel.date == search_date, 
            ExchangeRateModel.currency_code.in_(currencies.split(","))).all()
        
        #iterate the results
        for item, value in response_list.items():
            quote_currency = item
            quote_amount = round( value , 4)

            exchange_rate = next((aux_item for aux_item in exchange_list if aux_item.currency_code ==
                                quote_currency), None)
            
            #if not exist create
            if exchange_rate is None:
                exchange_rate = ExchangeRateModel()
                exchange_rate.date = search_date
                exchange_rate.currency_code = quote_currency
                exchange_rate.amount = quote_amount
                exchange_rate.estado = 1
                exchange_rate.usuario_creacion = username
                db.session.add(exchange_rate)
            #if exists update
            elif exchange_rate.amount != quote_amount:
                exchange_rate.amount = quote_amount
                exchange_rate.usuario_ultima_modificacion = username
                db.session.add(exchange_rate)
        
        db.session.commit()

        return response
    
    def get_latest_exchange_external(self, currencies):
        """
            Get the latest exchange rate (today) of all the currencies gived.
            param: currencies Currencies separates by comma (g.e. usd, mxn)

            return: Response request with rates
        """
        response = requests.get(self.base_url+'/latest.json?app_id='+self.account_id+'&symbols='+currencies, verify=False)
        response_json = response.json()

        return response_json
    
    def get_historical_exchange_external(self, search_date, currencies):
        """
            Get the exchange rate of the date and all the currencies gived.
            param: search_date (optional) Date to retrieve exchange rates
            param: currencies Currencies separates by comma (g.e. usd, mxn)

            return: Response request with rates
        """
        response = requests.get(self.base_url+'/historical/'+search_date+'.json?app_id='+self.account_id+'&symbols='+currencies, verify=False)
        response_json = response.json()

        return response_json
    