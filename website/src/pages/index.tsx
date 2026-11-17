import type {ReactNode} from 'react';
import Link from '@docusaurus/Link';
import Translate, {translate} from '@docusaurus/Translate';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

type Feature = {title: string; body: string};

const features: Feature[] = [
  {
    title: translate({id: 'home.feature.0.title', message: 'Checagem de empresas (CNPJ)'}),
    body: translate({id: 'home.feature.0.body', message: 'Situação cadastral, idade da empresa, atividade e sinais de alerta explicados, a partir de dados públicos.'}),
  },
  {
    title: translate({id: 'home.feature.1.title', message: 'Pode pagar? (Pix e bancos)'}),
    body: translate({id: 'home.feature.1.body', message: 'Verifica se o banco ou a instituição existe e participa do Pix, e cruza com o CNPJ de quem vai receber.'}),
  },
  {
    title: translate({id: 'home.feature.2.title', message: 'Explorador de dados abertos'}),
    body: translate({id: 'home.feature.2.body', message: 'Bancos, municípios, NCM e corretoras num só lugar, com busca, filtros e exportação CSV.'}),
  },
  {
    title: translate({id: 'home.feature.3.title', message: 'CLI e API'}),
    body: translate({id: 'home.feature.3.body', message: 'Tudo também na linha de comando e numa API documentada, para automatizar sua conferência.'}),
  },
  {
    title: translate({id: 'home.feature.4.title', message: 'Privacidade por padrão'}),
    body: translate({id: 'home.feature.4.body', message: 'Não guardamos o que você consulta: sem conta, sem histórico, sem IP em log. Pensado para a LGPD.'}),
  },
  {
    title: translate({id: 'home.feature.5.title', message: 'Software livre'}),
    body: translate({id: 'home.feature.5.body', message: 'Código aberto (AGPL-3.0-or-later), documentação em português e inglês, regras de risco explicáveis.'}),
  },
];

const roles = [
  translate({id: 'home.role.0', message: 'Compras e financeiro'}),
  translate({id: 'home.role.1', message: 'Segurança e antifraude'}),
  translate({id: 'home.role.2', message: 'Desenvolvedores'}),
  translate({id: 'home.role.3', message: 'Pesquisa e jornalismo'}),
];

export default function Home(): ReactNode {
  return (
    <Layout
      title={translate({id: 'home.title', message: 'Confira antes de pagar'})}
      description={translate({
        id: 'home.description',
        message: 'Confere checa empresas (CNPJ), bancos e participantes do Pix com dados públicos da BrasilAPI, sem guardar suas consultas.',
      })}>
      <header className={styles.hero}>
        <div className="container">
          <Heading as="h1" className={styles.title}>
            Confere
          </Heading>
          <p className={styles.tagline}>
            <Translate id="home.tagline">Confira empresas, bancos e participantes do Pix antes de pagar, com dados públicos e sem guardar suas consultas.</Translate>
          </p>
          <div className={styles.roles}>
            {roles.map((r) => (
              <span key={r} className={styles.role}>
                {r}
              </span>
            ))}
          </div>
          <div className={styles.buttons}>
            <Link className="button button--primary button--lg" to="/docs/intro">
              <Translate id="home.docs">Ler a documentação</Translate>
            </Link>
            <Link className="button button--secondary button--lg" to="/docs/roadmap">
              <Translate id="home.roadmap">Roadmap</Translate>
            </Link>
          </div>
        </div>
      </header>
      <main className="container">
        <section className={styles.features}>
          {features.map((f) => (
            <div key={f.title} className={styles.card}>
              <Heading as="h3">{f.title}</Heading>
              <p>{f.body}</p>
            </div>
          ))}
        </section>
      </main>
    </Layout>
  );
}
