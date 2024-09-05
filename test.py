import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
from datetime import datetime as dt
from dotenv import load_dotenv
import os
from multielo import MultiElo
from  matplotlib.ticker import FuncFormatter,  MaxNLocator
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
import gspread

# Setting file constants
m_d = 'data/match_data.csv' 
m_r = 'data/match_res_t.csv'
lb_d = 'data/leaderboard_t.csv'


leaderboard = pd.read_csv(lb_d)
Matches = pd.read_csv(m_r)
#Matches['New_Elo'] = Matches['New_Elo'].astype(int)

match = pd.DataFrame(Matches)
lead = pd.DataFrame(leaderboard)

leaderboard.to_csv(lb_d)
match.to_csv(m_r)

data = [match.columns.values.tolist()]
data.extend(match.values.tolist())
value_range_body = {"values": data}

dataL = [lead.columns.values.tolist()]
dataL.extend(lead.values.tolist())
bodyL = {"values": dataL}

print(dataL)