#list of commands:

#cbird species SPECIES
#default: prints common name, location, date
#   -l: print full location (state/province, county, lat/long)
#   -d: print full date info (date, time, duration)
#   -n: print notes about observation (breeding code, notes)
#   -s: print submission ID

#cbird lifelist
#default: finds first occurence of a species and prints common name, location, date. sorted by date, oldest first
#should also print non-species (sp and slash) separately
#   -l: print full location (state/province, county, lat/long)
#   -d: print full date info (date, time, duration)
#   -n: print notes about observation (breeding code, notes)
#   -s: print submission ID
#   -L: sort by last seen
#   -o: reverse order (newest first)

#cbird checklist
#default: prints all checklists (location, list of species, num of each species, date, protocol), oldest first
#   -f: filter for a specific value
#   -l: print full location
#   -d: print full date info
#   -s: print submission ID
#   -n: print checklist notes, species notes, and breeding codes
#   -o: reverse order (newest first)
#make some sort of way to edit a checklist

#cbird import FILEPATH
#takes in a csv file from ebird and generates a new csv file
# - ebird csv files have submission IDs, and this file creates new ids (local specific) and marks entries as in ebird

#cbird export
#creates csv file of all data that is not already in ebird

#cbird create
#adds a checklist from user prompting to local csv, marks what is added as not in ebird

#TO DO:
#   some sort of way to store photos associated with a checklist
#   add regional stats, so you can see how many bird you've seen in a certain area
#   user config file
#   compare import w/ local to remove duplicates
#   way to delete checklist

import click
import Levenshtein
import datetime

@click.group()
def cli():
    """
     \b
        __    _    -o'   __
  ____./ /_  (_)___( )__/ /
 / ___) _  \\/ / ___)"__  / 
/ (__/ /_) / / /  / (_/ /  
\\___/_.___/_/_/   \\__._/   

    """
    pass

def indexOf(array, element):
    index = 0
    for a in array:
        if a == element:
            return index
        index += 1
    return -1

def byDate(data):
    if str(type(data[0])) == "<class 'str'>":
        return data[10].replace("-", "")
    else:
        return data[0][10].replace("-", "")
    
def byTaxon(data):
    return int(data[3])

def byID(data):
    return data[0]

def split(string): #splits a csv string into an array, but ignores commas that are in double quotes
    list = string.split(",")
    quoteStartIndex = -1
    quoteEndIndex = -1
    index = 0
    newList = []
    for element in list:
        if element.startswith('"') and element.endswith('"'):
            newList.append(element)
        elif element.startswith('"'):
            quoteStartIndex = index
        elif element.endswith('"'):
            quoteEndIndex = index
            s = ""
            i = quoteStartIndex
            while i < quoteEndIndex:
                s += list[i] + ","
                i += 1
            s += list[i]
            newList.append(s)
            quoteStartIndex = -1
        elif not(index > quoteStartIndex and not(quoteStartIndex == -1)):
            newList.append(element)
        index += 1
    return newList


def generateLID(date, time):
    #recieves data and returns a Local ID generated from data. LIDs are used to distinguish checklists locally.
    date = date.replace("-", "")
    time = time.replace(":", "")
    if time[-3:] == " PM":
        time = time[:-3]
        time = int(time) + 1200
    elif time[-3:] == " AM":
        time = time[:-3]
    if len(str(time)) == 3:
        time = "0" + str(time)
    return date + str(time)

def getScientific(common):
    #gets scientific name from common name by fetching from ebird taxonomy
    f = open("eBird_taxonomy.csv")
    for line in f:
        if split(line)[4] == common:
            return split(line)[5]
    return "error"

def getTaxon(common):
    #gets taxon code
    f = open("eBird_taxonomy.csv")
    for line in f:
        if split(line)[4] == common:
            return split(line)[0]
    return "error"

