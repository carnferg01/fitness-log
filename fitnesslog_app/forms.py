# forms.py
from django import forms
from .models import Gear, Sport, HRzones, Activity, Injury, Illness
from django.core.exceptions import ValidationError

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
    sport = forms.ModelChoiceField(
        queryset=Sport.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    def __init__(self, *args, **kwargs):
        placeholder_obj = kwargs.pop('placeholder_data', None)
        self.file_default_sport = placeholder_obj.sport if placeholder_obj else None
        super().__init__(*args, **kwargs)

        # Apply Bootstrap class to all appropriate widgets
        for field_name, field in self.fields.items():
            widget = field.widget
            # Skip certain widgets that shouldn't have form-control
            if not isinstance(widget, (forms.CheckboxInput, forms.ClearableFileInput)):
                existing_classes = widget.attrs.get('class', '')
                classes = existing_classes.split()
                if 'form-control' not in classes:
                    classes.append('form-control')
                widget.attrs['class'] = ' '.join(classes)

        if self.file_default_sport:
            self.fields['sport'].empty_label = f"{self.file_default_sport.name} (File default)"
            self.fields['sport'].required = False
        else:
            self.fields['sport'].empty_label = "Select a sport"
            self.fields['sport'].required = True


    def clean(self):
        cleaned_data = super().clean()

        fields_to_check = ['start_datetime', 'start_timezone', 'elapsed_time', 'moving_time']
        errors = {}

        auto = getattr(self.instance, 'auto', None)

        for field in fields_to_check:
            value = cleaned_data.get(field)
            auto_value = getattr(auto, field, None) if auto else None

            if not value and not auto_value:
                errors[field] = f"Either '{field}' or 'auto.{field}' must be provided."

        for field, message in errors.items():
            self.add_error(field, message)

        return cleaned_data



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