from django.contrib import admin
from .models import (
    BoosterCategory, AgricultureProduct, AgricultureCollection,
    SchoolFeesCollection, BoosterPayment
)

@admin.register(BoosterCategory)
class BoosterCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

@admin.register(AgricultureProduct)
class AgricultureProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit_of_measure', 'current_market_price', 'price_last_updated', 'is_active')
    list_filter = ('is_active', 'price_last_updated')
    search_fields = ('name', 'description')

@admin.register(AgricultureCollection)
class AgricultureCollectionAdmin(admin.ModelAdmin):
    list_display = ('member', 'product', 'quantity', 'unit_price', 'total_value', 'collection_date', 'payment_status')
    list_filter = ('payment_status', 'collection_date', 'collection_location')
    search_fields = ('member__first_name', 'member__last_name', 'product__name', 'receipt_number')
    date_hierarchy = 'collection_date'
    raw_id_fields = ('member', 'product', 'collected_by')

@admin.register(SchoolFeesCollection)
class SchoolFeesCollectionAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'member', 'school_name', 'education_level', 'amount', 'collection_date', 'is_complete_payment')
    list_filter = ('education_level', 'term', 'is_complete_payment', 'collection_date')
    search_fields = ('student_name', 'member__first_name', 'member__last_name', 'school_name', 'receipt_number')
    date_hierarchy = 'collection_date'
    raw_id_fields = ('member', 'collected_by')

@admin.register(BoosterPayment)
class BoosterPaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_type', 'member', 'amount', 'payment_date', 'payment_method', 'reference_number', 'is_synced')
    list_filter = ('payment_type', 'payment_method', 'payment_date', 'is_synced')
    search_fields = ('reference_number', 'member__first_name', 'member__last_name', 'notes')
    date_hierarchy = 'payment_date'
    raw_id_fields = ('member', 'agriculture_collection', 'school_fees_collection', 'processed_by')
    readonly_fields = ('is_synced',)
