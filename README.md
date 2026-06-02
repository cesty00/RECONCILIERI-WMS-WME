# RECONCILIERI-WMS-WME

ReconControl WMS-WME is a reconciliation application for comparing and explaining differences between WMS and WME using event and document evidence.

## MVP scope

The initial MVP is an offline Python application for Depozit Principal, defined as Depozitare + Receptie. It will read Excel input files in later tasks and reconcile differences by product and document.

Current status: skeleton only. No parser, normalization, reconciliation, reporting, or UI logic is implemented yet.

## Development workflow

Development is performed only through controlled GitHub branches, commits, and Pull Requests. Changes must not be made directly on `main`, and Pull Requests must remain reviewable and scoped.

## Data policy

Real Excel files, operational WMS/WME data, partner data, lots, quantities, secrets, and credentials must not be committed to this repository.

The `data/input` and `data/output` folders are placeholders only. Their contents are ignored except for `.gitkeep` files.

## Minimal app entry point

After dependencies and future implementation are added, the minimal app entry point can be run with:

```bash
python -m app.main
```
