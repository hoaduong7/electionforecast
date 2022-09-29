from django.db import models
import csv
from djangoPandas.managers import DataFrameManager
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import operator
from django.contrib.auth.models import User
from datetime import datetime
import time

def getMegapoll():
    #returns megapoll pandas data frame
    return pd.readCsv(r"mainApp\static\polls\megapoll.csv")


class Constituency(models.Model):
    #an object will be created for every constituency in the country
    id = models.CharField(maxLength=100, primaryKey=True)
    name = models.CharField(maxLength=100, unique=True)
    
    #makes the name URL-safe rather thn having spaces and commas
    rawName = models.CharField(editable=True, maxLength=300, unique=True)
    
    #region of the constituency
    region = models.ForeignKey('Region', onDelete=models.SETNULL, null=True, blank=True)
    #party which won election in last election 
    incumbent = models.ForeignKey('Party', onDelete=models.SETNULL, null=True, blank=True)
    
    def prediction(self, censusDf):
        #uses getter function to obtain poll Pandas data frame
        pollDf = getMegapoll()

        #calls all objects of the Party class
        parties = Party.objects.all()
        projectedResults = {}

        #create dictionary of votes for each party object
        votes = {party:0 for party in parties}
        
        #filters data frame for only polling of specific region
        pollDf = pollDf[(pollDf['Region'] == self.region.name)]
        
        #filters census to only the relevant constituency
        constituencyCensus = censusDf[(censusDf['ID'] == self.id)].values.tolist()
        for indx, i in enumerate(constituencyCensus):
            
            #this selection corrects inconsistency in data tables from different govt departments
            if i[5] == "Age 16 to 24" or i[5] == "Age 25 to 34":
                age = "18-34"
            elif i[5] == "Age 35 to 44":
                age = "35-44"
                
            elif i[5] == "Age 45 to 54":
                age = "45-54"
            elif i[5] == "Age 55 to 64":
                age = "55-64"
            else:
                age = None
            
            #filter poll data frame into demographic groups, and turn into iterable list
            conditions = (pollDf['SocialGroup'] == i[3]) & (pollDf['Gender'] == i[2]) & (pollDf['AgeGroup'] == age)
            filteredPoll = pollDf[conditions].values.tolist()
            
            #try to weight each poll respondent - less respondents = higher individual weight
            try:
                weight = 1/len(filteredPoll)
            except:
                pass
            
            #add votes to respective parties
            for j in filteredPoll:
                votes[Party.objects.get(name=j[0])] += int(weight * i[6])
                
        newVotes = {}
        for x in votes:
            #gets average of the projection, and the previous result in each constituency
            newVotes[x] = (votes[x] + self.getResult().get(x, 0))//2
        #winning party is the one with the most votes
        projectedWinner = max(votes.items(), key=operator.itemgetter(1))[0]
        return newVotes, projectedWinner

    def euReferendum(self):
        with open('mainApp/static/csv/euReferendum.csv', 'r') as infile:
            reader = csv.reader(infile)
            #filters to ensure only the data for an individual constituency is considered
            #could use a different "match" method but this does the job
            filtered = filter(lambda p: self.id == p[0], reader)
            for rows in filtered:
                leave = round(float(rows[2]), 2)
                remain = 1 - leave
        return [remain, leave]

    def totalVotes(self):
        #gets the total of votes using another method
        return sum(getResult(self).values())

    def getResult(self):
        #opens results of 2017 election
        with open('mainApp/results.csv', 'r') as infile:
            reader = csv.reader(infile)
            #filters to get the constituency object
            filtered = filter(lambda p: self.id == p[10], reader)
            parties = {}
            for rows in filtered:
                #gets individual party results
                parties[Party.objects.get(shortname=rows[2])] = int(rows[4])
        return parties

    def getCensus(self):
        with open('mainApp/static/csv/census.csv', 'r') as infile:
            reader = csv.reader(infile)
            filtered = filter(lambda p: self.name == p[0], reader) #filters dataset so only one seat is iterated through
            census = {'Sex': {}, 'Social Grade': {}, 'Age': {}} #2d dictionary to show census data
            for row in filtered:
                #checks sex
                if row[2] in census['Sex']:
                    census['Sex'][row[2]] += int(row[6])
                else:
                    census['Sex'][row[2]] = int(row[6])
                    
                #checks social grade
                if row[3] in census['Social Grade']:
                    census['Social Grade'][row[3]] += int(row[6])
                else:
                    census['Social Grade'][row[3]] = int(row[6])
                    
                #checks age group
                if row[5] in census['Age']:
                    census['Age'][row[5]] += int(row[6])
                else:
                    census['Age'][row[5]] = int(row[6])
                
        return census
        

    def __str__(self):
        return self.name

