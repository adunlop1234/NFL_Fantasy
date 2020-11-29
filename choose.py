#!/usr/bin/python

'''
This script is designed for command-line use to select a team
'''
import sys, os
import optimiser



def main():

    # Check correct command-line usuage
    if len(sys.argv) != 1:
        print("USUAGE: python choose.py")
        exit(1)

    # Define dictionary with the rules for the game
    rules = {
        'SALARY_CAP' : 60000,
        'QB_min' : 1,
        'RB_min' : 2,
        'WR_min' : 3,
        'TE_min' : 1,
        'DEF_min' : 1,
        'Flex' : 1
    }

    # Define players to include/exclude
    player_list_inc = {
        'Derek Carr' : 'QB',
        'Kyler Murray' : 'QB',
        'Chase Edmonds' : 'RB'
    }

    player_list_exc = {
        'Antonio Gibson' : 'RB',
        'Terry McLaurin' : 'WR',
        'Jamaal Williams' : 'RB'
    }

    # Read in the data array
    data_in = optimiser.read_data()

    # Adjust the rules of the game based on player to include/exclude
    data_in, rules, team = optimiser.include_players(data_in, rules, player_list_inc, player_list_exc)

    # Find the optimal team
    optimal_team = optimiser.optimiser(data_in, rules, team)

    # Print the optimal team to the command line
    optimiser.output_team(optimal_team, data_in)

    print("WARNING: Need to call develop.py to ensure Injury Status up-to-date")




if __name__ == "__main__":
    main()
