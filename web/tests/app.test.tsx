import {cleanup, render, screen, waitFor} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {MemoryRouter} from 'react-router';
import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';

import {App} from '../src/App';
import {formatoCnpjOk, normalizarCnpj} from '../src/api';
import {I18nProvider, type Lang} from '../src/i18n';
import {en} from '../src/messages/en';
import {ptBR} from '../src/messages/pt-BR';
import {ALTO, SEM_INDICIOS} from './fixtures';

function montar(lang: Lang = 'pt-BR', rota = '/') {
  return render(
    <I18nProvider inicial={lang}>
      <MemoryRouter initialEntries={[rota]}>
        <App />
      </MemoryRouter>
    </I18nProvider>,
  );
}

function responder(corpo: unknown, status = 200) {
  const f = vi.fn().mockResolvedValue(new Response(JSON.stringify(corpo), {status, headers: {'content-type': 'application/json'}}));
  vi.stubGlobal('fetch', f);
  return f;
}

beforeEach(() => localStorage.clear());
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe('mensagens', () => {
  it('pt-BR e inglês têm as mesmas chaves e nenhuma vazia', () => {
    expect(Object.keys(en).sort()).toEqual(Object.keys(ptBR).sort());
    for (const v of [...Object.values(en), ...Object.values(ptBR)]) expect(v.trim()).not.toBe('');
  });
  it('marcadores {var} batem entre os idiomas', () => {
    const vars = (s: string) => [...s.matchAll(/\{(\w+)\}/g)].map((m) => m[1]).sort();
    for (const k of Object.keys(ptBR) as (keyof typeof ptBR)[]) expect(vars(en[k])).toEqual(vars(ptBR[k]));
  });
});

describe('cnpj', () => {
  it('normaliza e confere só o formato (dígitos são da API)', () => {
    expect(normalizarCnpj('11.222.333/0001-81')).toBe('11222333000181');
    expect(formatoCnpjOk('12.abc.345/01de-35')).toBe(true);
    expect(formatoCnpjOk('123')).toBe(false);
  });
});

describe('conferir empresa', () => {
  it('mostra nível, sinais e dados, sem guardar a consulta nem pôr dados na URL', async () => {
    const f = responder(SEM_INDICIOS);
    montar();
    await userEvent.type(screen.getByLabelText(ptBR['check.cnpj']), '11.222.333/0001-81');
    await userEvent.click(screen.getByRole('button', {name: ptBR['check.submit']}));
    expect(await screen.findByText(ptBR['result.level.sem_indicios'])).toBeTruthy();
    expect(screen.getByText('EXEMPLO COMERCIO LTDA')).toBeTruthy();
    expect(screen.getByText(ptBR['result.nosignals'])).toBeTruthy();
    const [url, init] = f.mock.calls[0];
    expect(url).toBe('/v1/cnpj/11222333000181/check?lang=pt-BR');
    expect(init.credentials).toBe('omit');
    expect(JSON.stringify({...localStorage})).not.toContain('11222333000181');
    expect(Object.keys({...localStorage})).toEqual([]); // nem o idioma, enquanto não escolhido
    expect(window.location.search).toBe('');
  });

  it('formato errado nem chama a API', async () => {
    const f = responder({});
    montar();
    await userEvent.type(screen.getByLabelText(ptBR['check.cnpj']), '123');
    await userEvent.click(screen.getByRole('button', {name: ptBR['check.submit']}));
    expect((await screen.findByRole('alert')).textContent).toBe(ptBR['err.format']);
    expect(f).not.toHaveBeenCalled();
  });

  it.each([
    [422, 'cnpj_invalido'],
    [404, 'nao_encontrado'],
    [429, 'limite_excedido'],
    [502, 'fonte_indisponivel'],
  ] as const)('erro %i vira mensagem clara', async (status, codigo) => {
    responder({codigo, mensagem: 'x'}, status);
    montar();
    await userEvent.type(screen.getByLabelText(ptBR['check.cnpj']), '11222333000181');
    await userEvent.click(screen.getByRole('button', {name: ptBR['check.submit']}));
    expect((await screen.findByRole('alert')).textContent).toBe(ptBR[`err.${codigo}` as const]);
  });

  it('falha de rede é avisada', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('x')));
    montar();
    await userEvent.type(screen.getByLabelText(ptBR['check.cnpj']), '11222333000181');
    await userEvent.click(screen.getByRole('button', {name: ptBR['check.submit']}));
    expect((await screen.findByRole('alert')).textContent).toBe(ptBR['err.rede']);
  });

  it('MEI: não mostra nome e avisa', async () => {
    responder({...SEM_INDICIOS, empresa: {...SEM_INDICIOS.empresa, individual: true, razao_social: null, nome_fantasia: null}});
    montar();
    await userEvent.type(screen.getByLabelText(ptBR['check.cnpj']), '11222333000181');
    await userEvent.click(screen.getByRole('button', {name: ptBR['check.submit']}));
    expect(await screen.findByText(ptBR['company.individual'])).toBeTruthy();
    expect(screen.queryByText(ptBR['company.name'])).toBeNull();
  });
});

