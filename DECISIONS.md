# Decisions

| Date | Decision | Rationale | Consequence |
| --- | --- | --- | --- |
| 2026-07 | Use local read-only evidence first. | Avoid token spend, credentials, and remote privacy risk. | No API polling or sign-in in the MVP. |
| 2026-07 | Keep Python standard library and SQLite/Tkinter for MVP. | Low idle cost and simple Windows deployment. | Tray behavior and richer UI remain later work. |
| 2026-07 | Preserve missing usage fields as unknown. | Trustworthy reporting is more important than complete-looking numbers. | UI must render unknown explicitly. |
| 2026-07 | Sanitize source paths at persistence boundary. | Absolute paths and traversal data are sensitive and non-portable. | Stored provenance uses safe labels or deterministic hashes. |
| 2026-07 | Use the project-local coordination board. | Product evidence must travel with product code. | Global coordination engine only monitors/coordinates it. |
