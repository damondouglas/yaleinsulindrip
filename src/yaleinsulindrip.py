"""
Implementation of yale insulin infusion (YII) protocol.

325064004  Insulin soluble human 100units/mL injection solution 10mL vial (product)
258666001  Unit

Reference:
Shetty S, Inzucchi SE, Goldberg PA, Cooper D, Siegel MD, Honiden S. 
Adapting to the new consensus guidelines for managing hyperglycemia 
during critical illness: The Updated Yale Insulin Infusion Protocol. 
Endocr Pract. 2012;18:363-370.
<http://inpatient.aace.com/sites/all/files/Yale_IIP_MICU120-160_2011.pdf; 
Accessed 06/28/2017>

"""
import Algorithmia

INCREMENT=0.5

def apply(input):
    """
    Method called by algorithmia platform

    """
    return "hello {}".format(input)

def round_nearest(x, a):
    """
    Computes x rounded to the nearest a.
    Note python3 rounds down at tie break but
    the YII protocol requires rounding up.

    Parameters
    ----------
    x : float
    a : float

    Returns
    -------
    float
    """
    (quotient, remainder) = divmod(x, a)
    base = quotient * a
    return base + (0 if remainder < a/2 else a)


def is_blood_glucose_target(bg):
    """
    Determines whether blood glucose level(mg/dL) is in target range.

    Parameters
    ----------
    bg : (int)

    Returns
    -------
    bool
    """
    return bg >= 120 and bg <= 160

def compute_initial(bg):
    """
    Computes initial bolus and infusion to nearest 0.5 units/hr
    based on blood glucose level (mg/dL).

    Parameters
    ----------
    bg : (int)

    Returns
    -------
    (float)
    """

    return round_nearest(bg/100, INCREMENT)

def _infusion_change_matrix(current_rate, delta_value):
    return [
        [(0, current_rate + 2 * delta_value)],
        [(0, current_rate + delta_value)],
        [(0, current_rate)],
        [(0, current_rate - delta_value)],
        [(0, 0), (30, current_rate - 2 * delta_value)]
    ]

def compute_insulin_case_bg_gt_200(current_rate, hourly_bg_change):
    """
    """
    delta_value = delta(current_rate)

    if hourly_bg_change > 0:
        return _infusion_change_matrix(current_rate, delta_value)[0]
    
    if hourly_bg_change >= -20 and hourly_bg_change <= 0:
        return _infusion_change_matrix(current_rate, delta_value)[1]

    if hourly_bg_change >= -60 and hourly_bg_change <= -21:
        return _infusion_change_matrix(current_rate, delta_value)[2]

    if hourly_bg_change >= -80 and hourly_bg_change <= -61:
        return _infusion_change_matrix(current_rate, delta_value)[3]
    
    if hourly_bg_change < -80:
        return _infusion_change_matrix(current_rate, delta_value)[4]

def compute_insulin_case_bg_btwn_160_199(current_rate, hourly_bg_change):
    """
    """
    delta_value = delta(current_rate)

    if hourly_bg_change > 60:
        return _infusion_change_matrix(current_rate, delta_value)[0]
    
    if hourly_bg_change >= 0 and hourly_bg_change <= 60:
        return _infusion_change_matrix(current_rate, delta_value)[1]

    if hourly_bg_change >= -40 and hourly_bg_change <= -1:
        return _infusion_change_matrix(current_rate, delta_value)[2]

    if hourly_bg_change >= -60 and hourly_bg_change <= -41:
        return _infusion_change_matrix(current_rate, delta_value)[3]
    
    if hourly_bg_change < -60:
        return _infusion_change_matrix(current_rate, delta_value)[4]

def compute_insulin_case_bg_btwn_120_159(current_rate, hourly_bg_change):
    """
    """
    delta_value = delta(current_rate)

    if hourly_bg_change > 40:
        return _infusion_change_matrix(current_rate, delta_value)[1]

    if hourly_bg_change >= -20 and hourly_bg_change <= 40: 
        return _infusion_change_matrix(current_rate, delta_value)[2]

    if hourly_bg_change >= -40 and hourly_bg_change <= -21:
        return _infusion_change_matrix(current_rate, delta_value)[3]
    
    if hourly_bg_change < -40:
        return _infusion_change_matrix(current_rate, delta_value)[4]

def compute_insulin_case_bg_btwn_100_119(current_rate, hourly_bg_change):
    """
    """
    delta_value = delta(current_rate)

    if hourly_bg_change >0: 
        return _infusion_change_matrix(current_rate, delta_value)[2]

    if hourly_bg_change >= -20 and hourly_bg_change <= 0:
        return _infusion_change_matrix(current_rate, delta_value)[3]
    
    if hourly_bg_change < -20:
        return _infusion_change_matrix(current_rate, delta_value)[4]


def delta(current_rate):
    if current_rate < 3:
        return INCREMENT
    
    if current_rate >= 3 and current_rate <= 6:
        return INCREMENT * 2
    
    if current_rate >= 6.5 and current_rate <= 9.5:
        return INCREMENT * 3
    
    if current_rate >= 10 and current_rate <= 14.5:
        return INCREMENT * 4

    if current_rate >= 15 and current_rate <= 19.5:
        return INCREMENT * 6
    
    if current_rate >= 20:
        return INCREMENT * 8

def compute_hourly_bg_change(current_bg, previous_bg):
    """
    """
    if (type(current_bg) != tuple or type(previous_bg) != tuple):
        raise TypeError("current_bg and previous_bg must be tuple")
    
    timediff_in_hour = abs(current_bg[1] - previous_bg[1]) / 60

    return int((current_bg[0] - previous_bg[0]) / timediff_in_hour)

def notes():
    return """
The following IIP is intended for use in hyperglycemic adult patients in the ICU, adapted from our earlier protocols, in keeping with the latest glucose guidelines from national organizations. It should
NOT be used in diabetic ketoacidosis (DKA) or hyperosmolar hyperglycemic state (HHS), as these patients may require higher initial insulin doses, IV dextrose at some point, and important
adjunctive therapies for their fluid/acid-base/electrolyte/divalent status. (See 'DKA Guidelines' in YNHH Clinical Practice Manual (CPM) for further instructions.) In any patient with BG >500 mg/dL,
the initial orders should also be carefully reviewed with the MD, since a higher initial insulin dose and additional monitoring/therapy may be required. If the patient’s response to the insulin infusion is
at any time unusual or unexpected, or if any situation arises that is not adequately addressed by this protocol, the MD must be contacted for assessment and further orders.

PATIENT SELECTION: Begin IIP in any ICU patient with more than 2 BGs >180 mg/dl who is not expected to rapidly normalize their
glycemic status. Patients who are eating (see #9 below); transferring out of ICU imminently (<24 hrs); or pre-terminal or being considered
for CMO status are generally not appropriate candidates for this IIP.

TARGET BLOOD GLUCOSE (BG) RANGE: .120-160 mg/dL

INSULIN INFUSION SOLUTION: Obtain from pharmacy (1 unit Regular Human Insulin / 1 cc 0.9 % NaCl).
PRIMING: Before connecting, flush 20 cc infusion through all tubing.

Reference:
Shetty S, Inzucchi SE, Goldberg PA, Cooper D, Siegel MD, Honiden S. 
Adapting to the new consensus guidelines for managing hyperglycemia 
during critical illness: The Updated Yale Insulin Infusion Protocol. 
Endocr Pract. 2012;18:363-370.
<http://inpatient.aace.com/sites/all/files/Yale_IIP_MICU120-160_2011.pdf; 
Accessed 06/28/2017>

    """