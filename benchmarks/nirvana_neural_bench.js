'use strict';
// Benchmark Nirvana Neural Memory: index + recall + query scaling. Temp projects only.
const fs = require('fs'), os = require('os'), path = require('path');
const NEURAL = path.join(process.argv[2], 'templates', 'neural');
const { NeuralMemory } = require(path.join(NEURAL, 'lib', 'memory.js'));
const { recall } = require(path.join(NEURAL, 'lib', 'recall.js'));
const G = require(path.join(NEURAL, 'lib', 'graph.js'));
const med = (a) => { const s = [...a].sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };
const p95 = (a) => { const s = [...a].sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(s.length * 0.95))]; };
const now = () => Number(process.hrtime.bigint()) / 1e6;
const out = {};

function mkProject(n) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'nirv-bench-'));
  fs.mkdirSync(path.join(root, 'docs', 'knowledge'), { recursive: true });
  const files = ['patterns.md', 'errors-aprendidos.md', 'business-rules.md'];
  const per = Math.ceil(n / files.length);
  files.forEach((f, fi) => {
    let txt = `# ${f}\n\n`;
    for (let i = 0; i < per; i++) {
      const k = fi * per + i;
      txt += `## Pattern number ${k} repository variant\nUse repository pattern variant ${k} for persistence with PostgreSQL module m${k % 20} and cache redis${k % 7}. Decision about authentication flow ${k % 13}.\n\n`;
    }
    fs.writeFileSync(path.join(root, 'docs', 'knowledge', f), txt);
  });
  fs.writeFileSync(path.join(root, 'docs', 'decisions.md'), '# Decisoes\n\n## Adotar PostgreSQL\nPostgreSQL principal.\n');
  return root;
}

(async () => {
  for (const n of [100, 1000, 5000]) {
    const root = mkProject(n);
    const mem = new NeuralMemory(root);
    let t = now();
    const r = await mem.indexSources('writer');
    const indexMs = now() - t;
    const s = mem.stats();
    const rec = [];
    for (let i = 0; i < 30; i++) { t = now(); await recall(mem, { role: 'architect', task: `melhorar autenticacao variant ${i * 7}`, budget: 1200 }); rec.push(now() - t); }
    const q = [];
    for (let i = 0; i < 30; i++) { t = now(); G.search(mem, `variant ${i * 3}`); q.push(now() - t); }
    // cold reopen (load event log from disk)
    t = now(); const m2 = new NeuralMemory(root); m2.stats(); const reopen = now() - t;
    let bytes = 0; const walk = (d) => { for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, e.name); e.isDirectory() ? walk(p) : (bytes += fs.statSync(p).size); } };
    walk(path.join(root, '.claude', 'neural') );
    out[`n=${n}`] = { index_ms: indexMs, memories: s.memories, connections: s.connections, events: s.events,
      recall_median_ms: med(rec), recall_p95_ms: p95(rec), search_median_ms: med(q), reopen_ms: reopen, store_bytes: bytes };
    console.log(n, JSON.stringify(out[`n=${n}`]));
  }
  fs.writeFileSync(process.argv[3], JSON.stringify(out, null, 2));
})().catch((e) => { console.error(e); process.exit(4); });
