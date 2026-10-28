# Delivery checks

## Mechanical audit

Run `scripts/audit_report.py` on the final HTML. The optional synthetic manifest in this folder documents supported fields. Its findings are a starting point; warnings need human/agent review. Never claim this script validates live facts or catches all privacy risks.

## Content and route checks

- Reconcile dates, weekdays, booked segments, hotel nights, event-pass access and local call times.
- Check every budget column on the same basis; reconcile group totals and per-person arithmetic.
- Verify names, substantive historical claims, official restrictions and the freshness of changing information.
- Confirm final itinerary matches maps, contents, practical pages and alternatives.
- Explain unresolved availability or routing constraints without burying them in a source appendix.

## Render inspection

Export using the relevant available document/PDF toolchain. Inspect every rendered page, initially as contact sheets, then full size for dense pages and all suspicious crops. Check page breaks, missing fonts, orphaned text, overlapping labels, unreadably small citations, white-on-white text and clipping. Rerender after fixes. Check the mobile HTML at a narrow viewport. Test core reading with the network unavailable if the guide is presented as offline-ready.

Click representative internal links and every unique destination class; audit all generated hrefs programmatically. QR codes need a quiet zone, high contrast, sufficient physical size and a nearby human-readable destination. Decode **each unique QR from the exported artifact**, not just its source SVG, and check its URL. Do not put reservation secrets in QRs. Validate maps visually against the actual geography; label schematics and avoid fake scale or precise minutes without evidence.

## Handoff

Provide an editable source plus the final requested artifact. Keep a source/credit record and build notes needed for later updates. Do not ship caches, account state, browser screenshots or working notes as part of the reader-facing package. State material unresolved issues in the handoff. Do not call a template or an unrendered draft a completed guide.
