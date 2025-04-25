from django.contrib import admin
from .models import (
    SavingsProduct, LoanProduct, IndividualSavingsAccount, GroupSavingsAccount,
    Transaction, Loan, LoanRepayment
)

@admin.register(SavingsProduct)
class SavingsProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'interest_rate', 'minimum_deposit', 'withdrawal_fee', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code', 'description')

@admin.register(LoanProduct)
class LoanProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'interest_rate', 'minimum_amount', 'maximum_amount', 'is_active')
    list_filter = ('is_active', 'individual_eligible', 'group_eligible')
    search_fields = ('name', 'code', 'description')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        ('Financial Terms', {
            'fields': ('interest_rate', 'processing_fee', 'minimum_amount', 'maximum_amount')
        }),
        ('Term and Fees', {
            'fields': ('minimum_term', 'maximum_term', 'grace_period', 'late_payment_fee')
        }),
        ('Eligibility', {
            'fields': ('individual_eligible', 'group_eligible', 'min_saving_percentage')
        }),
    )

@admin.register(IndividualSavingsAccount)
class IndividualSavingsAccountAdmin(admin.ModelAdmin):
    list_display = ('member', 'product', 'account_number', 'current_balance', 'date_opened', 'is_active')
    list_filter = ('is_active', 'product', 'date_opened')
    search_fields = ('member__first_name', 'member__last_name', 'account_number')
    date_hierarchy = 'date_opened'

@admin.register(GroupSavingsAccount)
class GroupSavingsAccountAdmin(admin.ModelAdmin):
    list_display = ('group', 'product', 'account_number', 'current_balance', 'date_opened', 'is_active')
    list_filter = ('is_active', 'product', 'date_opened')
    search_fields = ('group__name', 'account_number')
    date_hierarchy = 'date_opened'

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'amount', 'date', 'reference_number', 'is_synced')
    list_filter = ('transaction_type', 'date', 'is_synced')
    search_fields = ('reference_number', 'description')
    date_hierarchy = 'date'
    readonly_fields = ('is_synced',)

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('loan_number', 'loan_product', 'get_borrower', 'principal_amount', 'status',
                   'application_date', 'remaining_balance')
    list_filter = ('status', 'loan_product', 'application_date')
    search_fields = ('loan_number', 'member__first_name', 'member__last_name', 'group__name')
    date_hierarchy = 'application_date'
    
    def get_borrower(self, obj):
        if obj.member:
            return f"Member: {obj.member.get_full_name()}"
        elif obj.group:
            return f"Group: {obj.group.name}"
        else:
            return "Unknown Borrower"
    get_borrower.short_description = 'Borrower'

@admin.register(LoanRepayment)
class LoanRepaymentAdmin(admin.ModelAdmin):
    list_display = ('loan', 'amount', 'payment_date', 'reference_number', 'receipt_issued', 'is_synced')
    list_filter = ('payment_date', 'receipt_issued', 'is_synced')
    search_fields = ('reference_number', 'loan__loan_number')
    date_hierarchy = 'payment_date'
    readonly_fields = ('is_synced',)
