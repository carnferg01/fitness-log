# forms.py
from django import forms
from .models import Gear, Sport, HRzones

class GearForm(forms.ModelForm):
    class Meta:
        model = Gear
        fields = ['type', 'brand', 'model', 'nickname', 'retired']

class SportForm(forms.ModelForm):
    class Meta:
        model = Sport
        fields = ['name', 'colour', 'impact']

class HRzonesForm(forms.ModelForm):
    class Meta:
        model = HRzones
        fields = ['timestamp', 'zones', 'zone_multipliers']
