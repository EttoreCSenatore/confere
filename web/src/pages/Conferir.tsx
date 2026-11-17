import {useEffect, useRef, useState, type FormEvent} from 'react';

import {conferirCnpj, conferirPagamento, ErroApi, formatoCnpjOk, normalizarCnpj, type CodigoErro, type Resposta} from '../api';
import {Resultado} from '../components/Resultado';
import {useI18n} from '../i18n';

type Modo = 'empresa' | 'pagar';

export function Conferir() {
  const {t, lang} = useI18n();
  const [modo, setModo] = useState<Modo>('empresa');
  const [cnpj, setCnpj] = useState('');
  const [tipo, setTipo] = useState<'ispb' | 'banco'>('ispb');
  const [instituicao, setInstituicao] = useState('');
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState<CodigoErro | 'format' | null>(null);
  const [resposta, setResposta] = useState<Resposta | null>(null);
  const titulo = useRef<HTMLHeadingElement>(null);
  const abort = useRef<AbortController | null>(null);

  useEffect(() => () => abort.current?.abort(), []);
  useEffect(() => {
    if (resposta) titulo.current?.focus();
  }, [resposta]);

  async function enviar(ev: FormEvent) {
    ev.preventDefault();
    setErro(null);
    setResposta(null);
    const numero = normalizarCnpj(cnpj);
    if (!formatoCnpjOk(numero)) return setErro('format');
    abort.current?.abort();
    const ctl = (abort.current = new AbortController());
    setCarregando(true);
    try {
      const r =
        modo === 'empresa'
          ? await conferirCnpj(numero, lang, ctl.signal)
          : await conferirPagamento(numero, {tipo, valor: instituicao.trim()}, lang, ctl.signal);
      setResposta(r);
    } catch (e) {
      if (e instanceof DOMException && e.name === 'AbortError') return;
      setErro(e instanceof ErroApi ? e.codigo : 'desconhecido');
    } finally {
      setCarregando(false);
    }
  }

  function nova() {
    setResposta(null);
    setErro(null);
    setCnpj('');
    setInstituicao('');
  }

  return (
    <>
      <h1>{t('check.title')}</h1>
      <p className="lead">{t('check.lead')}</p>
      <div className="abas" role="tablist" aria-label={t('check.title')}>
        {(['empresa', 'pagar'] as const).map((m) => (
          <button
            key={m}
            type="button"
            role="tab"
            aria-selected={modo === m}
            className={modo === m ? 'aba ativa' : 'aba'}
            onClick={() => {
              setModo(m);
              setErro(null);
              setResposta(null);
            }}>
            {t(m === 'empresa' ? 'check.tab.company' : 'check.tab.pay')}
          </button>
        ))}
      </div>
      <form onSubmit={enviar} className="form" noValidate autoComplete="off">
        <label>
          {t('check.cnpj')}
          <input
            name="cnpj"
            value={cnpj}
            onChange={(e) => setCnpj(e.target.value)}
            inputMode="text"
            autoComplete="off"
            autoCapitalize="characters"
            spellCheck={false}
            maxLength={18}
            required
            aria-describedby="cnpj-dica"
            placeholder="00.000.000/0001-91"
          />
        </label>
        <p id="cnpj-dica" className="dica">
          {t('check.cnpj.hint')}
        </p>
        {modo === 'pagar' && (
          <fieldset>
            <legend>{t('check.inst.kind')}</legend>
            <label className="radio">
              <input type="radio" name="tipo" checked={tipo === 'ispb'} onChange={() => setTipo('ispb')} />
              {t('check.inst.ispb')}
            </label>
            <label className="radio">
              <input type="radio" name="tipo" checked={tipo === 'banco'} onChange={() => setTipo('banco')} />
              {t('check.inst.compe')}
            </label>
            <label>
              <span className="so-leitor">{t('check.inst.value')}</span>
              <input
                name="instituicao"
                value={instituicao}
                onChange={(e) => setInstituicao(e.target.value)}
                inputMode="numeric"
                autoComplete="off"
                maxLength={8}
                required
                aria-label={t('check.inst.value')}
                placeholder={tipo === 'ispb' ? '00000000' : '001'}
              />
            </label>
          </fieldset>
        )}
        <button type="submit" disabled={carregando}>
          {carregando ? t('check.loading') : t('check.submit')}
        </button>
        <p className="dica">{t('check.privacy')}</p>
      </form>

      <div aria-live="polite">
        {erro && (
          <p role="alert" className="erro">
            {t(erro === 'format' ? 'err.format' : (`err.${erro}` as const))}
          </p>
        )}
      </div>
      {resposta && <Resultado r={resposta} ref={titulo} onNova={nova} />}
    </>
  );
}
