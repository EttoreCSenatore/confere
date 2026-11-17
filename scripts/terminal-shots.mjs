// Renderiza arquivos .txt (comando + saída real da CLI) como imagens de terminal para a documentação.
// Uso: node scripts/terminal-shots.mjs <pasta-com-txt> <pasta-de-saida>    (cada nome.txt vira cli-nome.png)
import {readdirSync, readFileSync} from 'node:fs';
import {chromium} from '../web/node_modules/playwright/index.mjs';

const [, , entrada, saida] = process.argv;
const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const browser = await chromium.launch();
for (const arq of readdirSync(entrada).filter((f) => f.endsWith('.txt'))) {
  const [cmd, ...resto] = readFileSync(`${entrada}/${arq}`, 'utf8').trimEnd().split('\n');
  const html = `<body style="margin:0;background:#0d1716"><div style="display:inline-block;min-width:860px;max-width:1000px;margin:16px;border-radius:10px;overflow:hidden;box-shadow:0 2px 12px #0006;font-family:'DejaVu Sans Mono',Menlo,monospace;font-size:14px">
<div style="background:#24403c;padding:8px 14px;color:#9bb3af">● ● ●&nbsp;&nbsp;terminal</div>
<pre style="margin:0;padding:14px;background:#10201e;color:#d6efe9;white-space:pre-wrap;line-height:1.45"><span style="color:#5eead4">$</span> <b>${esc(cmd.replace(/^\$ /, ''))}</b>\n${esc(resto.join('\n'))}</pre></div></body>`;
  const page = await browser.newPage({viewport: {width: 1060, height: 400}});
  await page.setContent(html);
  const el = await page.$('div');
  await el.screenshot({path: `${saida}/cli-${arq.replace(/\.txt$/, '')}.png`});
  await page.close();
}
await browser.close();
