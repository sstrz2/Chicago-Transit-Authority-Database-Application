# Project 1 - CTA Database app
# This app uses Python and SQL to query a CTA ridership database and output various statistics, plots and images

import sqlite3
import matplotlib.pyplot as plt


##################################################################
#
# print_stats
#
# Given a connection to the CTA database, executes various
# SQL queries to retrieve and output basic stats.
#


# Prints general statistics about the connected datebase to the console
def print_stats(dbConn):
    dbCursor = dbConn.cursor()

    print("General Statistics:")

    dbCursor.execute("Select count(*) From Stations;")
    row = dbCursor.fetchone()
    print("  # of stations:", f"{row[0]:,}")

    dbCursor.execute("Select count(*) From Stops")
    row = dbCursor.fetchone()
    print("  # of stops:", f"{row[0]:,}")

    dbCursor.execute("Select count(*) From Ridership")
    row = dbCursor.fetchone()
    print("  # of ride entries:", f"{row[0]:,}")

    dbCursor.execute("Select MIN(date(Ride_Date)) From Ridership")
    row = dbCursor.fetchone()
    print("  date range:", row[0], end="")

    dbCursor.execute("Select MAX(date(Ride_Date)) From Ridership")
    row = dbCursor.fetchone()
    print(" -", row[0])

    dbCursor.execute("Select sum(Num_Riders) from Ridership")
    row = dbCursor.fetchone()
    print("  Total ridership:", f"{row[0]:,}")


# Prints all station names and their related IDs that match the users input
def choice1(dbConn):
    # Initial input and DB setup
    dbCursor = dbConn.cursor()
    sql = "Select Station_ID, Station_Name From Stations Where Station_Name Like ? order by Station_Name asc;"

    inp = input("\nEnter partial station name (wildcards _ and %): ")
    dbCursor.execute(sql, [inp])
    result = dbCursor.fetchall()
    # If station has matches, the names and IDs are printed
    if len(result) == 0:
        print("**No stations found...")
    else:
        for row in result:
            print(row[0], ":", row[1])


# Prints analytics about an inputted station, focusing around what number and percent of riders occured on Weekdays, Saturdays and Sundays
def choice2(dbConn):
    # Initial input and DB setup
    dbCursor = dbConn.cursor()
    sql = "Select Type_Of_Day, sum(Num_Riders) From Ridership Join Stations On Stations.Station_ID = Ridership.Station_ID Where Station_Name = ? group by Type_Of_Day order by Type_Of_Day asc;"

    inp = input("\nEnter the name of the station you would like to analyze: ")

    dbCursor.execute(sql, [inp])
    result = dbCursor.fetchall()
    # If station is found, analytics are calculated and printed
    if len(result) == 0:
        print("**No data found...")
    else:
        print("Percentage of ridership for the", inp, "station:")
        sat = result[0][1]
        sun = result[1][1]
        week = result[2][1]
        tot = sat + sun + week
        satP = (sat / tot) * 100
        sunP = (sun / tot) * 100
        weekP = (week / tot) * 100

        print(" Weekday ridership:", f"{week:,}", f"({weekP:.2f}%)")
        print(" Saturday ridership:", f"{sat:,}", f"({satP:.2f}%)")
        print(" Sunday/Holiday ridership:", f"{sun:,}", f"({sunP:.2f}%)")
        print(" Total ridership:", f"{tot:,}")


# Prints the weekday ridership total for each station in the database
def choice3(dbConn):
    # DB setup
    dbCursor = dbConn.cursor()
    sql = "Select Station_Name, sum(Num_Riders) from Ridership join Stations on Ridership.Station_ID = Stations.Station_ID where Type_Of_Day = 'W' group by Ridership.Station_ID order by sum(Num_Riders) desc;"

    dbCursor.execute(sql)
    result = dbCursor.fetchall()

    tot = 0
    # Find total riders on weekdays and use that to calculate percents
    for row in result:
        tot += row[1]
    print("Ridership on Weekdays for Each Station")

    for row in result:
        per = (row[1] / tot) * 100
        print(row[0], ":", f"{row[1]:,}", f"({per:.2f}%)")


