from django.contrib import admin
from .models import RankedProduct, VotingSession

# Register your models here.

admin.site.register(RankedProduct)
admin.site.register(VotingSession)
