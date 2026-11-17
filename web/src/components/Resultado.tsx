import {forwardRef} from 'react';

import type {Resposta, Sinal} from '../api';
import {useI18n} from '../i18n';

const ICONE = {sem_indicios: '✔', atencao: '!', alto: '✖'} as const;

function idade(data: string | null, t: ReturnType<typeof useI18n>['t']): string {
  if (!data) return t('company.unknown');
  const dias = Math.floor((Date.now() - new Date(`${data}T00:00:00`).getTime()) / 86_400_000);
  return dias >= 730 ? t('company.age', {n: Math.floor(dias / 365)}) : t('company.age.days', {n: Math.max(dias, 0)});
}

function Linha({rotulo, valor}: {rotulo: string; valor: string | null | undefined}) {
  return (
    <>
      <dt>{rotulo}</dt>
      <dd>{valor || '—'}</dd>
    </>
  );
}

function SinalItem({s}: {s: Sinal}) {
  const {t} = useI18n();
  return (
    <li className={`sinal sev-${s.gravidade}`}>
      <span className="etiqueta">{t(`result.sev.${s.gravidade}` as const)}</span>
      <p>{s.mensagem}</p>
      <details>
        <summary>{t('result.why')}</summary>
        <p>
          <strong>{t('result.rule')}:</strong> {s.regra}
        </p>
        <p>
          <strong>{t('result.weight')}:</strong> {s.peso} · <code>{s.codigo}</code>
        </p>
      </details>
    </li>
  );
}

export const Resultado = forwardRef<HTMLHeadingElement, {r: Resposta; onNova: () => void}>(function Resultado({r, onNova}, ref) {
  const {t, lang} = useI18n();
  const e = r.empresa;
  const i = r.instituicao;
  const moeda = new Intl.NumberFormat(lang, {style: 'currency', currency: 'BRL', maximumFractionDigits: 0});
  const sim = (v: boolean | null) => (v === null ? t('company.unknown') : v ? t('company.yes') : t('company.no'));
  return (
    <section className="resultado" aria-labelledby="res-titulo">
      <h2 id="res-titulo" tabIndex={-1} ref={ref}>
        {t('result.title')} · <span className="cnpj">{r.cnpj}</span>
      </h2>
      <div className={`nivel nivel-${r.nivel}`}>
        <span className="icone" aria-hidden="true">
          {ICONE[r.nivel]}
        </span>
        <div>
          <p className="nivel-titulo">{t(`result.level.${r.nivel}` as const)}</p>
          <p>{t(`result.level.hint.${r.nivel}` as const)}</p>
          <label className="pontos">
            {t('result.score', {n: r.pontuacao})}
            <progress value={r.pontuacao} max={100} />
          </label>
        </div>
      </div>

      <h3>{t('result.signals')}</h3>
      {r.sinais.length === 0 ? (
        <p>{t('result.nosignals')}</p>
      ) : (
        <ul className="sinais">
          {r.sinais.map((s) => (
            <SinalItem key={s.codigo} s={s} />
          ))}
        </ul>
      )}

      <h3>{t('company.title')}</h3>
      {e.individual && <p className="nota">{t('company.individual')}</p>}
      <dl className="dados">
        {!e.individual && <Linha rotulo={t('company.name')} valor={e.razao_social} />}
        {!e.individual && e.nome_fantasia && <Linha rotulo={t('company.fantasy')} valor={e.nome_fantasia} />}
        <Linha rotulo={t('company.status')} valor={e.situacao} />
        <Linha
          rotulo={t('company.since')}
          valor={e.data_abertura ? `${new Date(`${e.data_abertura}T00:00:00`).toLocaleDateString(lang)} (${idade(e.data_abertura, t)})` : null}
        />
        <Linha rotulo={t('company.nature')} valor={e.natureza_juridica} />
        <Linha rotulo={t('company.size')} valor={e.porte} />
        <Linha rotulo={t('company.cnae')} valor={e.cnae_principal.descricao} />
        <Linha rotulo={t('company.place')} valor={[e.municipio, e.uf].filter(Boolean).join(' / ')} />
        <Linha
          rotulo={t('company.partners')}
          valor={`${t('company.partners.value', {n: e.socios_total})}${e.socios_qualificacoes.length ? ` — ${e.socios_qualificacoes.join(', ')}` : ''}`}
        />
        {e.capital_social !== null && <Linha rotulo={t('company.capital')} valor={moeda.format(e.capital_social)} />}
        <Linha rotulo={t('company.simples')} valor={sim(e.optante_simples)} />
      </dl>

      {r.instituicao !== undefined && (
        <>
          <h3>{t('inst.title')}</h3>
          {i ? (
            <dl className="dados">
              <Linha rotulo={t('inst.name')} valor={i.nome} />
              <Linha rotulo={t('inst.ispb')} valor={i.ispb} />
              <Linha rotulo={t('inst.compe')} valor={i.codigo_compe === null ? null : String(i.codigo_compe)} />
              <Linha rotulo={t('inst.pix')} valor={i.participa_pix ? t('company.yes') : t('company.no')} />
              <Linha rotulo={t('inst.modality')} valor={i.modalidade_pix} />
              <Linha rotulo={t('inst.type')} valor={i.tipo_participacao} />
            </dl>
          ) : (
            <p className="nota">{t('inst.notfound')}</p>
          )}
          {r.limites && <p className="nota">{r.limites}</p>}
        </>
      )}

      <p className="aviso">{r.aviso}</p>
      <p className="meta">
        {t('result.at', {data: new Date(r.consultado_em).toLocaleString(lang)})} · {t('result.source')}
      </p>
      <button type="button" className="secundario" onClick={onNova}>
        {t('check.new')}
      </button>
    </section>
  );
});
