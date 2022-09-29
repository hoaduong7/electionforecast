import csv

#takes in a list of polls as a parameter
def createMegaPoll(pollsList):
    #iterates through all polls
    with open('static/polls/megapoll.csv' , 'w', newline='') as out:
        for indx, i in enumerate(pollsList):
            with open("static/polls/new/" + i + "-crosstabbed.csv", newline='') as inp:
                reader = list(csv.DictReader(inp))
                fieldnames = list(reader[0].keys()) + ["Poll"]
                #deletes the field "respondent ID" as not relevant in megapoll
                del fieldnames[0]
                writer = csv.DictWriter(out, fieldnames=fieldnames)
                if indx == 0:
                    writer.writeheader()
                for row in reader:
                    #adds column "Poll" to ordered dictionary
                    row['Poll'] = i
                    del row['RespondentId']
                    writer.writerow(row)
                
createMegaPoll(["survation-27-apr", "survation-26-may", "survation-3-jun"])
