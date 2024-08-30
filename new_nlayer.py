import numpy as np
import pandas as pd

LB = pd.read_csv('data/leaderboard.csv',usecols=lambda c: not c.startswith('Unnamed:'))

name = input('Input the name: ')

mean_Elo = np.mean(LB['Elo']).astype(int)

wins = 0

new_player = [[name, mean_Elo,wins]]
cols = ['Name','Elo','Wins']
new_player = pd.DataFrame(new_player,columns=cols)

LB = pd.concat([LB,new_player])

LB = LB.sort_values(by=['Elo'],ascending=False)

LB = LB.reset_index(drop=True)

LB.to_csv('data/leaderboard.csv', index=False)

print(LB)