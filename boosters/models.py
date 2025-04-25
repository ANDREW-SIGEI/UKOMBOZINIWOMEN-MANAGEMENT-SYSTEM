from django.db import models
from django.utils import timezone
from user_management.models import Member, Group, FieldOfficer


class BoosterCategory(models.Model):
    """Categories for booster collections (e.g., Agriculture, School Fees)."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Booster Categories"


class AgricultureProduct(models.Model):
    """Types of agricultural products tracked in the system."""
    name = models.CharField(max_length=100)
    unit_of_measure = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    current_market_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_last_updated = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.unit_of_measure})"


class AgricultureCollection(models.Model):
    """Records of agricultural produce collected from members."""
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    product = models.ForeignKey(AgricultureProduct, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_value = models.DecimalField(max_digits=12, decimal_places=2)
    collection_date = models.DateField(default=timezone.now)
    
    # Location and quality details
    collection_location = models.CharField(max_length=100)
    quality_grade = models.CharField(max_length=20, blank=True, null=True)
    
    # Officer who collected the produce
    collected_by = models.ForeignKey(FieldOfficer, on_delete=models.SET_NULL, null=True)
    
    # Receipt and payment info
    receipt_number = models.CharField(max_length=50, unique=True)
    payment_status = models.CharField(max_length=20, choices=(
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Fully Paid'),
    ), default='PENDING')
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    # Metadata for offline collections
    is_synced = models.BooleanField(default=True)
    offline_created_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.product.name} - {self.quantity} {self.product.unit_of_measure}"
    
    def save(self, *args, **kwargs):
        # Calculate total value if not set
        if not self.total_value:
            self.total_value = self.quantity * self.unit_price
            
        super().save(*args, **kwargs)


class SchoolFeesCollection(models.Model):
    """Records of school fees collected from members."""
    EDUCATION_LEVEL_CHOICES = (
        ('PRIMARY', 'Primary School'),
        ('SECONDARY', 'Secondary School'),
        ('COLLEGE', 'College'),
        ('UNIVERSITY', 'University'),
        ('OTHER', 'Other'),
    )
    
    TERM_CHOICES = (
        ('TERM1', 'Term 1'),
        ('TERM2', 'Term 2'),
        ('TERM3', 'Term 3'),
        ('SEMESTER1', 'Semester 1'),
        ('SEMESTER2', 'Semester 2'),
        ('YEARLY', 'Full Year'),
        ('OTHER', 'Other'),
    )
    
    # Member making the payment
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    
    # Student details
    student_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=50, blank=True, null=True)
    relation_to_member = models.CharField(max_length=50)
    
    # School and education details
    school_name = models.CharField(max_length=100)
    education_level = models.CharField(max_length=20, choices=EDUCATION_LEVEL_CHOICES)
    academic_year = models.CharField(max_length=20)
    term = models.CharField(max_length=20, choices=TERM_CHOICES)
    
    # Payment details
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    collection_date = models.DateField(default=timezone.now)
    receipt_number = models.CharField(max_length=50, unique=True)
    payment_method = models.CharField(max_length=50)
    
    # Officer who collected the fees
    collected_by = models.ForeignKey(FieldOfficer, on_delete=models.SET_NULL, null=True)
    
    # Status and notes
    is_complete_payment = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    
    # Metadata for offline collections
    is_synced = models.BooleanField(default=True)
    offline_created_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student_name} - {self.school_name} - {self.amount}"


class BoosterPayment(models.Model):
    """Payments made to members for agriculture collections or other booster programs."""
    PAYMENT_TYPES = (
        ('AGRICULTURE', 'Agriculture Collection Payment'),
        ('SCHOOL_FEES', 'School Fees Reimbursement'),
        ('OTHER', 'Other Booster Payment'),
    )
    
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    
    # References to linked collections
    agriculture_collection = models.ForeignKey(AgricultureCollection, on_delete=models.SET_NULL,
                                             null=True, blank=True)
    school_fees_collection = models.ForeignKey(SchoolFeesCollection, on_delete=models.SET_NULL,
                                             null=True, blank=True)
    
    # Payment details
    payment_method = models.CharField(max_length=50)
    reference_number = models.CharField(max_length=50, unique=True)
    
    # Officer who processed the payment
    processed_by = models.ForeignKey(FieldOfficer, on_delete=models.SET_NULL, null=True)
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    # Metadata for offline payments
    is_synced = models.BooleanField(default=True)
    offline_created_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_payment_type_display()} to {self.member.get_full_name()} - {self.amount}"
