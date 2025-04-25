from django import forms
from .models import Meeting
from user_management.models import Member, Group, FieldOfficer

class MeetingForm(forms.ModelForm):
    """Form for creating and editing meetings."""
    
    # Additional fields not directly on the model
    members = forms.ModelMultipleChoiceField(
        queryset=Member.objects.filter(is_active=True),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    
    field_officers = forms.ModelMultipleChoiceField(
        queryset=FieldOfficer.objects.filter(is_active=True),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    
    attendees = forms.ModelMultipleChoiceField(
        queryset=Member.objects.filter(is_active=True),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    
    group = forms.ModelChoiceField(
        queryset=Group.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Meeting
        fields = [
            'title', 'description', 'meeting_type', 'status', 
            'location', 'scheduled_date', 'start_time', 'end_time',
            'recurrence', 'agenda', 'minutes'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'meeting_type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'recurrence': forms.Select(attrs={'class': 'form-control'}),
            'agenda': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'minutes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        } 