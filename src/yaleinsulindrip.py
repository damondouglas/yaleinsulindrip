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

    return round_nearest(bg/100, 0.5)

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