def getSpecies(name):
    #recieves a species name and returns a name present in taxonomy, or it returns a list of "near miss" names if none are found
    arr = []
    name = str(name).lower()
    f = open("eBird_taxonomy.csv")
    for line in f:
        common = split(line)[4]
        if str(common).lower() == name:
            return [common]
        else:
            dist = Levenshtein.distance(name, str(common).lower())
            if dist < 3:
                arr.append(common)
            i = 0
            while i < len(common) - len(name):
                dist = Levenshtein.distance(name, str(common).lower()[i:i + len(name) + 1])
                if dist < 3 and indexOf(arr, common) == -1:
                    arr.append(common)
                i += 1
    return arr

def isValidTime(time):
    #recieves 24-h time and determines if it is a valid value
    if not(str(time).find(":") == -1):
        hour = int(str(time).split(":")[0])
        minute = int(str(time).split(":")[0])
        if hour > 24 or hour < 0:
            return False
        elif hour == 24:
            if minute != 0:
                return False
            else:
                return True
        else:
            if minute > 59 or minute < 0:
                return False
            else:
                return True
    else:
        return False

def to12HourTime(time):
    #converts a time to 12-hour, does NOT check if it is valid
    if str(time).lower().find("AM") != -1 or str(time).lower().find("PM") != -1:
        if str(time[-2:]).lower() == "pm":
            time = time[:-3]
            hour = int(str(time).split(":")[0])
            minute = str(time).split(":")[1]
            hour += 12

def addQuotes(s):
    if not(str(s).find(",") == -1):
        s = '"' + s + '"'
    return s

#species
@cli.command()
@click.argument("species", type=str)
@click.option("-l", "--location", is_flag = True, help="Print full location info (state/province, county, latitude and longitude)")
@click.option("-d", "--date", is_flag = True, help="Print time and duration, in addition to date")
@click.option("-n", "--notes", is_flag = True, help="Print species notes and breeding codes")
def species(species, location, date, notes): #add additional filters? (ex: by date or location)
    """Prints location and date of a given species."""
    f = open("data.csv")
    found = False
    for line in f:
        line = line.replace("\n", "")
        data = split(line)
        if data[1].lower() == species.lower():
            found = True
            strP = data[1] + '\nLocation: ' + data[8] + '\n'
            if location:
                strP += 'Country: ' + data[6] + '\nState/Province: ' + data[5] + '\nCounty: ' + data[7] + '\nLatitude: ' + data[9] + '\nLongitude: ' + data[10] + '\n'
            strP += 'Date: ' + data[11] + '\n'
            if date:
                strP += 'Time: ' + data[12] + '\nDuration: ' + data[14] + ' min\n'
            if notes:
                if data[18] != "":
                    strP += 'Notes: ' + data[18] + '\n'
            strP = str(strP).replace('"','')
            click.echo(strP)
    if not(found):
        click.echo("Species not found")
    f.close()

