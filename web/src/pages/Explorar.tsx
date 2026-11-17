import {useEffect, useMemo, useState} from 'react';
import {useNavigate} from 'react-router';

import {consultaDados, ErroApi, explorar, listarUfs, type Celula, type CodigoErro, type Conjunto, type Pagina, type Uf} from '../api';
import {useI18n} from '../i18n';
import type {Messages} from '../messages/pt-BR';

const CONJUNTOS: Conjunto[] = ['bancos', 'pix', 'municipios', 'ncm', 'corretoras'];
const LIMITE = 25;
const STATUS = [
  ['EM FUNCIONAMENTO NORMAL', 'explore.status.normal'],
  ['CANCELADA', 'explore.status.cancelada'],
] as const;

export function Explorar() {
  const {t, lang} = useI18n();
  const navigate = useNavigate();
  const [conjunto, setConjunto] = useState<Conjunto>('bancos');
  const [busca, setBusca] = useState('');
  const [q, setQ] = useState(''); // busca já "assentada" (debounce)
  const [uf, setUf] = useState('');
  const [status, setStatus] = useState('');
  const [offset, setOffset] = useState(0);
  const [ufs, setUfs] = useState<Uf[]>([]);
  const [pagina, setPagina] = useState<Pagina | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState<CodigoErro | null>(null);
  const precisaUf = conjunto === 'municipios';
  const mostraUf = precisaUf || conjunto === 'corretoras';

  useEffect(() => {
    const id = setTimeout(() => {
      setQ(busca);
      setOffset(0);
    }, 300);
    return () => clearTimeout(id);
  }, [busca]);

  useEffect(() => {
    const ctl = new AbortController();
    listarUfs(ctl.signal)
      .then((r) => setUfs(r.itens))
      .catch(() => undefined); // sem a lista, o filtro de UF só fica vazio
    return () => ctl.abort();
  }, []);

  useEffect(() => {
    if (precisaUf && !uf) {
      setPagina(null);
      setErro(null);
      return;
    }
    const ctl = new AbortController();
    setCarregando(true);
    setErro(null);
    explorar(conjunto, {q, uf: mostraUf ? uf : '', status: conjunto === 'corretoras' ? status : '', limite: LIMITE, offset}, ctl.signal)
      .then(setPagina)
      .catch((e) => {
        if (e instanceof DOMException && e.name === 'AbortError') return;
        setPagina(null);
        setErro(e instanceof ErroApi ? e.codigo : 'desconhecido');
      })
      .finally(() => !ctl.signal.aborted && setCarregando(false));
    return () => ctl.abort();
  }, [conjunto, q, uf, status, offset, precisaUf, mostraUf]);

  function trocar(c: Conjunto) {
    setConjunto(c);
    setOffset(0);
    setStatus('');
    if (c !== 'municipios' && c !== 'corretoras') setUf('');
  }

  const csv = useMemo(
    () => `/v1/dados/${conjunto}?${consultaDados({q, uf: mostraUf ? uf : '', status: conjunto === 'corretoras' ? status : '', limite: LIMITE, offset: 0}, true)}`,
    [conjunto, q, uf, status, mostraUf],
  );
  const paginas = pagina ? Math.max(1, Math.ceil(pagina.total / LIMITE)) : 1;
  const atual = Math.floor(offset / LIMITE) + 1;

  function celula(v: Celula) {
    if (v === null || v === '') return '—';
    if (typeof v === 'boolean') return v ? t('company.yes') : t('company.no');
    return String(v);
  }

  function acao(linha: Record<string, Celula>) {
    if (conjunto === 'corretoras' && linha.cnpj)
      return (
        <button type="button" className="link" onClick={() => navigate('/', {state: {modo: 'empresa', cnpj: linha.cnpj}})}>
          {t('explore.action.check')}
        </button>
      );
    if ((conjunto === 'bancos' || conjunto === 'pix') && linha.ispb)
      return (
        <button type="button" className="link" onClick={() => navigate('/', {state: {modo: 'pagar', ispb: linha.ispb}})}>
          {t('explore.action.pay')}
        </button>
      );
    return null;
  }

  const comAcao = conjunto === 'corretoras' || conjunto === 'bancos' || conjunto === 'pix';

  return (
    <>
      <h1>{t('explore.title')}</h1>
      <p className="lead">{t('explore.lead')}</p>
      <div className="abas" role="tablist" aria-label={t('explore.set')}>
        {CONJUNTOS.map((c) => (
          <button key={c} type="button" role="tab" aria-selected={conjunto === c} className={conjunto === c ? 'aba ativa' : 'aba'} onClick={() => trocar(c)}>
            {t(`explore.set.${c}` as keyof Messages)}
          </button>
        ))}
      </div>
      <div className="form filtros">
        <label>
          {t('explore.search')}
          <input
            type="search"
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
            maxLength={80}
            autoComplete="off"
            spellCheck={false}
            aria-describedby="busca-dica"
          />
        </label>
        <p id="busca-dica" className="dica">
          {t('explore.search.hint')}
        </p>
        {mostraUf && (
          <label>
            {t('explore.uf')}
            <select
              value={uf}
              onChange={(e) => {
                setUf(e.target.value);
                setOffset(0);
              }}>
              <option value="">{precisaUf ? t('explore.uf.pick') : t('explore.uf.all')}</option>
              {ufs.map((u) => (
                <option key={u.sigla} value={u.sigla}>
                  {u.sigla} · {u.nome}
                </option>
              ))}
            </select>
          </label>
        )}
        {conjunto === 'corretoras' && (
          <label>
            {t('explore.status')}
            <select
              value={status}
              onChange={(e) => {
                setStatus(e.target.value);
                setOffset(0);
              }}>
              <option value="">{t('explore.status.all')}</option>
              {STATUS.map(([valor, chave]) => (
                <option key={valor} value={valor}>
                  {t(chave)}
                </option>
              ))}
            </select>
          </label>
        )}
      </div>

      <div aria-live="polite">
        {erro && (
          <p role="alert" className="erro">
            {t(`err.${erro}` as keyof Messages)}
          </p>
        )}
        {precisaUf && !uf && <p className="nota">{t('explore.needuf')}</p>}
        {carregando && <p className="dica">{t('explore.loading')}</p>}
      </div>

      {pagina && (
        <section aria-label={t(`explore.set.${conjunto}` as keyof Messages)}>
          <div className="barra">
            <strong>{t('explore.total', {n: pagina.total.toLocaleString()})}</strong>
            {pagina.total > 0 && (
              <a className="botao-link" href={csv} download>
                {t('explore.csv')}
              </a>
            )}
          </div>
          {pagina.itens.length === 0 ? (
            <p>{t('explore.none')}</p>
          ) : (
            <div className="tabela-rolagem">
              <table>
                <caption className="so-leitor">{t(`explore.set.${conjunto}` as keyof Messages)}</caption>
                <thead>
                  <tr>
                    {comAcao && (
                      <th scope="col">
                        <span className="so-leitor">{t('explore.action')}</span>
                      </th>
                    )}
                    {pagina.colunas.map((c) => (
                      <th key={c} scope="col">
                        {t(`col.${c}` as keyof Messages)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {pagina.itens.map((linha, i) => (
                    <tr key={`${offset}-${i}`}>
                      {comAcao && <td>{acao(linha)}</td>}
                      {pagina.colunas.map((c) => (
                        <td key={c}>{celula(linha[c])}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <nav className="paginas" aria-label={t('explore.page', {p: atual, n: paginas})}>
            <button type="button" className="secundario" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - LIMITE))}>
              {t('explore.prev')}
            </button>
            <span>{t('explore.page', {p: atual, n: paginas})}</span>
            <button type="button" className="secundario" disabled={atual >= paginas} onClick={() => setOffset(offset + LIMITE)}>
              {t('explore.next')}
            </button>
          </nav>
          {pagina.atualizado_em && (
            <p className={pagina.desatualizado ? 'erro' : 'dica'} role={pagina.desatualizado ? 'status' : undefined}>
              {t(pagina.desatualizado ? 'explore.stale' : pagina.origem === 'fonte' ? 'explore.asof.live' : 'explore.asof', {
                data: new Date(`${pagina.atualizado_em}T00:00:00`).toLocaleDateString(lang),
              })}
            </p>
          )}
          <p className="dica">{t('explore.note')}</p>
        </section>
      )}
    </>
  );
}
