import {cleanup, render, screen, waitFor, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {MemoryRouter} from 'react-router';
import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';

import {App} from '../src/App';
import {consultaDados} from '../src/api';
import {I18nProvider} from '../src/i18n';
import {ptBR} from '../src/messages/pt-BR';

const UFS = {itens: [{sigla: 'SP', nome: 'São Paulo', regiao: 'Sudeste', capital: 'São Paulo'}, {sigla: 'RJ', nome: 'Rio de Janeiro', regiao: 'Sudeste', capital: 'Rio de Janeiro'}]};
const COL_BANCOS = ['codigo_compe', 'ispb', 'nome', 'nome_completo', 'participa_pix'];
const COL_COR = ['cnpj', 'nome_social', 'nome_comercial', 'status', 'uf', 'municipio', 'codigo_cvm', 'data_registro'];

function pagina(conjunto: string, colunas: string[], itens: Record<string, unknown>[], total = itens.length) {
  return {conjunto, total, limite: 25, offset: 0, colunas, itens};
}

/** fetch simulado: roteia por caminho e guarda as URLs pedidas. */
function simular(resp: (url: URL, init?: RequestInit) => unknown) {
  const f = vi.fn(async (entrada: string, init?: RequestInit) => {
    const url = new URL(entrada, 'http://x');
    const r = resp(url, init) as {status?: number; corpo: unknown};
    return new Response(JSON.stringify(r.corpo), {status: r.status ?? 200, headers: {'content-type': 'application/json'}});
  });
  vi.stubGlobal('fetch', f);
  return f;
}

function montar() {
  return render(
    <I18nProvider inicial="pt-BR">
      <MemoryRouter initialEntries={['/explorar']}>
        <App />
      </MemoryRouter>
    </I18nProvider>,
  );
}

beforeEach(() => localStorage.clear());
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe('consultaDados', () => {
  it('monta a query sem campos vazios e o CSV sem paginação', () => {
    const f = {q: ' café ', uf: '', status: '', limite: 25, offset: 50};
    expect(consultaDados(f)).toBe('q=caf%C3%A9&limite=25&offset=50');
    expect(consultaDados({...f, uf: 'SP'}, true)).toBe('q=caf%C3%A9&uf=SP&formato=csv');
  });
});

describe('Explorar', () => {
  it('lista bancos, mostra total e link de CSV', async () => {
    const f = simular((url) =>
      url.pathname === '/v1/dados/ufs'
        ? {corpo: UFS}
        : {corpo: pagina('bancos', COL_BANCOS, [{codigo_compe: 1, ispb: '00000000', nome: 'BCO DO BRASIL S.A.', nome_completo: 'Banco do Brasil S.A.', participa_pix: true}])},
    );
    montar();
    expect(await screen.findByText('BCO DO BRASIL S.A.')).toBeTruthy();
    expect(screen.getByText(ptBR['explore.total'].replace('{n}', '1'))).toBeTruthy();
    const csv = screen.getByRole('link', {name: ptBR['explore.csv']});
    expect(csv.getAttribute('href')).toBe('/v1/dados/bancos?formato=csv');
    expect(csv.hasAttribute('download')).toBe(true);
    expect(f.mock.calls.some(([u]) => String(u).startsWith('/v1/dados/bancos?limite=25&offset=0'))).toBe(true);
  });

  it('a busca espera o debounce, volta à página 1 e vai para o CSV', async () => {
    const f = simular((url) =>
      url.pathname === '/v1/dados/ufs' ? {corpo: UFS} : {corpo: pagina('bancos', COL_BANCOS, [], 0)},
    );
    montar();
    await screen.findByText(ptBR['explore.none']);
    await userEvent.type(screen.getByRole('searchbox'), 'itau');
    await waitFor(() => expect(f.mock.calls.some(([u]) => String(u).includes('q=itau'))).toBe(true));
    // digitar não dispara uma chamada por tecla
    expect(f.mock.calls.filter(([u]) => String(u).includes('q=')).length).toBe(1);
    expect(JSON.stringify({...localStorage})).not.toContain('itau');
  });

  it('municípios pedem a UF antes de consultar', async () => {
    const f = simular((url) =>
      url.pathname === '/v1/dados/ufs'
        ? {corpo: UFS}
        : {corpo: pagina('municipios', ['codigo_ibge', 'nome', 'uf'], [{codigo_ibge: '3509502', nome: 'CAMPINAS', uf: 'SP'}])},
    );
    montar();
    await userEvent.click(screen.getByRole('tab', {name: ptBR['explore.set.municipios']}));
    expect(await screen.findByText(ptBR['explore.needuf'])).toBeTruthy();
    expect(f.mock.calls.some(([u]) => String(u).includes('/municipios'))).toBe(false);
    await screen.findByRole('option', {name: /SP · São Paulo/});
    await userEvent.selectOptions(screen.getByLabelText(ptBR['explore.uf']), 'SP');
    expect(await screen.findByText('CAMPINAS')).toBeTruthy();
    expect(screen.getByRole('link', {name: ptBR['explore.csv']}).getAttribute('href')).toBe('/v1/dados/municipios?uf=SP&formato=csv');
  });

  it('pagina com Anterior/Próxima', async () => {
    const f = simular((url) =>
      url.pathname === '/v1/dados/ufs'
        ? {corpo: UFS}
        : {corpo: pagina('bancos', COL_BANCOS, [{codigo_compe: 1, ispb: '1', nome: 'A', nome_completo: 'A', participa_pix: false}], 60)},
    );
    montar();
    await screen.findByText(ptBR['explore.page'].replace('{p}', '1').replace('{n}', '3'));
    expect((screen.getByRole('button', {name: ptBR['explore.prev']}) as HTMLButtonElement).disabled).toBe(true);
    await userEvent.click(screen.getByRole('button', {name: ptBR['explore.next']}));
    await waitFor(() => expect(f.mock.calls.some(([u]) => String(u).includes('offset=25'))).toBe(true));
    await screen.findByText(ptBR['explore.page'].replace('{p}', '2').replace('{n}', '3'));
  });

  it.each([
    [429, 'limite_excedido'],
    [502, 'fonte_indisponivel'],
  ] as const)('erro %i vira mensagem clara', async (status, codigo) => {
    simular((url) => (url.pathname === '/v1/dados/ufs' ? {corpo: UFS} : {status, corpo: {codigo, mensagem: 'x'}}));
    montar();
    expect((await screen.findByRole('alert')).textContent).toBe(ptBR[`err.${codigo}` as const]);
  });

  it('corretoras: botão Conferir CNPJ leva ao formulário já preenchido, sem pôr o CNPJ na URL', async () => {
    simular((url, init) => {
      if (url.pathname === '/v1/dados/ufs') return {corpo: UFS};
      if (url.pathname.startsWith('/v1/dados/corretoras'))
        return {
          corpo: pagina('corretoras', COL_COR, [
            {cnpj: '11.222.333/0001-81', nome_social: 'ALFA CORRETORA', nome_comercial: null, status: 'EM FUNCIONAMENTO NORMAL', uf: 'SP', municipio: 'SAO PAULO', codigo_cvm: '123', data_registro: '1990-01-01'},
          ]),
        };
      void init;
      return {corpo: pagina('bancos', COL_BANCOS, [])};
    });
    montar();
    await userEvent.click(screen.getByRole('tab', {name: ptBR['explore.set.corretoras']}));
    const linha = (await screen.findByText('ALFA CORRETORA')).closest('tr') as HTMLElement;
    await userEvent.click(within(linha).getByRole('button', {name: ptBR['explore.action.check']}));
    expect((screen.getByLabelText(ptBR['check.cnpj']) as HTMLInputElement).value).toBe('11.222.333/0001-81');
    expect(window.location.search).toBe('');
  });

  it('bancos: "Pode pagar?" abre a aba certa com o ISPB', async () => {
    simular((url) =>
      url.pathname === '/v1/dados/ufs'
        ? {corpo: UFS}
        : {corpo: pagina('bancos', COL_BANCOS, [{codigo_compe: 1, ispb: '00000000', nome: 'BCO DO BRASIL S.A.', nome_completo: 'x', participa_pix: true}])},
    );
    montar();
    const linha = (await screen.findByText('BCO DO BRASIL S.A.')).closest('tr') as HTMLElement;
    await userEvent.click(within(linha).getByRole('button', {name: ptBR['explore.action.pay']}));
    expect(screen.getByRole('tab', {name: ptBR['check.tab.pay']}).getAttribute('aria-selected')).toBe('true');
    expect((screen.getByLabelText(ptBR['check.inst.value']) as HTMLInputElement).value).toBe('00000000');
  });
});
