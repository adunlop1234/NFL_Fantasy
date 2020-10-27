'''
This script uses our algorithm to process the data

The formulae can be found here:
https://docs.google.com/document/d/1gwx1Za9LCGU4VGipsq30La1J1sJUEpA_yAlV2kTgtu8/edit?usp=sharing
'''

#! Classes https://www.tutorialspoint.com/python/python_classes_objects.htm

class Factors:
    'Contains factors used for alogirthm'

    def __init__(self):

        # Passing
        self.alpha_1 = 0
        self.alpha_2 = 0
        self.alpha_3 = 0

        # Rushing
        self.beta_1 = 0
        self.beta_2 = 0
        self.beta_3 = 0

        # QB
        self.gamma = 0


class Normalisers:
    'Contains normalisers used for alogirthm'

    def __init__(self):

        # Passing
        self.pass_yds = 235
        self.pass_yds_att = 7.2
        self.pass_TD = 1.6

        # Rushing
        self.rush_yds = 113
        self.rush_yds_att = 4.3
        self.rush_TD = 0.9

        # QB
        self.INT = 0.9

      