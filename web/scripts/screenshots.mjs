// Gera as imagens da documentação com dados de demonstração (sem rede e sem servidor de API).
// Uso: npm run build && npx vite preview --port 4173   e depois   npm run screenshots -- ../website/static/img/screenshots
// Com --real, antes de tudo faz uma consulta de verdade pelo proxy (precisa da API no ar) e falha se houver erro no console.
import {chromium} from 'playwright';

import {ALTO, SEM_INDICIOS} from '../tests/fixtures.ts';

const args = process.argv.slice(2);
const real = args.includes('--real');
const out = args.find((a) => !a.startsWith('--')) ?? '.';
const BASE = process.env.CONFERE_WEB ?? 'http://localhost:4173';

const ATENCAO = {
  ...SEM_INDICIOS,
  nivel: 'atencao',
  pontuacao: 35,
  sinais: [
    {codigo: 'EMPRESA_NOVA', gravidade: 'atencao', peso: 25, mensagem: 'Empresa aberta há menos de 6 meses.', regra: 'Início de atividade entre 30 e 179 dias atrás.'},
    {codigo: 'SEM_CONTATO_PUBLICO', gravidade: 'atencao', peso: 10, mensagem: 'Sem e-mail nem telefone públicos no cadastro.', regra: 'Nenhum e-mail ou telefone no cadastro.'},
  ],
  empresa: {...SEM_INDICIOS.empresa, data_abertura: '2026-07-20'},
};
const MEI = {
  ...SEM_INDICIOS,
  sinais: [{codigo: 'EMPRESARIO_INDIVIDUAL', gravidade: 'info', peso: 0, mensagem: 'Empresário individual ou MEI: o CNPJ identifica uma pessoa. Nome e endereço foram omitidos.', regra: 'Natureza jurídica 2135 ou opção pelo MEI. Só mostramos o necessário (LGPD).'}],
  empresa: {...SEM_INDICIOS.empresa, individual: true, razao_social: null, nome_fantasia: null, capital_social: null, socios_total: 0, socios_qualificacoes: []},
};
const PIX_OK = {
  ...SEM_INDICIOS,
  instituicao: {ispb: '00000000', nome: 'BCO DO BRASIL S.A.', codigo_compe: 1, participa_pix: true, modalidade_pix: 'Provedor de Conta Transacional', tipo_participacao: 'Direta'},
  limites: 'Só confirmamos que a instituição existe e participa do Pix. Não verificamos o titular da chave nem a conta de destino.',
};

const EN_TEXT = {
  [ATENCAO.sinais[0].codigo]: ['Company opened less than 6 months ago.', 'Activity start between 30 and 179 days ago.'],
  [ATENCAO.sinais[1].codigo]: ['No public e-mail or phone in the registry.', 'No e-mail or phone in the registry.'],
};
const emIngles = (r) => ({
  ...r,
  sinais: r.sinais.map((s) => (EN_TEXT[s.codigo] ? {...s, mensagem: EN_TEXT[s.codigo][0], regra: EN_TEXT[s.codigo][1]} : s)),
  aviso: 'Indications from public data; not proof of fraud nor a credit analysis. No signals does not mean it is safe.',
});

const browser = await chromium.launch();

async function contexto({lang, scheme = 'light', w = 1100, h = 800, mock}) {
  const ctx = await browser.newContext({viewport: {width: w, height: h}, colorScheme: scheme, locale: lang === 'en' ? 'en-US' : 'pt-BR'});
  await ctx.addInitScript((l) => localStorage.setItem('confere.idioma', l), lang);
  const page = await ctx.newPage();
  if (mock) {
    await page.route('**/v1/**', (route) => {
      const r = mock(route.request());
      return route.fulfill({status: r.status ?? 200, contentType: 'application/json', body: JSON.stringify(r.body)});
    });
  }
  return page;
}

async function consultar(page, {pagar = false, cnpj = '11.222.333/0001-81', inst = '00000000'}) {
  const t = await page.evaluate(() => document.documentElement.lang);
  if (pagar) await page.getByRole('tab').nth(1).click();
  await page.getByRole('textbox').first().fill(cnpj);
  if (pagar) await page.getByRole('textbox').nth(1).fill(inst);
  await page.getByRole('button', {name: t === 'en' ? 'Check' : 'Conferir'}).click();
  await page.waitForSelector('.resultado, .erro');
  await page.waitForTimeout(150);
}