# From an inputted line color and directions, prints the all station names, direction and if they are handicap accessible that are on that line and go in that direction
def choice4(dbConn):
    # Initial input and DB setup
    inp = input("\nEnter a line color (e.g. Red or Yellow): ")
    inp = inp.lower()

    dbCursor = dbConn.cursor()
    sql = "Select Line_ID from Lines where lower(Color) = ?;"

    dbCursor.execute(sql, [inp])
    result = dbCursor.fetchall()
    # If line color is found, query direction
    if len(result) == 0:
        print("**No such line...")
    else:
        inp1 = input("Enter a direction (N/S/W/E): ")
        inp1 = inp1.upper()

        sql = "Select Stop_Name, ADA from Lines join StopDetails on Lines.Line_ID = StopDetails.Line_ID join Stops on StopDetails.Stop_ID = Stops.Stop_ID where lower(Color) = ? and Direction = ? order by Stop_Name asc;"

        dbCursor.execute(sql, [inp, inp1])
        results = dbCursor.fetchall()

        # If given line runs in that direction, find and print all stops on given line and direction
        if len(results) == 0:
            print("**That line does not run in the direction chosen...")
        else:
            for row in results:
                if row[1] == 1:
                    ada = "(handicap accessible)"
                else:
                    ada = "(not handicap accessible)"
                print(row[0], ": direction =", inp1, ada)


# Prints the number of stops for each line color, seperated by direction as well as what percent each group of stops make up of the overall stops
def choice5(dbConn):
    # DB setup
    dbCursor = dbConn.cursor()
    sql = "Select Color, Direction, count(Stops.Stop_ID) from Lines join StopDetails on Lines.Line_ID = StopDetails.Line_ID join Stops on StopDetails.Stop_ID = Stops.Stop_ID group by Color,Direction order by Color asc;"

    dbCursor.execute(sql)
    result = dbCursor.fetchall()

    # Need to count from DB, as adding together stops from previous query didn't net correct result
    sql = "Select count(Stops.Stop_ID) from Stops;"

    dbCursor.execute(sql)
    total = dbCursor.fetchone()
    final = total[0]

    print("Number of Stops For Each Color By Direction")

    for row in result:
        percent = (row[2] / final) * 100
        print(row[0], "going", row[1], ":", row[2], f"({percent:.2f}%)")


# Takes the input of a station, and prints the yearly ridership for all years in the database. There is then an option to plot the data as well
def choice6(dbConn):
    # Initial input and DB setup
    inp = input("\nEnter a station name (wildcards _ and %): ")

    dbCursor = dbConn.cursor()
    sql = "Select Station_Name from Stations where Station_Name like ?;"
    dbCursor.execute(sql, [inp])
    name = dbCursor.fetchall()

    # Checking to see if station is found/singular, it it is yearly ridership is printed for that station and option to plot is made available
    if len(name) == 0:
        print("**No station found...")
    elif len(name) > 1:
        print("**Multiple stations found...")
    else:
        sql = """Select strftime('%Y',Ride_Date) as Year,sum(Num_Riders) from Stations join Ridership on Stations.Station_ID = Ridership.Station_ID where Station_Name like ? group by Year order by Year asc;"""
        dbCursor.execute(sql, [inp])
        result = dbCursor.fetchall()

        print("Yearly Ridership at", name[0][0])

        for row in result:
            print(row[0], ":", f"{row[1]:,}")

        # Plotting portion starts here
        choice = input("Plot? (y/n) ")

        if choice == "y":
            x = []
            y = []
            title = "Yearly riders at " + name[0][0]
            plt.title(title)
            plt.xlabel("Years")
            plt.ylabel("Millions of Riders")
            plt.yticks(
                [0.2e6, 0.4e6, 0.6e6, 0.8e6, 1.0e6, 1.2e6, 1.4e6, 1.6e6, 1.8e6],
                [
                    "0.2M",
                    "0.4M",
                    "0.6M",
                    "0.8M",
                    "1.0M",
                    "1.2M",
                    "1.4M",
                    "1.6M",
                    "1.8M",
                ],
            )

            for row in result:
                x.append(row[0])
                y.append(row[1])

            plt.ioff()
            plt.plot(x, y)
            plt.xticks(x, fontsize=6)
            plt.show()


