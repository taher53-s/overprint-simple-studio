"""Generate the two-page proposal and seven-page report from the measured results.
Optional dependencies: reportlab, python-docx. Run from the repository root.
"""
from pathlib import Path
import json, html
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, Preformatted
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from docx import Document
from docx.shared import Inches, Pt, RGBColor

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs'
b=json.loads((ROOT/'results/benchmarks.json').read_text())
demo=json.loads((ROOT/'results/demo-plan.json').read_text())['result']
PAPER=colors.HexColor('#F3F0E8'); INK=colors.HexColor('#242720'); ORANGE=colors.HexColor('#EB5F36')
styles={
 'title':ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=32,leading=35,textColor=INK,spaceAfter=12),
 'sub':ParagraphStyle('sub',fontName='Times-Italic',fontSize=20,leading=23,textColor=INK,spaceAfter=14),
 'h':ParagraphStyle('h',fontName='Helvetica-Bold',fontSize=12.5,leading=16,textColor=INK,spaceBefore=10,spaceAfter=5),
 'p':ParagraphStyle('p',fontName='Helvetica',fontSize=9.3,leading=13.5,textColor=INK,spaceAfter=9),
 'small':ParagraphStyle('small',fontName='Helvetica',fontSize=8.2,leading=12,textColor=colors.HexColor('#686D5E'),spaceAfter=8),
 'cell':ParagraphStyle('cell',fontName='Helvetica',fontSize=7.9,leading=10.5,textColor=INK),
 'code':ParagraphStyle('code',fontName='Courier',fontSize=8.1,leading=12,textColor=INK,spaceAfter=10),
}
def t(title): return ('title',title)
def sub(text): return ('sub',text)
def h(text): return ('h',text)
def p(text): return ('p',text)
def small(text): return ('small',text)
def table(rows,widths=None): return ('table',rows,widths)
def code(text): return ('code',text)
def pic(path,w,h): return ('image',str(path),w,h)
team=[['TEAM MEMBER','APP ID'],['Taher Sohagpurwala','2409540'],['Harsh Agrawal','Pending confirmation']]
proposal=[[
 t('OVERPRINT'),sub('Less ink. More intent.'),small('PROJECT PROPOSAL  /  ADVANCED ALGORITHM, CIA 3  /  2026-27'),
 table(team,[300,200]),
 h('The design problem'),
 p('A student preparing a small-run poster can easily design with eight or more screen colours, then discover that the available press supports only a few inks. Choosing which colours to merge is both a production decision and a design judgment. A simple nearest-colour replacement ignores the combined setup cost of the chosen inks; manual trial and error becomes difficult as the palette and stock catalogue grow.'),
 h('Proposed application'),
 p('OVERPRINT is a local web studio that maps a target artwork palette to available stock inks. It selects an approximate low-cost ink cover, shows the resulting colour shifts on an original SVG study, and identifies the colours a designer should inspect first. It exposes the intermediate algorithm decisions instead of hiding them behind a single score.'),
 h('Target users and workflow'),
 p('Student designers, small creative studios and print-workshop coordinators. The user enters or imports a palette, enables available inks, adjusts relative setup costs and a colour tolerance, runs the Java planner, reviews the colour mapping, then exports the plan and specimen proof. A press limit is checked after planning and reported independently from colour coverage.'),
 h('Scope of the prototype'),
 p('The prototype edits the palette of a fixed, original SVG specimen. It does not extract colours from arbitrary images. D65 CIELAB distance supplies an understandable screen-colour proxy; physical ink mixing, paper and printer calibration are outside scope. The product supports design decisions rather than claiming a press-accurate preview.'),
 small('Team size: 2. Harsh Agrawal\'s ID and final individual contributions remain to be confirmed. Topic approval and review dates are faculty decisions; no approval is implied.')
],[
 t('Methods & evidence'),sub('A design decision with visible working.'),
 table([['TECHNIQUE','ROLE AND SYLLABUS FIT'],['Weighted greedy set cover','Unit 5: an ink covers target colours within a Delta E threshold. Select minimum cost per newly covered colour. Approximate weighted setup cost; do not claim exact optimality.'],['Randomized Quickselect','Unit 6 / CO5: find the top-k error boundary and nearest-rank p90 without sorting the full error list. Random pivots; reproducible seed; expected linear time.']],[165,335]),
 h('Architecture and data'),
 p('A plain HTML/CSS/JavaScript frontend communicates with a Java HTTP API. The Java application validates input, converts colours, constructs the coverage matrix, runs both assessed algorithms and returns assignments, warnings and a decision trace. All core logic is self-implemented. No database or external account is needed.'),
 p('Synthetic data includes a poster palette, packaging palette, infeasible neon palette, exact-match case, duplicate case and invalid-empty case. Stock costs are relative weights, not market prices. Larger algorithm-only datasets are seeded and generated by the benchmark runner.'),
 h('Measurable acceptance criteria'),
 table([['CHECK','TARGET'],['Workflow','Enter/import data, change meaningful parameters, execute Java logic, interpret and export results.'],['Correctness','At least five tests per core algorithm; compare small set-cover cases with exhaustive search and selection with full sorting.'],['Scale and comparison','Record three increasing sizes; compare greedy setup cost with a per-colour baseline and Quickselect time with full sorting.'],['Honest failure handling','Expose uncovered colours, repeated inputs, invalid values and press-limit violations. Never label a partial plan as a valid proof.'],['Reproducibility','JDK 17+ setup, sample inputs, tests, source, recorded evidence, proposal and technical report.']],[125,375]),
 h('Suggested team responsibilities'),
 p('Taher: visual direction, artwork studies, interaction design and colour-model review. Harsh: algorithm review, correctness evidence, API and benchmark reproduction. These are proposed roles; the contribution record must reflect actual work completed.'),
 small('Final handoff: runnable source repository, two-page proposal, seven-page technical report, demonstration guide and editable document copies. Browser verification is pending because the managed preview infrastructure failed; local browser checks are part of the team handoff.')
]]
report=[[
 t('OVERPRINT'),sub('A design-led ink palette planner.'),small('TECHNICAL REPORT  /  CIA 3  /  ATLAS uGDX  /  SEMESTER V, B.TECH CS AI & ML'),
 table(team,[300,200]),
 h('1. Problem and objective'),
 p('The application helps a designer trade screen-colour fidelity against the setup cost of a limited ink palette. Given target colour swatches, available stock inks and a maximum permitted colour distance, it chooses a weighted greedy cover. It then identifies the largest colour changes for human review. The central design question is whether fewer ink setups can preserve the intended visual character.'),
 p('The optimisation objective is the sum of selected ink setup weights. It is not an exact minimum-ink-count solver. A separate press limit tells the user when the proposed greedy plan exceeds the available number of ink stations. Since the coverage structure depends on colour tolerance, changing that tolerance can change both feasibility and cost.'),
 h('Input, output and assumptions'),
 table([['INPUT','CONSTRAINT / INTERPRETATION'],['Target palette','1-256 six-digit sRGB colours; repeated values merge in source order. Each unique colour has equal importance; the cream background represents unprinted paper.'],['Stock inks','1-64 distinct colours; finite setup cost in (0,1000]. Costs are synthetic relative units.'],['Parameters','API tolerance 0-100 Delta E76; studio range 0-60. Press limit 1-64. Review count 1-256, clamped to palette size.'],['Output','Selected inks, nearest assignments, uncovered indices, setup weight, baseline, error review set, p90 and greedy trace.']],[125,375]),
 h('Default case'),
 p(f'The supplied poster has eight unique target colours. The executed Java plan selects four inks, covers all eight targets, and has setup weight {demo["cost"]:.1f}; the per-colour baseline also costs {demo["baselineCost"]:.1f}. This example demonstrates a usable reduction, not a measured saving over that baseline. The p90 colour shift is {demo["p90"]:.2f} Delta E76.'),
 small('All sample palettes and the specimen artwork are synthetic project studies. No production printer or external dataset is represented. Preparation date: 17 November 2026.')
],[
 t('System & workflow'),sub('Java makes the decisions.'),
 h('2. Architecture'),
 table([['LAYER','RESPONSIBILITY'],['Browser studio','Palette controls, input import, adjustable stock costs, original/proof toggle, warnings, SVG/JSON export and algorithm evidence.'],['HTTP server','JDK HttpServer, static assets, bounded URL-encoded requests, structured JSON errors and eight request threads.'],['Planner service','Input validation, duplicate normalisation, colour conversion, coverage construction, ink assignment and review-set assembly.'],['Algorithm classes','WeightedSetCover and RandomizedSelect contain self-implemented assessed algorithms. Java collections and PRNG are supporting infrastructure.'],['Evidence tools','Java correctness tests and benchmarks; independent Python HTTP integration suite. No database or external service.']],[125,375]),
 code('Browser palette / stock inks / parameters\n              | POST /api/plan\n              v\nJava validation -> sRGB/XYZ/Lab -> coverage matrix\n              |\nWeighted set cover -> nearest selected-ink errors\n              |\nRandomized Quickselect -> top-k cutoff + p90\n              | JSON\nSVG proof / ink ticket / trace / export'),
 h('API contract'),
 p('GET /api/health identifies the Java backend. POST /api/plan accepts URL-encoded targets, inks, tolerance, maxInks, review and seed. Targets are comma-separated hex values; inks are comma-separated hex:cost pairs. GET /api/benchmarks serves the recorded experiment. The request body is bounded at 64 KiB. Errors use an error string and 400, 404, 405, 413, 415 or 500 status as appropriate.'),
 h('Colour model'),
 p('sRGB channels are linearised, transformed to XYZ using the standard D65 matrix, and normalised against the D65 reference white. CIELAB coordinates follow the piecewise cube-root transform. Euclidean distance in this common Lab space is Delta E 1976. Coverage[j][i] is true exactly when the distance between stock ink j and target i is no greater than the tolerance.'),
 small('Both compared Lab values retain D65. The model is internally consistent but does not use CSS Lab\'s D50 adaptation or a printer ICC transform. It is not ink-mixing, optical-overprint or paper-absorption simulation.')
],[
 t('The ink-cover method'),sub('Cost per new colour.'),
 h('3. Weighted greedy set cover - Unit 5'),
 p('Let U contain n target colours. There are m available inks; ink j has positive cost c[j] and covers subset S[j]. Choose a family whose union covers U with low total cost. Weighted set cover is NP-hard, so this implementation uses the standard weighted greedy approximation. If the union of all available subsets is smaller than U, the uncovered colours are returned explicitly.'),
 code('covered = empty; selected = []\nwhile some target is uncovered:\n    for every unused ink j:\n        gain[j] = |S[j] minus covered|\n    choose j with minimum c[j] / gain[j], gain[j] > 0\n    if no such j exists: stop\n    selected.append(j)\n    covered = covered union S[j]\nreturn selected, U minus covered'),
 h('Correctness and termination'),
 p('Invariant: covered is exactly the union of the selected ink subsets. Initially both are empty. Each update adds precisely S[j], preserving the invariant. Every successful iteration covers at least one new colour and marks an unused ink, so there are at most min(n,m) iterations. If no positive-gain ink remains, no unselected ink covers any remaining colour. Therefore a feasible union is fully covered, while an infeasible union is reported without fabricated assignments.'),
 h('Quality bound and a deliberate counterexample'),
 p('For feasible instances with positive costs, charge each newly covered element the chosen cost/gain. The standard charging argument bounds total greedy cost by H_n times the optimal weighted cover, where H_n = 1 + 1/2 + ... + 1/n. This bound does not apply to satisfying a separate hard ink-count budget. The app checks that budget after selection.'),
 p('For three colours, A covers the first two at cost 1.9, B covers only the third at cost 2, and C covers all three at cost 3. Greedy first takes A (0.95 per new colour), then B, costing 3.9. The optimum C costs 3. This case is a passing test precisely because the program does not claim exact optimality.'),
 h('Time and space'),
 p('The colour-distance and coverage matrices cost O(nm) time and space to build. Each of r selected inks requires scanning m candidates and n colours: O(rmn), with r <= min(n,m). The solver adds O(n+m) working space beyond its input matrix. The baseline chooses the cheapest eligible ink independently for each colour and deduplicates the resulting set in O(nm) time.'),
 small('The implementation uses boolean arrays, not bitsets. Candidate-order tie breaking is deterministic. It minimises weighted cost heuristically; it does not optimise perceptual error among all equally priced covers.')
],[
 t('The review method'),sub('Find the boundary, keep the order.'),
 h('4. Randomized Quickselect - Unit 6 / CO5'),
 p('After selection, each target is mapped to its nearest selected ink. The resulting error array has one distance per unique target. The review count k defines a practical attention budget: the designer will inspect k colours. Quickselect finds ascending zero-based rank n-k, the boundary of the k largest errors. A second call finds nearest-rank p90 at ceil(0.9n)-1.'),
 code('a = copy(errors); low = 0; high = n - 1\nwhile low < high:\n    pivot = a[random index in low..high]\n    partition a[low..high] into <, = and > pivot\n    if rank is in the equal interval: return pivot\n    if rank is left of the equal interval: shrink high\n    else: advance low\nreturn a[low]'),
 h('Partition invariant and correctness'),
 p('During three-way partitioning, the completed left region contains values below the pivot, the middle region contains equal values, and the completed right region contains greater values. Each iteration classifies an unknown element, so the unknown interval shrinks. When partitioning ends, any requested rank in the equal region has the pivot value. Otherwise removing the opposite region cannot change the requested order statistic. Repeating eventually yields the correct value.'),
 p('All errors above the cutoff enter the review set. Boundary ties are added in original palette order until exactly k colours are selected. The result is a review set, not a fully sorted ranking. The public selection method clones the error array so original colour-index relationships remain intact.'),
 h('Randomisation, complexity and reproducibility'),
 p('The pivot index comes from Java Random using a supplied seed; the UI fixes it to 2409540. Random-pivot selection has expected O(n) time, while unlucky sequences can require O(n squared). Three-way partitioning handles equal values in one partition. The iterative implementation uses O(1) partition state, but the input-preserving copy makes total extra space O(n). The follow-up review scan is O(n).'),
 p('A fixed seed supports repeatable demonstrations and test traces; it does not imply a deterministic worst-case linear-time guarantee. The operation counter records element classifications, not the exact number of primitive less-than/greater-than comparisons.'),
 h('Missing and partial plans'),
 p('If no ink can be selected, assignments and error quantiles are null and the review set is empty. For a partial plan, errors are measured against the nearest selected ink, including out-of-tolerance targets; uncovered indices remain explicit. The visual proof retains unmatched original colours and disables valid-proof export until full coverage and press-limit compliance are achieved.')
],[
 t('Correctness evidence'),sub('Check the claim independently.'),
 h('5. Verification strategy'),
 p('The Java suite contains 22 named checks, including 1,200 generated oracle cases. Exhaustive subset enumeration is independent of the greedy algorithm; full sorting is independent of Quickselect. Five colour/planner checks and boundary checks supplement the two core-method suites. Detailed names and results are in results/tests.txt.'),
 table([['CORE METHOD','DOCUMENTED CHECKS AND EXPECTED BEHAVIOUR'],['Set cover SC01-SC03','Empty universe costs zero; shared ink can beat separate inks; weighted cost/gain can beat choosing the largest raw coverage.'],['Set cover SC04-SC06','Unreachable colours remain uncovered; equal ratios use candidate order; empty stock leaves all targets uncovered.'],['Set cover SC07-SC08','Invalid cost/dimensions rejected; explicit 3.9 versus 3.0 counterexample confirms non-optimal greedy behaviour.'],['Set cover SC09','200 seeded small feasible instances checked for actual coverage, cost >= exact optimum and cost <= H_n times optimum.'],['Quickselect QS01-QS03','Singleton; minimum/maximum rank; duplicate values preserve rank semantics.'],['Quickselect QS04-QS06','All-equal input terminates in one partition; sorted/reversed arrays; input preserved and seeded traces repeat.'],['Quickselect QS07-QS08','Empty/bad-rank/non-finite input rejected; 1,000 random arrays match an independent full-sort order statistic.']],[125,375]),
 h('Integration and numerical checks'),
 p('Known D65 black, white and red coordinates check colour conversion; identity distance must be zero. Planner tests check duplicate consolidation, exact top-k tie handling, null statistics with no eligible ink and separate press-limit warnings. Six invalid input classes are exercised through the HTTP API.'),
 p('The separate HTTP suite passes 19 checks: Java health, HTML/CSS/JS delivery, the default four-ink plan, exact assignments, review cardinality, zero tolerance, duplicate targets, infeasible neon, budget warnings, invalid payloads, request size, content type, method handling, repeated keys, missing/path-traversal requests and benchmark delivery.'),
 h('Observed default output'),
 p('The executed default trace chooses Carbon, Marigold, Vermilion and Cobalt in that order. Each covers two new colours. Their cost/new-colour scores are 0.55, 0.75, 0.95 and 1.05. The complete machine-readable output is in results/demo-plan.json.'),
 small('Verification limit: managed browser and preview relay did not initialise. Browser layout, keyboard traversal, imports and download interactions remain pending local checks. JavaScript syntax and the generated SVG are verified separately; no browser screenshots or passed UI tests are claimed.')
],[
 t('Measured performance'),sub('Three sizes. Two comparisons.'),
 h('6. Methodology'),
 p(f'The Java benchmark uses nested synthetic colour records of 100, 1,000 and 10,000 elements, 32 fixed stock inks and tolerance 18. A seeded generator (2409540) perturbs RGB samples around stock colours. Some perturbations can remain outside tolerance; coverage is reported. Each method has 15 warmups and 21 measured repetitions; the median is recorded. Environment: Java {b["java"]}, {b["os"]}, {b["processors"]} reported processors.'),
 p('The timed kernels exclude colour conversion, coverage construction, network transport and SVG rendering. Quickselect and full sorting both include input cloning. A volatile sink consumes results. These shared-machine microbenchmarks are indicative, not JMH or production latency measurements. Large arrays call algorithm classes directly; the UI has a separate 256-colour validation limit.'),
 table([['n','GREEDY ms','BASELINE ms','SELECT ms','SORT ms']]+[[str(r['n']),f'{r["greedyMs"]:.3f}',f'{r["baselineMs"]:.3f}',f'{r["quickselectMs"]:.3f}',f'{r["sortMs"]:.3f}'] for r in b['rows']],[65,110,110,110,105]),
 table([['n','COVERED','GREEDY COST','BASELINE COST','INKS']]+[[str(r['n']),f'{r["covered"]}/{r["n"]}',f'{r["greedyCost"]:.1f}',f'{r["baselineCost"]:.1f}',str(r['greedyInks'])] for r in b['rows']],[65,110,110,110,105]),
 h('Interpretation'),
 p('Quickselect is faster than full sorting at each recorded size. At 10,000 elements the measured full-sort time is %.2f times the selection time. This is consistent with the expected linear versus n log n distinction, but three timings do not prove an asymptotic bound. Small-input results are sensitive to JVM warmup and measurement overhead.' % (b['rows'][-1]['sortMs']/b['rows'][-1]['quickselectMs'])),
 p('Greedy spends more time than the per-colour baseline in every recorded row. Its purpose is a coordinated cost choice, not a faster scan. Setup weight ties the baseline at n=100, and is lower by 2.5 units at n=1,000 and n=10,000. Neither result establishes universal superiority. At the largest size, 19 targets remain outside all available ink coverage; cost comparisons apply to the shared reachable universe.'),
 h('Reproduce'),code('./run.sh test\n./run.sh benchmark\npython3 scripts/test_api.py'),
 small('Raw outputs: results/benchmarks.json and results/benchmarks.csv. Source: src/test/java/studio/Benchmark.java. Re-running overwrites recorded results; regenerate this document afterwards with scripts/build_documents.py so tables stay consistent.')
],[
 t('Scope & handoff'),sub('What the result can honestly say.'),
 h('7. Limitations and next steps'),
 p('The model compares individual stock-ink colours to unique target swatches. It ignores image area, ink mixing, overprint transparency, paper, lighting, dot gain and ICC profiles. Delta E76 is not uniformly perceptual across all colours. Setup weights are synthetic. Greedy minimises cost approximately, then checks the press limit; it can exceed that limit even if another valid smaller cover exists. The fixed specimen demonstrates palette changes rather than arbitrary image processing.'),
 p('A useful next iteration would accept a student-authored SVG with controlled fill extraction, compare Delta E2000 against the current metric, add a small-instance exact solver for quality studies, and collect calibrated stock-ink measurements. A hard cardinality-constrained solver would be a distinct optimisation feature and needs its own correctness and complexity analysis.'),
 h('Contribution record'),
 table([['MEMBER','PROPOSED AREA; ACTUAL WORK TO CONFIRM'],['Taher Sohagpurwala / 2409540','Visual direction, artwork studies, interaction design and colour-model review.'],['Harsh Agrawal / ID pending','Algorithm review, tests, benchmark reproduction and API walkthrough.']],[190,310]),
 p('Initial code, synthetic assets and document drafts were prepared with development assistance. The tests were executed in the managed environment. Proposed roles above are not verified contribution claims. Each student must record actual changes and be able to explain both core methods; see docs/CONTRIBUTIONS.md.'),
 h('Reproducibility and submission status'),
 p('JDK 17 or newer is sufficient. Run ./run.sh on macOS/Linux, or run.cmd on Windows, and open http://127.0.0.1:3000. No runtime dependencies, external accounts, secrets or database are needed. The source package includes samples, tests, raw benchmark results, a demo guide and editable documents. Confirm Harsh\'s ID, local browser checks, faculty scope approval and individual contributions before submission.'),
 h('References'),
 small('1. Cormen, Leiserson, Rivest and Stein. Introduction to Algorithms, 4th ed., MIT Press, 2022. Randomized selection and approximation algorithms.<br/>2. Chvatal, V. A Greedy Heuristic for the Set-Covering Problem. Mathematics of Operations Research 4(3), 233-235, 1979. DOI: 10.1287/moor.4.3.233.<br/>3. CIE. Colorimetry, 3rd ed., CIE 15:2004.<br/>4. W3C. CSS Color Module Level 4, sample sRGB/XYZ conversion methods. https://www.w3.org/TR/css-color-4/ . Both app Lab values retain D65.<br/>5. Supplied ATLAS uGDX CIA 3 Advanced Algorithm Project Guidelines, 2026-27. Assessment brief.'),
 small('IDEATION RECORD: 15 initial ideas were rejected in full, followed by a new set of 15. OVERPRINT was selected from the second set for visual authorship, meaningful algorithm integration and a reproducible scope. The complete process is in docs/IDEA_PROCESS.md.')
]]

