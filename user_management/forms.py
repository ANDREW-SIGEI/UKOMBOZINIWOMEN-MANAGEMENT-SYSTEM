from django import forms
from django.utils import timezone
from .models import Member, Group, GroupMembership, FieldOfficer


class MemberForm(forms.ModelForm):
    """Form for creating and editing members."""
    
    class Meta:
        model = Member
        fields = [
            'first_name', 'last_name', 'id_number', 'gender', 'date_of_birth', 
            'phone_number', 'email', 'physical_address', 'is_active',
            'profile_photo', 'occupation', 'next_of_kin_name', 
            'next_of_kin_phone', 'next_of_kin_relation', 'field_officer'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'physical_address': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'next_of_kin_name': forms.TextInput(attrs={'class': 'form-control'}),
            'next_of_kin_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'next_of_kin_relation': forms.TextInput(attrs={'class': 'form-control'}),
            'field_officer': forms.Select(attrs={'class': 'form-control select2'}),
        }
    
    def clean_date_of_birth(self):
        """Ensure member is at least 18 years old."""
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = timezone.now().date()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 18:
                raise forms.ValidationError("Member must be at least 18 years old.")
        return dob


class GroupForm(forms.ModelForm):
    """Form for creating and editing groups."""
    
    class Meta:
        model = Group
        fields = [
            'name', 'registration_number', 'formation_date', 'meeting_schedule',
            'meeting_location', 'description', 'is_active', 'chairperson',
            'secretary', 'treasurer', 'field_officer'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
            'formation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'meeting_schedule': forms.TextInput(attrs={'class': 'form-control'}),
            'meeting_location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'chairperson': forms.Select(attrs={'class': 'form-control select2'}),
            'secretary': forms.Select(attrs={'class': 'form-control select2'}),
            'treasurer': forms.Select(attrs={'class': 'form-control select2'}),
            'field_officer': forms.Select(attrs={'class': 'form-control select2'}),
        }


class GroupMembershipForm(forms.ModelForm):
    """Form for adding members to a group."""
    
    class Meta:
        model = GroupMembership
        fields = ['member', 'position', 'is_active']
        widgets = {
            'member': forms.Select(attrs={'class': 'form-control select2'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BulkMemberAddForm(forms.Form):
    """Form for adding multiple members to a group."""
    
    members = forms.ModelMultipleChoiceField(
        queryset=Member.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        required=True
    )
    position = forms.ChoiceField(
        choices=GroupMembership.POSITION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='MEMBER'
    ) 