# Takes the input of a station and a year, and prints the monthly ridership for that station and that year, with an option to plot the data as well
def choice7(dbConn):
    # Initial inputs and DB setup
    inp = input("\nEnter a station name (wildcards _ and %): ")

    dbCursor = dbConn.cursor()
    sql = "Select Station_Name from Stations where Station_Name like ?;"
    dbCursor.execute(sql, [inp])
    name = dbCursor.fetchall()

    # Checking if station is found/singular, if it is year is asked
    if len(name) == 0:
        print("**No station found...")
    elif len(name) > 1:
        print("**Multiple stations found...")
    else:
        # After year is asked, monthly ridership for that year/station is printed, and option to plot is asked
        year = input("Enter a year: ")
        sql = "Select strftime('%m',Ride_Date) as Month, sum(Num_Riders) from Ridership join Stations on Stations.Station_ID = Ridership.Station_ID where Station_Name = ? and strftime('%Y',Ride_Date) = ? group by Month order by Month asc;"
        dbCursor.execute(sql, [name[0][0], year])
        results = dbCursor.fetchall()

        print("Monthly Ridership at", name[0][0], "for", year)

        for row in results:
            date = row[0] + "/" + year
            print(date, ":", f"{row[1]:,}")

        # Plotting portion starts here
        plot = input("Plot? (y/n) ")

        if plot == "y":
            x = []
            y = []
            title = "Monthly Ridership at " + name[0][0] + " Station (" + year + ")"
            plt.title(title)
            plt.xlabel("Months")
            plt.ylabel("Number of Riders")

            for row in results:
                x.append(row[0])
                y.append(row[1])

            plt.ioff()
            plt.plot(x, y)
            plt.show()


# Takes input of two station names and a year, prints the first and last 5 daily ridership days for each station in that given year, then has an optional plot that shows the fully range of ridership for each station in that year
def choice8(dbConn):
    # Taking initial inputs and setting up DB
    year = input("\nYear to compare against? ")
    station1 = input("\nEnter station 1 (wildcards _ and %): ")

    dbCursor = dbConn.cursor()
    sql = "Select Station_ID,Station_Name from Stations where Station_Name like ?;"
    dbCursor.execute(sql, [station1])
    name1 = dbCursor.fetchall()

    # Checking if that station is found/singular, if it is input is taken for the second station
    if len(name1) == 0:
        print("**No station found...")
    elif len(name1) > 1:
        print("**Multiple stations found...")
    else:
        station2 = input("\nEnter station 2 (wildcards _ and %): ")
        dbCursor.execute(sql, [station2])
        name2 = dbCursor.fetchall()

        # Checking if that station is found/singular, if it is the information for both stations is printed and plot option is asked
        if len(name2) == 0:
            print("**No station found...")
        elif len(name2) > 1:
            print("**Multiple stations found...")
        else:
            sql = "Select date(Ride_Date),Num_Riders from Ridership join Stations on Ridership.Station_ID = Stations.Station_ID where Station_Name = ? and strftime('%Y',Ride_Date) = ? order by Ride_Date;"
            dbCursor.execute(sql, [name1[0][1], year])
            results1 = dbCursor.fetchall()

            print("Station 1:", name1[0][0], name1[0][1])

            count = 1
            tot = len(results1)

            for row in results1:
                if count > tot - 5 or count <= 5:
                    print(row[0], row[1])
                count = count + 1

            dbCursor.execute(sql, [name2[0][1], year])
            results2 = dbCursor.fetchall()

            print("Station 2:", name2[0][0], name2[0][1])

            count = 1
            tot = len(results2)

            for row in results2:
                if count > tot - 5 or count <= 5:
                    print(row[0], row[1])
                count = count + 1

            # Plotting portion starts here
            plot = input("Plot? (y/n) ")

            if plot == "y":
                x = []
                y = []
                y2 = []
                title = "Ridership Each Day of " + year
                plt.title(title)
                plt.xlabel("Day")
                plt.ylabel("Number of Riders")
                day = 0

                for row in results1:
                    x.append(day)
                    y.append(row[1])
                    day = day + 1

                for row in results2:
                    y2.append(row[1])

                plt.ioff()
                plt.plot(x, y, label=name1[0][1])
                plt.plot(x, y2, label=name2[0][1])
                plt.legend()
                plt.legend(loc="upper right")
                plt.show()


