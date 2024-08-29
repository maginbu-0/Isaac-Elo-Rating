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
m_d = 'Data/Match_data.csv'
m_r = 'Data/Match_Res.csv'
lb_d = 'Data/Leaderboard.csv'


# Load Google Sheet

load_dotenv()
ss_id = os.getenv('key')

SERVICE_ACCOUNT_FILE = 'creds.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = None
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

service = build('sheets','v4',credentials=creds)

sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=ss_id,
                            range='Data!A1:F').execute()

values = result.get('values',[])

values = pd.DataFrame(values)
new_header = values.iloc[0] 
values = values[1:]
values.columns = new_header
values = values.set_index('Name') 


# Create Imported Results
df_matches = values
df_matches['New_Elo'] = df_matches['New_Elo'].astype(float).astype(int)
df_matches.to_csv(m_r)



# Backup data
currentDateTime = datetime.now().strftime("%Y%m%d%H%M")
print(currentDateTime)
df_matches.to_csv(f"Matches_Backup/Match_Res_backup_{currentDateTime}.csv")

# Filter out non-null data
df_matches = df_matches[df_matches['Elo'].isnull()]
df_matches.to_csv(m_d)


# Read out cleaned data
df = pd.read_csv(m_d)
df['Date'] = pd.to_datetime(df['Date'])

loaded_LB_df = pd.read_csv(lb_d)
match_res = pd.read_csv(m_r)

# Spread data on latest and match number
#
# I can put this into the for loop 
#


df1 = df[df.Date == df.Date.max()]

df_collec = {y: df1[df1['Match']==y] for y in df1['Match'].unique()}


# Conditional, if no new data
if len(df_collec) == 0:

    # No new data: print out results and leaderboard
    print(loaded_LB_df)
    print(match_res)



else:

    # New data, update results and leader board
    match_res = []

    for i in range(1,len(df_collec)+1):

        # Calculate new Elo rating for each player and each match.
        df_i = pd.DataFrame(df_collec[i].set_index('Name'))
        lb = loaded_LB_df.set_index('Name')['Elo']

    
        df_i['Elo'] = df_i['Elo'].fillna(lb)
        df_i = df_i.sort_values(by=['Result'])

        lb = pd.DataFrame(lb)
        c_elo = df_i.set_index('Result')['Elo']
        c_elo = np.array(c_elo)

        elo = MultiElo()

        n_elo = elo.get_new_ratings(c_elo)

        df_i['New_Elo'] = n_elo

        res_elo = df_i.drop(['Date','Result','Match'],axis=1)
    

        lb = pd.merge(lb, res_elo, on = ['Name', 'Elo'], how = 'outer')

        lb['Elo'] = lb['New_Elo'].fillna(lb['Elo'])
        lb['Wins'] = np.nan
        lb = lb.drop('New_Elo',axis=1)

        match_res.append(df_i)

        lb['Elo'] = lb['Elo'].astype(float).astype(int)

        lb.to_csv(lb_d)

    
    # Concatenate match data into the results 
    match_res = pd.concat(match_res)

    # Load original results and append new results
    load_match_res = pd.read_csv(m_r)
    lmr = load_match_res.set_index('Name')
    
    lmr['Date'] = pd.to_datetime(lmr['Date'])
    match_res_p = lmr.append(match_res)
    match_res_p.to_csv(m_r)    



# Load Leaderbooard and Matches, and setup data
Leaderboard = pd.read_csv(lb_d)
Matches = pd.read_csv(m_r)
Matches['New_Elo'] = Matches['New_Elo'].astype(int)

match = pd.DataFrame(Matches)
lead = pd.DataFrame(Leaderboard)

Leaderboard = Leaderboard.set_index('Name')

Leaderboard = Leaderboard.sort_values(by=['Elo'],ascending=False)



m = Matches.drop('Date', axis=1)

m = m[m['Result'] == 1]['Name'].value_counts()

# Count wins per player
Leaderboard['Wins'] = m
Leaderboard['Wins'] = Leaderboard['Wins'].fillna(0)

# Count matches played
Matches['count'] = Matches.groupby('Name').cumcount() + 1

# Plot graph
sns.lineplot(data=Matches,x='count',y='New_Elo',hue='Name')

sns.scatterplot(data=Matches,x='count',y='New_Elo',hue='Name',legend=False)

plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

plt.ylabel('Elo Rating')
plt.xlabel('Games Played')

plt.savefig('Leaderboard_graph.png')

# Save clean data
Leaderboard.to_csv(lb_d)
match.to_csv(m_r)

data = [match.columns.values.tolist()]
data.extend(match.values.tolist())
value_range_body = {"values": data}

dataL = [lead.columns.values.tolist()]
dataL.extend(lead.values.tolist())
bodyL = {"values": dataL}

request = sheet.values().update(spreadsheetId=ss_id, range='Data!A1', valueInputOption='USER_ENTERED',body=value_range_body).execute()
request = sheet.values().update(spreadsheetId=ss_id, range='Leaderboard!A1', valueInputOption='USER_ENTERED',body=bodyL).execute()


