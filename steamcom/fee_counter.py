import math, warnings

from steamcom.models import FeePrice


class FeeCounter:
    def __init__(self, fee_percent: float = 0.05,  market_minimum: int = 1,
                 currency_increment: int = 1,
                 publisher_fee_percent_default: float = 0.1):
        self.fee_percent = fee_percent
        self.market_minimum = market_minimum
        self.currency_increment = currency_increment
        self.publisher_fee_percent_default = publisher_fee_percent_default

    def get_int_price(self, float_price):
        if not float_price:
            return 0
        elif float_price < 0.03:
            float_price = 0.03
        float_amount = float_price * 100
        int_amount = math.floor(0 if not type(float_amount) else float_amount + 0.000001)
        int_amount = max(int_amount, 0)
        return int_amount

    def to_valid_market_price(self, price):
        if price <= self.market_minimum:
            return self.market_minimum
        if self.currency_increment > 1:
            amount = price/self.currency_increment
            sign = -1 if amount < 0 else 1
            amount = sign * math.floor(abs(amount) + 0.5) * self.currency_increment
            return amount
        return price
    
    def calculate_fee(self, price, percent):
        if percent <= 0:
            return 0
        return self.to_valid_market_price(math.floor(price * percent))
    
    def get_total_with_fees(self, price):
        valid_market_price = self.to_valid_market_price(price)
        pub_fee = self.calculate_fee(price, self.publisher_fee_percent_default)
        steam_fee = self.calculate_fee(price, self.fee_percent)
        return valid_market_price + pub_fee + steam_fee

    def get_item_price_from_total(self, total_price: int) -> int:
        initial_guess = math.floor(
            total_price / ( 1.0 + self.publisher_fee_percent_default + self.fee_percent))
        max_base = total_price - (2 * self.market_minimum)
        base_price = self.to_valid_market_price(min(initial_guess, max_base))
        higher = False
        for _ in range(30):
            calculated = self.get_total_with_fees(base_price)
            if calculated == total_price:
                return base_price
            if calculated < total_price:
                if higher:
                    break
                base_price += self.currency_increment
            else:
                if base_price <= self.market_minimum:
                    break
                base_price -= self.currency_increment
                higher = True
        return max(self.market_minimum, base_price)
    
    def calculate_seller_price(self, buyer_price: float) -> FeePrice:
        """
        Removes market commission from the price

        Returns:
        The prices is in minor units, which Steam market works with
        """
        int_buyer_price = self.get_int_price(buyer_price)
        seller_receive = self.get_item_price_from_total(int_buyer_price)
        buyer_pay = self.get_total_with_fees(seller_receive)
        return FeePrice(buyer_pay, seller_receive)



class OldFeeCounter:
    """
    This is an old algorithm that calculates fees incorrectly
    Use FeeCounter instead. This class will be removed in the next version
    """
    def __init__(self, fee_base: int = 0, fee_percent: float = 0.05,
                 fee_minimum: int = 1):
        self.fee_base = fee_base
        self.fee_percent = fee_percent
        self.fee_minimum = fee_minimum


    def get_int_price(self, strAmount):
        if not strAmount:
            return 0
        elif strAmount < 0.03:
            strAmount = 0.03
        flAmount = float(strAmount) * 100
        nAmount = math.floor(0 if not type(flAmount) else flAmount + 0.000001)
        nAmount = max(nAmount, 0)
        return nAmount


    def calculate_fee_amount(self, amount, publisherFee):
        publisherFee = 0.1
        iterations = 0
        received = int((amount - self.fee_base) / (
            self.fee_percent + float(publisherFee) + 1))
        bEverUndershot = False
        fees = self.sended(received, publisherFee)

        while (fees['amount'] != amount and iterations < 10):
            if fees['amount'] > amount:
                if bEverUndershot:
                    fees = self.sended(received-1, publisherFee)
                    fees['steam_fee'] += amount - fees['amount']
                    fees['amount'] = amount
                    break
                else:
                    received -= 1
            else:
                bEverUndershot = True
                received += 1

            fees = self.sended(received, publisherFee)
            iterations += 1

        return fees


    def sended(self, receivedAmount, publisherFee):
        nSteamFee = int(math.floor(max(receivedAmount * self.fee_percent,
                        self.fee_minimum) + self.fee_base))
        nPublisherFee = int(math.floor(max(
            receivedAmount * publisherFee, 1) if publisherFee > 0 else 0))
        nAmountToSend = receivedAmount + nSteamFee + nPublisherFee
        return {
            'steam_fee': nSteamFee,
            'publisher_fee': nPublisherFee,
            'fees': nSteamFee + nPublisherFee,
            'buyer_pay': int(nAmountToSend),
            'amount': int(nAmountToSend),
            'seller_receive': receivedAmount
        }


def count(price: float) -> dict:
    """"
    This is an old algorithm that calculates fees incorrectly
    Use FeeCounter instead. This function will be removed in the next version
    """
    warnings.warn(
        (
            "This is an old algorithm that calculates fees incorrectly. "
            "Use FeeCounter instead. "
            "This function will be removed in the next version"
        ),
        DeprecationWarning,
        stacklevel=2
    )
    old_fee_counter = OldFeeCounter()
    priceInt = old_fee_counter.get_int_price(price)
    fees = old_fee_counter.calculate_fee_amount(priceInt, 0.1)
    return fees
