import math



class FeeCounter:
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


    def count(self, price: float) -> dict:
        priceInt = self.get_int_price(price)
        fees = self.calculate_fee_amount(priceInt, 0.1)
        return fees

