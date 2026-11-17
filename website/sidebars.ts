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
      items: ['funcionalidades/experimente', 'funcionalidades/conferir-empresa', 'funcionalidades/pode-pagar', 'funcionalidades/explorar', 'funcionalidades/cli', 'funcionalidades/interface'],
    },
    {
      type: 'category',
      label: 'Técnico',
      collapsed: false,
      items: ['tecnico/arquitetura', 'tecnico/implantacao', 'tecnico/api', 'tecnico/seguranca-e-lgpd', 'tecnico/desenvolvimento'],
    },
  ],
};

export default sidebars;
