import csv
import random
import time

def p2f(x):
    #checks if the string is a hyphen or empty
    if x == "-" or x == "- ":
        #changes hyphen into 0.00%, normalises input
        x = "0.00%"
    #returns decimal result as float
    return float(x.strip('%'))/100

def getTotal(totals, reader, row, attribute):
    #gets total votes for an individual categorical variable
    #useful because there may be duplicates that need to be merged
    totalVotes = int(round(round(p2f(reader[row + 1][attribute]), 4) * int(totals[attribute]),0))
    return totalVotes

def writeCrossTabs(participants, writer, fieldnames):
    #iterates through all respondents to survey
    for i in participants:
        participantDict = {}
        x = 0
        #iterates through dictionary keys
        for field in fieldnames:
            participantDict[field] = i[x]
            x += 1
        #writes output to csv file
        writer.writerow(participantDict)

def getGroup(groupNo, groupDict, participants, party):
    #instantiates empty list
    temp = []
    #iterates and enumerates dictionary of group
    for key, value in groupDict.items():
        #checks if the number of respondents from group and party (crosstab) has been exceeded
        if value < len([x for x in participants if x[groupNo] == key and x[1] == party]):
            #if yes, add the party to the temp list 
            temp.append(key)
    #deletes all items in both temp and groupDict
    #this means that a party can only have as many respondents as the survey suggests
    for j in temp:
        del groupDict[j]
    
    #Localised parties can only get votes in specific regions
    try:
        if party == "Scottish National Party" and groupNo == 4:
            return "Scotland"
        elif party == "Plaid Cymru" and groupNo == 4:
            return "Wales"

        else:
        #otherwise, random choice of the dictionary keys is allowed
            return random.choice(list(groupDict.keys()))
    except:
        return "Did not vote"

def survation(pollId):
    pollrows = []
    #opens an input and an output file
    with open("static/polls/" + pollId + ".csv", newline='') as inp, open('static/polls/new/' + pollId + "-crosstabbed.csv" , 'w', newline='') as out:
        reader = list(csv.DictReader(inp))
        #changes type of the reader from iterable to list - makes it indexable
        fieldnames = ['RespondentId', 'Party', 'Gender', 'AgeGroup', 'Region' ,'SocialGroup', 'PastVote', 'Brexit']
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        respondentNo = 1
        totals = reader[0]
        participants = []
        #gets the value of Weighted Total
        for row in range (len(reader)):
            if reader[row]['Party'] != '' and reader[row]['Party'] != "SIGMA" and reader[row]['Party'] != "Weighted Total":
                totalVotes = getTotal(totals, reader, row, 'Total')
                
                #each categorical variable is assigned a dictionary
                genders = {"Male": getTotal(totals, reader, row, "Male"),
                           "Female": getTotal(totals, reader, row, "Female")}
                ageGroups = {'18-34': getTotal(totals, reader, row, "18-34"),
                             '35-44': getTotal(totals, reader, row, "35-44"),
                             '45-54': getTotal(totals, reader, row, "45-54"),
                             '55-64': getTotal(totals, reader, row, "55-64"),
                             '65+': getTotal(totals, reader, row, "65+")}
                regions = {'London': getTotal(totals, reader, row, "London"),
                             'South': getTotal(totals, reader, row, "South"),
                             'Midlands': getTotal(totals, reader, row, "Midlands"),
                             'North': getTotal(totals, reader, row, "North"),
                             'Scotland': getTotal(totals, reader, row, "Scotland"),
                             'Wales': getTotal(totals, reader, row, "North"),
                             'Northern Ireland': getTotal(totals, reader, row, "Northern Ireland"),}
                socialGroups = {'DE': getTotal(totals, reader, row, "No Qualifications / Level 1"),
                             'C2': getTotal(totals, reader, row, "Level 2 / Apprenticeship / Other"),
                             'C1': getTotal(totals, reader, row, "Level 3"),
                             'AB': getTotal(totals, reader, row, "Level 4+"),}
                pastVotes = {'Conservative': getTotal(totals, reader, row, "CON"),
                             'Labour': getTotal(totals, reader, row, "LAB"),
                             'Liberal Democrats': getTotal(totals, reader, row, "LD"),
                             'Other': getTotal(totals, reader, row, "OTH"),}
                brexitVotes = {'Leave': getTotal(totals, reader, row, "Leave"),
                             'Remain': getTotal(totals, reader, row, "Remain"),}

                for i in range(0, totalVotes):
                    #default option is that all fields are set to 0
                    party = reader[row]['Party']
                    
                    gender = getGroup(2, genders, participants, party) #assign gender
                    ageGroup = getGroup(3, ageGroups, participants, party) #assign age group
                    region = getGroup(4, regions, participants, party) #assign region
                    socialGroup = getGroup(5, socialGroups, participants, party) #assign region
                    pastVote = getGroup(6, pastVotes, participants, party) #assign past vote
                    brexit = getGroup(7, brexitVotes, participants, party) #assign past vote

                    participants.append([respondentNo, party, gender, ageGroup, region, socialGroup, pastVote, brexit])
                    
                    respondentNo += 1
        writeCrossTabs(participants, writer, fieldnames)
            

#performance modelling
start = time.time()
#crosstabs all survey instances
survation("survation-26-may")
survation("survation-27-apr")
survation("survation-3-jun")
end = time.time()
print(end - start)
