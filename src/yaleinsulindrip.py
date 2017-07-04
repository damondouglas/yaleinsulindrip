"""
Implementation of yale insulin infusion (YII) protocol.

Note [snomed](http://browser.ihtsdotools.org/) codes used below:
325064004  Insulin soluble human 100units/mL injection solution 10mL vial (product)
258666001  Unit
258949000  Unit/hour
255560000  Intravenous
166888009  Blood glucose method

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

    Parameter
    =========
    input : (dict) of algorithm variables:

    current_rate: current insulin infusion rate (units/hr)
    current_bg: current blood glucose level (mg/dL)
    consecutive_bg_in_target_count: number of blood glucose measures continuously at target
    hourly_bg_change: change in blood glucose level (mg/dL - hr)
    show_notes: whether notes about the algorithm should be displayed

    """
    required_params = ['current_bg']
    for key in required_params:
        if key not in input:
            raise AlgorithmError("required params: " + required_params)

    current_bg = input['current_bg']

    response = {}
    if 'show_notes' in input:
        response['notes'] = notes()

    if 'current_rate' not in input:
        dose = compute_initial_insulin(current_bg)
        return {
            'bolus': {
                'product': 325064004,
                'frequency': 'once',
                'dose': dose,
                'uom': 258666001,
                'route': 255560000
            },
            'infusion': {
                'product': 325064004,
                'rate': dose,
                'uom': 258949000,
                'route': 255560000
            },
            'current_bg': current_bg,
            'at_target_bg': is_blood_glucose_target(current_bg),
            'next_bg_check': compute_next_bg_check_time(current_bg, 0)
        }

    else:
        required_params = ['hourly_bg_change','consecutive_bg_in_target_count', 'current_rate']
        for key in required_params:
            if key not in input:
                raise AlgorithmError("required params: " + required_params)
                
        current_rate = input['current_rate']
        consecutive_bg_in_target_count = input['consecutive_bg_in_target_count']
        hourly_bg_change = input['hourly_bg_change']
        dose = compute_insulin(current_rate, current_bg, hourly_bg_change)

        return {
            'current_bg': current_bg,
            'at_target_bg': is_blood_glucose_target(current_bg),
            'next_bg_check': compute_next_bg_check_time(current_bg, consecutive_bg_in_target_count),
            'infusion': {
                'product': 325064004,
                'rate': dose,
                'uom': 258949000,
                'route': 255560000
            },
        }

    return response

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

def compute_initial_insulin(bg):
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

def compute_next_bg_check_time(current_bg, consecutive_in_target_count):
    if current_bg < 90:
        return 15

    elif is_blood_glucose_target(current_bg) and consecutive_in_target_count == 2:
        return 2 * 60

    else:
        return 60

def compute_special_instructions(current_bg):
    if current_bg < 50:
        return """
        D/C INSULIN INFUSION and administer 1 amp (25 g) D50 IV;
        recheck BG q 15 minutes until BG >= 90 mg/dL.
        Then, recheck BG Q1H when BG >= 140,
        wait 30 min, restart insulin infusion at 50% of most recent rate
        """

    if current_bg >= 50 and current_bg <=74:
        return """
        D/C INSULIN INFUSION and administer 1/2 amp (25 g) D50 IV;
        recheck BG q 15 minutes until BG >= 90 mg/dL.
        Then, recheck BG Q1H when BG >= 140,
        wait 30 min, restart insulin infusion at 50% of most recent rate
        """

    if current_bg >= 75 and current_bg <= 99:
        return """
        Recheck BG q 15 minutes until BG >= 90 mg/dL.
        Then, recheck BG Q1H when BG >= 140,
        wait 30 min, restart insulin infusion at 75% of most recent rate
        """

def compute_insulin(current_rate, current_bg, hourly_bg_change):

    if current_bg < 100:
        return compute_insulin_case_lt_100()

    if current_bg >= 100 and current_bg <= 119:
        return compute_insulin_case_bg_btwn_100_119(current_rate, hourly_bg_change)

    if current_bg >= 120 and current_bg <= 159:
        return compute_insulin_case_bg_btwn_120_159(current_rate, hourly_bg_change)

    if current_bg >= 160 and current_bg <= 199:
        return compute_insulin_case_bg_btwn_160_199(current_rate, hourly_bg_change)

    if current_bg > 200:
        return compute_insulin_case_bg_gt_200(current_rate, hourly_bg_change)

def _infusion_change_matrix(current_rate, delta_value):
    return [
        [(0, current_rate + 2 * delta_value)],
        [(0, current_rate + delta_value)],
        [(0, current_rate)],
        [(0, current_rate - delta_value)],
        [(0, 0), (30, current_rate - 2 * delta_value)]
    ]

def compute_insulin_case_lt_100():
    return [(0,0)]

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

class AlgorithmError(Exception):
    """Define error handling class."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value).replace("\\n", "\n")
