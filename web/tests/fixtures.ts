import type {Resposta} from '../src/api';

export const SEM_INDICIOS: Resposta = {
  cnpj: '11.222.333/0001-81',
  consultado_em: '2026-11-17T17:30:00Z',
  nivel: 'sem_indicios',
  pontuacao: 0,
  sinais: [],
  empresa: {
    cnpj: '11222333000181',
    individual: false,
    razao_social: 'EXEMPLO COMERCIO LTDA',
    nome_fantasia: 'EXEMPLO',
    situacao: 'ATIVA',
    data_abertura: '2012-03-15',
    natureza_juridica: 'Sociedade Empresária Limitada',
    porte: 'DEMAIS',
    capital_social: 250000,
    optante_simples: false,
    mei: false,
    cnae_principal: {codigo: 4712100, descricao: 'Comércio varejista de mercadorias em geral'},
    municipio: 'SAO PAULO',
    uf: 'SP',
    socios_total: 2,
    socios_qualificacoes: ['Sócio-Administrador'],
  },
  aviso: 'Indícios a partir de dados públicos; não é prova de fraude nem análise de crédito. Ausência de sinais não significa que seja seguro.',
  fonte: {nome: 'BrasilAPI', url: 'https://brasilapi.com.br/'},
};

export const ALTO: Resposta = {
  ...SEM_INDICIOS,
  nivel: 'alto',
  pontuacao: 100,
  sinais: [
    {
      codigo: 'SITUACAO_NAO_ATIVA',
      gravidade: 'alto',
      peso: 60,
      mensagem: 'A situação cadastral não é ATIVA.',
      regra: 'Situação cadastral diferente de ATIVA na Receita Federal.',
    },
    {
      codigo: 'INSTITUICAO_NAO_ENCONTRADA',
      gravidade: 'alto',
      peso: 50,
      mensagem: 'O banco ou instituição informado não consta nas listas do Banco Central.',
      regra: 'ISPB ou código COMPE ausente da lista de bancos e dos participantes do Pix.',
    },
  ],
  empresa: {...SEM_INDICIOS.empresa, situacao: 'BAIXADA'},
  instituicao: null,
  limites: 'Só confirmamos que a instituição existe e participa do Pix. Não verificamos o titular da chave nem a conta de destino.',
};
