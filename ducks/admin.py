from django.contrib import admin

from .models import Duck, DuckFact

# Register your models here.

admin.site.register(Duck)
admin.site.register(DuckFact)
