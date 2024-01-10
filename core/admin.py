from django.contrib import admin
from .models import Team, ConceptImage


class CoreAdmin(admin.ModelAdmin):
    search_fields = ["id"]


# Register your models here.
admin.site.register(Team)
admin.site.register(ConceptImage)