if (real) {
  const page = await contexto({lang: 'pt-BR'});
  const problemas = [];
  page.on('console', (m) => ['error', 'warning'].includes(m.type()) && problemas.push(m.text()));
  page.on('pageerror', (e) => problemas.push(String(e)));
  await page.goto(BASE);
  await consultar(page, {cnpj: '00.000.000/0001-91'});
  const nivel = await page.locator('.nivel-titulo').textContent();
  console.log('consulta real:', nivel);
  if (problemas.length || !nivel) {
    console.error('problemas no console:', problemas);
    process.exit(1);
  }
}

for (const lang of ['pt-BR', 'en']) {
  const sfx = lang === 'en' ? '-en' : '';
  const loc = (r) => (lang === 'en' ? emIngles(r) : r);
  const shot = (page, nome, opts = {}) => page.screenshot({path: `${out}/app-${nome}${sfx}.png`, ...opts});
  const porCaminho = (map) => (req) => {
    const u = new URL(req.url());
    return map(u.pathname, req) ?? {status: 500, body: {codigo: 'desconhecido'}};
  };

  let page = await contexto({lang, mock: porCaminho(() => ({body: loc(SEM_INDICIOS)}))});
  await page.goto(BASE);
  await shot(page, 'conferir');
  await consultar(page, {});
  await shot(page, 'resultado-empresa', {fullPage: true});
  await page.close();

  page = await contexto({lang, mock: porCaminho(() => ({body: loc(ATENCAO)}))});
  await page.goto(BASE);
  await consultar(page, {});
  await page.locator('details').first().locator('summary').click();
  await shot(page, 'resultado-atencao', {fullPage: true});
  await page.close();

  page = await contexto({lang, mock: porCaminho(() => ({body: loc(MEI)}))});
  await page.goto(BASE);
  await consultar(page, {});
  await shot(page, 'resultado-mei', {fullPage: true});
  await page.close();

  page = await contexto({lang, mock: porCaminho(() => ({body: loc(PIX_OK)}))});
  await page.goto(BASE);
  await consultar(page, {pagar: true});
  await shot(page, 'pode-pagar', {fullPage: true});
  await page.close();

  page = await contexto({lang, mock: porCaminho(() => ({body: {...loc(ALTO), limites: lang === 'en' ? 'We only confirm that the institution exists and takes part in Pix. We do not verify the key holder or the destination account.' : ALTO.limites}}))});
  await page.goto(BASE);
  await consultar(page, {pagar: true, inst: '12345678'});
  await shot(page, 'pode-pagar-alto', {fullPage: true});
  await page.close();

  page = await contexto({lang, mock: porCaminho(() => ({status: 422, body: {codigo: 'cnpj_invalido', mensagem: 'x'}}))});
  await page.goto(BASE);
  await consultar(page, {cnpj: '11222333000182'});
  await shot(page, 'erro');
  await page.close();

  page = await contexto({lang, scheme: 'dark', mock: porCaminho(() => ({body: loc(ATENCAO)}))});
  await page.goto(BASE);
  await consultar(page, {});
  await shot(page, 'escuro', {fullPage: true});
  await page.close();

  page = await contexto({lang, w: 390, h: 800, mock: porCaminho(() => ({body: loc(ATENCAO)}))});
  await page.goto(BASE);
  await consultar(page, {});
  await shot(page, 'celular', {fullPage: true});
  await page.close();

  // Explorar: dados de demonstração (sem rede). Os nomes de corretoras são fictícios.
  const colunas = {
    bancos: ['codigo_compe', 'ispb', 'nome', 'nome_completo', 'participa_pix'],
    municipios: ['codigo_ibge', 'nome', 'uf'],
    ncm: ['codigo', 'descricao', 'data_inicio', 'data_fim'],
    corretoras: ['cnpj', 'nome_social', 'nome_comercial', 'status', 'uf', 'municipio', 'codigo_cvm', 'data_registro'],
  };
  const linhas = {
    bancos: [
      {codigo_compe: 1, ispb: '00000000', nome: 'BCO DO BRASIL S.A.', nome_completo: 'Banco do Brasil S.A.', participa_pix: true},
      {codigo_compe: 33, ispb: '90400888', nome: 'BCO SANTANDER (BRASIL) S.A.', nome_completo: 'Banco Santander (Brasil) S.A.', participa_pix: true},
      {codigo_compe: 341, ispb: '60701190', nome: 'ITAÚ UNIBANCO S.A.', nome_completo: 'ITAÚ UNIBANCO S.A.', participa_pix: true},
    ],
    municipios: [
      {codigo_ibge: '3509502', nome: 'CAMPINAS', uf: 'SP'},
      {codigo_ibge: '3550308', nome: 'SÃO PAULO', uf: 'SP'},
      {codigo_ibge: '3548500', nome: 'SANTOS', uf: 'SP'},
    ],
    ncm: [
      {codigo: '09.01', descricao: 'Café, mesmo torrado ou descafeinado; cascas e películas de café.', data_inicio: '2022-04-01', data_fim: '9999-12-31'},
      {codigo: '0901.21.00', descricao: '- - Não descafeinado', data_inicio: '2022-04-01', data_fim: '9999-12-31'},
      {codigo: '0901.22.00', descricao: '- - Descafeinado', data_inicio: '2022-04-01', data_fim: '9999-12-31'},
    ],
    corretoras: [
      {cnpj: '11.222.333/0001-81', nome_social: 'EXEMPLO CORRETORA DE VALORES S.A.', nome_comercial: 'EXEMPLO', status: 'EM FUNCIONAMENTO NORMAL', uf: 'SP', municipio: 'SÃO PAULO', codigo_cvm: '1234', data_registro: '1990-05-10'},
      {cnpj: '11.444.777/0001-61', nome_social: 'MODELO DTVM LTDA', nome_comercial: null, status: 'CANCELADA', uf: 'RJ', municipio: 'RIO DE JANEIRO', codigo_cvm: '5678', data_registro: '2001-02-03'},
    ],
  };
  const ufs = {itens: [{sigla: 'RJ', nome: 'Rio de Janeiro'}, {sigla: 'SP', nome: 'São Paulo'}]};
  const mockDados = (req) => {
    const u = new URL(req.url());
    if (u.pathname === '/v1/dados/ufs') return {body: ufs};
    const c = u.pathname.split('/').pop();
    return {body: {conjunto: c, total: linhas[c].length, limite: 25, offset: 0, colunas: colunas[c], itens: linhas[c]}};
  };
  const ROT = lang === 'en'
    ? {bancos: 'Banks', municipios: 'Municipalities', ncm: 'NCM codes', corretoras: 'Brokers (CVM)', uf: 'State', busca: 'Search'}
    : {bancos: 'Bancos', municipios: 'Municípios', ncm: 'NCM', corretoras: 'Corretoras (CVM)', uf: 'UF', busca: 'Buscar'};
  for (const [nome, aba, busca, uf] of [
    ['explorar', ROT.bancos, '', ''],
    ['explorar-municipios', ROT.municipios, '', 'SP'],
    ['explorar-ncm', ROT.ncm, 'café', ''],
    ['explorar-corretoras', ROT.corretoras, '', ''],
  ]) {
    page = await contexto({lang, mock: mockDados});
    await page.goto(`${BASE}/explorar`);
    await page.getByRole('tab', {name: aba}).click();
    if (uf) await page.getByLabel(ROT.uf).selectOption(uf);
    if (busca) await page.getByLabel(ROT.busca, {exact: true}).fill(busca);
    await page.waitForSelector('table');
    await page.waitForTimeout(500);
    await shot(page, nome, {fullPage: true});
    await page.close();
  }

  for (const [rota, nome] of [['/api', 'api'], ['/privacidade', 'privacidade']]) {
    page = await contexto({lang});
    await page.goto(`${BASE}${rota}`);
    await shot(page, nome);
    await page.close();
  }
}
await browser.close();
console.log('imagens geradas em', out);
