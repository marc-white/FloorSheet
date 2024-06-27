# -*- coding: utf-8 -*-


from django.contrib import admin
from . import models

# Register your models here.

# admin.site.register(models.Team)
admin.site.register(models.Competition)
admin.site.register(models.Venue)

class DivisionAdmin(admin.ModelAdmin):
    model = models.Division
    filter_horizontal = ('teams',)
admin.site.register(models.Division, DivisionAdmin)

class PlayerInline(admin.TabularInline):
    model = models.Player


class TeamAdmin(admin.ModelAdmin):
    inlines = [
        PlayerInline,
    ]
admin.site.register(models.Team, TeamAdmin)
