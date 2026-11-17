import {useI18n} from '../i18n';

const CNPJ = "curl 'https://SEU-SERVIDOR/v1/cnpj/00000000000191/check?lang=pt-BR'";
const PAGAR = `curl -X POST https://SEU-SERVIDOR/v1/pagamento/check \\
  -H 'content-type: application/json' \\
  -d '{"cnpj": "00000000000191", "ispb": "00000000"}'`;

export function ApiCli() {
  const {t} = useI18n();
  return (
    <>
      <h1>{t('api.title')}</h1>
      <p className="lead">{t('api.lead')}</p>
      <h2>{t('api.cnpj')}</h2>
      <pre>
        <code>{CNPJ}</code>
      </pre>
      <h2>{t('api.pay')}</h2>
      <pre>
        <code>{PAGAR}</code>
      </pre>
      <p>
        <a href="https://ettorecsenatore.github.io/confere/docs/tecnico/api" rel="noopener noreferrer">
          {t('api.docs')}
        </a>
      </p>
      <p className="nota">{t('api.cli')}</p>
    </>
  );
}
