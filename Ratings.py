import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
from datetime import datetime as dt
from dotenv import load_dotenv
import os
from multielo import MultiElo
from  matplotlib.ticker import FuncFormatter,  MaxNLocator


# Load Google Sheet
load_dotenv()
sheet_key = os.getenv('key')
df_url = pd.read_csv(f'https://docs.google.com/spreadsheets/d/{sheet_key}/export?format=csv')


# Create Imported Results
df_matches = pd.DataFrame(df_url).set_index('Name')
df_matches['New_Elo'] = df_matches['New_Elo'].astype(int)
df_matches.to_csv('Match_Res.csv')

# Filter out non-null data
df_matches = df_matches[df_matches['Elo'].isnull()]
df_matches.to_csv('Match_data.csv')


# Read out cleaned data
df = pd.read_csv('Match_data.csv')
df['Date'] = pd.to_datetime(df['Date'])

loaded_LB_df = pd.read_csv('Leaderboard.csv')
match_res = pd.read_csv('Match_Res.csv')

# Spread data on latest and match number
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

        lb['Elo'] = lb['Elo'].astype(int)

        lb.to_csv('Leaderboard.csv')

    
    # Concatenate match data into the results 
    match_res = pd.concat(match_res)

    # Load original results and append new results
    load_match_res = pd.read_csv('Match_Res.csv')
    lmr = load_match_res.set_index('Name')
    print(lmr)
    lmr['Date'] = pd.to_datetime(lmr['Date'])
    match_res_p = lmr.append(match_res)
    match_res_p.to_csv('Match_Res.csv')    
    print(match_res_p)


# PO
Leaderboard = pd.read_csv('Leaderboard.csv')
Matches = pd.read_csv('Match_Res.csv')


Leaderboard = Leaderboard.set_index('Name')

Leaderboard = Leaderboard.sort_values(by=['Elo'],ascending=False)

Matches['New_Elo'] = Matches['New_Elo'].astype(int)


m = Matches.drop('Date', axis=1)

m = m[m['Result'] == 1]['Name'].value_counts()

Leaderboard['Wins'] = m
Leaderboard['Wins'] = Leaderboard['Wins'].fillna(0)

Matches['count'] = Matches.groupby('Name').cumcount() + 1

sns.lineplot(data=Matches,x='count',y='New_Elo',hue='Name')

sns.scatterplot(data=Matches,x='count',y='New_Elo',hue='Name',legend=False)

plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

plt.ylabel('Elo Rating')
plt.xlabel('Games Played')

plt.savefig('Leaderboard_graph.png')

Leaderboard.to_csv('Leaderboard.csv')

print(Leaderboard)


print(len(df_matches))