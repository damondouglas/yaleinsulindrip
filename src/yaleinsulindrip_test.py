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

def test_compute_hourly_bg_change():
    assert yaleinsulindrip.compute_hourly_bg_change(
        (200, 0),
        (100, 60)
    ) == 100

    assert yaleinsulindrip.compute_hourly_bg_change(
        (200, 0),
        (100, 120)
    ) == 50

def test_delta():
    for rate in [0,0.5,1,1.5,2,2.5]:
        assert yaleinsulindrip.delta(rate) == 0.5

    for rate in [3,3.5,4,4.5,5,5.5,6]:
        assert yaleinsulindrip.delta(rate) == 1

    for rate in [6.5, 7, 7.5, 8, 8.5, 9, 9.5]:
        assert yaleinsulindrip.delta(rate) == 1.5

    for rate in [10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5]:
        assert yaleinsulindrip.delta(rate) == 2

    for rate in [15, 15.5, 16, 16.5, 17, 17.5, 18, 18.5, 19, 19.5]:
        assert yaleinsulindrip.delta(rate) == 3

    for rate in [20, 21, 22, 23, 24]:
        assert yaleinsulindrip.delta(rate) == 4
        

def test_case_bg_gt_200():
    current_rate = 3

    for hourly_bg_change in range(1,20):
        assert yaleinsulindrip.case_bg_gt_200(current_rate, hourly_bg_change) == [(0,5)]
    
    for hourly_bg_change in range(-20, 0):
        assert yaleinsulindrip.case_bg_gt_200(current_rate, hourly_bg_change) == [(0,4)]
    
    for hourly_bg_change in range(-60, -21):
        assert yaleinsulindrip.case_bg_gt_200(current_rate, hourly_bg_change) == [(0,3)]

    for hourly_bg_change in range(-80, -61):
        assert yaleinsulindrip.case_bg_gt_200(current_rate, hourly_bg_change) == [(0,2)]
    
    for hourly_bg_change in range(-100, -81):
        assert yaleinsulindrip.case_bg_gt_200(current_rate, hourly_bg_change) == [(0,0),(30,1)]


`

