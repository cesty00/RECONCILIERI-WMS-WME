# Input Format Contracts

This document defines the expected input format contracts for the four MVP source files before parser implementation. It is documentation only and does not include real source data.

Future parsers must fail clearly when required fields are missing, ambiguous, malformed, or inconsistent with these contracts.

## 1. Current WMS/WME Stock Report

### Purpose

Provides the current stock comparison between WMS and WME for Depozit Principal.

### Expected File Type

Excel workbook, normally `.xlsx` or `.xls` from controlled runtime input. Real source files must not be committed.

### Expected Sheet Handling

- Future parser should support an explicitly selected sheet or a single-sheet workbook.
- If multiple candidate sheets exist and no sheet is selected, the parser must raise a validation error.
- Hidden, empty, or summary-only sheets must not be silently parsed as source data.

### Required Columns

- CodArticol
- DenumireArticol
- QuantityERP
- QuantityWMS
- Rezervat
- QuantityDifference
- Gestiune

### Key Fields

- CodArticol
- Gestiune

### Quantity Fields

- QuantityERP
- QuantityWMS
- Rezervat
- QuantityDifference

Rules:

- QuantityDifference = QuantityWMS - QuantityERP
- Rezervat is informational only and must not be subtracted from QuantityERP

### Date/Time Fields

- Report timestamp may be external metadata or an input parameter when not present in the workbook.
- Future parser must require an explicit report time when timing classification depends on it.

### Product Identification Fields

- CodArticol
- DenumireArticol

### Location/Warehouse Fields

- Gestiune
- Depozit Principal = Depozitare + Receptie

### Known Caveats

- Quantity columns may contain localized numeric formatting.
- Rezervat may be present even when not relevant for reconciliation.
- Gestiune values may need normalization before Depozit Principal filtering.
- QuantityDifference must be validated against QuantityWMS - QuantityERP, allowing only future approved rounding tolerance.

### Validation Errors Future Parsers Must Raise

- Missing required column.
- Duplicate required column after normalization.
- Non-numeric quantity value in required quantity fields.
- QuantityDifference inconsistent with QuantityWMS - QuantityERP.
- Missing or unsupported Gestiune value.
- Multiple sheets without explicit sheet selection.
- Empty data rows after header detection.

## 2. Baseline Stock Report After WME Consumption Documents

### Purpose

Provides the baseline stock report after WME consumption documents, also called the post-BC state. It is used as the starting point for movement reconciliation.

### Expected File Type

Excel workbook, normally `.xlsx` or `.xls` from controlled runtime input. Real source files must not be committed.

### Expected Sheet Handling

- Expected to follow the same sheet handling rules as the current WMS/WME stock report.
- Future parser should support an explicitly selected sheet or a single-sheet workbook.
- Multiple candidate sheets without explicit selection must produce a validation error.

### Required Columns

Expected same column family as the current WMS/WME stock report:

- CodArticol
- DenumireArticol
- QuantityERP
- QuantityWMS
- Rezervat
- QuantityDifference
- Gestiune

### Key Fields

- CodArticol
- Gestiune

### Quantity Fields

- QuantityERP
- QuantityWMS
- Rezervat
- QuantityDifference

Rules:

- QuantityDifference = QuantityWMS - QuantityERP
- Rezervat is informational only and must not be subtracted from QuantityERP

### Date/Time Fields

- Baseline report timestamp may be external metadata or an input parameter.
- Future parser must require explicit baseline time when movement windows depend on it.

### Product Identification Fields

- CodArticol
- DenumireArticol

### Location/Warehouse Fields

- Gestiune
- Depozit Principal = Depozitare + Receptie

### Known Caveats

- The baseline file must represent the post-consumption-document state.
- It may use the same columns as the current stock report but a different export timestamp.
- Future reconciliation must distinguish baseline state from current state.

### Validation Errors Future Parsers Must Raise

- Missing required column from the expected stock column family.
- Non-numeric quantity value in required quantity fields.
- QuantityDifference inconsistent with QuantityWMS - QuantityERP.
- Missing report/baseline timestamp when required by movement reconciliation.
- Multiple sheets without explicit sheet selection.
- Empty data rows after header detection.

## 3. WMS Traceability

### Purpose

Provides WMS movement evidence used to explain stock differences by product, document, operation type, lot, location, and timing.

### Expected File Type

Excel workbook, normally `.xlsx` or `.xls` from controlled runtime input. Real source files must not be committed.

### Expected Sheet Handling

