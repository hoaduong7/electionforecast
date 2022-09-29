from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from .models import Prediction, Party

class NewUserForm(UserCreationForm):
    #inherits from UserCreationForm superclass
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        #user needs to enter username, email and password confirmation
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleanedData["email"]
        #if the form is valid, create a new user
        if commit:
            user.save()
        return user

class PredictionForm(forms.Form):
    #vote share of an individual party prediction
    voteShare = forms.DecimalField(required=True, decimalPlaces = 1, minValue = 0.0, maxValue = 100.0, initial=0.0)
    