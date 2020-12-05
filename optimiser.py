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

def include_players(data_in, rules, player_list_inc=None, player_list_exc=None):

    '''
    player_list_inc - dict with key e.g.

    player_list_exc = {
        'Antonio Gibson' : 'RB',
        'Terry McLaurin' : 'WR',
        'Jamaal Williams' : 'RB'
    }

    player_list_inc = {
        'Derek Carr' : 'QB',
        'Kyler Murray' : 'QB',
        'Chase Edmonds' : 'RB'
    }
    '''
 
    # Initialise team array
    team = {
        'QB' : [],
        'RB' : [],
        'WR' : [],
        'TE' : [],
        'DEF' : []
        }

    # Hardcode players into selection
    if player_list_inc:
        for player, position in player_list_inc.items():

            # Find location in list and check if the player is matched
            idx = data_in[position]['Name'].str.match(player)

            if idx.any():

                # Check there is space
                # Salary cap space
                if rules['SALARY_CAP'] - data_in[position]['Salary'].loc[idx].values[0] < 0:
                    print('WARNING: ' + player + ' cannot be added to team due to salary cap limit.')
                    continue

                elif position == 'QB' and rules['QB_min'] > 0:
                    team[position].append(player)
                    rules['SALARY_CAP'] -= data_in[position]['Salary'].loc[idx].values[0]
                    rules['QB_min'] -= 1
                    continue

                elif position == 'DEF' and rules['DEF_min'] > 0:
                    team[position].append(player)
                    rules['SALARY_CAP'] -= data_in[position]['Salary'].loc[idx].values[0]
                    rules['DEF_min'] -= 1
                    continue

                elif rules['Flex'] > 0 and ((position == 'RB' and rules['RB_min'] == 0) or (position == 'RB' and rules['RB_min'] == 0) or (position == 'RB' and rules['RB_min'] == 0)):
                    team[position].append(player)
                    rules['SALARY_CAP'] -= data_in[position]['Salary'].loc[idx].values[0]
                    rules['Flex'] -= 1
                    continue

                elif position == 'RB' and rules['RB_min'] > 0:
                    team[position].append(player)
                    rules['SALARY_CAP'] -= data_in[position]['Salary'].loc[idx].values[0]
                    rules['RB_min'] -= 1
                    continue

                elif position == 'WR' and rules['WR_min'] > 0:
                    team[position].append(player)
                    rules['SALARY_CAP'] -= data_in[position]['Salary'].loc[idx].values[0]
                    rules['WR_min'] -= 1
                    continue

                elif position == 'TE' and rules['TE_min'] > 0:
                    team[position].append(player)
                    rules['SALARY_CAP'] -= data_in[position]['Salary'].loc[idx].values[0]
                    rules['TE_min'] -= 1
                    continue

                else:
                    print('WARNING: ' + player + ' cannot be added as no room left at ' + position + '.')
                    continue

            else:
                print('WARNING: ' + player + ' cannot be matched and included in team.')

    # Remove player from data list
    if player_list_exc:
        for player, position in player_list_exc.items():
        
            # Find location in list and check if the player is matched
            idx = data_in[position]['Name'].str.match(player)

            # Remove the player from the input data
            if idx.any():
                data_in[position]['Name'] = data_in[position]['Name'].loc[~idx] 
                data_in[position]['Salary'] = data_in[position]['Salary'].loc[~idx] 
                data_in[position]['Predicted'] = data_in[position]['Predicted'].loc[~idx]

                # Print that the player has been removed
                print(player + ' has been removed from the possible selections.')

            else:
                print('WARNING: ' + player + ' cannot be matched and removed.')
        
    print('')

    return data_in, rules, team

def optimiser(data_in, rules, team={'QB' : [], 'RB' : [], 'WR' : [], 'TE' : [], 'DEF' : []}):
    
    # Create inferred rules
    rules['RB_max'] = rules['RB_min'] + rules['Flex']
    rules['WR_max'] = rules['WR_min'] + rules['Flex']
    rules['TE_max'] = rules['TE_min'] + rules['Flex']

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
    prob = pulp.LpProblem("Fantasy_Team", pulp.LpMaximize)

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
    
    prob += (salary_const <= rules['SALARY_CAP'])

    # Define number of QBs
    QB_const = ""
    for player_var in selections['QB'].values():

        QB_const += player_var

    prob += (QB_const == rules['QB_min'])

    # Define number of defences
    DEF_const = ""
    for player_var in selections['DEF'].values():

        DEF_const += player_var

    prob += (DEF_const == rules['DEF_min'])

    # Define number of rb, wr, te player quantitites
    RB_const = WR_const = TE_const = ""
    for rb_player_var, wr_player_var, te_player_var in zip(selections['RB'].values(), selections['WR'].values(), selections['TE'].values()):

        RB_const += rb_player_var
        WR_const += wr_player_var
        TE_const += te_player_var

    # Define number of rbs, wrs, tes and flexes
    prob += (RB_const >= rules['RB_min'])
    prob += (RB_const <= rules['RB_max'])
    prob += (WR_const >= rules['WR_min'])
    prob += (WR_const <= rules['WR_max'])
    prob += (TE_const >= rules['TE_min'])
    prob += (TE_const <= rules['TE_max'])
    prob += (RB_const + WR_const + TE_const == rules['TE_min'] + rules['WR_min'] + rules['RB_min'] + rules['Flex'])

    # Write the problem
    prob.writeLP('Processed/Fantasy_Team.lp')

    # Solve the problem
    optimisation_result = prob.solve(pulp.PULP_CBC_CMD(msg=0))
    assert optimisation_result == pulp.LpStatusOptimal
    
    print("The solution found is:", pulp.LpStatus[prob.status])

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

    # Add data for preselected players
    for position in team.keys():

        for name in team[position]:

            # Add the total for score, salary
            salary_out += np.array(data_in[position]['Salary'][data_in[position]['Name'] == name])[0]
            score_out += np.array(data_in[position]['Predicted'][data_in[position]['Name'] == name])[0]
    
    # Assign output data structure
    data_out = {
        'QB' : players['QB'] + team['QB'],
        'RB' : players['RB'] + team['RB'],
        'WR' : players['WR'] + team['WR'],
        'TE' : players['TE'] + team['TE'],
        'DEF' : players['DEF'] + team['DEF'],
        'Salary' : salary_out,
        'Predicted' : score_out
    }

    return data_out


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

        # Print players with missing salary info
        for index, row in df.iterrows():
            if pd.isnull(row.Salary):
                if position != 'DEF':
                    print(str(row.Name) + " has no salary data. They are predicted " + str(row["Predicted"]) + " points")
                else:
                    print(str(row.Team) + " has no salary data. They are predicted " + str(row["Predicted"]) + " points")

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
