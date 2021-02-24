from models.country import Country as cnModel
from models.market_segment import MarketSegment as mkModel

class Market():
    #Obtener market
    def getMarketInfo(self,market_code):
        
        data = mkModel.query.join(cnModel,cnModel.idmarket_segment==mkModel.iddef_market_segment\
        ).filter(mkModel.estado==1, cnModel.country_code==market_code, cnModel.estado==1).first()

        if data is None:
            raise Exception("Codigo de mercado no encontrado, favor de verificar")
        
        return data