- Future parser should support an explicitly selected sheet or a single-sheet workbook.
- If multiple traceability sheets are present, the parser must not guess without selection.
- Empty or report-summary sheets must be rejected.

### Required Fields If Present In Export

- Data
- Tip operatiune
- Numar comanda
- Cod articol
- Denumire articol
- Locatie sursa
- Locatie destinatie
- Lot
- Cantitate
- Cod-motiv
- Partener
- Document comanda
- Document intrare
- Depozit

Future parser implementation may define a strict minimum subset after sample review, but these fields are the expected contract when available in the export.

### Key Fields

- Cod articol
- Numar comanda
- Document comanda
- Document intrare
- Lot
- Tip operatiune

### Quantity Fields

- Cantitate

### Date/Time Fields

- Data

### Product Identification Fields

- Cod articol
- Denumire articol

### Location/Warehouse Fields

- Locatie sursa
- Locatie destinatie
- Depozit

### Movement Rules

- Livrare and Receptie may be economic movements.
- Mutare and internal movements may be LOCATION_ONLY / STATUS_ONLY.
- VER100 -> VER100 is not economic outbound.
- REC100 -> shelf/location is a location movement.
- Documents after report time are TIMING_RISK.

### Known Caveats

- Operation names may be localized or exported with inconsistent spacing.
- Location codes may encode operational meaning and need normalization.
- WMS movements must not be treated as economic differences until operation type, source, destination, and document context are evaluated.
- Timing depends on a reliable report timestamp.

### Validation Errors Future Parsers Must Raise

- Missing movement date when timing classification is required.
- Non-numeric Cantitate.
- Missing product identifier.
- Missing operation type.
- Missing both document fields and command/order number.
- Invalid or unparseable date/time value.
- Multiple sheets without explicit sheet selection.
- Empty traceability data after header detection.

## 4. WME Stock Card

### Purpose

Provides WME document-level stock card movements used to match WMS evidence against WME documents and explain differences.

### Expected File Type

Excel workbook, normally `.xlsx` or `.xls` from controlled runtime input. Real source files must not be committed.

### Expected Sheet Handling

- Source may be semi-structured and may not have a clean header row.
- Future parser must support positional interpretation for the stock card layout.
- If multiple candidate sheets exist, the parser must require explicit sheet selection.
- Header, footer, subtotal, and blank rows must be detected and excluded without losing valid movement rows.

### Expected Positional Interpretation

- column 2: document type
- column 3: document number
- column 4: date
- column 5: in quantity
- column 6: out quantity
- column 7: stock after
- column 10: partner
- column 11: product name
- column 13: internal WME product code
- column 14: warehouse/location
- column 15: unit of measure

Column numbering is one-based and follows the source spreadsheet layout.

### Document Types To Mention

- StocInitial
- AE
- BC
- NT
- NP
- PV
- F
- FE

### Key Fields

- document type
- document number
- internal WME product code
- warehouse/location

### Quantity Fields

- in quantity
- out quantity
- stock after

### Date/Time Fields

- date

### Product Identification Fields

- product name
- internal WME product code

### Location/Warehouse Fields

- warehouse/location

### Known Caveats

- The source may be semi-structured and may not expose stable headers.
- Document numbers may be numeric, text, or formatted with prefixes elsewhere in the workflow.
- Quantities may appear in either in quantity or out quantity depending on document type.
- Stock-after values are audit context and must not replace movement quantity parsing.
- Split WME lines for the same document must be aggregated before verdict.

### Validation Errors Future Parsers Must Raise

- Required positional column missing.
- Document type missing or not recognized for a movement row.
- Document number missing for a movement row.
- Invalid or unparseable date.
- Non-numeric in quantity, out quantity, or stock after where present.
- Missing internal WME product code when needed for product matching.
- Multiple sheets without explicit sheet selection.
- No valid movement rows after semi-structured row filtering.

## Matching Implications

Future reconciliation must normalize and match document references across systems before verdicts are assigned.

Examples:

- SFA47326 -> AE 47326
- WME112133 -> AE 112133
- Document intrare 69138 -> NT 69138
- Split WME lines for same document must be aggregated before verdict.

Matching must be by product and document, not raw totals.

## Data Protection

- Real source files must not be committed.
- Fixtures must be anonymized.
- `data/input` is local/runtime only.
- `data/output` is local/runtime only.
- Operational Excel, CSV, partner, lot, quantity, movement, and warehouse-card exports must stay outside repository history.
