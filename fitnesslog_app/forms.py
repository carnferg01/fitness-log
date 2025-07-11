# forms.py
from django import forms
from .models import Gear, Sport, HRzones, Activity, Injury, Illness
from django.utils.safestring import mark_safe
from django.forms import ChoiceField

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
    required_fields = ['sport', 'start_datetime', 'start_timezone', 'elapsed_time', 'moving_time']

    sport = forms.ModelChoiceField(
        queryset=Sport.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    def __init__(self, *args, **kwargs):
        # Get auto
        self.auto = kwargs.pop('activity_auto', None)
        # convert json->object

        super().__init__(*args, **kwargs)

        if self.auto:
            # For each field
            for field_name, field in self.fields.items():
                widget = field.widget

                # Set placeholder if widget supports it and value exists
                if isinstance(widget, (forms.TextInput, forms.Textarea, forms.NumberInput, forms.DateTimeInput)):
                    value = getattr(self.auto, field_name, None)
                    if value is not None:
                        widget.attrs['placeholder'] = str(value)

                # Custom empty label for sport
                if isinstance(field, ChoiceField):
                    auto_value = getattr(self.auto, field_name, None)
                    if auto_value:
                        # Show default option label from file
                        field.empty_label = f"{auto_value} (File default)"
                        field.required = False
                    else:
                        field.empty_label = "---------"
                        field.required = True


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

        for field_name in self.required_fields:
            if field_name in self.fields:
                label = self.fields[field_name].label or field_name.replace('_', ' ').capitalize()
                self.fields[field_name].label = mark_safe(f"{label} <span class='text-danger'>*</span>")
        
    def clean(self):
        cleaned_data = super().clean()
        errors = {}
        for field in self.required_fields:
            value = cleaned_data.get(field)
            auto_value = getattr(self.auto, field) if self.auto else None

            if not value and not auto_value:
                errors[field] = f" Specify by file or enter manually."

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