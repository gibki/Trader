from xtb import XTBClient

def test_login():
    with XTBClient():
        assert True
