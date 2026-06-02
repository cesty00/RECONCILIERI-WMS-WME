# Business Rules

Confirmed business rules for ReconControl WMS-WME:

- Depozit Principal = Depozitare + Receptie
- Rezervat is informational and must not be subtracted from QuantityERP
- QuantityDifference = QuantityWMS - QuantityERP
- Reconciliation is by product and document, not raw totals
- Internal WMS movements are LOCATION_ONLY / STATUS_ONLY
- VER100 -> VER100 is not an economic outbound
- REC100 -> raft is a location movement
- Documents after report time are TIMING_RISK
- WMS without WME counterpart is WMS_ONLY
- WME without WMS counterpart is WME_ONLY
- Split WME lines for same document are aggregated before verdict
