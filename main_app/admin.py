from django.contrib import admin

from .models import Region, Constituency, Party, Poll, Prediction, PartyPrediction

admin.site.register(Region)
admin.site.register(Constituency)
admin.site.register(Party)
admin.site.register(Prediction)
admin.site.register(PartyPrediction)