class Region(models.Model):
    #an object will be created for every region in the country
    id = models.AutoField(primaryKey=True)
    name = models.CharField(maxLength=100, unique=True)
    widerRegion = models.CharField(maxLength=100, null=True, blank=True)

    def getResult(self):
        #opens results fo 2017 election
        with open('mainApp/results.csv', 'r') as infile:
            reader = csv.reader(infile)
            #filters so one party is considered at a time
            filtered = filter(lambda p: self.name == p[1], reader)
            parties = {}
            for row in filtered:
                #checks if the party being checked has already been added to the dictionary
                if Party.objects.get(shortname=row[2]) in parties:
                    #if it has been added already, add to the existing value of votes in the region
                    parties[Party.objects.get(shortname=row[2])][0] += int(row[4])
                    if Party.objects.get(shortname=row[2]) == Constituency.objects.get(name=row[0]).incumbent:
                        #if the party won a seat, add a seat for them in the region
                        parties[Party.objects.get(shortname=row[2])][1] += 1
                else:
                    #if the party has not been already added, add their vote total to the parties dictionary
                    parties[Party.objects.get(shortname=row[2])] = [0, 0]
                    parties[Party.objects.get(shortname=row[2])][0] += int(row[4])
        return parties    
    
    def totalVotes(self):
        #complicated zip calculation, but the idea is that a summation of all party votes must be made
        #I made this convoluted because over-reliance on the getResult() method could slow runtime significantly
        return sum([sum(i) for i in zip(*(self.getResult().values()))])
    
    def __str__(self):
        return self.name
    
class Party(models.Model):
    id = models.AutoField(primaryKey=True)
    name = models.CharField(maxLength=100)
    rawName = models.CharField(editable=False, maxLength=300)
    fullname = models.CharField(maxLength=100)
    shortname = models.CharField(maxLength=6)
    leader = models.CharField(maxLength=100)
    hexColour = models.CharField(maxLength=7)
    
    def totalPartyVotes(self):
        proj = pd.readExcel(r'mainApp\static\polls\globalProjection.xlsx')
        proj.drop(columns=["Constituency"])
        #Total sum per column
        proj.loc['Total',:]= proj.sum(axis=0)

        #Total sum per row: 
        proj.loc[:,'Total'] = proj.sum(axis=1)
        
        #returns percentage of total vote in global prediction
        return round(proj.loc['Total', self.name]/proj.loc['Total', 'Total'] * 100,1)

    def numberOfSeats(self):
        return Constituency.objects.filter(incumbent=self).count()
        
    def Str__(self):
        return self.name

class Poll(models.Model):
    id = models.AutoField(primaryKey=True)
    date = models.DateField()
    sampleSize = models.IntegerField()
    pollster = models.CharField(maxLength=100)

    def Str__(self):
        return self.pollster + str(self.date)


    
class Prediction(models.Model):
    id = models.AutoField(primaryKey=True)
    user = models.ForeignKey(User, onDelete=models.SETNULL, null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    
    def Str__(self):
        return str(self.date.strftime("%d %b %Y, %H:%M:%S")) + " (" + str(self.user.username) + ")" 

class PartyPrediction(models.Model):
    id = models.AutoField(primaryKey=True)
    prediction = models.ForeignKey(Prediction, onDelete=models.SETNULL, null=True)
    party = models.ForeignKey(Party, onDelete=models.SETNULL, null=True, blank=True)
    voteShare = models.DecimalField(maxDigits=4, decimalPlaces=1)
    
    def Str__(self):
        return str(self.id) + self.party.name
