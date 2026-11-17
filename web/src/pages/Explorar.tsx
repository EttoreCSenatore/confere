import {useI18n} from '../i18n';

export function Explorar() {
  const {t} = useI18n();
  return (
    <>
      <h1>{t('explore.title')}</h1>
      <p className="lead">{t('explore.soon')}</p>
    </>
  );
}
