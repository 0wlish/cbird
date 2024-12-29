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

import click


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
        return data[11].replace("-", "")
    else:
        return data[0][11].replace("-", "")

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
        else:
            newList.append(element)
        index += 1
    return newList


def generateLID(data):
    #recieves data and returns a Local ID generated from data. LIDs are used to distinguish checklists locally.
    date = data[11].replace("-", "")
    time = data[12].replace(":", "")
    if time[-3:] == " PM":
        time = time[:-3]
        time = int(time) + 1200
    elif time[-3:] == " AM":
        time = time[:-3]
    return date + str(time)

#species
@cli.command()
@click.argument("species", type=str)
@click.option("-l", "--location", is_flag = True, help="Print full location info (state/province, county, latitude and longitude)")
@click.option("-d", "--date", is_flag = True, help="Print time and duration, in addition to date")
@click.option("-n", "--notes", is_flag = True, help="Print species notes and breeding codes")
@click.option("-s", "--sid", is_flag = True, help="Print submission ID")
def species(species, location, date, notes, sid): #add additional filters? (ex: by date or location)
    """Prints location and date of a given species."""
    f = open("MyEBirdData.csv")
    found = False
    for line in f:
        line = line.replace("\n", "")
        data = split(line)
        if data[1].lower() == species.lower():
            found = True
            str = data[1] + '\nLocation: ' + data[8] + '\n'
            if location:
                str += 'State/Province: ' + data[5] + '\nCounty: ' + data[6] + '\nLatitude: ' + data[9] + '\nLongitude: ' + data[10] + '\n'
            str += 'Date: ' + data[11] + '\n'
            if date:
                str += 'Time: ' + data[12] + '\nDuration: ' + data[14] + '\n'
            if notes:
                if len(data) > 20:
                    str += 'Breeding code: ' + data[19] + '\nNotes: ' + data[20] + '\n'
                elif len(data) > 19:
                    str += 'Breeding code: ' + data[19] + '\nNotes:\n'
                else:
                    str += 'Breeding code:\nNotes:\n'
            if sid:
                str += 'Submission ID: ' + data[20] + '\n'
            click.echo(str)
    if not(found):
        click.echo("Species not found")
    f.close()

#lifelist
@cli.command()
@click.option("-l", "--location", is_flag = True, help="Print full location info (state/province, county, latitude and longitude)")
@click.option("-d", "--date", is_flag = True, help="Print time and duration, in addition to date")
@click.option("-n", "--notes", is_flag = True, help="Print species notes and breeding codes")
@click.option("-s", "--sid", is_flag = True, help="Print submission ID")
@click.option("-L", "--last", is_flag = True, help="Sort by last seen")
@click.option("-o", "--order", is_flag = True, help="Sort by newest sightings first")
@click.option("-a", "--additional", is_flag = True, help="List additional taxa (spuhs and slashes) if present")
def lifelist(location, date, notes, sid, last, order, additional):
    """Prints life list sorted by date. Oldest sightings first, sorted by first seen"""
    f = open("MyEBirdData.csv")
    species = "Common Name"
    prevData = []
    lifelist = []
    additionals = [] #spuh/slash list
    for line in f:
        line = line.replace("\n", "")
        data = split(line)
        if last:
            if not(data[1] == species):
                if data[1].find(".") == -1 and data[1].find("/") == -1: #if not spuh/slash
                    lifelist.append(data)
                else:
                    if additional:
                        additionals.append(data)
        else:
            if not(data[1] == species):
                species = data[1]
                if not(prevData[1] == "Common Name"):
                    if data[1].find(".") == -1 and data[1].find("/") == -1: #if not spuh/slash
                        lifelist.append(data)
                    else:
                        if additional:
                            additionals.append(data)
                prevData = data
            else:
                prevData = data
    lifelist.sort(key = byDate, reverse = order)
    for data in lifelist:
        str = data[1] + '\nLocation: ' + data[8] + '\n'
        if location:
            str += 'State/Province: ' + data[5] + '\nCounty: ' + data[6] + '\nLatitude: ' + data[9] + '\nLongitude: ' + data[10] + '\n'
        str += 'Date: ' + data[11] + '\n'
        if date:
            str += 'Time: ' + data[12] + '\nDuration: ' + data[14] + '\n'
        if notes:
            if len(data) > 20:
                str += 'Breeding code: ' + data[19] + '\nNotes: ' + data[20] + '\n'
            elif len(data) > 19:
                str += 'Breeding code: ' + data[19] + '\nNotes:\n'
            else:
                str += 'Breeding code:\nNotes:\n'
        if sid:
            str += 'Submission ID: ' + data[0] + '\n'
        click.echo(str)
    if additional:
        click.echo("Additional taxa:\n")
        for data in additionals:
            str = data[1] + '\nLocation: ' + data[8] + '\n'
            if location:
                str += 'State/Province: ' + data[5] + '\nCounty: ' + data[6] + '\nLatitude: ' + data[9] + '\nLongitude: ' + data[10] + '\n'
            str += 'Date: ' + data[11] + '\n'
            if date:
                str += 'Time: ' + data[12] + '\nDuration: ' + data[14] + '\n'
            if notes:
                if len(data) > 20:
                    str += 'Breeding code: ' + data[19] + '\nNotes: ' + data[20] + '\n'
                elif len(data) > 19:
                    str += 'Breeding code: ' + data[19] + '\nNotes:\n'
                else:
                    str += 'Breeding code:\nNotes:\n'
            if sid:
                str += 'Submission ID: ' + data[0] + '\n'
            click.echo(str)
    f.close()

