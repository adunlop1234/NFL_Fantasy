'''
Set of scripts that find the optimum team with limited salary.
'''

import pulp
import sys
import numpy as np
import pandas as pd
import os
import re
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
    QB_list = [str(name) for name in data_in['QB']['Name']]
    RB_list = [str(name) for name in data_in['RB']['Name']]
    WR_list = [str(name) for name in data_in['WR']['Name']]
    TE_list = [str(name) for name in data_in['TE']['Name']]
    DEF_list = [str(name) for name in data_in['DEF']['Name']]

    selections = {}
    selections['QB'] = pulp.LpVariable.dicts('QB', QB_list, cat = 'Binary')
    selections['RB']  = pulp.LpVariable.dicts('RB', RB_list, cat = 'Binary')
    selections['WR']  = pulp.LpVariable.dicts('WR', WR_list, cat = 'Binary')
    selections['TE']  = pulp.LpVariable.dicts('TE', TE_list, cat = 'Binary')
    selections['DEF']  = pulp.LpVariable.dicts('DEF', DEF_list, cat = 'Binary')
    
    # Initialise problem
    prob = pulp.LpProblem("Fantasy Team", pulp.LpMaximize)

    # Define cost function
    total_points = ""
    for position in ['QB', 'RB', 'WR', 'TE', 'DEF']:

        players = selections[position]

        for i, player_var in enumerate(players.values()):
            
            total_points += np.array(data_in[position]['Predicted'])[i] * player_var  
    
    prob += total_points

    # Define salary constraint
    salary_const = ""
    for position in ['QB', 'RB', 'WR', 'TE', 'DEF']:

        players = selections[position]

        for i, player_var in enumerate(players.values()):

            salary_const += np.array(data_in[position]['Salary'])[i] * player_var  
    
    prob += (salary_const <= SALARY_CAP)

    # Define number of QBs
    QB_const = ""
    for player_var in selections['QB'].values():

        QB_const += player_var

    prob += (QB_const == QB_min)

    # Define number of defences
    DEF_const = ""
    for player_var in selections['DEF'].values():

        DEF_const += player_var

    prob += (DEF_const == DEF_min)

    # Define number of rb, wr, te player quantitites
    RB_const = WR_const = TE_const = ""
    for rb_player_var, wr_player_var, te_player_var in zip(selections['RB'].values(), selections['WR'].values(), selections['TE'].values()):

        RB_const += rb_player_var
        WR_const += wr_player_var
        TE_const += te_player_var

    # Define number of rbs, wrs, tes and flexes
    prob += (RB_const >= RB_min)
    prob += (RB_const <= RB_max)
    prob += (WR_const >= WR_min)
    prob += (WR_const <= WR_max)
    prob += (TE_const >= TE_min)
    prob += (TE_const <= TE_max)
    prob += (RB_const + WR_const + TE_const == TE_min + WR_min + RB_min + 1)

    # Write the problem
    prob.writeLP('Fantasy_Team.lp')

    # Solve the problem
    optimisation_result = prob.solve()
    assert optimisation_result == pulp.LpStatusOptimal
    print("Status:", pulp.LpStatus[prob.status])

    # Strip the output
    variable_names = []
    for v in prob.variables():
        if v.varValue:
            variable_names.append(v.name)

    # Check the total salary it came to
    salary_out = 0
    score_out = 0
    players = {'QB' : [],
    'RB' : [],
    'WR' : [],
    'TE' : [],
    'DEF' : []}
    for name in variable_names:

        # Get position
        position = name.split('_')[0]

        # Get the name
        name = re.sub(r'DEF_|QB_|RB_|WR_|TE_', '', name).replace('_', ' ')
        
        # Add the total for score, salary
        salary_out += np.array(data_in[position]['Salary'][data_in[position]['Name'] == name])[0]
        score_out += np.array(data_in[position]['Predicted'][data_in[position]['Name'] == name])[0]

        players[position].append(name)
    
    # Assign output data structure
    data_out = {
        'QB' : players['QB'],
        'RB' : players['RB'],
        'WR' : players['WR'],
        'TE' : players['TE'],
        'DEF' : players['DEF'],
        'Salary' : salary_out,
        'Predicted' : score_out
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

        # Remove any rows that have injury status of IR or O
        if not position == 'DEF':
            df = df[df['Injury'] != 'O']
            df = df[df['Injury'] != 'IR']

        # Limit the data to just salary, name and the points (either predicted or week).
        if position == 'DEF':
            df = df[['Team', 'Salary', 'Predicted']]
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
        ['DEFENCE', team['DEF'][0], data['DEF']['Salary'][data['DEF']['Name'] == team['DEF'][0]].values[0], data['DEF']['Predicted'][data['DEF']['Name'] == team['DEF'][0]].values[0]],
        [' ', ' ', ' ', ' '],
        ['Total', ' ', team['Salary'], round(team['Predicted'], 2)]
    ]

    # Print in a table format
    print('')
    print(tabulate(rows, headers = ['Position', 'Name', 'Salary', 'Points'], tablefmt='github'))
    print('')


def main():

    # Read in the data array
    data_in = read_data()

    # Find the optimal team
    optimal_team = optimiser(data_in)

    # Print the optimal team to the command line
    output_team(optimal_team, data_in)

if __name__ == "__main__":
    main()