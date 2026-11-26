from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class Organisation(TimeStampedModel):
    name = models.CharField(max_length=180)
    legal_name = models.CharField(max_length=220, blank=True)
    registration_number = models.CharField(max_length=100, blank=True)
    default_currency = models.CharField(max_length=3, default="MWK")
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name

class Facility(TimeStampedModel):
    organisation = models.ForeignKey(Organisation, on_delete=models.PROTECT, related_name="facilities")
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=180)
    facility_type = models.CharField(max_length=50, default="Clinic")
    address = models.TextField(blank=True)
    district = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["organisation", "code"], name="unique_facility_code_per_org")]
        ordering = ["name"]
    def __str__(self): return f"{self.code} — {self.name}"

class Department(TimeStampedModel):
    facility = models.ForeignKey(Facility, on_delete=models.PROTECT, related_name="departments")
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["facility", "code"], name="unique_department_code_per_facility")]
        ordering = ["name"]
    def __str__(self): return f"{self.facility.code} / {self.name}"

class User(AbstractUser):
    class Role(models.TextChoices):
        ORG_ADMIN = "ORG_ADMIN", "Organisation administrator"
        FACILITY_MANAGER = "FACILITY_MANAGER", "Facility manager"
        CLINICIAN = "CLINICIAN", "Clinician"
        PHARMACIST = "PHARMACIST", "Pharmacist"
        ACCOUNTANT = "ACCOUNTANT", "Accountant"
        PROCUREMENT = "PROCUREMENT", "Procurement officer"
        RECEPTION = "RECEPTION", "Receptionist"
        STOREKEEPER = "STOREKEEPER", "Storekeeper"
        VIEWER = "VIEWER", "Read-only management"
    organisation = models.ForeignKey(Organisation, null=True, blank=True, on_delete=models.PROTECT, related_name="users")
    role = models.CharField(max_length=30, choices=Role.choices, default=Role.VIEWER)
    phone = models.CharField(max_length=40, blank=True)
    must_change_password = models.BooleanField(default=True)
    def __str__(self): return self.get_full_name() or self.username

class UserFacilityAccess(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="facility_access")
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="user_access")
    can_manage = models.BooleanField(default=False)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "facility"], name="unique_user_facility_access")]

class Patient(TimeStampedModel):
    organisation = models.ForeignKey(Organisation, on_delete=models.PROTECT)
    patient_number = models.CharField(max_length=50)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["organisation", "patient_number"], name="unique_patient_number_per_org")]

class Encounter(TimeStampedModel):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="encounters")
    facility = models.ForeignKey(Facility, on_delete=models.PROTECT)
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.PROTECT)
    attending_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT)
    encounter_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=30, default="OPEN")
    clinical_note = models.TextField(blank=True)

class Service(TimeStampedModel):
    facility = models.ForeignKey(Facility, on_delete=models.PROTECT)
    code = models.CharField(max_length=40)
    name = models.CharField(max_length=160)
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.PROTECT)
    standard_fee = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["facility", "code"], name="unique_service_code_per_facility")]

class Invoice(TimeStampedModel):
    facility = models.ForeignKey(Facility, on_delete=models.PROTECT)
    patient = models.ForeignKey(Patient, null=True, blank=True, on_delete=models.PROTECT)
    invoice_number = models.CharField(max_length=50)
    issue_date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=20, default="UNPAID")
    currency = models.CharField(max_length=3, default="MWK")
    class Meta:
        constraints = [models.UniqueConstraint(fields=["facility", "invoice_number"], name="unique_invoice_per_facility")]

class InvoiceLine(TimeStampedModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="lines")
    description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    unit_price = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    unit_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])

class Payment(TimeStampedModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0.01)])
    method = models.CharField(max_length=30)
    reference = models.CharField(max_length=100, blank=True)
    received_by = models.ForeignKey(User, null=True, on_delete=models.PROTECT)
    received_at = models.DateTimeField(default=timezone.now)

