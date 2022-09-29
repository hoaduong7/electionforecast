from models import Constituency, Region, Party
import csv
with open('winningparties.csv', mode='r') as infile:
    reader = csv.reader(infile)
    mydict = {rows[0]:[rows[1],rows[2]] for rows in reader}

for i in mydict:
    newconst = Constituency.objects.create(name=i, region=Region.objects.get(name=i[0]), incumbent=Party.objects.get(shortname=i[1]))