#lifelist
@cli.command()
@click.option("-l", "--location", is_flag = True, help="Print full location info (state/province, county, latitude and longitude)")
@click.option("-d", "--date", is_flag = True, help="Print time and duration, in addition to date")
@click.option("-n", "--notes", is_flag = True, help="Print species notes and breeding codes")
@click.option("-L", "--last", is_flag = True, help="Sort by last seen")
@click.option("-o", "--order", is_flag = True, help="Sort by newest sightings first")
@click.option("-a", "--additional", is_flag = True, help="List additional taxa (spuhs and slashes) if present")
def lifelist(location, date, notes, last, order, additional):
    """Prints life list sorted by date. Oldest sightings first, sorted by first seen"""
    f = open("data.csv")
    lifelist = [] #array of species arrays of data arrays
    additionals = [] #spuh/slash list
    list = []

    for line in f:
        line = line.replace("\n", "")
        data = split(line)
        if len(list) == 0:
            list.append([data])
        else:
            isAdded = False
            for specieslist in list:
                if specieslist[0][1] == data[1]:
                    isAdded = True
                    specieslist.append(data)
            if not(isAdded):
                list.append([data])
    for specieslist in list:
        specieslist.sort(key = byDate, reverse = last)
        if specieslist[0][1].find(".") == -1 and specieslist[0][1].find("/") == -1: #if not spuh/slash
            lifelist.append(specieslist[0])
        else:
            if additional:
                additionals.append(specieslist[0])
    lifelist.sort(key = byDate, reverse = order)
    for data in lifelist:
        strP = data[1] + '\nLocation: ' + data[8] + '\n'
        if location:
            strP += 'Country: ' + data[6] + '\nState/Province: ' + data[5] + '\nCounty: ' + data[7] + '\nLatitude: ' + data[9] + '\nLongitude: ' + data[10] + '\n'
        strP += 'Date: ' + data[11] + '\n'
        if date:
            strP += 'Time: ' + data[12] + '\nDuration: ' + data[14] + ' min\n'
        if notes:
            if data[18] != "":
                strP += 'Notes: ' + data[18] + '\n'
        strP = str(strP).replace('"', '')
        click.echo(strP)
    if additional:
        click.echo("Additional taxa:\n")
        for data in additionals:
            strP = data[1] + '\nLocation: ' + data[8] + '\n'
            if location:
                strP += 'Country: ' + data[6] + '\nState/Province: ' + data[5] + '\nCounty: ' + data[7] + '\nLatitude: ' + data[9] + '\nLongitude: ' + data[10] + '\n'
            strP += 'Date: ' + data[11] + '\n'
            if date:
                strP += 'Time: ' + data[12] + '\nDuration: ' + data[14] + ' min\n'
            if notes:
                if data[18] != "":
                    strP += 'Notes: ' + data[18] + '\n'
            strP = str(strP).replace('"', '')
            click.echo(strP)
    f.close()

#checklist
@cli.command()
@click.option("-f", "--filter", type=str, help="Value to filter checklists by")
@click.option("-l", "--location", is_flag = True, help="Print full location info (state/province, county, latitude and longitude)")
@click.option("-d", "--date", is_flag = True, help="Print time and duration, in addition to date")
@click.option("-n", "--notes", is_flag = True, help="Print species notes and breeding codes")
@click.option("-o", "--order", is_flag = True, help="Sort by newest checklists first")
def checklist(filter, location, date, notes, order):
    """Print all checklists, or filter by location, species, date etc."""

    f = open("data.csv")
    list = [] #list of entries that meet filter criteria (all if no filter)
    checklists = [] #array of array of entries
    ids = [] #list of submission ids associated with filter
    
    for line in f:
        line = line.replace("\n", "")
        data = split(line)
        if filter:
            if not(indexOf(data, filter) == -1): #if filter term exists in data
                ids.append(data[0])
        else:
            ids.append(data[0]) #currently also prints out first line --> don't need to change bc will not be a problem with import function
    
    if len(ids) > 0: #if there are ids that match filter
        f = open("data.csv")
        for line in f:
            data = split(line)
            for id in ids:
                if (data[0] == id) and (indexOf(list, data) == -1): #only add if data is not already in list
                    list.append(data)
        list.sort(key = byID)

        id = list[0][0]
        checklist = []
        for data in list:
            if data[0] == id:
                checklist.append(data)
            else:
                checklists.append(checklist)
                checklist = []
                checklist.append(data)
                id = data[0]
        checklists.append(checklist)
        checklists.sort(key = byDate, reverse = order)
        for checklist in checklists:
            checklist.sort(key = byTaxon)
            strP = 'Location: ' + checklist[0][8] + '\n'
            if location:
                strP += 'Country: ' + checklist[0][6] + '\nState/Province: ' + checklist[0][5] + '\nCounty: ' + checklist[0][7] + '\nLatitude: ' + checklist[0][9] + '\nLongitude: ' + checklist[0][10] + '\n'
            strP += 'Date: ' + checklist[0][11] + '\nProtocol: ' + checklist[0][13] + '\n'
            if checklist[0][13] == "Traveling":
                strP += 'Distance: ' + checklist[0][16] + ' mi\n'
            if date:
                strP += 'Time: ' + checklist[0][12] + '\nDuration: ' + checklist[0][14] + ' min\n'
            if checklist[0][15] == "Y":
                strP += "Complete Checklist\n"
            else:
                strP += "Incomplete Checklist\n"
            if notes:
                if checklist[0][19] != "":
                    strP += 'Notes: ' + checklist[0][19] + '\n'
            for data in checklist:
                strP += '\t' + data[4] + ' ' + data[1] + '\n'
                if notes:
                    if data[18] != "":
                        strP += '\t\tNotes: ' + data[18] + '\n'
            strP = str(strP).replace('"', '')
            click.echo(strP)
    else:
        click.echo("Nothing matches your filter.")
    f.close()

