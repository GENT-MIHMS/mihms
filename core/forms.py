from django import forms
from .models import Facility, Department

class FacilityForm(forms.ModelForm):
    class Meta:
        model = Facility
        fields = ["code", "name", "facility_type", "address", "district", "phone", "email", "is_active"]
        widgets = {"address": forms.Textarea(attrs={"rows": 3})}

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["code", "name", "is_active"]
