from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from user_management.models import Member, Group, FieldOfficer


class SavingsProduct(models.Model):
    """Defines the different types of savings products offered."""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2,
                                        help_text="Annual interest rate as a percentage (e.g. 5.25 for 5.25%)")
    minimum_deposit = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    withdrawal_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                         validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class LoanProduct(models.Model):
    """Defines the different types of loan products offered."""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2,
                                        help_text="Annual interest rate as a percentage (e.g. 12.5 for 12.5%)")
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    minimum_amount = models.DecimalField(max_digits=12, decimal_places=2)
    maximum_amount = models.DecimalField(max_digits=12, decimal_places=2)
    minimum_term = models.IntegerField(help_text="Minimum loan term in months")
    maximum_term = models.IntegerField(help_text="Maximum loan term in months")
    grace_period = models.IntegerField(default=0, help_text="Grace period in days before late fees apply")
    late_payment_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    
    # Customer eligibility
    individual_eligible = models.BooleanField(default=True)
    group_eligible = models.BooleanField(default=True)
    min_saving_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                               help_text="Minimum percentage of loan amount that must be saved")
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class IndividualSavingsAccount(models.Model):
    """Savings accounts for individual members."""
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    product = models.ForeignKey(SavingsProduct, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20, unique=True)
    date_opened = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.account_number}"


class GroupSavingsAccount(models.Model):
    """Savings accounts for groups."""
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    product = models.ForeignKey(SavingsProduct, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20, unique=True)
    date_opened = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.group.name} - {self.account_number}"


class Transaction(models.Model):
    """Records all financial transactions (deposits, withdrawals, payments, etc.)."""
    TRANSACTION_TYPES = (
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('LOAN_DISBURSEMENT', 'Loan Disbursement'),
        ('LOAN_REPAYMENT', 'Loan Repayment'),
        ('INTEREST_EARNED', 'Interest Earned'),
        ('INTEREST_PAID', 'Interest Paid'),
        ('FEE', 'Fee'),
        ('TRANSFER', 'Transfer'),
        ('OTHER', 'Other'),
    )
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    reference_number = models.CharField(max_length=50, unique=True)
    
    # Relations to accounts (one of these will be null)
    individual_savings_account = models.ForeignKey(IndividualSavingsAccount, on_delete=models.CASCADE, 
                                                 null=True, blank=True)
    group_savings_account = models.ForeignKey(GroupSavingsAccount, on_delete=models.CASCADE,
                                            null=True, blank=True)
    
    # Field officer who processed the transaction
    field_officer = models.ForeignKey(FieldOfficer, on_delete=models.SET_NULL, null=True)
    
    # Metadata for offline transactions
    is_synced = models.BooleanField(default=True)
    offline_created_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        if self.individual_savings_account:
            account = f"Individual: {self.individual_savings_account.account_number}"
        elif self.group_savings_account:
            account = f"Group: {self.group_savings_account.account_number}"
        else:
            account = "No account"
        
        return f"{self.transaction_type} - {self.amount} - {account} - {self.date.date()}"


class Loan(models.Model):
    """Represents loans given to members or groups."""
    STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('DISBURSED', 'Disbursed'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('DEFAULTED', 'Defaulted'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    )
    
    loan_product = models.ForeignKey(LoanProduct, on_delete=models.PROTECT)
    loan_number = models.CharField(max_length=20, unique=True)
    
    # Borrower (either individual or group)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    
    # Loan details
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term_months = models.IntegerField()
    application_date = models.DateField(default=timezone.now)
    approval_date = models.DateField(null=True, blank=True)
    disbursement_date = models.DateField(null=True, blank=True)
    expected_end_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    approved_by = models.ForeignKey(FieldOfficer, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approved_loans')
    disbursed_by = models.ForeignKey(FieldOfficer, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='disbursed_loans')
    
    # Financial tracking
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_interest = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remaining_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Notes
    purpose = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    def __str__(self):
        borrower = self.member.get_full_name() if self.member else self.group.name
        return f"Loan {self.loan_number} - {borrower} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Calculate financials if this is a new loan
        if not self.pk:
            # Simple interest calculation
            self.total_interest = (self.principal_amount * (self.interest_rate / 100) * self.term_months) / 12
            self.total_amount_due = self.principal_amount + self.total_interest
            self.remaining_balance = self.total_amount_due
            
        # If disbursement date is set, calculate expected end date
        if self.disbursement_date and not self.expected_end_date:
            from datetime import timedelta
            self.expected_end_date = self.disbursement_date + timedelta(days=30 * self.term_months)
            
        super().save(*args, **kwargs)


class LoanRepayment(models.Model):
    """Records payments made toward loans."""
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='repayments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    received_by = models.ForeignKey(FieldOfficer, on_delete=models.SET_NULL, null=True)
    reference_number = models.CharField(max_length=50, unique=True)
    
    # Payment breakdown
    principal_component = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    interest_component = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    penalty_component = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Notes and receipt info
    notes = models.TextField(blank=True, null=True)
    receipt_issued = models.BooleanField(default=False)
    
    # Offline sync tracking
    is_synced = models.BooleanField(default=True)
    offline_created_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Payment of {self.amount} for Loan {self.loan.loan_number} on {self.payment_date.date()}"
    
    def save(self, *args, **kwargs):
        # Update loan's paid amount and balance
        if not self.pk:  # Only for new payments
            self.loan.total_amount_paid += self.amount
            self.loan.remaining_balance -= self.amount
            
            # Update loan status if fully paid
            if self.loan.remaining_balance <= 0:
                self.loan.status = 'COMPLETED'
                self.loan.actual_end_date = timezone.now().date()
                
            self.loan.save()
            
        super().save(*args, **kwargs)
