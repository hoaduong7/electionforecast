from django.shortcuts import render
from main_app.models import Constituency, Party, Region, Prediction, PartyPrediction
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from datetime import datetime
import operator
from decimal import Decimal
import csv
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import logout, authenticate, login
from django.forms import BaseFormSet
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from .forms import NewUserForm, PredictionForm
from django.forms import formset_factory
from django.contrib import messages
from django.contrib.auth.models import User
# Create your views here.



def return_map(input_data, name, col):
    #creates color map of all the parties
    color_map = colors.ListedColormap(["#0087DC","#6AB023","#DDDDDD","#FAA61A","#DC241f","#008142","#FDF38E"], name='from_list', N=None)
    
    #reads in map file
    map_df = gpd.read_file(r"main_app/static/maps/Westminster_Parliamentary_Constituencies__December_2017__Boundaries_UK.shp")

    #merges map with previous election data    
    election_data = map_df.set_index("pcon17nm").join(input_data.set_index("Constituency")).reset_index()
    
    #plots map
    f, ax = plt.subplots(1, figsize=(20, 20))
    election_data.plot(column=col, cmap=color_map, categorical=True, 
    edgecolor="black", linewidth=0.15,
    legend=True, ax=ax)
    #turns off axis
    ax.set_axis_off()
    
    #saves map as jpg image
    plt.savefig('main_app/static/images/' + name + '.jpg')

def get_megapoll():
    #returns megapoll pandas data frame
    return pd.read_csv(r"main_app\static\polls\megapoll.csv")

def update_prediction(request):
    #reads in census as Pandas data frame
    census_df = pd.read_csv(r"main_app\static\csv\census.csv")
    
    #instantiates empty dictionary using lambda calculus
    #default is that every party is assigned 0 seats
    seats = {party: 0 for party in Party.objects.all()}
    
    #merge dictionaries while preserving order - mainly for the dict headers.
    field_dict = {**{"Constituency": None}, **seats}
    
    #opens projection csv file to write prediction to
    #if it does not exist, it will create one in the target directory
    with open(r'main_app\static\polls\global_projection.csv', 'w') as f:
    
        #writes header of CSV
        w = csv.DictWriter(f, field_dict.keys())
        w.writeheader()
        
        #iterates through all constituencies
        for constituency in Constituency.objects.all():
        
            #uses Constituency method to obtain localised prediction
            projection = constituency.prediction(census_df)[0]
            #appends projection to CSV file
            votes = projection
            w.writerow({**{'Constituency': constituency}, **votes})
    
    #renders the request and deploys the update_prediction placeholder template
    return render(request, "update_prediction.html", {'seats' : seats})

    
    
def prediction(request):
    #creates list of all parties
    parties = [party for party in Party.objects.all()]
    
    #creates dictionary of party seats
    #when empty, parties default as having 0 seats
    seats = {party: 0 for party in Party.objects.all()}
    
    #empty list of results - will be populated with constituencies
    results = []
    
    #opens projection to read
    with open(r'main_app\static\polls\global_projection.csv', 'r') as f:
        #sorts results by constituency, and reads in as a dictionary
        results_reader = sorted(csv.DictReader(f), key=lambda d: d['Constituency'])
        
        #iterates through each row - a single constituency predicted result
        for row in results_reader:
            
            #holds the constituency name, which will be needed in order to service later GET request
            constituency = row["Constituency"]
            
            #new list created with each element holding a party vote share total
            newlist = [constituency] + [int(x) for x in list(row.values())[1:] if (x != '')]
            
            #obtains the index of the highest value in the list
            #sets the party with that index as winner
            #increments the dictionary for party
            max_index = newlist.index(max(newlist[1:])) - 1
            winner = parties[max_index]
            seats[winner] += 1
            
            #replaces string value of constituency with object
            newlist[0] = Constituency.objects.get(name=newlist[0])
            
            #appends list to master results list
            results.append(newlist)
    
    #services HTTP request for prediction, returning context dictionary to templates
    return render(request, "prediction.html", {'results': results, 'parties': parties, 'seats': seats})


def index(request):
    #creates ordered query set of all constituencies and all parties
    constituencies = Constituency.objects.all().order_by('name')
    parties = Party.objects.all()
    
    #creates map on index page
    results_data = pd.read_csv(r"main_app\results.csv") #reads in last election's data
    #conditions = results_data["Winner"].isnull() == False #applies not null condition
    #filtered = results_data[conditions]
    #return_map(filtered, 'index-map', 'Winner') #creates index-map.jpg file
    
    #services HTTP request for index, with context dictionary returned to temolate
    return render(request, "index.html", {'constituencies': constituencies, 'parties': parties})