#checklist
@cli.command()
@click.option("-f", "--filter", type=str, help="Value to filter checklists by")
@click.option("-l", "--location", is_flag = True, help="Print full location info (state/province, county, latitude and longitude)")
@click.option("-d", "--date", is_flag = True, help="Print time and duration, in addition to date")
@click.option("-n", "--notes", is_flag = True, help="Print species notes and breeding codes")
@click.option("-s", "--sid", is_flag = True, help="Print submission ID")
@click.option("-o", "--order", is_flag = True, help="Sort by newest checklists first")
def checklist(filter, location, date, notes, sid, order):
    """Print all checklists, or filter by location, species, ID, etc."""

    f = open("MyEBirdData.csv")
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
        f = open("MyEBirdData.csv")
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
            str = 'Location: ' + checklist[0][8] + '\n'
            if location:
                str += 'State/Province: ' + checklist[0][5] + '\nCounty: ' + checklist[0][6] + '\nLatitude: ' + checklist[0][9] + '\nLongitude: ' + checklist[0][10] + '\n'
            str += 'Date: ' + checklist[0][11] + '\nProtocol: ' + checklist[0][13] + '\n'
            if date:
                str += 'Time: ' + checklist[0][12] + '\nDuration: ' + checklist[0][14] + '\n'
            if checklist[0][15] == 1:
                str += "Complete Checklist\n"
            else:
                str += "Incomplete Checklist\n"
            if notes and len(checklist[0]) > 21:
                str += 'Notes: ' + checklist[0][21] + '\n'
            if sid:
                str += 'Submission ID: ' + checklist[0][0] + '\n'
            for data in checklist:
                str += '\t' + data[4] + ' ' + data[1] + '\n'
                if notes and len(data) > 20:
                    str += '\t\tNotes: ' + data[20]
            click.echo(str)
    else:
        click.echo("Nothing matches your filter.")
    f.close()

#importdata
@cli.command()
@click.argument("filepath", type=click.Path(exists=True, dir_okay=False))
def Import(filepath):
    """Import eBird data to this program."""
    #eliminate taxonomic order, location ID, breeding code, ML catalog numbers
    #modify SID (to LID)
    #modify date, time, dist traveled, area covered according to user config
    if filepath[-4:] != ".csv":
        click.echo("Filetype must be .csv")
    else:
        f = open(filepath)
        w = open("data.csv", "a")
        for line in f:
            line = line.replace("\n", "")
            data = split(line)
            print(data)
            if data[0] != "Submission ID":
                lid = generateLID(data)
                newdata = [lid + ',', data[1] + ',', data[2] + ',', data[4] + ',', data[5] + ',', data[6] + ',', data[8] + ',', data[9] + ',', data[10] + ',', data[11] + ',', data[12] + ',', data[13] + ',', data[14] + ',', data[15] + ',', data[16] + ',', data[17] + ',', data[18] + ',']
                if len(data) > 20:
                    newdata.append(data[20] + ',')
                else:
                    newdata.append(',')
                if len(data) > 21:
                    newdata.append(data[21] + ',')
                else:
                    newdata.append(',')
                str = ""
                for d in newdata:
                    str += d
                str = str.replace("\n", "")
                str = str[:-1]
                w.write(str + "\n")


            

        

#exportdata
@cli.command()
def export():
    """Export data from this program to eBird."""