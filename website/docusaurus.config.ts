import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Confere',
  tagline: 'Confira empresas, bancos e participantes do Pix antes de pagar.',
  favicon: 'img/favicon.svg',

  future: {
    v4: true,
  },

  url: 'https://ettorecsenatore.github.io',
  baseUrl: '/confere/',
  organizationName: 'EttoreCSenatore',
  projectName: 'confere',
  trailingSlash: false,

  onBrokenLinks: 'throw',

  markdown: {
    mermaid: true,
    hooks: {
      onBrokenMarkdownLinks: 'throw',
    },
  },
  themes: ['@docusaurus/theme-mermaid'],

  i18n: {
    defaultLocale: 'pt-BR',
    locales: ['pt-BR', 'en'],
    localeConfigs: {
      'pt-BR': {label: 'Português (BR)', htmlLang: 'pt-BR'},
      en: {label: 'English', htmlLang: 'en'},
    },
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          showLastUpdateTime: false,
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    colorMode: {
      defaultMode: 'light',
      respectPrefersColorScheme: true,
    },
    mermaid: {
      theme: {light: 'neutral', dark: 'dark'},
    },
    navbar: {
      title: 'Confere',
      logo: {
        alt: 'Logo do Confere',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docsSidebar',
          position: 'left',
          label: 'Documentação',
        },
        {to: '/docs/roadmap', label: 'Roadmap', position: 'left'},
        {type: 'localeDropdown', position: 'right'},
        {
          href: 'https://github.com/EttoreCSenatore/confere',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Produto',
          items: [
            {label: 'Visão geral', to: '/docs/intro'},
            {label: 'Roadmap', to: '/docs/roadmap'},
          ],
        },
        {
          title: 'Funcionalidades',
          items: [
            {label: 'Experimente', to: '/docs/funcionalidades/experimente'},
            {label: 'Conferir uma empresa', to: '/docs/funcionalidades/conferir-empresa'},
            {label: 'Pode pagar?', to: '/docs/funcionalidades/pode-pagar'},
            {label: 'Explorar dados abertos', to: '/docs/funcionalidades/explorar'},
            {label: 'Linha de comando', to: '/docs/funcionalidades/cli'},
          ],
        },
        {
          title: 'Técnico',
          items: [
            {label: 'Arquitetura', to: '/docs/tecnico/arquitetura'},
            {label: 'Segurança e LGPD', to: '/docs/tecnico/seguranca-e-lgpd'},
            {label: 'API', to: '/docs/tecnico/api'},
            {label: 'Implantação', to: '/docs/tecnico/implantacao'},
            {label: 'Desenvolvimento', to: '/docs/tecnico/desenvolvimento'},
          ],
        },
        {
          title: 'Projeto',
          items: [
            {label: 'Licença', to: '/docs/licenca'},
            {label: 'BrasilAPI', href: 'https://brasilapi.com.br/'},
          ],
        },
      ],
      copyright: `Confere © ${new Date().getFullYear()} Ettore Senatore. Software livre (AGPL-3.0-or-later). Feito com Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['json', 'bash', 'python', 'sql'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
