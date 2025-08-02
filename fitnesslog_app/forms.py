# forms.py
from django import forms
import pytz
from .models import ActivityViewModel, Gear, Sport, HRzones, Activity, Injury, Illness
from django.utils.safestring import mark_safe
from django.forms import ChoiceField
from django.forms.models import fields_for_model

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
    required_fields = ['sport', 'start_timezone', 'elapsed_time', 'moving_time']

    sport = forms.ModelChoiceField(
        queryset=Sport.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    #start_datetime_local = forms.DateTimeField(label="Start datetime (in local time)")

    def __init__(self, *args, **kwargs):
        # Get auto
        self.auto = kwargs.pop('activity_auto', None)
        # convert json->object

        super().__init__(*args, **kwargs)

        # if self.instance and self.instance.start_datetime_utc and self.instance.start_timezone:
        #     tz = pytz.timezone(self.instance.start_timezone)
        #     # Convert UTC datetime to stored timezone for display in form field
        #     local_dt = self.instance.start_datetime_utc.astimezone(tz).replace(tzinfo=None)
        #     self.fields['start_datetime_local'].initial = local_dt
        #     self.fields['start_timezone'].initial = self.instance.start_timezone

        if self.auto:
            # For each field
            for field_name, field in self.fields.items():
                widget = field.widget

                # Set placeholder if widget supports it and value exists
                if isinstance(widget, (forms.TextInput, forms.Textarea, forms.NumberInput, forms.DateTimeInput)):
                    value = getattr(self.auto, field_name, None)
                    if value is not None:
                        widget.attrs['placeholder'] = str(value)

                if isinstance(field, forms.ModelChoiceField):
                    auto_value = getattr(self.auto, field_name, None)
                    if auto_value:
                        # Set placeholder
                        field.empty_label = f"{auto_value} (From file)"
                    #else:
                        # Fallback
                    #    field.empty_label = "Select an option"
                # # Custom empty label for sport
                if field_name == 'sport': #isinstance(field, ChoiceField):
                    if getattr(self.auto, field_name, None):
                        # has auto value
                        field.required = False
                    else:
                        # don't have auto value
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

        # local_dt = cleaned_data.get('start_datetime_local')
        # tz_name = cleaned_data.get('start_timezone')

        # if local_dt and tz_name:
        #     tz = pytz.timezone(tz_name)
        #     # Localize naive local datetime
        #     if local_dt.tzinfo is None:
        #         aware_local_dt = tz.localize(local_dt)
        #     else:
        #         aware_local_dt = local_dt.astimezone(tz)

        #     # Convert to UTC for storage
        #     cleaned_data['start_datetime_utc'] = aware_local_dt.astimezone(pytz.UTC)


        # Validate required fields presence
        errors = {}
        for field in self.required_fields:
            value = cleaned_data.get(field)
            auto_value = getattr(self.auto, field) if self.auto else None

            if not value and not auto_value:
                errors[field] = "Specify by file or enter manually."

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
            #'start_datetime',
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
            'calories',
            'gear'
        ]



class ActivityViewModelForm(forms.Form):
    def __init__(self, *args, vm=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.vm = vm

        field_names = [
            #'sport',
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
            'calories',
            #'gear'
        ]
        self.fields.update(fields_for_model(vm._activity, fields=field_names))

        # Add virtual fields manually
        self.fields['start_datetime'] = forms.DateTimeField(
            label='Start Time (local)',
            required=False
        )

        if vm and not self.is_bound:
            for name in self.fields:
                val = getattr(vm, name, None)
                if hasattr(val, 'all') and callable(val.all):
                    val = list(val.all())
                if val is None or val == '':
                    fallback = getattr(vm._auto, name, None) if vm._auto else None
                    if hasattr(fallback, 'all') and callable(fallback.all):
                        fallback = list(fallback.all())
                    val = fallback
                self.initial[name] = val

    # def clean_distance(self):
    #     val = self.cleaned_data.get('distance')
    #     auto_val = getattr(self.vm._auto, 'distance', None)
    #     if auto_val and val and val < 0.5 * auto_val:
    #         raise forms.ValidationError("Distance is unusually low compared to auto estimate.")
    #     return val

    def save(self):
        ### TODO: Make the following more efficent
        # Set start_timezone first if present
        if 'start_timezone' in self.cleaned_data:
            setattr(self.vm, 'start_timezone', self.cleaned_data['start_timezone'])
        # Then set start_datetime so it uses the updated timezone
        if 'start_datetime' in self.cleaned_data:
            setattr(self.vm, 'start_datetime', self.cleaned_data['start_datetime'])
    

        for name in self.fields:
            setattr(self.vm, name, self.cleaned_data[name])
        self.vm.save()
        return self.vm


class InjuryForm(forms.ModelForm):
    class Meta:
        model = Injury
        fields = ['title', 'start_datetime', 'location', 'side', 'notes', 'severity']

class IllnessForm(forms.ModelForm):
    class Meta:
        model = Illness
        fields = ['title', 'start_datetime', 'location', 'notes', 'severity']

class MydayForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True,
        label='Pick a date'
    )