#import
@cli.command()
@click.argument("filepath", type=click.Path(exists=True, dir_okay=False))
def Import(filepath):
    """Import eBird data to this program.""" #N0TE: Delete province, county, lat, long? <--will users want to enter all this in manually?
    if filepath[-4:] != ".csv":
        click.echo("Filetype must be .csv")
    else:
        f = open(filepath)
        w = open("data.csv", "a")
        for line in f:
            line = line.replace("\n", "")
            data = split(line)
            #print(data)
            if data[0] != "Submission ID":
                lid = generateLID(data[11], data[12])
                state = data[5].split("-")[1]
                country = data[5].split("-")[0]
                p = ""
                if data[13] == "eBird - Traveling Count":
                    p = "Traveling"
                elif data[13] == "eBird - Casual Observation":
                    p = "Casual"
                elif data[13] == "eBird - Stationary Count":
                    p = "Stationary"
                elif data[13] != "Historical":
                    p = "Other"
                complete = ""
                if data[15] == "0":
                    complete = "N"
                else:
                    complete = "Y"
                newdata = [lid + ',', data[1] + ',', data[2] + ',', data[3] + ',', data[4] + ',', state + ',', country + ',', data[6] + ',', data[8] + ',', data[9] + ',', data[10] + ',', data[11] + ',', data[12] + ',', p + ',', data[14] + ',', complete + ',', data[16] + ',', data[18] + ',']
                if len(data) > 20:
                    newdata.append(data[20] + ',')
                else:
                    newdata.append(',')
                if len(data) > 21:
                    newdata.append(data[21] + ',')
                else:
                    newdata.append(',')
                newdata.append("T") #stands for Tracked, indicates that this entry is up-to-date w/ ebird
                strP = ""
                for d in newdata:
                    strP += d
                strP = strP.replace("\n", "")
                w.write(strP + "\n")
        f.close()
        click.echo("Data imported")
   

#export
@cli.command()
@click.option("-a", "--all", is_flag = True, help="Export all data")
def export(all):
    """Export data from this program to eBird Record Format."""
    f = open("data.csv")
    exportlist = []
    lifelist = ""
    for line in f:
        data = split(line)
        if data[20][0:1] == "U":
            exportlist.append(data)
        lifelist += line[:-2] + "T\n"
    f.close()
    exportfile = open(exportlist[0][0] + ".csv", "w") #filename is LID of first checklist
    for data in exportlist:
        ef = ""
        if data[15] == "0":
            ef = "N"
        else:
            ef = "Y"
        date = data[11].split("-")[1] + "/" + data[11].split("-")[2] + "/" + data[11].split("-")[0]
        exportfile.write(data[1] + ',,,' + data[4] + ',' + data[18] + ',' + data[8] + ',' + data[9] + ',' + data[10] + ',' + date + ',' + data[12] + ',' + data[5] + ',' + data[6] + ',' + data[13] + ',' + data[17] + ',' + data[14] + ',' + ef + ',' + data[16] + ',,' + data[19] + ',\n')
    f = open("data.csv", "w")
    f.write(lifelist)
    f.close()
    click.echo("Data exported to " + exportlist[0][0] + ".csv")

