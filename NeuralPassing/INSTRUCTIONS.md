features.py -> creates csv of feature inputs


A model will be constructed to predict passing yards by a QB.

The following features will be used:
* QB stats for each past 6 weeks (P1, P2, P3 with P2 being 2 weeks previous etc.):
    - home or away (or BYE)
    - pass_cmp
    - pass_att
    - pass_yds
    - pass_td
    - pass_int
    - pass_sacked
    - rush_att
    - rush_yds
    - rush_td
* Other offence stats for past 6 weeks (O1, O2 etc.)
    - rush_att
    - rush_yds
    - rush_td
* Mean stats for each opposition defence for past 6 weeks (D1, D2, D3 etc.)
e.g. if week 9 upcoming, for each week 3-8 the oppositions defence's mean stats for past 6 weeks (this means it will contain data from after they played too)
    - home or away (or BYE)
    - pass_cmp
    - pass_att
    - pass_yds
    - pass_td
    - pass_int
    - pass_sacked
    - rush_att
    - rush_yds
    - rush_td
* Mean stats for the upcoming opposition's defence:
    - home or away (or BYE)
    - pass_cmp
    - pass_att
    - pass_yds
    - pass_td
    - pass_int
    - pass_sacked
    - rush_att
    - rush_yds
    - rush_td
