# MIHMS v1.0 — Multi-Facility Integrated Health Management System

A first Django foundation for one organisation managing multiple health facilities. Includes:
- Login/logout and Django password hashing
- Organisation, facility and department records
- Role field on user accounts
- Facility access assignments
- Organisation-admin facility creation
- Facility-scoped dashboard and facility detail pages
- Initial domain schema for patients, encounters, services, invoices, payments, inventory, procurement, expenses, accounting, assets and audit logs
- Malawi timezone and MWK default currency

## Important status
This is a development starter, not a production-ready clinical or accounting system. Patient workflows, stock posting, billing, double-entry validation, approvals, reporting, automated tests, deployment hardening and legal/security review remain to be implemented before real use. Do not enter real patient or financial data.

## Run locally

Requires Python 3.11+.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations core
python manage.py migrate
python manage.py seed_demo --password 'Choose-A-Strong-Temporary-Password'
python manage.py runserver
```

Open http://127.0.0.1:8000/ and sign in:
- Username: `mihmsadmin`
- Password: the temporary password supplied to `seed_demo`

Change the temporary password immediately after first login. The seed command does not overwrite an existing user's password.

## PostgreSQL

Set `DATABASE_URL`, for example:
`postgresql://mihms_user:strong-password@localhost:5432/mihms`

Set a long random `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, and `DJANGO_ALLOWED_HOSTS` before deployment. Configure HTTPS, secure cookies, backups, monitoring, email-based password reset and a managed PostgreSQL service. Never deploy with the development secret or DEBUG enabled.

## Initial roles
- ORG_ADMIN
- FACILITY_MANAGER
- CLINICIAN
- PHARMACIST
- ACCOUNTANT
- PROCUREMENT
- RECEPTION
- STOREKEEPER
- VIEWER

The current first version enforces facility scoping on dashboard and facility pages. Before enabling clinical, pharmacy or financial screens, enforce permissions and facility scope in every API and query, not only in the user interface.

## Database design notes
- Organisation owns facilities.
- Users belong to an organisation and can be assigned to one or more facilities.
- Products and suppliers are organisation-wide; batches and stock movements are facility-specific.
- Patients are organisation-wide to support continuity between facilities; encounters are facility-specific.
- Every invoice, payment, expense, purchase order, journal and asset is linked to a facility where applicable.
- Financial records should be immutable after posting; corrections should use audited reversals.
- Stock must be ledger-based: never change stock balances without recording a stock movement.
- Use FEFO for medicine dispensing and maintain batch/expiry traceability.
- Enforce balanced journal entries (total debits = total credits) before posting in the accounting implementation.

## Suggested next implementation milestones
1. User administration UI, password reset, account deactivation and invitation workflow.
2. Patient registration and encounter workflow with consent, confidentiality and audit controls.
3. Service catalogue, invoices, receipts and payment reconciliation.
4. Pharmacy and supplies with batch ledger, FEFO, transfers, counts and reorder alerts.
5. Procurement approvals, goods received notes and supplier invoices.
6. Full double-entry accounting, cashbook, bank reconciliation, budgets and financial statements.
7. Automated tests, security assessment, backup/restore drills and production deployment.
