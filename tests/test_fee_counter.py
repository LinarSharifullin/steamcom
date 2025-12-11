from steamcom.fee_counter import FeeCounter


def test_rub():
    fee_counter = FeeCounter(market_minimum=77)
    assert fee_counter.calculate_seller_price(-1000) == 77
    assert fee_counter.calculate_seller_price(-5.5) == 77
    assert fee_counter.calculate_seller_price(-1) == 77
    assert fee_counter.calculate_seller_price(0) == 77
    assert fee_counter.calculate_seller_price(0.01) == 77
    assert fee_counter.calculate_seller_price(1) == 77
    assert fee_counter.calculate_seller_price(1.7) == 77
    assert fee_counter.calculate_seller_price(2.31) == 77
    assert fee_counter.calculate_seller_price(2.33) == 79
    assert fee_counter.calculate_seller_price(3) == 146
    assert fee_counter.calculate_seller_price(5.4) == 386
    assert fee_counter.calculate_seller_price(10) == 845
    assert fee_counter.calculate_seller_price(11.5) == 995
    assert fee_counter.calculate_seller_price(12) == 1042
    assert fee_counter.calculate_seller_price(120) == 10436
    assert fee_counter.calculate_seller_price(1000) == 86958
    assert fee_counter.calculate_seller_price(50000.99) == 4347913

def test_kzt():
    fee_counter = FeeCounter(market_minimum=500, currency_increment=100)
    assert fee_counter.calculate_seller_price(-1000) == 500
    assert fee_counter.calculate_seller_price(-5.5) == 500
    assert fee_counter.calculate_seller_price(-1) == 500
    assert fee_counter.calculate_seller_price(0) == 500
    assert fee_counter.calculate_seller_price(0.01) == 500
    assert fee_counter.calculate_seller_price(1) == 500
    assert fee_counter.calculate_seller_price(10) == 500
    assert fee_counter.calculate_seller_price(15) == 500
    assert fee_counter.calculate_seller_price(16) == 600
    assert fee_counter.calculate_seller_price(25) == 1500
    assert fee_counter.calculate_seller_price(25.4) == 1500
    assert fee_counter.calculate_seller_price(125) == 10900
    assert fee_counter.calculate_seller_price(200.5) == 17400
    assert fee_counter.calculate_seller_price(999) == 86900
    assert fee_counter.calculate_seller_price(10000) == 869500
    assert fee_counter.calculate_seller_price(100000) == 8695600
    assert fee_counter.calculate_seller_price(300000) == 26086900

def test_brl():
    fee_counter = FeeCounter(market_minimum=5)
    assert fee_counter.calculate_seller_price(-100) == 5
    assert fee_counter.calculate_seller_price(-1.5) == 5
    assert fee_counter.calculate_seller_price(0) == 5
    assert fee_counter.calculate_seller_price(0.05) == 5
    assert fee_counter.calculate_seller_price(0.15) == 5
    assert fee_counter.calculate_seller_price(0.16) == 6
    assert fee_counter.calculate_seller_price(0.18) == 8
    assert fee_counter.calculate_seller_price(0.25) == 15
    assert fee_counter.calculate_seller_price(0.99) == 86
    assert fee_counter.calculate_seller_price(1.5) == 131
    assert fee_counter.calculate_seller_price(2) == 175
    assert fee_counter.calculate_seller_price(5.5) == 479
    assert fee_counter.calculate_seller_price(100) == 8697
    assert fee_counter.calculate_seller_price(10000) == 869566
    assert fee_counter.calculate_seller_price(100000.5) == 8695697
