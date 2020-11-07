'''
Set of scripts that find the optimum team with limited salary.
'''

import cvxpy
import sys
import numpy as np
import pandas as pd
import os
from tabulate import tabulate

# Define salary cap
SALARY_CAP = 60000

# Define selection limits
QB_min = 1
RB_min = 2
WR_min = 3
TE_min = 1
DEF_min = 1
RB_max = RB_min + 1
WR_max = WR_min + 1
TE_max = TE_min + 1

def optimiser(data_in):
    
    # The variable we are solving for
    selection_QB = cvxpy.Variable(len(data_in['QB']['Salary']), boolean=True)
    selection_RB = cvxpy.Variable(len(data_in['RB']['Salary']), boolean=True)
    selection_WR = cvxpy.Variable(len(data_in['WR']['Salary']), boolean=True)
    selection_TE = cvxpy.Variable(len(data_in['TE']['Salary']), boolean=True)
    selection_DEF = cvxpy.Variable(len(data_in['DEF']['Salary']), boolean=True)
    
    # The sum of the salaries should be less than or equal to the salary cap
    constraints = [

    # Define the salary cap limit
    sum([sum(cvxpy.atoms.affine.binary_operators.multiply(data_in['QB']['Salary'], selection_QB)),
    sum(cvxpy.atoms.affine.binary_operators.multiply(data_in['RB']['Salary'], selection_RB)),
    sum(cvxpy.atoms.affine.binary_operators.multiply(data_in['WR']['Salary'], selection_WR)),
    sum(cvxpy.atoms.affine.binary_operators.multiply(data_in['TE']['Salary'], selection_TE)),
    sum(cvxpy.atoms.affine.binary_operators.multiply(data_in['DEF']['Salary'], selection_DEF))]) <= SALARY_CAP,
    
    # Define the number of QB and D
    sum(selection_QB) == QB_min,
    sum(selection_DEF) == DEF_min,

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
    total_points = sum([sum(cvxpy.atoms.affine.binary_operators.multiply(data_in['QB']['Predicted'], selection_QB)), 
                        sum(cvxpy.atoms.affine.binary_operators.multiply(data_in['RB']['Predicted'], selection_RB)), 
                        sum(cvxpy.atoms.affine.binary_operators.multiply(data_in['WR']['Predicted'], selection_WR)), 
                        sum(cvxpy.atoms.affine.binary_operators.multiply(data_in['TE']['Predicted'], selection_TE)), 
                        sum(cvxpy.atoms.affine.binary_operators.multiply(data_in['DEF']['Predicted'] , selection_DEF))])
    
    # Set up the problem
    fantasy_team = cvxpy.Problem(cvxpy.Maximize(total_points), constraints)
    
    # Solving the problem
    fantasy_team.solve(solver=cvxpy.GLPK_MI)

    # Assign the output selections
    QB = np.array(data_in['QB']['Name'])[np.where(selection_QB.value.astype(int)==1)]
    RB = np.array(data_in['RB']['Name'])[np.where(selection_RB.value.astype(int)==1)]
    WR = np.array(data_in['WR']['Name'])[np.where(selection_WR.value.astype(int)==1)]
    TE = np.array(data_in['TE']['Name'])[np.where(selection_TE.value.astype(int)==1)]
    DEF = np.array(data_in['DEF']['Name'])[np.where(selection_DEF.value.astype(int)==1)]

    # Define the total salary for the selections
    salary_out = (sum(np.multiply(np.array(data_in['QB']['Salary']),selection_QB.value))+
    sum(np.multiply(np.array(data_in['RB']['Salary']),selection_RB.value))+
    sum(np.multiply(np.array(data_in['WR']['Salary']),selection_WR.value))+
    sum(np.multiply(np.array(data_in['TE']['Salary']),selection_TE.value))+
    sum(np.multiply(np.array(data_in['DEF']['Salary']),selection_DEF.value)))

    # Assign output data structure
    data_out = {
        'QB' : QB,
        'RB' : RB,
        'WR' : WR,
        'TE' : TE,
        'DEF' : DEF,
        'Salary' : salary_out,
        'Predicted' : fantasy_team.value 
    }

    return data_out

# Function to return the projected points for a given team
def points(team, data_in):

    # Initialise total and define positions
    total = 0
    positions = ['QB', 'RB', 'WR', 'TE', 'DEF']

    # Loop over each position
    for position in positions:
        players = team[position]

        # Loop over every player detailed at the position adding points
        for player in players:

            # Check if the player is in the list
            try: 
                player_index = data_in[position]['Name'].index(player)
            except ValueError:
                print(player + ' is not in the list. Available players at ' + position + ' are:')
                print(data_in[position]['Name'])
                raise

            total += data_in[position]['Predicted'][player_index]

    return total

# Read in the desired data - either predicted or previous week (specify the integer week in the argument)
def read_data(week = 'Predicted'):

    # Positions
    positions = ['QB', 'RB', 'WR', 'TE', 'DEF']

    # Define the column names
    cols = ['Name', 'Salary', 'Predicted']

    # Replace the points with the week points to be used
    if type(week) == int:
        week = "Week " + str(week)
        cols[cols.index('Predicted')] = week

    # Create dict
    data_in = dict()
    for position in positions:
        data_in[position] = {}

    # Load each position data into input dictionary
    for position in positions:
        
        # Read the predicted points for position
        df = pd.read_csv(os.path.join('Output', position + '.csv'))

        # Limit the data to just salary, name and the points (either predicted or week).
        if position == 'DEF':
            df = df[['Team', 'Salary', 'Avg Points (3 weeks)']]
            print('WARNING: Defence predicted points is based on Avg from last 3 weeks.')
        else:
            df = df[cols]

        # Remove all players/teams that dont have salary data
        df = df.dropna()

        # Read through each column and enter into data array
        for col in cols:

            # To be removed when defence is correctly predicted
            if position == 'DEF':
                if col == 'Name':
                    data_in[position][col] = df['Team']
                elif col == week:
                    data_in[position][col] = df['Avg Points (3 weeks)']
                else:
                    data_in[position][col] = df[col]
            else:
                data_in[position][col] = df[col]

        # Change the points entry to be detailed 'Predicted' so the optimiser works the same
        data_in[position]['Predicted'] = data_in[position][week]
        if not week == 'Predicted':
            del data_in[position][week]

    return data_in

def output_team(team, data):

    # Strip the flex position
    if len(team['RB']) > 2:
        flex = team['RB'][-1]
        flex_position = 'RB'
        np.delete(team['RB'], -1)
    elif len(team['WR']) > 3:
        flex = team['WR'][-1]
        flex_position = 'WR'
        np.delete(team['WR'], -1)
    elif len(team['TE']) > 1:
        flex = team['TE'][-1]
        flex_position = 'TE'
        np.delete(team['TE'], -1)

    # Assemble rows in the list
    rows = [
        ['QB', team['QB'][0], data['QB']['Salary'][data['QB']['Name'] == team['QB'][0]].values[0], data['QB']['Predicted'][data['QB']['Name'] == team['QB'][0]].values[0]],
        ['RB1', team['RB'][0], data['RB']['Salary'][data['RB']['Name'] == team['RB'][0]].values[0], data['RB']['Predicted'][data['RB']['Name'] == team['RB'][0]].values[0]],
        ['RB2', team['RB'][1], data['RB']['Salary'][data['RB']['Name'] == team['RB'][1]].values[0], data['RB']['Predicted'][data['RB']['Name'] == team['RB'][1]].values[0]],
        ['WR1', team['WR'][0], data['WR']['Salary'][data['WR']['Name'] == team['WR'][0]].values[0], data['WR']['Predicted'][data['WR']['Name'] == team['WR'][0]].values[0]],
        ['WR2', team['WR'][1], data['WR']['Salary'][data['WR']['Name'] == team['WR'][1]].values[0], data['WR']['Predicted'][data['WR']['Name'] == team['WR'][1]].values[0]],
        ['WR3', team['WR'][2], data['WR']['Salary'][data['WR']['Name'] == team['WR'][2]].values[0], data['WR']['Predicted'][data['WR']['Name'] == team['WR'][2]].values[0]],
        ['TE', team['TE'][0], data['TE']['Salary'][data['TE']['Name'] == team['TE'][0]].values[0], data['TE']['Predicted'][data['TE']['Name'] == team['TE'][0]].values[0]],
        ['FLEX - ' + flex_position, flex, data[flex_position]['Salary'][data[flex_position]['Name'] == flex].values[0], data[flex_position]['Predicted'][data[flex_position]['Name'] == flex].values[0]],
        [' ', ' ', ' ', ' '],
        ['Total', ' ', team['Salary'], team['Predicted']]
    ]

    # Print in a table format
    print(tabulate(rows, headers = ['Position', 'Name', 'Salary', 'Points']))


def main():

    # Read in the data array
    data_in = read_data()

    # Find the optimal team
    optimal_team = optimiser(data_in)

    # Print the optimal team to the command line
    output_team(optimal_team, data_in)

if __name__ == "__main__":
    main()