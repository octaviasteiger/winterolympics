"""pip install statsmodels
and add it to the requirements files

analysis.py 
Aggregates the completed medal data and runs an OLS regression to test whether host countries experience a 
measurable performance advantage at the Winter Olympics. 
"""

import pandas as pd
import numpy as np
import sqlite3
import statsmodels.formula.api as smf
import os

