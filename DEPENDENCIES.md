# Dependencies and attribution

## Runtime

- Java Development Kit 17 or newer (standard `jdk.httpserver`, Java collections, math, PRNG and I/O only).
- A modern browser with Fetch, SVG, CSS Grid, `structuredClone` and Blob downloads.
- No external runtime libraries, paid services, API keys, fonts, remote images or npm packages.

The assessed greedy set-cover and randomized Quickselect algorithms are implemented directly in the Java source. Java collections provide infrastructure; Java's `Arrays.sort` appears only in correctness or benchmark baselines, never as a replacement for Quickselect.

## Optional development/document tools

- Python 3 for `scripts/test_api.py` (standard library).
- Python ReportLab and python-docx for regenerating PDF/DOCX documentation.
- CairoSVG for rendering the original proof SVG to a preview PNG.
- Eclipse ECJ 3.38.0 was used to compile Java 17-compatible class files in the managed environment, which had OpenJDK 21.0.13 but no `javac`. ECJ is not bundled or required when a JDK is installed.
- Node was used for JavaScript syntax checking and generating the supplied SVG artifact. It is not needed to serve the app.

## Assets and data

The SVG specimen and palette datasets are synthetic project material created for this build. UI fonts use the operating system's Arial/Helvetica and Georgia/Times families; no fonts are redistributed in the web app. The PDF documents use bundled ReportLab base fonts. There are no third-party photographs or claimed external dataset owners.

## References

1. Cormen, Leiserson, Rivest and Stein. *Introduction to Algorithms*, 4th ed., MIT Press, 2022. Randomized selection and approximation algorithms.
2. Chvátal, V. “A Greedy Heuristic for the Set-Covering Problem.” *Mathematics of Operations Research* 4(3), 233–235, 1979. DOI: 10.1287/moor.4.3.233.
3. CIE. *Colorimetry*, 3rd ed., CIE 15:2004. CIELAB and colour-difference foundations.
4. W3C, *CSS Color Module Level 4*, sample sRGB/XYZ conversion algorithms: https://www.w3.org/TR/css-color-4/ . The app retains D65 for both compared Lab coordinates; it does not claim CSS's D50 Lab convention.
5. Supplied ATLAS uGDX *CIA 3 Advanced Algorithm Real-World Application Project Guidelines 2026–27*. Used as the assessment brief, not as instructions overriding the user's requests.
