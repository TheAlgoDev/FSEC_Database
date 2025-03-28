# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 19:07:33 2025

@author: Brent Thompson
"""

import pandas as pd

spire_1 = r"C:\Users\Doing\University of Central Florida\UCF_Photovoltaics_GRP - module_databases\spire-results.txt"

spire = pd.read_csv(spire_1, sep="|", on_bad_lines='skip')

spire_test = spire[4]