class Product(TimeStampedModel):
    class Kind(models.TextChoices):
        MEDICINE = "MEDICINE", "Medicine"
        SUPPLY = "SUPPLY", "Medical supply"
        OTHER = "OTHER", "Other"
    organisation = models.ForeignKey(Organisation, on_delete=models.PROTECT)
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=180)
    kind = models.CharField(max_length=20, choices=Kind.choices)
    unit = models.CharField(max_length=40, default="unit")
    is_active = models.BooleanField(default=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["organisation", "code"], name="unique_product_code_per_org")]

class StockBatch(TimeStampedModel):
    facility = models.ForeignKey(Facility, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    batch_number = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    quantity_on_hand = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    unit_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    reorder_level = models.DecimalField(max_digits=14, decimal_places=2, default=0)

class StockMovement(TimeStampedModel):
    class MovementType(models.TextChoices):
        RECEIPT = "RECEIPT", "Receipt"
        DISPENSE = "DISPENSE", "Dispensing"
        ISSUE = "ISSUE", "Issue to department"
        TRANSFER_IN = "TRANSFER_IN", "Transfer in"
        TRANSFER_OUT = "TRANSFER_OUT", "Transfer out"
        ADJUSTMENT = "ADJUSTMENT", "Adjustment"
        RETURN = "RETURN", "Return"
    facility = models.ForeignKey(Facility, on_delete=models.PROTECT)
    batch = models.ForeignKey(StockBatch, on_delete=models.PROTECT)
    movement_type = models.CharField(max_length=20, choices=MovementType.choices)
    quantity_delta = models.DecimalField(max_digits=14, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True)
    performed_by = models.ForeignKey(User, null=True, on_delete=models.PROTECT)
    notes = models.TextField(blank=True)

class Supplier(TimeStampedModel):
    organisation = models.ForeignKey(Organisation, on_delete=models.PROTECT)
    name = models.CharField(max_length=180)
    contact_person = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

class PurchaseOrder(TimeStampedModel):
    facility = models.ForeignKey(Facility, on_delete=models.PROTECT)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    order_number = models.CharField(max_length=50)
    order_date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=20, default="DRAFT")
    created_by = models.ForeignKey(User, null=True, on_delete=models.PROTECT)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["facility", "order_number"], name="unique_po_per_facility")]

class PurchaseOrderLine(TimeStampedModel):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name="lines")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity_ordered = models.DecimalField(max_digits=14, decimal_places=2)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)

class Expense(TimeStampedModel):
    facility = models.ForeignKey(Facility, on_delete=models.PROTECT)
    category = models.CharField(max_length=100)
    description = models.CharField(max_length=220)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    expense_date = models.DateField(default=timezone.localdate)
    reference = models.CharField(max_length=100, blank=True)
    recorded_by = models.ForeignKey(User, null=True, on_delete=models.PROTECT)

class Account(TimeStampedModel):
    organisation = models.ForeignKey(Organisation, on_delete=models.PROTECT)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=140)
    account_type = models.CharField(max_length=20, choices=[
        ("ASSET","Asset"),("LIABILITY","Liability"),("EQUITY","Equity"),
        ("REVENUE","Revenue"),("EXPENSE","Expense")])
    is_active = models.BooleanField(default=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["organisation", "code"], name="unique_account_code_per_org")]

class JournalEntry(TimeStampedModel):
    organisation = models.ForeignKey(Organisation, on_delete=models.PROTECT)
    facility = models.ForeignKey(Facility, null=True, blank=True, on_delete=models.PROTECT)
    entry_number = models.CharField(max_length=50)
    entry_date = models.DateField(default=timezone.localdate)
    description = models.CharField(max_length=220)
    posted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, null=True, on_delete=models.PROTECT)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["organisation", "entry_number"], name="unique_journal_number_per_org")]

class JournalLine(TimeStampedModel):
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.PROTECT, related_name="lines")
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    debit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=14, decimal_places=2, default=0)

class Asset(TimeStampedModel):
    facility = models.ForeignKey(Facility, on_delete=models.PROTECT)
    asset_code = models.CharField(max_length=50)
    name = models.CharField(max_length=180)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    condition = models.CharField(max_length=50, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)

class AuditLog(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    organisation = models.ForeignKey(Organisation, null=True, blank=True, on_delete=models.SET_NULL)
    facility = models.ForeignKey(Facility, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=100)
    object_type = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=80, blank=True)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