def constituency(request, id, raw_name):
    #reads in census as Pandas data frame
    census_df = pd.read_csv(r"main_app\static\csv\census.csv")
    
    #uses raw_name parameter derived from URL and gets relevant constituency object
    constituency = Constituency.objects.get(raw_name=raw_name)
    
    #uses Constituency public methods and returns results
    getResults = Constituency.get_result(constituency)
    getCensus = Constituency.get_census(constituency)
    population = sum(getCensus["Sex"].values())
    totalVotes = sum(getResults.values())
    euref = Constituency.eu_referendum(constituency)
    
    #gets prediction - element 0 of tuple is dict of votes, element 1 is the winning party
    prediction = Constituency.prediction(constituency, census_df)[0]
    projected_winner = Constituency.prediction(constituency, census_df)[1]
    
    #services HTTP request for an individual constituency page, returning context dictionary
    return render(request, "constituency.html", {'constituency': constituency, 'population': population, 'totalVotes': totalVotes, 'getResults': getResults, 'getCensus': getCensus, 'euref': euref, 'prediction': prediction, 'projected_winner': projected_winner})

def party(request, id, name):
    #uses id parameter to get party object
    party = Party.objects.get(id=id)
    
    #filters all constituency objects to find where the party won in last election
    constituencies = Constituency.objects.filter(incumbent=party)
    
    #services HTTP request for an individual party page, returning context dictionary
    return render(request, "party.html", {'party': party, 'constituencies': constituencies})

def region(request, id):
    #uses id parameter to get region object
    region = Region.objects.get(id=id)
    
    #returns query set of all party objects and constituency objects, filtered by region
    parties = Party.objects.all()
    constituencies = Constituency.objects.filter(region=region)

    #services HTTP request for an individual party page, returning context dictionary
    return render(request, "region.html", {'region': region, 'parties': parties, 'constituencies': constituencies})

def signup(request):
    #checks if POST request has been sent to the server
    if request.method == "POST":
        #contents of new user form put into form variable
        form = NewUserForm(request.POST)
        
        #if the form matches the validation criteria
        if form.is_valid():
            #put user into database
            user = form.save()
            username = form.cleaned_data.get('username')
            
            #displays message of success on screen
            messages.success(request, f"New account created: {username}")
            
            #automatically authenticates new user
            login(request, user)
            return redirect("/tutorial") #redirects user to tutorial after signing up

        else:
            #highlights error if there is one to the user
            for msg in form.error_messages:
                #displays on screen
                messages.error(request, f"{msg}: {form.error_messages[msg]}")

            return render(request = request,
                          template_name = "signup.html",
                          context={"form":form})

    form = NewUserForm
    return render(request = request,
                  template_name = "signup.html",
                  context={"form":form})
                  
def logout_request(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("/")
    
def login_request(request):
    #automatically logs out if viewing login form
    logout(request)
    
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        
        #checks that username and password match hashes
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                #redirects to home page and message displayed of success
                messages.info(request, f"You are now logged in as {username}")
                return redirect('/')
            else:
                #shows invalid message on screen
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request = request,
                    template_name = "login.html",
                    context={"form":form})
                    


def get_user_profile(request, username):
    #get user object
    user = User.objects.get(username=username)
    
    #get list of predictions
    predictions = Prediction.objects.filter(user=user)
    party_predictions = []
    
    #get dictionaries of party predictions within each prediction
    for i in enumerate(predictions):
        party_predictions += PartyPrediction.objects.filter(prediction=i[1])
    return render(request, 'user_profile.html', {"user":user, "predictions": predictions, "party_predictions": party_predictions})

class BasePredictionFormSet(BaseFormSet):
    #validator
    def clean(self):
        #if the form itself has errors then no point processing it
        if any(self.errors):
            return
        #set total variable as 0
        total = 0
        for form in self.forms:
            #get vote share from form
            vote_share = form.cleaned_data.get("vote_share")
            #add vote share to total
            total += vote_share
            #total must not exceed 100%
            if total > 100:
                raise ValidationError("Vote shares must total maximum of 100%")
    
