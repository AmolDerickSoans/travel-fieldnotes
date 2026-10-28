---
name: travel-fieldnotes
description: Create or improve a researched travel-magazine guide from a rough trip brief, itinerary or existing report. Use for personalised travel field guides with real place and accommodation photos, coherent routes, maps, budgets, QR links and engaging destination stories, delivered as readable HTML and/or PDF. Also supports privacy-safe excerpts when the user explicitly requests a public showcase. Does not book travel or publish content.
---

# Travel Fieldnotes

Make a guide someone wants to read before departure and can actually use on the trip. Combine the judgment of a travel planner, the specificity of a good destination writer and the restraint of an editor. A beautiful page must also be true and useful.

## Start with the actual trip

Inspect any existing guide and available source material before restarting research. Preserve accepted decisions and useful design work. Keep the scope the user requested: an edit does not require a new itinerary.

Resolve only missing details that materially change the plan: year and dates; arrival/departure windows; travellers and room/bed configuration; booked travel and fixed commitments; interests, pace and crowd tolerance; dietary/access needs if relevant; work connectivity; budget currency and whether it is per person or total, with paid items included or excluded. Ask a few focused questions while progressing independent work. Do not infer frailty from age, luxury from income, or interests from family roles.

Create a working brief with **fixed constraints, preferences, assumptions and open questions**. Honour existing bookings. Read [research-and-planning.md](references/research-and-planning.md) before making recommendations.

## Research before composing

Use the user's chosen browser or available service tools. Verify changing information with current sources. Prioritise official venue calendars, transport operators, property listings and direct ticket conditions; use recent visitor accounts for texture and recurring concerns. Never claim an agent visited a place or treat a Reddit comment as an official rule.

Keep a compact evidence ledger: claim, source URL, checked date, applicability and confidence. For price quotes, record travel dates, party, rooms, taxes, meal basis and cancellation conditions. Label **observed quote**, **published tariff**, **estimate** or **unresolved**. Never invent availability or force a target budget to appear achievable. If the booking window is not open, state that and use labelled allowances rather than fabricated future quotes.

Assess stays through actual bedroom, bathroom and shared-space images, recent review patterns, neighbourhood and room layout. Attractive photography is not evidence of reliable Wi-Fi or quiet. Offer a small, meaningfully different shortlist and identify what remains unverified.

## Build a trip that works

Group places geographically. Check weekdays, closures, last entry, ticket/pass access, transfer margins, hotel nights and the day after late events. Convert work calls into local time, including date changes. Separate essential anchors from optional detours; leave room for weather and appetite.

Compare budgets using the same trip basket. Distinguish group/per-person costs, paid travel, remaining spend and refundable deposits. Explain trade-offs rather than producing imaginary savings. Use estimates as ranges when precision would mislead.

## Find the editorial story

Read [editorial-and-design.md](references/editorial-and-design.md). Write a one-sentence purpose for each proposed page or section. It must orient, help a decision, reveal a particular place or object, or assist during the trip. Cut pages that exist only to fill a template.

Let the city supply the narrative: a carved scene in a museum, a plant's journey, a neighbourhood's working life, a dish with local roots. Explain something concrete. Avoid repeated instructions to slow down, reflect, choose favourites or discuss dinner. Do not repeatedly sell the plan back to the traveller as “perfect for you.”

Adapt depth to the reader. A long guide can contain substantial essays; a weekend guide may be brief. Write original prose, not imitation of a named publication. Keep uncertainty close to practical claims without turning every paragraph into a disclaimer.

## Design and build

Agree a visual direction through the brief and existing references; do not pause for routine font or colour choices. Use real photographs of the actual places and shortlisted rooms, with source and rights information. Do not use browser-window screenshots as destination imagery. Never generate a fake hotel, restaurant or attraction photograph. Use illustration sparingly, labelled, when it explains something photography cannot.

Choose maps and graphics by the question they answer. Use actual geographic data, attribution, readable labels and honest route/time precision. A schematic must say it is a schematic. No invented map geometry, fake scale bars or charts merely to satisfy a visual quota.

Default to portable HTML plus a print-ready PDF when the user wants a shareable magazine; honour any requested format. Include clickable contents, useful links and, where useful, a restrained set of labelled QR codes with readable destination names. Omit QR codes that do not help the reader act. Keep assets local where rights allow. Use static map fallbacks for print/offline reading. No API key should be required merely to read an exported guide.

[assets/editorial.css](assets/editorial.css) supplies optional layout primitives, not a required design. Keep body type comfortable at final print size, photo crops intentional and navigation quiet. Do not shrink text to force a page count.

## Edit, verify, deliver

Read [delivery-checks.md](references/delivery-checks.md). Review separately for trip feasibility, factual support, editorial purpose and visual quality. Use an independent editor when authorised; otherwise perform these as distinct passes yourself. Act on findings rather than merely appending an audit.

Run `python3 scripts/audit_report.py REPORT.html --as-of YYYY-MM-DD` using the actual review date. Optionally provide `--manifest` following [example-manifest.json](references/example-manifest.json) for arithmetic, dates and nights. The script checks a limited set of mechanical errors; it does not prove source accuracy, availability, map correctness, privacy or QR readability.

Render the final artifact and inspect all pages, plus mobile HTML if provided. Decode QRs, inspect links and reconcile costs. Do a freshness sweep of “next,” “current,” “available,” booking windows and deadlines; an old research footer does not make stale wording acceptable. Resolve defects and rerender changed pages.

Deliver the actual files with a short account of what is ready and any consequential unresolved issue. Never imply a booking was made. Booking, messaging and publishing require the user's applicable authorisation.

## Public excerpts, only when requested

Read [public-excerpts.md](references/public-excerpts.md) before creating a social post, video or public sample. Build a separate allowlisted artifact from safe material; never distribute the private report with cosmetic blurring. Recheck rights, text, links, QR destinations, metadata and every video frame. Keep the private source files outside the public package.
