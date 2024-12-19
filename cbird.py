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

#cbird import FILEPATH
#takes in a csv file from ebird and generates a new csv file
# - ebird csv files have submission IDs, and this file creates new ids (local specific) and marks entries as in ebird

#cbird export
#creates csv file of all data that is not already in ebird

#cbird add
#adds a checklist from user prompting to local csv, marks what is added as not in ebird

import click

@click.group()
def cli():
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

def split(str): #splits a csv element by comma, but ignores commas in quotes
    list = str.split(",")
    quoteStartIndex = -1
    quoteEndIndex = -1
    index = 0
    for element in list:
        if element.startswith('"'):
            quoteStartIndex = index
        if element.endswith('"') or element.endswith('"\n'):
            quoteEndIndex = index
            s = ""
            i = quoteStartIndex
            while i < quoteEndIndex:
                s += list[i] + ","
                i += 1
            s += list[i]
            s = s.replace('"', "")
            list[quoteStartIndex:quoteEndIndex+1] = [s]
            diff = quoteEndIndex - quoteStartIndex
            index -= diff
        index += 1
    return list

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
        data = split(line)
        if not(indexOf(data, filter) == -1): #if filter term exists in data
            ids.append(data[0])
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
            if notes and len(checklist[0]) > 21:
                str += 'Notes: ' + checklist[0][21] + '\n'
            if sid:
                str += 'Submission ID: ' + checklist[0][0] + '\n'
            for data in checklist:
                str += '\t' + data[4] + ' ' + data[1] + '\n'
                if notes:
                    if len(data) > 20:
                        str += '\t\tBreeding code: ' + data[19] + '\n\t\tNotes: ' + data[20]
                    elif len(data) > 19:
                        str += '\t\tBreeding code: ' + data[19] + '\n\t\tNotes:\n'
                    else:
                        str += '\t\tBreeding code:\n\t\tNotes:\n'
            click.echo(str)
    else:
        click.echo("Nothing matches your filter.")
    f.close()