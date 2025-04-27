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
    
    # Member number within the group (sequential number from 1 to n)
    member_number = models.PositiveIntegerField(default=0, help_text="Sequential number of member within the group")
    
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
        ordering = ['member_number']
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.group.name} (Member #{self.member_number})"
    
    def save(self, *args, **kwargs):
        # If no member number is assigned, get the next available number
        if self.member_number == 0:
            last_member = GroupMembership.objects.filter(group=self.group).order_by('-member_number').first()
            self.member_number = 1 if last_member is None else last_member.member_number + 1
        super().save(*args, **kwargs)


# Field Officer Report models
class FieldOfficerReport(models.Model):
    """Model to track field officer daily reports that matches the paper form"""
    # Basic report information
    date = models.DateField(default=timezone.now)
    po_name = models.CharField(max_length=100)
    
    # Group visit information
    group_names = models.TextField()
    visit_venue = models.CharField(max_length=200, blank=True, null=True)
    visit_time = models.CharField(max_length=50, blank=True, null=True)
    total_groups = models.IntegerField()
    total_attendees = models.IntegerField()
    
    # Administrative information
    admin_for_group = models.TextField()
    project_registration = models.TextField(blank=True, null=True)
    mem_reg = models.TextField(blank=True, null=True)
    
    # Financial information - Loans
    long_term_loan = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    short_term_loan = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    savings_before = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_loan_repaid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    loan_principle = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    loan_interest = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    short_term_loan_repaid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Financial information - Savings and other collections
    savings_this_month = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    welfare = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    project = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fines_and_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Legacy fields for backward compatibility
    group_loans = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    project_loans = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_money = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Report by {self.po_name} on {self.date}"
    
    def save(self, *args, **kwargs):
        # Calculate total savings
        self.total_savings = (
            self.savings_this_month + 
            self.welfare + 
            self.project + 
            self.fines_and_charges
        )
        
        # Calculate total money collected for backward compatibility
        self.total_money = (
            self.total_loan_repaid + 
            self.total_savings
        )
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-date']
        verbose_name = "Field Officer Report"
        verbose_name_plural = "Field Officer Reports"


# Loan models
class LoanType(models.Model):
    """Defines different types of loans that members can take"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Interest rate in percentage")
    repayment_period = models.PositiveIntegerField(help_text="Repayment period in months")
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.interest_rate}%)"


class Loan(models.Model):
    """Tracks loans given to members through their groups"""
    # Loan status choices
    STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('DISBURSED', 'Disbursed'),
        ('REPAYING', 'Repaying'),
        ('COMPLETED', 'Completed'),
        ('DEFAULTED', 'Defaulted'),
        ('REJECTED', 'Rejected'),
    )
    
    # Loan type (group loan, individual loan, project loan, etc.)
    loan_type = models.ForeignKey(LoanType, on_delete=models.PROTECT)
    
    # Member who received the loan
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='loans')
    
    # Group through which the loan was given (important for group-based lending)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='group_loans')
    
    # Group membership record (to track the member's number in the group)
    group_membership = models.ForeignKey(GroupMembership, on_delete=models.SET_NULL, null=True, blank=True, related_name='loans')
    
    # Financial details
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Interest rate in percentage")
    total_interest = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Principal + Interest")
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Loan timeline
    application_date = models.DateField(default=timezone.now)
    approval_date = models.DateField(null=True, blank=True)
    disbursement_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    
    # Loan status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Loan purpose and additional notes
    purpose = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-application_date']
    
    def __str__(self):
        return f"Loan #{self.id} - {self.member.get_full_name()} - {self.principal_amount}"
    
    def save(self, *args, **kwargs):
        # Calculate total amount with interest
        if self.principal_amount and self.interest_rate:
            self.total_interest = (self.principal_amount * self.interest_rate) / 100
            self.total_amount = self.principal_amount + self.total_interest
            
        # Calculate current balance
        self.balance = self.total_amount - self.amount_paid
        
        # Update status based on payment progress
        if self.status == 'DISBURSED' or self.status == 'REPAYING':
            if self.balance <= 0:
                self.status = 'COMPLETED'
                self.completion_date = timezone.now().date()
            else:
                self.status = 'REPAYING'
                
        super().save(*args, **kwargs)


class LoanRepayment(models.Model):
    """Tracks repayments made against loans"""
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='repayments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    principal_portion = models.DecimalField(max_digits=12, decimal_places=2)
    interest_portion = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    receipt_number = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Who recorded this payment
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Repayment #{self.id} - {self.loan} - {self.amount}"
    
    def save(self, *args, **kwargs):
        # Update the loan's paid amount and balance
        is_new = self.pk is None
        
        super().save(*args, **kwargs)
        
        if is_new:  # Only update loan on new payments to avoid double-counting
            loan = self.loan
            loan.amount_paid += self.amount
            loan.save()  # This will recalculate balance in the Loan.save() method