def new_prediction(request):
    #gets all parties in query set
    parties = Party.objects.all().exclude(name="Undecided").exclude(name="Refused")
    num_parties = parties.count()
    
    
    #generates prediction form set
    PredictionFormSet = formset_factory(form=PredictionForm, formset=BasePredictionFormSet,
                                    max_num=num_parties, validate_max=True,
                                    min_num=num_parties, validate_min=True)
    #parties configured
    initial = [{'party': [p, str(p.total_party_votes())+"%"]} for p in parties]
    if request.method == 'POST':
        #generate form set
        formset = PredictionFormSet(request.POST, initial=initial)
        if formset.is_valid():
            #create overall prediction
            pred = Prediction()
            pred.date = datetime.utcnow()
            pred.user = request.user
            pred.save()
            total_shares = 0
            for form in formset:
                #create dictionary of {party: votes}
                party = form.initial['party']
                form.cleaned_data[party[0]] = form.cleaned_data.pop("vote_share")
                vote_share = form.cleaned_data[party[0]]
                total_shares += vote_share
                
                #instantiate new party prediction with fields filled correctly.
                obj = PartyPrediction.objects.create(prediction= Prediction.objects.get(id=pred.id), party=party[0], vote_share=vote_share)
            undecideds = PartyPrediction.objects.create(prediction= Prediction.objects.get(id=pred.id), party=Party.objects.get(name="Undecided"), vote_share=Decimal(Decimal(100.0)-total_shares))
            
            refused = PartyPrediction.objects.create(prediction= Prediction.objects.get(id=pred.id), party=Party.objects.get(name="Refused"), vote_share=Decimal(0))

            #returns user to user profile
            return redirect('/user/' + request.user.username)
    else:
        #if invalid input, try again
        formset = PredictionFormSet(initial=initial)
        
    return render(request, 'new_prediction.html', {'parties': parties, 'formset': formset})

def prediction_splash(request, id):
    #get relevant objects
    prediction = Prediction.objects.get(id=id)
    party_predictions = PartyPrediction.objects.filter(prediction=prediction)
    
    #sets party votes as default
    party_votes = {p: [p.total_party_votes(), 0] for p in Party.objects.all()}
    #multipliers represents the proportional increase/decrease of votes in each constituency based on prediction
    multipliers = {}
    
    #gets global prediction
    base_case = pd.read_excel(r'main_app\static\polls\global_projection.xlsx')

    for p in party_predictions:
        party_votes[p.party][1] = float(p.vote_share)
        #prevents division by zero
        multipliers[p.party] = party_votes[p.party][1]/(party_votes[p.party][0]+0.00001)
        
        #multiplies constituency totals by multiplier
        base_case.loc[:, p.party.name] *= multipliers[p.party]
        #integer to reflect that people are whole numbers
        base_case[p.party.name] = base_case[p.party.name].round(0).astype(int)

    #rename columns to link to objects
    base_case.columns = ["Constituency"] + [r"<a style='color: " + p.party.hex_colour + "' href='/party/" + str(p.party.id) + "/" + p.party.raw_name + "'>" + p.party.name + "</a>" for p in party_predictions]
    #drop undecideds and refused votes
    base_case = base_case.drop(columns=[r"<a style='color: grey' href='/party/13/'>Undecided</a>", r"<a style='color: grey' href='/party/14/'>Refused</a>"])
    
    #get winner in constituency
    results = base_case.copy()
    base_case["Winner"] = base_case.loc[:, base_case.columns != 'Constituency'].idxmax(axis=1)
    results.columns = ["Constituency"] + [p.party for p in party_predictions][:-2]
    results["Winner"] = results.loc[:, results.columns != 'Constituency'].idxmax(axis=1)
    
    #gets map
    results_new = results.copy()
    results_new["Winner"] = results_new["Winner"].astype(str)
    return_map(results_new, str(id), 'Winner')
    
    for p in party_predictions:
        #count number of seats per party
        p.seats = results.loc[results.Winner == p.party, 'Winner'].count()
        #change since 2017 incumbents
        p.change = p.seats - len(Constituency.objects.filter(incumbent=p.party))
    return render(request,  'prediction_splash.html', {"prediction": prediction, "id": str(id), "party_predictions": party_predictions, 'results': base_case.to_html(index=False, escape=False, classes="table")})

def tutorial(request):
    return render(request, 'faq.html', {})