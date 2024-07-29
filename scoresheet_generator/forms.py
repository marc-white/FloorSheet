from django import forms
from . import models
from django.contrib.admin.widgets import AdminSplitDateTime

# from datetimewidget.widgets import DateTimeWidget


class TeamColorChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "{} ({})".format(obj.team_name, obj.color)


class ScoresheetGeneratorForm(forms.Form):

    # Define form fields
    comp = forms.ModelChoiceField(
        queryset=models.Division.objects.filter(active=True),
        # initial=models.Competition.objects.first(),
        required=False,
        label="Competition",
    )
    start_time = forms.SplitDateTimeField(
        required=True,
        widget=forms.SplitDateTimeWidget(
            date_attrs={
                "class": "datepicker",
            },
            time_attrs={
                "class": "timepicker",
            },
        ),
    )
    venue = forms.ModelChoiceField(
        queryset=models.Venue.objects.all(),
        # initial=models.Venue.objects.first(),
        required=False,
    )
    match_id = forms.CharField(max_length=30, required=False, label="Match ID")

    home_team = TeamColorChoiceField(
        queryset=models.Team.objects.all(), required=True, initial=None
    )
    away_team = TeamColorChoiceField(
        queryset=models.Team.objects.all(), required=True, initial=None
    )
    duty_team = TeamColorChoiceField(
        queryset=models.Team.objects.all(),
        required=False,
        initial=None,
        help_text="Define if a team is " "assigned to duty",
    )