def draw_page(c,doc):
    c.saveState(); c.setFillColor(PAPER); c.rect(0,0,595.276,841.89,fill=1,stroke=0)
    c.setStrokeColor(INK); c.setLineWidth(.6);c.line(47,800,548,800)
    c.setFillColor(INK);c.setFont('Helvetica-Bold',9);c.drawString(47,810,'OVERPRINT')
    c.setFont('Courier',7);c.drawRightString(548,810,'DESIGN x ALGORITHMS / 2026-27')
    c.setFillColor(ORANGE);c.rect(47,28,24,3,fill=1,stroke=0)
    c.setFillColor(INK);c.setFont('Helvetica',7);c.drawString(79,27,doc.title)
    c.setFont('Courier',8);c.drawRightString(548,27,f'{doc.page:02d}')
    c.restoreState()

def make_pdf(name,pages):
    doc=SimpleDocTemplate(str(OUT/(name+'.pdf')),pagesize=(595.276,841.89),leftMargin=47,rightMargin=48,topMargin=63,bottomMargin=48,title='OVERPRINT / '+name.replace('_',' '),author='Project team draft')
    flow=[]
    for page_i,page in enumerate(pages):
        if page_i:flow.append(PageBreak())
        for e in page:
            kind=e[0]
            if kind in styles and kind!='code':flow.append(Paragraph(e[1],styles[kind]))
            elif kind=='code':
                block=Preformatted(e[1],styles['code']);flow.extend([Spacer(1,6),block])
            elif kind=='image':flow.append(Image(e[1],width=e[2],height=e[3]))
            elif kind=='table':
                rows=[[Paragraph(html.escape(str(x)),styles['cell']) for x in row] for row in e[1]]
                tb=Table(rows,colWidths=e[2],hAlign='LEFT',repeatRows=1)
                tb.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E2E2D7')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.8,INK),('LINEBELOW',(0,1),(-1,-1),.35,colors.HexColor('#D0D1C3')),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
                flow.extend([Spacer(1,7),tb,Spacer(1,8)])
    doc.build(flow,onFirstPage=draw_page,onLaterPages=draw_page)

