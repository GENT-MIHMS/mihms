from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

@admin.register(User)
class MIHMSUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("MIHMS access", {"fields": ("organisation", "role", "phone", "must_change_password")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("MIHMS access", {"fields": ("organisation", "role", "phone")}),)

class FacilityAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "organisation", "district", "is_active")
    list_filter = ("organisation", "facility_type", "is_active")
    search_fields = ("code", "name", "district")
admin.site.register(Facility, FacilityAdmin)
admin.site.register([Organisation, Department, UserFacilityAccess, Patient, Encounter, Service,
                     Invoice, InvoiceLine, Payment, Product, StockBatch, StockMovement, Supplier,
                     PurchaseOrder, PurchaseOrderLine, Expense, Account, JournalEntry, JournalLine,
                     Asset, AuditLog])