#create
@cli.command()
def create():
    """Create a new checklist."""
    click.echo("* = required question")
    date = click.prompt("*Date (yyyy-mm-dd)")
    time = click.prompt("*Start time")
    lid = generateLID(date, time)
    isNew = True
    toWrite = []
    f = open("data.csv")
    for line in f:
        data = split(line)
        if data[0] == lid:
            isNew = False
        toWrite.append(data)
    f.close()

    if isNew:
        protocol = click.prompt("*Protocol", type=click.Choice(["Traveling", "Stationary", "Casual"]), show_choices=True)
        if not(protocol == "Casual"):
            duration = click.prompt("*Duration (min)")
            if click.prompt("*All species reported (y/n)", type=click.Choice(["y", "n"]), show_choices=False) == "y":
                effort = "Y"
            else:
                effort = "N"
            if protocol == "Traveling":
                distance = click.prompt("*Distance traveled (mi)")
        else: #if it is casual
            effort = "N"
        observers = click.prompt("*Party size", type=int)
        location = addQuotes(click.prompt("*Location"))
        duration = ""
        effort = ""
        distance = ""
        country = click.prompt(" Country", default="", show_default=False)
        stprov = click.prompt(" State/province", default="", show_default=False)
        county = click.prompt(" County", default="", show_default=False)
        latitude = click.prompt(" Latitude", default="", show_default=False)
        longitude = click.prompt(" Longitude", default="", show_default=False)
        comments = addQuotes(click.prompt(" Checklist comments", default="", show_default=False))
        species = []
        s = ""
        click.echo("Enter species and how many. One species at a time. Type \"stop\" when you are finished.")
        while not(s == "stop"):
            s = click.prompt("*Enter species")
            if not(s == "stop"):
                slist = getSpecies(s)
                if len(slist) == 1:
                    s = slist[0]  
                else:
                    while len(slist) > 1 or len(slist) == 0:
                        if len(slist) > 1:
                            click.echo("You've entered a species that's not in the eBird taxonomy. Did you mean to enter one of these species instead?")
                            for l in slist:
                                click.echo(l)
                        else:
                            click.echo("You've entered a species that's not in the eBird taxonomy.")
                        s = click.prompt("*Enter species")
                        slist = getSpecies(s)
                    s = slist[0]
                n = click.prompt("*How many")
                c = addQuotes(click.prompt(" Comments", default="", show_default=False))
                species.append([s, n, c])
        for s in species:
            scientific = getScientific(s[0])
            taxon = str(getTaxon(s[0]))
            entry = [str(lid), s[0], scientific, taxon, str(s[1]), stprov, country, county, location, str(latitude), str(longitude), date, time, protocol, str(duration), str(effort), str(distance), str(observers), s[2], comments, 'U\n']
            toWrite.append(entry)
        toWrite.sort(key=byTaxon)
        f = open("data.csv", "w")
        for line in toWrite:
            data = ""
            for l in line:
                data += (l + ",")
            data = data[:-1]
            f.write(data)
    else:
        click.echo("A checklist already exists at that date and time. Use \"cbird edit\" command to edit it.")

