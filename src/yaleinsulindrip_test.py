from . import yaleinsulindrip

def test_roundnearest():
    assert yaleinsulindrip.round_nearest(3.25, 0.5) == 3.5
    assert yaleinsulindrip.round_nearest(2.74, 0.5) == 2.5 

def test_is_blood_glucose_target():
    for k in range(120,160):
        assert yaleinsulindrip.is_blood_glucose_target(k)
    
    assert yaleinsulindrip.is_blood_glucose_target(119) == False
    assert yaleinsulindrip.is_blood_glucose_target(161) == False

def test_compute_initial():
    assert yaleinsulindrip.compute_initial(350) == 3.5
    assert yaleinsulindrip.compute_initial(274) == 2.5