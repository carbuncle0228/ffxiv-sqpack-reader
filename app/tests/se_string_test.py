from app.se_string import SeString


def Macro_HYPHEN(arg):
    return "-"


def Macro_NEW_LINE(arg):
    return "<hex:02100103>"


def test_se_string():
    str_bytes = b"Defeat the notorious monsters Barometz, Slippery Sykes, Gluttonous Gertrude, bomb baron, Unknown Soldier, great buffalo, and Old Six\x02\x1f\x01\x03arms."
    se_string = SeString(str_bytes)
    s = str(se_string)
    evaluated_value = eval(f'f"""{s}"""')

    assert (
        s
        == "Defeat the notorious monsters Barometz, Slippery Sykes, Gluttonous Gertrude, bomb baron, Unknown Soldier, great buffalo, and Old Six{Macro_HYPHEN(b'')}arms."
    )
    assert (
        evaluated_value
        == "Defeat the notorious monsters Barometz, Slippery Sykes, Gluttonous Gertrude, bomb baron, Unknown Soldier, great buffalo, and Old Six-arms."
    )


def test_se_string_new_line():
    str_bytes = b"Obtain a complete set of harlequin armor consisting of a harlequin's cap, a harlequin's acton, and a pair of harlequin's tights.\x02\x10\x01\x03\xe2\x80\xbbSpeak to Jonathas in Old Gridania with all three items equipped."
    se_string = SeString(str_bytes)
    s = str(se_string)
    evaluated_value = eval(f'f"""{s}"""')
    assert (
        s
        == "Obtain a complete set of harlequin armor consisting of a harlequin's cap, a harlequin's acton, and a pair of harlequin's tights.{Macro_NEW_LINE(b'')}※Speak to Jonathas in Old Gridania with all three items equipped."
    )
    assert (
        evaluated_value
        == "Obtain a complete set of harlequin armor consisting of a harlequin's cap, a harlequin's acton, and a pair of harlequin's tights.<hex:02100103>※Speak to Jonathas in Old Gridania with all three items equipped."
    )


def test_se_string_italic():
    str_bytes = b"Obtain Curtana, a Holy Shield, a pair of Sphairai, Bravura, Gae Bolg, the Artemis Bow, Thyrus, a Stardust Rod, the Veil of Wiyu, and a copy of the \x02\x1a\x02\x02\x03Omnilex\x02\x1a\x02\x01\x03 in the quest \xe2\x80\x9cA Relic Reborn.\xe2\x80\x9d"
    se_string = SeString(str_bytes)
    s = str(se_string)
    evaluated_value = eval(f'f"""{s}"""')
    assert (
        s
        == "Obtain a complete set of harlequin armor consisting of a harlequin's cap, a harlequin's acton, and a pair of harlequin's tights.{Macro_NEW_LINE(b'')}※Speak to Jonathas in Old Gridania with all three items equipped."
    )
    assert (
        evaluated_value
        == "Obtain a complete set of harlequin armor consisting of a harlequin's cap, a harlequin's acton, and a pair of harlequin's tights.<hex:02100103>※Speak to Jonathas in Old Gridania with all three items equipped."
    )
