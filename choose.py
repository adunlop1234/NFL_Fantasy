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

    # Read in the data array
    data_in = optimiser.read_data()

    # Find the optimal team
    optimal_team = optimiser.optimiser(data_in)

    # Print the optimal team to the command line
    optimiser.output_team(optimal_team, data_in)

    print("WARNING: Need to call develop.py to ensure Injury Status up-to-date")




if __name__ == "__main__":
    main()
