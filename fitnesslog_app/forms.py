# forms.py
from django import forms
from .models import Gear, Sport, HRzones, Activity, Injury, Illness

class GearForm(forms.ModelForm):
    class Meta:
        model = Gear
        fields = ['type', 'brand', 'model', 'nickname', 'retired']

class SportForm(forms.ModelForm):
    class Meta:
        model = Sport
        fields = ['name', 'colour', 'impact']
        widgets = {
            'colour': forms.TextInput(attrs={'type': 'color'}),
        }

class HRzonesForm(forms.ModelForm):
    zones = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 1}),  # or forms.TextInput if you prefer
        initial='[]',
        #help_text='e.g. [110, 132, 148, 159, 168]'
    )
    zone_multipliers = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 1}),  # or forms.TextInput if you prefer
        initial='[]',
        #help_text='e.g. [0.6, 1, 1.5, 2, 4, 8]'
    )

    class Meta:
        model = HRzones
        fields = ['timestamp', 'zones', 'zone_multipliers']
        widgets = {
            'timestamp': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = [
            'sport',
            'activity_type',
            'location',
            'intensity',
            'feeling',
            'terrain',
            'start_datetime',
            'start_timezone',
            'elapsed_time',
            'tracked_time',
            'moving_time',
            'distance',
            'elevation_gain',
            'elevation_loss',
            'elevation_max',
            'elevation_min',
            'time_at_HR',
            'time_at_pace',
            'calories'
        ]

class InjuryForm(forms.ModelForm):
    class Meta:
        model = Injury
        fields = ['title', 'start_datetime', 'location', 'side', 'notes', 'severity']

class IllnessForm(forms.ModelForm):
    class Meta:
        model = Illness
        fields = ['title', 'start_datetime', 'location', 'notes', 'severity']