# Architecture

ReconControl WMS-WME MVP is an offline Python application.

## Input

The MVP will use Excel input files uploaded or placed in a controlled input location. Real operational Excel files must not be committed to the repository.

## Layers

- Parser layer: future extraction of data from WMS and WME Excel files.
- Normalization layer: future normalization of products, documents, locations, dates, and quantities.
- Reconciliation layer: future document-level matching and classification of differences.
- Reporting layer: future generation of auditable reconciliation outputs.
- Future Streamlit UI: future local interface for upload, review, and export flows.

## Core model layer

- `statuses.py` contains reconciliation, source-system, and movement-direction enums.
- `stock.py` contains the stock snapshot row model.
- `events.py` contains WMS and WME event models.
- Parser error classes are defined before parser implementation.

This task creates the skeleton and foundational model layer only. It does not implement parser, normalization, reconciliation, reporting, or UI logic.
