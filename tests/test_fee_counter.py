from steamcom.fee_counter import FeeCounter

COMMISSION_TESTS = {
    "RUB": {
        "market_minimum": 79,
        "currency_increment": 1,
        "cases": [
            (-1.5, 79, 237),
            (0, 79, 237),
            (0.79, 79, 237),
            (2.37, 79, 237),
            (2.38, 80, 238),
            (9.55, 797, 955),
            (9.56, 798, 956),
            (9.58, 799, 957),
            (9.68, 809, 968),
            (9.79, 819, 979),
            (9.80, 819, 979),
            (9.81, 820, 981),
            (10, 838, 1000),
            (1150.09, 100009, 115009),
            (1150.10, 100009, 115009),
            (1150.11, 100010, 115011),
            (100000.00, 8695653, 10000000),
        ],
    }
}


def test_calculate_seller_price():
    for currency_data in COMMISSION_TESTS.values():
        fc = FeeCounter(
            market_minimum=currency_data["market_minimum"],
            currency_increment=currency_data["currency_increment"],
        )
        for price, seller_receive, buyer_pay in currency_data["cases"]:
            fee_price = fc.calculate_seller_price(price)
            assert fee_price.seller_receive == seller_receive
            assert fee_price.buyer_pay == buyer_pay
