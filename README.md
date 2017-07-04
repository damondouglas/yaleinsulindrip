Yale Insulin Infusion Protocol
==============================

# About

The Yale Insulin Infusion (YII) is a protocol that aims to control blood glucose levels in hyperglycemic patients in critical care.  This implementation serves to enable YII as a REST api deployed on [Algorithmia](https://algorithmia.com/).

Note [snomed](http://browser.ihtsdotools.org/) codes used below:

| Code       | Description |
| ---------- | ----------- |
| 325064004  | Insulin soluble human 100units/mL injection solution 10mL vial (product) |
| 258666001  | Unit |
| 258949000  | Unit/hour |
| 255560000  | Intravenous |
| 166888009  | Blood glucose method |

# Usage

## Compute Initial Bolus and Infusion
### Example Input

```json
{
  "current_bg": 300
}
```
### Example Output

```json
{
  "at_target_bg": false,
  "bolus": {
    "dose": 3,
    "frequency": "once",
    "product": 325064004,
    "route": 255560000,
    "uom": 258666001
  },
  "current_bg": 300,
  "infusion": {
    "product": 325064004,
    "rate": 3,
    "route": 255560000,
    "uom": 258949000
  },
  "next_bg_check": 60
}

```

## Compute Infusion

### Example Input

```json
{
  "hourly_bg_change": 0,
  "consecutive_bg_in_target_count": 0,
  "current_rate": 3,
  "current_bg": 300
}
```

### Example Output

```json
{
  "at_target_bg": false,
  "current_bg": 300,
  "infusion": {
    "product": 325064004,
    "rate": [[0, 4]],
    "route": 255560000,
    "uom": 258949000
  },
  "next_bg_check": 60
}
```

# Reference

Reference:
Shetty S, Inzucchi SE, Goldberg PA, Cooper D, Siegel MD, Honiden S.
Adapting to the new consensus guidelines for managing hyperglycemia
during critical illness: The Updated Yale Insulin Infusion Protocol.
Endocr Pract. 2012;18:363-370.
<http://inpatient.aace.com/sites/all/files/Yale_IIP_MICU120-160_2011.pdf;
Accessed 06/28/2017>

_PDF can also be found here: https://github.com/damondouglas/yaleinsulindrip/files/1112949/Yale_IIP_MICU120-160_2011.pdf_

# Errors/Issues

[Report here](https://github.com/damondouglas/yaleinsulindrip/issues)
