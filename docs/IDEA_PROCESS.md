# Two rounds, thirty ideas

Selection process for Taher Sohagpurwala (2409540) and Harsh Agrawal (ID pending).
The first round is deliberately rejected in full, following Taher's direction. These are project concepts, not claims that no similar product exists.

## Round one — explored, then rejected

1. **Shelf** — a searchable design-asset library using a trie and a Bloom filter.
2. **Crit Club** — match students into balanced design-critique groups.
3. **Wallplan** — assign exhibition pieces to compatible wall spaces.
4. **Queuepress** — prioritize and schedule jobs at a campus print shop.
5. **Foundry Finder** — search a typography catalogue by prefix and metadata.
6. **Portfolio Path** — choose a sequence of projects for a portfolio walkthrough.
7. **Poster Reach** — choose noticeboards that cover a campus audience.
8. **Studio Match** — allocate freelancers to design briefs by skill and availability.
9. **Moodboard Clean-up** — detect repeated assets in a collected reference library.
10. **Archive Lens** — search labels and notes in a visual research archive.
11. **Material Room** — track availability and risk in a studio material inventory.
12. **Workshop Seats** — allocate limited places across creative workshops.
13. **Street Gallery** — plan a route through public art installations.
14. **Feedback Radar** — index repeated phrases across client feedback documents.
15. **Display Shift** — assign volunteers to gallery desk and installation shifts.

**Decision:** none selected. Most start with a conventional search, scheduling or matching product and add a design context. The next round should make a specific design decision itself computational.

## Round two — a fresh set

16. **OVERPRINT** — reduce an artwork's colour palette to an available set of stock inks while making the colour compromises visible. Weighted set cover chooses inks; randomized Quickselect finds the shifts to review.
17. **Tactile Atlas** — select a compact set of tactile symbols that distinguishes the decisions along a museum route. Set cover handles decision coverage; randomized selection prioritizes high-confusion decisions.
18. **Seam Kit** — choose reusable sign modules that cover the messages required across several event layouts. Set cover plus randomized selection of the least reusable modules.
19. **Borrowed Light** — assign artworks to daylight-sensitive display windows without exceeding exposure capacity. Max-flow matching plus randomized selection of high-risk exposure cases.
20. **Glyph Cargo** — build a multilingual event-font subset from real sign text. Trie-based glyph/word indexing plus a Bloom filter for checking new glyph demand before exact lookup.
21. **Afterimage** — track which changes to a brand system propagate through a publication's pages. Segment-tree range queries plus randomized selection of the highest-impact revisions.
22. **Quiet Route** — compose a short museum route with quiet-stop coverage and disclosed metric assumptions. Set-cover selection, metric-TSP approximation, and randomized selection for sensory-priority stops.
23. **Fold Frequency** — choose reusable fold patterns that satisfy a catalogue of flat-pack packaging briefs. Weighted set cover plus randomized selection of the least well-served briefs.
24. **Shadow Script** — assign projected text cues to sightline-safe surfaces in an installation. Bipartite matching plus randomized selection of the cues with the smallest visibility margin.
25. **Repair Language** — find recurring visual-system naming errors across token and stylesheet exports. KMP plus a Bloom filter for exact-verified token membership.
26. **Microtype Triage** — prioritize spacing defects across a large batch of typeset labels. Segment trees over line measurements plus randomized selection of the largest recorded defects.
27. **One Sheet, Many Voices** — choose a minimal set of multilingual poster variants covering audience-language needs. Set cover plus randomized selection of underserved language groups.
28. **Retake Less** — assign existing product photographs to a shot-list before commissioning new images. Max-flow matching plus a Bloom filter for repeated image fingerprints.
29. **Edge Cases** — choose a compact set of device/text-size test combinations that exposes the most layout failures. Set cover plus randomized selection of the largest overflow measurements.
30. **Echo Objects** — retrieve repeated motifs across a collection of laser-cut vector path strings. KMP plus exact-verified Bloom membership for known path signatures.

## Selection from round two

Scores are editorial judgments on a five-point scale, not experimental measurements.

| Candidate | Design authorship | Algorithm fit | Demo clarity | Feasible scope | Total / 20 |
|---|---:|---:|---:|---:|---:|
| OVERPRINT | 5 | 5 | 5 | 5 | 20 |
| Tactile Atlas | 5 | 4 | 4 | 3 | 16 |
| Seam Kit | 4 | 5 | 4 | 4 | 17 |
| Borrowed Light | 5 | 4 | 4 | 3 | 16 |
| Edge Cases | 4 | 5 | 4 | 4 | 17 |

**Chosen: OVERPRINT.** It creates an immediately visible before/after result, uses two syllabus techniques in a real workflow, and makes room for Taher's typography, composition and colour decisions. It can be demonstrated locally with no third-party account or invented dataset provenance.

The distinctive feature is the combination of limited-ink planning and a designer's review queue. This is a credible course-project direction, not a claim of patent-level novelty. The colour model is deliberately explicit and limited: one stock ink per target colour, measured in D65 CIELAB with Delta E 1976. It is not a physical press simulator.

## Visual decisions

- A warm paper background and printed-rule structure echo a physical proof sheet.
- The type pairs a compact grotesk interface with editorial serif headlines.
- The central specimen is an original SVG composition, not a stock mockup or generated photograph.
- Ink tickets, crop marks, source-to-ink swatches and a visible error queue carry useful information.
- Orange denotes an action or a colour needing review. No decorative fake metrics.
- The same artwork is used for before/after comparison so composition does not obscure colour changes.

The studio is a starting direction. Taher's own artwork, swatches and type choices should replace or extend the sample during the team's design review.
