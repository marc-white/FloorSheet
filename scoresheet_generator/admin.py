# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from . import models

# Register your models here.

# admin.site.register(models.Team)
admin.site.register(models.Competition)
admin.site.register(models.Division)
admin.site.register(models.Venue)


class PlayerInline(admin.TabularInline):
    model = models.Player


class TeamAdmin(admin.ModelAdmin):
    inlines = [
        PlayerInline,
    ]
admin.site.register(models.Team, TeamAdmin)
