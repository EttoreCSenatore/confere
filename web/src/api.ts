// Cliente da API do Confere. Os dados da consulta vão no corpo (POST) ou no caminho, nunca em query string
// com dados pessoais; nada é guardado no navegador.

export type Sinal = {codigo: string; gravidade: 'alto' | 'atencao' | 'info'; peso: number; mensagem: string; regra: string};
export type Empresa = {
  cnpj: string;
  individual: boolean;
  razao_social: string | null;
  nome_fantasia: string | null;
  situacao: string;
  data_abertura: string | null;
  natureza_juridica: string | null;
  porte: string | null;
  capital_social: number | null;
  optante_simples: boolean | null;
  mei: boolean | null;
  cnae_principal: {codigo: number | null; descricao: string | null};
  municipio: string | null;
  uf: string | null;
  socios_total: number;
  socios_qualificacoes: string[];
};
export type Instituicao = {
  ispb: string;
  nome: string;
  codigo_compe: number | null;
  participa_pix: boolean;
  modalidade_pix: string | null;
  tipo_participacao: string | null;
};
export type Nivel = 'sem_indicios' | 'atencao' | 'alto';
export type Resposta = {
  cnpj: string;
  consultado_em: string;
  nivel: Nivel;
  pontuacao: number;
  sinais: Sinal[];
  empresa: Empresa;
  aviso: string;
  fonte: {nome: string; url: string};
  instituicao?: Instituicao | null;
  limites?: string;
};

export type CodigoErro =
  | 'cnpj_invalido'
  | 'instituicao_invalida'
  | 'nao_encontrado'
  | 'limite_excedido'
  | 'fonte_indisponivel'
  | 'filtro_invalido'
  | 'requisicao_invalida'
  | 'conjunto_desconhecido'
  | 'rede'
  | 'desconhecido';

export class ErroApi extends Error {
  constructor(public codigo: CodigoErro) {
    super(codigo);
  }
}

const CONHECIDOS = new Set<CodigoErro>([
  'cnpj_invalido',
  'instituicao_invalida',
  'nao_encontrado',
  'limite_excedido',
  'fonte_indisponivel',
  'filtro_invalido',
  'requisicao_invalida',
  'conjunto_desconhecido',
]);

async function tratar<T = Resposta>(resp: Response): Promise<T> {
  if (resp.ok) return (await resp.json()) as T;
  let codigo: CodigoErro = 'desconhecido';
  try {
    const corpo = (await resp.json()) as {codigo?: string};
    if (corpo.codigo && CONHECIDOS.has(corpo.codigo as CodigoErro)) codigo = corpo.codigo as CodigoErro;
  } catch {
    /* corpo sem JSON */
  }
  throw new ErroApi(codigo);
}

async function chamar<T = Resposta>(url: string, init: RequestInit): Promise<T> {
  try {
    return await tratar<T>(await fetch(url, {...init, credentials: 'omit', referrerPolicy: 'no-referrer', cache: 'no-store'}));
  } catch (e) {
    if (e instanceof ErroApi) throw e;
    if (e instanceof DOMException && e.name === 'AbortError') throw e;
    throw new ErroApi('rede');
  }
}

export const conferirCnpj = (cnpj: string, lang: string, sinal?: AbortSignal) =>
  chamar(`/v1/cnpj/${encodeURIComponent(cnpj)}/check?lang=${encodeURIComponent(lang)}`, {signal: sinal});

export type Instituicao_ = {tipo: 'ispb' | 'banco'; valor: string};
export const conferirPagamento = (cnpj: string, inst: Instituicao_, lang: string, sinal?: AbortSignal) =>
  chamar('/v1/pagamento/check', {
    method: 'POST',
    headers: {'content-type': 'application/json'},
    body: JSON.stringify({cnpj, [inst.tipo]: inst.valor, lang}),
    signal: sinal,
  });

export type Conjunto = 'bancos' | 'pix' | 'municipios' | 'ncm' | 'corretoras';
export type Celula = string | number | boolean | null;
export type Pagina = {conjunto: Conjunto; total: number; limite: number; offset: number; colunas: string[]; itens: Record<string, Celula>[]};
export type Uf = {sigla: string; nome: string; regiao: string | null; capital: string | null};
export type FiltrosDados = {q: string; uf: string; status: string; limite: number; offset: number};

/** Parâmetros da exploração; a mesma string serve ao link de CSV (sem paginação). */
export function consultaDados(f: FiltrosDados, csv = false): string {
  const p = new URLSearchParams();
  if (f.q.trim()) p.set('q', f.q.trim());
  if (f.uf) p.set('uf', f.uf);
  if (f.status) p.set('status', f.status);
  if (csv) p.set('formato', 'csv');
  else {
    p.set('limite', String(f.limite));
    p.set('offset', String(f.offset));
  }
  return p.toString();
}

export const explorar = (c: Conjunto, f: FiltrosDados, sinal?: AbortSignal) =>
  chamar<Pagina>(`/v1/dados/${c}?${consultaDados(f)}`, {signal: sinal});
export const listarUfs = (sinal?: AbortSignal) => chamar<{itens: Uf[]}>('/v1/dados/ufs', {signal: sinal});

/** Tira pontuação e põe em maiúsculas. A validação dos dígitos é só da API (única dona das regras). */
export const normalizarCnpj = (v: string) => v.replace(/[.\-/\s]/g, '').toUpperCase();
export const formatoCnpjOk = (v: string) => /^[0-9A-Z]{12}[0-9]{2}$/.test(normalizarCnpj(v));
