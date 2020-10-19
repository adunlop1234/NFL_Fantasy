'''
Set of scripts that find the optimum team with limited salary.
'''

import cvxpy
import sys
import numpy as np
import pandas as pd

# Define salary cap
SALARY_CAP = 50000

# Define selection limits
QB_min = 1
RB_min = 2
WR_min = 3
TE_min = 1
D_min = 1
RB_max = RB_min + 1
WR_max = WR_min + 1
TE_max = TE_min + 1

def optimiser(data_in):
    
    # The variable we are solving for
    selection_QB = cvxpy.Variable(len(data_in['QB']['Salary']), boolean=True)
    selection_RB = cvxpy.Variable(len(data_in['RB']['Salary']), boolean=True)
    selection_WR = cvxpy.Variable(len(data_in['WR']['Salary']), boolean=True)
    selection_TE = cvxpy.Variable(len(data_in['TE']['Salary']), boolean=True)
    selection_D = cvxpy.Variable(len(data_in['D']['Salary']), boolean=True)
    
    # The sum of the salaries should be less than or equal to the salary cap
    constraints = [

    # Define the salary cap limit
    sum([sum(cvxpy.atoms.affine.binary_operators.multiply(data_in['QB']['Salary'], selection_QB)),
    sum(cvxpy.atoms.affine.binary_operators.multiply(data_in['RB']['Salary'], selection_RB)),
    sum(cvxpy.atoms.affine.binary_operators.multiply(data_in['WR']['Salary'], selection_WR)),
    sum(cvxpy.atoms.affine.binary_operators.multiply(data_in['TE']['Salary'], selection_TE)),
    sum(cvxpy.atoms.affine.binary_operators.multiply(data_in['D']['Salary'], selection_D))]) <= SALARY_CAP,
    
    # Define the number of QB and D
    sum(selection_QB) == QB_min,
    sum(selection_D) == D_min,

    # Define the upper and lower bounds of number of FLEX eligibles.
    sum(selection_RB) >= RB_min,
    sum(selection_WR) >= WR_min,
    sum(selection_TE) >= TE_min,
    sum(selection_RB) <= RB_max,
    sum(selection_WR) <= WR_max,
    sum(selection_TE) <= TE_max,

    # Define that there is only one FLEX
    sum(selection_RB) + sum(selection_WR) + sum(selection_TE) == TE_min + RB_min + WR_min + 1
    
    ]

    # Parameter we want to maximise
    total_points = sum([sum(cvxpy.atoms.affine.binary_operators.multiply(data_in['QB']['FPPG'], selection_QB)), 
                        sum(cvxpy.atoms.affine.binary_operators.multiply(data_in['RB']['FPPG'], selection_RB)), 
                        sum(cvxpy.atoms.affine.binary_operators.multiply(data_in['WR']['FPPG'], selection_WR)), 
                        sum(cvxpy.atoms.affine.binary_operators.multiply(data_in['TE']['FPPG'], selection_TE)), 
                        sum(cvxpy.atoms.affine.binary_operators.multiply(data_in['D']['FPPG'] , selection_D))])
    
    # Set up the problem
    fantasy_team = cvxpy.Problem(cvxpy.Maximize(total_points), constraints)
    
    # Solving the problem
    fantasy_team.solve(solver=cvxpy.GLPK_MI)

    # Assign the output selections
    QB = np.array(data_in['QB']['Nickname'])[np.where(selection_QB.value.astype(int)==1)]
    RB = np.array(data_in['RB']['Nickname'])[np.where(selection_RB.value.astype(int)==1)]
    WR = np.array(data_in['WR']['Nickname'])[np.where(selection_WR.value.astype(int)==1)]
    TE = np.array(data_in['TE']['Nickname'])[np.where(selection_TE.value.astype(int)==1)]
    D = np.array(data_in['D']['Nickname'])[np.where(selection_D.value.astype(int)==1)]

    # Define the total salary for the selections
    salary_out = (sum(np.multiply(np.array(data_in['QB']['Salary']),selection_QB.value))+
    sum(np.multiply(np.array(data_in['RB']['Salary']),selection_RB.value))+
    sum(np.multiply(np.array(data_in['WR']['Salary']),selection_WR.value))+
    sum(np.multiply(np.array(data_in['TE']['Salary']),selection_TE.value))+
    sum(np.multiply(np.array(data_in['D']['Salary']),selection_D.value)))

    # Assign output data structure
    data_out = {
        'QB' : QB,
        'RB' : RB,
        'WR' : WR,
        'TE' : TE,
        'D' : D,
        'Salary' : salary_out,
        'Points' : fantasy_team.value 
    }

    return data_out

# Function to return the projected points for a given team
def points(team, data_in):

    # Initialise total and define positions
    total = 0
    positions = ['QB', 'RB', 'WR', 'TE', 'D']

    # Loop over each position
    for position in positions:
        players = team[position]

        # Loop over every player detailed at the position adding points
        for player in players:

            # Check if the player is in the list
            try: 
                player_index = data_in[position]['Nickname'].index(player)
            except ValueError:
                print(player + ' is not in the list. Available players at ' + position + ' are:')
                print(data_in[position]['Nickname'])
                raise

            total += data_in[position]['FPPG'][player_index]

    return total

def main():

    # Read the data
    df = pd.read_csv('Fan_Duel_Data.csv').sort_values(by='FPPG', ascending=False)

    # Positions
    positions = ['QB', 'RB', 'WR', 'TE', 'D']

    # Create dict
    data_in = dict()
    for position in positions:
        data_in[position] = {}
    
    # Define the column names
    cols = ['Nickname', 'Salary', 'FPPG']

    # Strip data
    for position in positions:
        data_in[position][cols[0]] = df[cols[0]][df['Position'].str.match(position)].head(30).values.tolist()
        for col in cols[1:]:
            data_in[position][col] = df[col][df['Position'].str.match(position)].head(30).values

    # Find the optimal team
    optimal_team = optimiser(data_in)

    # Find the points from the team used
    team_used = {
    'QB' : ["Nick Foles"],
    'RB' : ["Derrick Henry", "Jonathan Taylor", "David Montgomery"],
    'WR' : ["Adam Thielen", "Chase Claypool", "Calvin Ridley"],
    'TE' : ["Trey Burton"],
    'D' : ["Chicago Bears"]
    }

    points_for_team = points(team_used, data_in)

if __name__ == "__main__":
    main()