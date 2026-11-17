import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  docsSidebar: [
    'intro',
    'licenca',
    'roadmap',
    {
      type: 'category',
      label: 'Funcionalidades',
      collapsed: false,
      items: ['funcionalidades/conferir-empresa', 'funcionalidades/pode-pagar', 'funcionalidades/interface'],
    },
    {
      type: 'category',
      label: 'Técnico',
      collapsed: false,
      items: ['tecnico/arquitetura', 'tecnico/api', 'tecnico/seguranca-e-lgpd', 'tecnico/desenvolvimento'],
    },
  ],
};

export default sidebars;