#edit
@cli.command()
def edit():
    """Edit a checklist."""
    click.echo("* = required question")
    date = click.prompt("*Date (yyyy-mm-dd)")
    time = click.prompt("*Start time")
    lid = generateLID(date, time)
    isNew = True
    f = open("data.csv")
    for line in f:
        data = split(line)
        if data[0] == lid:
            isNew = False
    f.close()
    if not(isNew):
        checklist = []
        toWrite = [] #stores rows to write back to file
        f = open("data.csv")
        for line in f:
            data = split(line)
            if data[0] == lid:
                checklist.append(data)
            else:
                toWrite.append(data)
        checklist.sort(key = byTaxon)
        strP = '\nLocation: ' + checklist[0][8] + '\nCountry: ' + checklist[0][6] + '\nState/Province: ' + checklist[0][5] + '\nCounty: ' + checklist[0][7] + '\nLatitude: ' + checklist[0][9] + '\nLongitude: ' + checklist[0][10] + '\nDate: ' + checklist[0][11] + '\nProtocol: ' + checklist[0][13]
        strP += '\nDistance (mi): ' + checklist[0][16]
        strP += '\nTime: ' + checklist[0][12] + '\nDuration (min): ' + checklist[0][14]
        strP += "\nComplete (Y/N): " + checklist[0][15] + "\n"
        strP += 'Number of observers: ' +checklist[0][17] + '\nNotes: ' + checklist[0][19] + '\nSpecies:\n'
        for data in checklist:
            strP += '\t' + data[4] + ' ' + data[1] + '\n\t\tNotes: ' + data[18] + '\n'
        strP = str(strP).replace('"', '')
        click.echo(strP)
        if click.prompt("Are you sure that you want to edit this checklist? (y/n)", type=click.Choice(["y", "n"]), show_choices=False) == "y":
            checklistStr = click.edit(strP)
            checklistStr = str(checklistStr).replace("\t", "")
            checklistArr = checklistStr.split("\n") #split edited string file into data, then check to make sure data (dates, names) are correct
            location = addQuotes(checklistArr[1][10:]) #test what happens w/ no edits
            country = checklistArr[2][9:]
            stprov = checklistArr[3][16:]
            county = checklistArr[4][8:]
            lat = checklistArr[5][10:]
            long = checklistArr[6][11:]
            date = checklistArr[7][6:]
            protocol = checklistArr[8][10:]
            distance = checklistArr[9][15:]
            time = checklistArr[10][6:]
            duration = checklistArr[11][16:]
            complete = checklistArr[12][16:]
            observers = checklistArr[13][21:]
            notes = addQuotes(checklistArr[14][7:])
            species = checklistArr[16:]
            #print(species)
            i = 0
            while i < (len(species) - 1):
                num = species[i].split(maxsplit=1)[0]
                name = species[i].split(maxsplit=1)[1]
                snotes = addQuotes(species[i + 1][7:])
                slist = getSpecies(name)
                sname = ""
                if len(slist) == 1:
                    name = slist[0]  
                else:
                    while len(slist) > 1 or len(slist) == 0:
                        if len(slist) > 1:
                            click.echo("You've entered a species that's not in the eBird taxonomy. Did you mean to enter one of these species instead?")
                            for l in slist:
                                click.echo(l)
                        else:
                            click.echo("You've entered a species that's not in the eBird taxonomy. Please enter which species you meant.")
                        name = click.prompt("Species") #give option to enter an out-of-taxonomy species
                        slist = getSpecies(name)
                    name = slist[0]
                sname = getScientific(name)
                taxon = getTaxon(name)
                newData = [lid, name, sname, taxon, num, stprov, country, county, location, lat, long, date, time, protocol, duration, complete, distance, observers, snotes , notes, 'U\n']
                #print(strW)
                toWrite.append(newData)
                i += 2
            click.echo("Note: to see these changes reflected in eBird, you will need to delete the checklist on eBird then use \"cbird export\" to export and upload untracked data.")
            toWrite.sort(key=byTaxon)
            f = open("data.csv", "w")
            for line in toWrite:
                data = ""
                for l in line:
                    data += (l + ",")
                data = data[:-1]
                f.write(data)

    else:
        click.echo("A checklist does not exist at that date and time. Use \"cbird create\" to create a new checklist.")

