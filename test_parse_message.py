from trader import parse_message
from xtb import CMD

def test_parse_message1():
    text = '''
CHFJPY BUY @ 164.83 / 164.88

            TP: 165.03 (scalper) 
            TP: 165.33 (intraday) 
            TP: 165.83 (swing)
            SL: 164.23

            🟢 Uzywaj MM  2-3%
'''
    result = parse_message(text)
    assert result is not None
    print(result)
    assert result['symbol'] == 'CHFJPY'
    assert result['command'] == CMD.BUY
    assert round(result['price'], 2) == round(164.83, 2)
    assert round(result['tp1'], 2) == round(165.03, 2)
    assert round(result['tp2'], 2) == round(165.33, 2)
    assert round(result['tp3'], 2) == round(165.83, 2)
    assert round(result['sl'], 2) == round(164.23, 2)

def test_parse_message2():
    text = '''
GBPCHF sell 📉

ENTRY @  1.08702 
SL:    1.09244 (-50) pips ❌

TP1:  1.08197 (+50) pips   
TP2:  1.07695 (+100) pips 
TP3:  1.07162 (+160) pips       
'''
    result = parse_message(text)
    assert result is not None
    print(result)
    assert result['symbol'] == 'GBPCHF'
    assert result['command'] == CMD.SELL
    assert round(result['price'], 5) == round(1.08702, 5)
    assert round(result['tp1'], 5) == round(1.08197, 5)
    assert round(result['tp2'], 5) == round(1.07695, 5)
    assert round(result['tp3'], 5) == round(1.07162, 5)
    assert round(result['sl'], 5) == round(1.09244 , 5)

def test_parse_message3():
    text = '''
US30 SELL  37630 📉

SL 37750 ❌

TP 37600
TP 37530
TP 37450
TP 37000

Probujemy shorta na DJ 📉
'''
    result = parse_message(text)
    assert result is not None
    print(result)
    assert result['symbol'] == 'US30'
    assert result['command'] == CMD.SELL
    assert round(result['price'], 5) == round(37630, 5)
    assert round(result['tp1'], 5) == round(37600, 5)
    assert round(result['tp2'], 5) == round(37530, 5)
    assert round(result['tp3'], 5) == round(37450, 5)
    assert round(result['sl'], 5) == round(37750 , 5)
