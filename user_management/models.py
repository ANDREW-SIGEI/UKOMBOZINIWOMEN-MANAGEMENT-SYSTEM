from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class FieldOfficer(models.Model):
    """Field officers who collect data and work with members and groups."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, help_text="Format: +254XXXXXXXXX")
    id_number = models.CharField(max_length=20, unique=True)
    location = models.CharField(max_length=100)
    assigned_area = models.CharField(max_length=100)
    date_joined = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.assigned_area}"


class Member(models.Model):
    """Individual members of the UkomboziniWomen system."""
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    id_number = models.CharField(max_length=20, unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=15, help_text="Format: +254XXXXXXXXX")
    email = models.EmailField(blank=True, null=True)
    physical_address = models.CharField(max_length=100)
    registration_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    # Member metadata
    profile_photo = models.ImageField(upload_to='members/photos/', blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    next_of_kin_name = models.CharField(max_length=100, blank=True, null=True)
    next_of_kin_phone = models.CharField(max_length=15, blank=True, null=True)
    next_of_kin_relation = models.CharField(max_length=50, blank=True, null=True)
    
    # Field officer who registered/manages this member
    field_officer = models.ForeignKey(FieldOfficer, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.id_number}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_age(self):
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


class Group(models.Model):
    """Groups of members for collective savings and loans."""
    name = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=50, unique=True)
    formation_date = models.DateField()
    meeting_schedule = models.CharField(max_length=100, help_text="E.g., 'Every Monday at 2pm'")
    meeting_location = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # Group officials
    chairperson = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, related_name='chairperson_of')
    secretary = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, related_name='secretary_of')
    treasurer = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, related_name='treasurer_of')
    
    # Field officer assigned to this group
    field_officer = models.ForeignKey(FieldOfficer, on_delete=models.SET_NULL, null=True)
    
    # Group members (many-to-many relationship)
    members = models.ManyToManyField(Member, through='GroupMembership')
    
    def __str__(self):
        return self.name
    
    def total_members(self):
        return self.members.count()


class GroupMembership(models.Model):
    """Association table for members and groups with additional attributes."""
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    join_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    exit_date = models.DateField(blank=True, null=True)
    exit_reason = models.TextField(blank=True, null=True)
    
    # Positions in the group
    POSITION_CHOICES = (
        ('MEMBER', 'Regular Member'),
        ('CHAIR', 'Chairperson'),
        ('SEC', 'Secretary'),
        ('TREAS', 'Treasurer'),
        ('VICE', 'Vice Chairperson'),
    )
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, default='MEMBER')
    
    class Meta:
        unique_together = ('member', 'group')
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.group.name} ({self.position})"
