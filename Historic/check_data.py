import pandas as pd
import matplotlib.pyplot as plt

# Latest week played
week = 11

# Check that games played is correct by approx constant pass attempts per game
# Store in list
PA_Game = []

# Read in data for each week
for i in range(7,week+1):
    df = pd.read_csv("Historic/D_tot_Week_" + str(i) + ".csv")

    df["PA/Game"] = df["Pass Att"] / df["Games Played"]

    PA_Game.append(pd.Series(df["PA/Game"].values,index=df.Team).to_dict())


# Create list of all teams
teams = PA_Game[0].keys()

# Add all teams to a plot
for team in teams:
    x = []
    y = []
    for i in range(7,week+1):
        x.append(i)
        y.append(PA_Game[i-7][team])

    plt.plot(x,y,label=team) 

plt.legend()
plt.show()