describe('pode pagar', () => {
  it('envia POST com os dados no corpo, não na URL', async () => {
    const f = responder(ALTO);
    montar();
    await userEvent.click(screen.getByRole('tab', {name: ptBR['check.tab.pay']}));
    await userEvent.type(screen.getByLabelText(ptBR['check.cnpj']), '11222333000181');
    await userEvent.type(screen.getByLabelText(ptBR['check.inst.value']), '12345678');
    await userEvent.click(screen.getByRole('button', {name: ptBR['check.submit']}));
    expect(await screen.findByText(ptBR['result.level.alto'])).toBeTruthy();
    const [url, init] = f.mock.calls[0];
    expect(url).toBe('/v1/pagamento/check');
    expect(init.method).toBe('POST');
    expect(JSON.parse(init.body)).toEqual({cnpj: '11222333000181', ispb: '12345678', lang: 'pt-BR'});
    expect(screen.getByText(ptBR['inst.notfound'])).toBeTruthy();
    expect(screen.getByText(ALTO.limites!)).toBeTruthy();
    expect(screen.getAllByText(ptBR['result.why'])).toHaveLength(2);
  });

  it('código do banco usa a chave "banco"', async () => {
    const f = responder(ALTO);
    montar();
    await userEvent.click(screen.getByRole('tab', {name: ptBR['check.tab.pay']}));
    await userEvent.type(screen.getByLabelText(ptBR['check.cnpj']), '11222333000181');
    await userEvent.click(screen.getByLabelText(ptBR['check.inst.compe']));
    await userEvent.type(screen.getByLabelText(ptBR['check.inst.value']), '1');
    await userEvent.click(screen.getByRole('button', {name: ptBR['check.submit']}));
    await waitFor(() => expect(f).toHaveBeenCalled());
    expect(JSON.parse(f.mock.calls[0][1].body)).toEqual({cnpj: '11222333000181', banco: '1', lang: 'pt-BR'});
  });
});

describe('idioma e páginas', () => {
  it('troca de idioma, lembra só o idioma e muda o lang do documento', async () => {
    montar();
    await userEvent.selectOptions(screen.getByRole('combobox'), 'en');
    expect(screen.getByRole('heading', {level: 1}).textContent).toBe(en['check.title']);
    expect(document.documentElement.lang).toBe('en');
    expect(localStorage.getItem('confere.idioma')).toBe('en');
    expect(localStorage.length).toBe(1);
  });
  it('envia o idioma à API para as mensagens dos sinais', async () => {
    const f = responder(SEM_INDICIOS);
    montar('en');
    await userEvent.type(screen.getByLabelText(en['check.cnpj']), '11222333000181');
    await userEvent.click(screen.getByRole('button', {name: en['check.submit']}));
    await screen.findByText(en['result.level.sem_indicios']);
    expect(f.mock.calls[0][0]).toContain('lang=en');
  });
  it.each([
    ['/explorar', 'explore.title'],
    ['/api', 'api.title'],
    ['/privacidade', 'privacy.title'],
  ] as const)('página %s existe', (rota, chave) => {
    montar('pt-BR', rota);
    expect(screen.getByRole('heading', {level: 1}).textContent).toBe(ptBR[chave]);
  });
});
