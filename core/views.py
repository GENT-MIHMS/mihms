from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from .forms import FacilityForm
from .models import Facility, UserFacilityAccess, Department, Patient, Encounter, AuditLog

def accessible_facilities(user):
    qs = Facility.objects.filter(organisation=user.organisation, is_active=True)
    if user.is_superuser or user.role == "ORG_ADMIN":
        return qs
    return qs.filter(user_access__user=user).distinct()

@login_required
def dashboard(request):
    facilities = accessible_facilities(request.user)
    selected_id = request.GET.get("facility")
    if selected_id and selected_id != "all":
        facilities = facilities.filter(pk=selected_id)
    context = {
        "facilities": accessible_facilities(request.user),
        "active_facilities": facilities,
        "facility_count": facilities.count(),
        "department_count": Department.objects.filter(facility__in=facilities, is_active=True).count(),
        "patient_count": Patient.objects.filter(organisation=request.user.organisation).count(),
        "encounter_count": Encounter.objects.filter(facility__in=facilities).count(),
        "selected_facility": selected_id or "all",
    }
    return render(request, "core/dashboard.html", context)

@login_required
def facility_list(request):
    facilities = accessible_facilities(request.user)
    return render(request, "core/facility_list.html", {"facilities": facilities})

@login_required
def facility_create(request):
    if request.user.role != "ORG_ADMIN" and not request.user.is_superuser:
        raise PermissionDenied("Only organisation administrators can add facilities.")
    if request.method == "POST":
        form = FacilityForm(request.POST)
        if form.is_valid():
            facility = form.save(commit=False)
            facility.organisation = request.user.organisation
            facility.save()
            UserFacilityAccess.objects.get_or_create(user=request.user, facility=facility, defaults={"can_manage": True})
            AuditLog.objects.create(user=request.user, organisation=request.user.organisation,
                                    facility=facility, action="FACILITY_CREATED",
                                    object_type="Facility", object_id=str(facility.pk))
            messages.success(request, "Facility created successfully.")
            return redirect("facility_list")
    else:
        form = FacilityForm()
    return render(request, "core/facility_form.html", {"form": form})

@login_required
def facility_detail(request, pk):
    facility = get_object_or_404(accessible_facilities(request.user), pk=pk)
    departments = facility.departments.all()
    return render(request, "core/facility_detail.html", {"facility": facility, "departments": departments})
