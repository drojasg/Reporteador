import re
from calendar import monthrange, datetime

from models.payment_card_type import PaymentCardType

'''
    Card validation class
'''
class CardValidation():
    cards = {
        "visa": {
            "code": "visa",
            "regex": re.compile(r'^4\d{12}(\d{3})?$')
        },
        "mastercard": {
            "code": "mastercard",
            "regex": re.compile(r'''
                ^(5[1-5]\d{4}|677189)\d{10}$|
                ^(222[1-9]|2[3-6]\d{2}|27[0-1]\d|2720)\d{12}$
            ''', re.VERBOSE)
        },
        "amex": {
            "code": "amex",
            "regex": re.compile(r'^3[47]\d{13}$')
        }
    }

    def __init__(self, number, exp_month = None, exp_year = None):
        #just valid digits
        self.number = re.compile(r'\D').sub('', number)
        self.expired_after = None
        
        if exp_month is not None and exp_year is not None:
            weekday, day_count = monthrange(exp_year, exp_month)

            self.expired_after = datetime.datetime(
                exp_year,
                exp_month,
                day_count,
                23,
                59,
                59,
                999999
            )
    
    @property
    def is_valid(self):
        '''
            Valid Luhn algorithm on the number
        '''
        if not self.number:
            return False
        
        dub, tot = 0, 0
        for i in range(len(self.number) - 1, -1, -1):
            for c in str((dub + 1) * int(self.number[i])):
                tot += int(c)
            dub = (dub + 1) % 2

        return (tot % 10) == 0

    @property
    def is_expired(self):
        '''
            Check if the date is expired
        '''
        #if not set exp_mont & exp_year is expired
        if self.expired_after is None:
            return True
        
        #retrieve current datetime in UTC
        utc_now = datetime.datetime.utcnow()

        #retrieve datetime of Cancun
        cancun_now = utc_now - datetime.timedelta(hours=5)
        
        # check if card expiration is valid
        return cancun_now > self.expired_after
    

    @property
    def code(self):
        '''
            Get the card brand code
        '''
        for key, item in self.cards.items():
            regexp = item["regex"]
            if regexp.match(self.number):
                return item["code"]
        
        return None
    
    @property
    def code_fin(self):
        '''
            Get the code for Finance Clever API
        '''
        payment_card_type = PaymentCardType.query.filter(PaymentCardType.code == self.code,\
            PaymentCardType.estado == 1).first()
        
        if payment_card_type is not None:
            return payment_card_type.code_fin

        return None