def plain(s):return s.replace('<br/>','\n').replace('<b>','').replace('</b>','')
def make_docx(name,pages):
    doc=Document();section=doc.sections[0];section.top_margin=Inches(.75);section.bottom_margin=Inches(.65)
    normal=doc.styles['Normal'];normal.font.name='Calibri';normal.font.size=Pt(10)
    normal.paragraph_format.space_after=Pt(7)
    for sty in ['Title','Heading 1','Heading 2']:
        doc.styles[sty].font.color.rgb=RGBColor.from_string('242720')
    section.header.paragraphs[0].text='OVERPRINT                                      DESIGN x ALGORITHMS / 2026-27'
    for i,page in enumerate(pages):
        if i:doc.add_page_break()
        for e in page:
            if e[0]=='table':
                tb=doc.add_table(rows=0,cols=len(e[1][0]));tb.style='Light Shading Accent 1'
                for row in e[1]:
                    cells=tb.add_row().cells
                    for cell,text in zip(cells,row):cell.text=str(text)
            elif e[0]=='image':doc.add_picture(e[1],width=Inches(e[2]/72))
            elif e[0]=='code':
                run=doc.add_paragraph().add_run(e[1]);run.font.name='Consolas';run.font.size=Pt(9)
            elif e[0]=='title':doc.add_heading(plain(e[1]),0)
            elif e[0]=='sub':doc.add_paragraph(plain(e[1]),'Subtitle')
            elif e[0]=='h':doc.add_heading(plain(e[1]),2)
            else:doc.add_paragraph(plain(e[1]))
    doc.save(OUT/(name+'.docx'))

for name,pages in [('Proposal',proposal),('Technical_Report',report)]:
    make_pdf(name,pages);make_docx(name,pages)
    lines=[]
    for page in pages:
        for e in page:
            if e[0] in ('title','sub','h','p','small'):lines.append(('# ' if e[0]=='title' else '## ' if e[0]=='h' else '')+plain(e[1]))
            elif e[0]=='code':lines.append('```text\n'+e[1]+'\n```')
            elif e[0]=='table':
                rows=e[1];lines.append('\n'.join([' | '.join(str(x) for x in rows[0]),' | '.join('---' for _ in rows[0])]+[' | '.join(str(x) for x in row) for row in rows[1:]]))
    (OUT/(name+'.md')).write_text('\n\n'.join(lines)+'\n')
    print('Generated',name)
