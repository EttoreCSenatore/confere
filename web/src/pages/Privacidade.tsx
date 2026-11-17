import {useI18n} from '../i18n';

export function Privacidade() {
  const {t} = useI18n();
  const itens = ['privacy.l1', 'privacy.l2', 'privacy.l3', 'privacy.l4', 'privacy.l5', 'privacy.l7', 'privacy.l6'] as const;
  return (
    <>
      <h1>{t('privacy.title')}</h1>
      <p className="lead">{t('privacy.draft')}</p>
      <ul className="lista">
        {itens.map((k) => (
          <li key={k}>{t(k)}</li>
        ))}
      </ul>
      <p>{t('privacy.rights')}</p>
      <p>
        <a href="https://github.com/EttoreCSenatore/confere/blob/main/.lgpd/policies/privacy-policy-v1.md" rel="noopener noreferrer">
          {t('privacy.policy')}
        </a>
      </p>
    </>
  );
}
