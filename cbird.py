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

#cbird add
#adds a checklist from user prompting to local csv, marks what is added as not in ebird

#some sort of way to store photos associated with a checklist

#add regional stats, so you can see how many bird you've seen in a certain area

#other features:
#   user config file
#   check user entered species against ebird taxonomy

import click
import Levenshtein

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

def nearMiss(name):
    #recieves a name not present in taxonomy and returns array of "near miss names"
    arr = []
    f = open("eBird_taxonomy.csv")
    for line in f:
        dist = Levenshtein.distance(name, split(line)[4])
        print("comp is " + split(line)[4])
        print("Dist is " + str(dist))
        if dist < 3:
            arr.append(split(line)[4])
        if split(line)[4].find(name) != -1: #if name exists in line
            arr.append(split(line)[4])
    f = open("eBird_taxonomy.csv")
    narr = arr.copy()
    for line in f:
        for n in narr:
            if split(line)[4].find(n) != -1:
                arr.append(split(line)[4])
    return arr

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
            str = data[1] + '\nLocation: ' + data[8] + '\n'
            if location:
                str += 'Country: ' + data[6] + '\nState/Province: ' + data[5] + '\nCounty: ' + data[7] + '\nLatitude: ' + data[9] + '\nLongitude: ' + data[10] + '\n'
            str += 'Date: ' + data[11] + '\n'
            if date:
                str += 'Time: ' + data[12] + '\nDuration: ' + data[14] + ' min\n'
            if notes:
                if data[18] != "":
                    str += 'Notes: ' + data[18] + '\n'
            click.echo(str)
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
    species = ""
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
        str = data[1] + '\nLocation: ' + data[8] + '\n'
        if location:
            str += 'Country: ' + data[6] + '\nState/Province: ' + data[5] + '\nCounty: ' + data[7] + '\nLatitude: ' + data[9] + '\nLongitude: ' + data[10] + '\n'
        str += 'Date: ' + data[11] + '\n'
        if date:
            str += 'Time: ' + data[12] + '\nDuration: ' + data[14] + ' min\n'
        if notes:
            if data[18] != "":
                str += 'Notes: ' + data[18] + '\n'
        click.echo(str)
    if additional:
        click.echo("Additional taxa:\n")
        for data in additionals:
            str = data[1] + '\nLocation: ' + data[8] + '\n'
            if location:
                str += 'Country: ' + data[6] + '\nState/Province: ' + data[5] + '\nCounty: ' + data[7] + '\nLatitude: ' + data[9] + '\nLongitude: ' + data[10] + '\n'
            str += 'Date: ' + data[11] + '\n'
            if date:
                str += 'Time: ' + data[12] + '\nDuration: ' + data[14] + ' min\n'
            if notes:
                if data[18] != "":
                    str += 'Notes: ' + data[18] + '\n'
            click.echo(str)
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
            str = 'Location: ' + checklist[0][8] + '\n'
            if location:
                str += 'Country: ' + checklist[0][6] + '\nState/Province: ' + checklist[0][5] + '\nCounty: ' + checklist[0][7] + '\nLatitude: ' + checklist[0][9] + '\nLongitude: ' + checklist[0][10] + '\n'
            str += 'Date: ' + checklist[0][11] + '\nProtocol: ' + checklist[0][13] + '\n'
            if checklist[0][13] == "Traveling":
                str += 'Distance: ' + checklist[0][16] + ' mi\n'
            if date:
                str += 'Time: ' + checklist[0][12] + '\nDuration: ' + checklist[0][14] + ' min\n'
            if checklist[0][17] == 1:
                str += "Complete Checklist\n"
            else:
                str += "Incomplete Checklist\n"
            if notes:
                if checklist[0][19] != "":
                    str += 'Notes: ' + checklist[0][19] + '\n'
            for data in checklist:
                str += '\t' + data[4] + ' ' + data[1] + '\n'
                if notes:
                    if data[18] != "":
                        str += '\t\tNotes: ' + data[18] + '\n'
            click.echo(str)
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
                newdata = [lid + ',', data[1] + ',', data[2] + ',', data[3] + ',', data[4] + ',', state + ',', country + ',', data[6] + ',', data[8] + ',', data[9] + ',', data[10] + ',', data[11] + ',', data[12] + ',', p + ',', data[14] + ',', data[15] + ',', data[16] + ',', data[18] + ',']
                if len(data) > 20:
                    newdata.append(data[20] + ',')
                else:
                    newdata.append(',')
                if len(data) > 21:
                    newdata.append(data[21] + ',')
                else:
                    newdata.append(',')
                newdata.append("T") #stands for Tracked, indicates that this entry is up-to-date w/ ebird
                str = ""
                for d in newdata:
                    str += d
                str = str.replace("\n", "")
                w.write(str + "\n")
   

#export
@cli.command()
def export():
    """Export data from this program to eBird."""

#create
@cli.command()
def create():
    """Create a new checklist."""
    #required: protocol, date, time, effort, num birdwatchers
    #required if stationary or traveling: duration
    #required if traveling: distance
    #optional: lat, long

    protocol = click.prompt("Protocol", type=click.Choice(["Traveling", "Stationary", "Casual"]), show_choices=True)
    date = click.prompt("Date (yyyy-mm-dd)")
    time = click.prompt("Time")
    #calculate LID here, and it is already present ask them if they'd like to edit that checklist instead
    observers = click.prompt("Party size", type=int)
    location = click.prompt("Location")
    if location.find(',') != -1:
        location = '"' + location + '"'
    duration = ""
    effort = ""
    distance = ""
    if not(protocol == "Casual"):
        duration = click.prompt("Duration (min)")
        if click.prompt("All species reported (y/n)", type=click.Choice(["y", "n"]), show_choices=False) == "y":
            effort = "1"
        else:
            effort = "0"
        if protocol == "Traveling":
            distance = click.prompt("Distance traveled")
    else: #if it is casual
        effort = "0"
    comments = click.prompt("Checklist comments", default="", show_default=False)
    if comments.find(',') != -1:
        comments = '"' + comments + '"'
    country = click.prompt("Country", default="", show_default=False)
    stprov = click.prompt("State/province", default="", show_default=False)
    county = click.prompt("County", default="", show_default=False)
    latitude = click.prompt("Latitude", default="", show_default=False)
    longitude = click.prompt("Longitude", default="", show_default=False)
    species = []
    s = ""
    click.echo("Enter species and how many. One species at a time. Type \"stop\" when you are finished.")
    while not(s == "stop"):
        s = click.prompt("Enter species")
        if not(s == "stop"):
            n = click.prompt("How many")
            c = ""
            if click.prompt("Add comments (y/n)", type=click.Choice(["y", "n"]), show_choices=False) == "y":
                c = click.prompt("Comments")
                if c.find(',') != -1:
                    c = '"' + c + '"'
            species.append([s, n, c])
            print(nearMiss(s))
    print(species)
    #near miss method --> if common name is not found, looks for names that are one letter off or contain part of that name
    scientific = getScientific(s[0])
    taxon = str(getTaxon(s[0]))
    entry = ""
    for s in species:
        lid = generateLID(date, time)
        entry += str(lid) + ',' + s[0] + ',' + scientific + ',' + taxon + ',' + str(s[1]) + ',' + stprov + ',' + country + ',' + county + ',' + location + ',' + str(latitude) + ',' + str(longitude) + ',' + date + ',' + time + ',' + protocol + ',' + str(duration) + ',' + str(effort) + ',' + str(distance) + ',' + str(observers) + ',' + s[2] + ',' + comments + ',U\n'
    print(entry)