# Takes a latitude and longitude, prints all station names and their related coordinates that are within 1 square mile of the given coordinates. Then there is an optional plot, that will label a picture of chicago obtained from OpenStreetMaps with said station names, plotted where the stations are in the picture
def choice9(dbConn):
    # Taking initial inputs and setting up DB
    dbCursor = dbConn.cursor()
    lat = input("\nEnter a latitude: ")
    lat = float(lat)

    if lat > 43 or lat < 40:
        print("**Latitude entered is out of bounds...")
    else:
        lon = input("Enter a longitude: ")
        lon = float(lon)

        if lon > -87 or lon < -88:
            print("**Longitude entered is out of bounds...")
        else:
            # Finding the latitude and longitude bounds for stations within 1 square mile
            latBound = 1 / 69
            lonBound = 1 / 51

            upLat = lat + latBound
            lowLat = lat - latBound
            upLon = lon + lonBound
            lowLon = lon - lonBound

            upLat = round(upLat, 3)
            lowLat = round(lowLat, 3)
            upLon = round(upLon, 3)
            lowLon = round(lowLon, 3)

            sql = "Select Distinct Station_Name, Latitude, Longitude from Stations join Stops on Stations.Station_ID = Stops.Station_ID where Latitude >= ? and Latitude <= ? and Longitude >= ? and Longitude <= ? order by Station_Name asc;"
            dbCursor.execute(sql, [lowLat, upLat, lowLon, upLon])
            result = dbCursor.fetchall()

            # Check if there are any stations found, if there are print them out and ask to plot
            if len(result) == 0:
                print("**No stations found...")
            else:
                print("\nList of Stations Within a Mile")
                for row in result:
                    cords = "(" + str(row[1]) + ", " + str(row[2]) + ")"
                    print(row[0], ":", cords)

                # Plotting portions starts here
                plot = input("\nPlot? (y/n) ")

                if plot == "y":
                    x = []
                    y = []
                    image = plt.imread("chicago.png")
                    xydims = [-87.9277, -87.5569, 41.7012, 42.0868]
                    plt.imshow(image, extent=xydims)
                    plt.title("Stations Near You")
                    plt.plot(x, y)

                    for row in result:
                        plt.annotate(row[0], (row[2], row[1]))

                    plt.xlim([-87.9277, -87.5569])
                    plt.ylim([41.7012, 42.0868])
                    plt.show()


##################################################################
#
# main
#
print("** Welcome to CTA L analysis app **")
print()

dbConn = sqlite3.connect("CTA2_L_daily_ridership.db")

print_stats(dbConn)

choice = input("\nPlease enter a command (1-9, x to exit): ")
while choice != "x":
    if choice == "1":
        choice1(dbConn)
    elif choice == "2":
        choice2(dbConn)
    elif choice == "3":
        choice3(dbConn)
    elif choice == "4":
        choice4(dbConn)
    elif choice == "5":
        choice5(dbConn)
    elif choice == "6":
        choice6(dbConn)
    elif choice == "7":
        choice7(dbConn)
    elif choice == "8":
        choice8(dbConn)
    elif choice == "9":
        choice9(dbConn)
    else:
        print("**Error, unknown command, try again...")

    choice = input("\nPlease enter a command (1-9, x to exit): ")


#
# done
#
