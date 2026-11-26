from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Organisation, Facility, Department, UserFacilityAccess

class Command(BaseCommand):
    help = "Create a demo organisation, three facilities and an initial administrator."
    def add_arguments(self, parser):
        parser.add_argument("--username", default="mihmsadmin")
        parser.add_argument("--password", required=True)
        parser.add_argument("--email", default="admin@example.com")
    def handle(self, *args, **opts):
        org, _ = Organisation.objects.get_or_create(name="MIHMS Demonstration Organisation",
                                                    defaults={"default_currency": "MWK"})
        facilities = [
            ("FAC001", "Central Medical Centre", "Lilongwe"),
            ("FAC002", "Northside Clinic", "Mzuzu"),
            ("FAC003", "Lakeshore Health Centre", "Salima"),
        ]
        for code, name, district in facilities:
            f, _ = Facility.objects.get_or_create(organisation=org, code=code,
                defaults={"name": name, "district": district, "facility_type": "Clinic"})
            for dcode, dname in [("OPD","Outpatient"),("PHARM","Pharmacy"),("LAB","Laboratory"),
                                 ("MAT","Maternity"),("ADMIN","Administration")]:
                Department.objects.get_or_create(facility=f, code=dcode, defaults={"name": dname})
        User = get_user_model()
        user, created = User.objects.get_or_create(username=opts["username"], defaults={
            "email": opts["email"], "organisation": org, "role": "ORG_ADMIN",
            "is_staff": True, "is_superuser": True, "must_change_password": True
        })
        if created:
            user.set_password(opts["password"])
            user.save()
        else:
            self.stdout.write(self.style.WARNING("User already existed; password was not changed."))
        for f in org.facilities.all():
            UserFacilityAccess.objects.get_or_create(user=user, facility=f, defaults={"can_manage": True})
        self.stdout.write(self.style.SUCCESS("Demo data created. Sign in using the administrator credentials supplied."))
