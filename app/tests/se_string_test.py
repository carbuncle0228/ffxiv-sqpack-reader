from app.se_string import SeString


def test_se_string():
    str_bytes = b"Defeat the notorious monsters Barometz, Slippery Sykes, Gluttonous Gertrude, bomb baron, Unknown Soldier, great buffalo, and Old Six\x02\x1f\x01\x03arms."
    se_string = SeString(str_bytes)
    s = str(se_string)
    assert s
