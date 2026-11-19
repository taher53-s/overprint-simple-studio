// Optional: regenerate the actual default plan's SVG with the same renderer as the UI.
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const { svgArtwork } = require(path.join(root, 'web/artwork.js'));
const { result } = JSON.parse(fs.readFileSync(path.join(root, 'results/demo-plan.json')));
if (!result.feasible || !result.withinPressLimit) throw new Error('The recorded plan is not exportable.');
fs.writeFileSync(path.join(root, 'docs/Proof_Study.svg'), svgArtwork(result.mappings.map(x => x.ink), 'REMAPPED / SCREEN STUDY'));
console.log('Wrote docs/Proof_Study.svg');
