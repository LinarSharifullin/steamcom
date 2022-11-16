import math


WALLET_FEE_BASE = 0
WALLET_FEE_PERCENT = 0.05
WALLET_FEE_MINIMUM = 1


def get_int_price(strAmount):
    if not strAmount:
        return 0
    elif strAmount < 0.03:
        strAmount = 0.03
    flAmount = float(strAmount) * 100
    nAmount = math.floor(0 if not type(flAmount) else flAmount + 0.000001)
    nAmount = max(nAmount, 0)
    return nAmount


def calculate_fee_amount(amount, publisherFee):
    publisherFee = 0.1
    iterations = 0
    received = int((amount - int(WALLET_FEE_BASE)) / (
        float(WALLET_FEE_PERCENT) + float(publisherFee) + 1))
    bEverUndershot = False
    fees = sended(received, publisherFee)

    while (fees['amount'] != amount and iterations < 10):
        if fees['amount'] > amount:
            if bEverUndershot:
                fees = sended(received-1, publisherFee)
                fees['steam_fee'] += amount - fees['amount']
                fees['amount'] = amount
                break
            else:
                received -= 1
        else:
            bEverUndershot = True
            received += 1

        fees = sended(received, publisherFee)
        iterations += 1

    return fees


def sended(receivedAmount, publisherFee):
    nSteamFee = int(math.floor(max(receivedAmount * float(WALLET_FEE_PERCENT),
                    WALLET_FEE_MINIMUM) + int(WALLET_FEE_BASE)))
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
    priceInt = get_int_price(price)
    fees = calculate_fee_amount(priceInt, 0.1)
    return fees
