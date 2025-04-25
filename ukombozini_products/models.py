from django.db import models
from django.utils import timezone
from user_management.models import Member, Group, FieldOfficer


class FinancialProduct(models.Model):
    """Financial products offered by Ukombozini."""
    PRODUCT_TYPES = (
        ('LOAN', 'Loan Product'),
        ('SAVINGS', 'Savings Product'),
        ('INVESTMENT', 'Investment Product'),
        ('INSURANCE', 'Insurance Product'),
        ('OTHER', 'Other Product'),
    )
    
    name = models.CharField(max_length=100)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    terms_and_conditions = models.TextField()
    
    # Product availability
    launch_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    # Financial terms
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Annual interest rate in %")
    minimum_amount = models.DecimalField(max_digits=12, decimal_places=2)
    maximum_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Fees
    application_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Eligibility
    individual_eligible = models.BooleanField(default=True)
    group_eligible = models.BooleanField(default=True)
    minimum_membership_months = models.IntegerField(default=0, 
                                                   help_text="Minimum membership period in months")
    
    def __str__(self):
        return f"{self.name} ({self.get_product_type_display()})"


class GroupTopUpProject(models.Model):
    """Projects funded by group top-ups."""
    STATUS_CHOICES = (
        ('PROPOSED', 'Proposed'),
        ('APPROVED', 'Approved'),
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )
    
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    objective = models.TextField()
    
    # Project timeline
    proposal_date = models.DateField(default=timezone.now)
    approval_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    expected_end_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    
    # Financial details
    total_budget = models.DecimalField(max_digits=12, decimal_places=2)
    group_contribution = models.DecimalField(max_digits=12, decimal_places=2)
    ukombozini_contribution = models.DecimalField(max_digits=12, decimal_places=2)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PROPOSED')
    approved_by = models.CharField(max_length=100, blank=True, null=True)
    
    # Location and beneficiaries
    location = models.CharField(max_length=200)
    estimated_beneficiaries = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.title} - {self.group.name} - {self.status}"


class ProjectExpense(models.Model):
    """Expenses incurred for group top-up projects."""
    project = models.ForeignKey(GroupTopUpProject, on_delete=models.CASCADE, related_name='expenses')
    expense_date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    
    # Categories and details
    category = models.CharField(max_length=100)
    receipt_number = models.CharField(max_length=50, blank=True, null=True)
    vendor = models.CharField(max_length=100)
    
    # Approval and verification
    approved_by = models.CharField(max_length=100)
    verified_by = models.CharField(max_length=100, blank=True, null=True)
    
    # Attachments (would normally be file uploads)
    has_receipt = models.BooleanField(default=False)
    receipt_image = models.ImageField(upload_to='project_expenses/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.project.title} - {self.amount} - {self.expense_date}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update project total spent
        self.project.total_spent = ProjectExpense.objects.filter(project=self.project).aggregate(
            models.Sum('amount'))['amount__sum'] or 0
        self.project.save()


class IndividualProject(models.Model):
    """Individual projects funded by Ukombozini."""
    STATUS_CHOICES = (
        ('PROPOSED', 'Proposed'),
        ('APPROVED', 'Approved'),
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )
    
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    project_type = models.CharField(max_length=100)
    
    # Project timeline
    proposal_date = models.DateField(default=timezone.now)
    approval_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    expected_end_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    
    # Financial details
    total_budget = models.DecimalField(max_digits=12, decimal_places=2)
    member_contribution = models.DecimalField(max_digits=12, decimal_places=2)
    ukombozini_contribution = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PROPOSED')
    approved_by = models.CharField(max_length=100, blank=True, null=True)
    field_officer = models.ForeignKey(FieldOfficer, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Location and impact
    location = models.CharField(max_length=200)
    expected_impact = models.TextField()
    
    def __str__(self):
        return f"{self.title} - {self.member.get_full_name()} - {self.status}"


class ProductApplication(models.Model):
    """Applications for financial products."""
    STATUS_CHOICES = (
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    )
    
    product = models.ForeignKey(FinancialProduct, on_delete=models.CASCADE)
    application_date = models.DateField(default=timezone.now)
    
    # Applicant (either individual or group)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    
    # Application details
    amount_requested = models.DecimalField(max_digits=12, decimal_places=2)
    purpose = models.TextField()
    term_months = models.IntegerField(null=True, blank=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    reviewed_by = models.CharField(max_length=100, blank=True, null=True)
    review_date = models.DateField(null=True, blank=True)
    approved_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Field officer who assisted with the application
    field_officer = models.ForeignKey(FieldOfficer, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        applicant = self.member.get_full_name() if self.member else self.group.name
        return f"{applicant} - {self.product.name} - {self.amount_requested} - {self.status}"
