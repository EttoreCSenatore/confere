import {createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode} from 'react';

import {en} from './messages/en';
import {ptBR, type Messages} from './messages/pt-BR';

export type Lang = 'pt-BR' | 'en';
const CATALOGS: Record<Lang, Messages> = {'pt-BR': ptBR, en};
const CHAVE = 'confere.idioma'; // a única coisa que o app guarda no navegador: o idioma escolhido

function lerPreferencia(): Lang {
  try {
    const salvo = localStorage.getItem(CHAVE);
    if (salvo === 'pt-BR' || salvo === 'en') return salvo;
  } catch {
    /* armazenamento bloqueado: segue sem lembrar */
  }
  return (navigator.language || 'pt-BR').toLowerCase().startsWith('pt') ? 'pt-BR' : 'en';
}

type Ctx = {lang: Lang; setLang: (l: Lang) => void; t: (k: keyof Messages, vars?: Record<string, string | number>) => string};
const I18nContext = createContext<Ctx | null>(null);

export function I18nProvider({children, inicial}: {children: ReactNode; inicial?: Lang}) {
  const [lang, setLangState] = useState<Lang>(inicial ?? lerPreferencia());
  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);
  const setLang = useCallback((l: Lang) => {
    setLangState(l);
    try {
      localStorage.setItem(CHAVE, l);
    } catch {
      /* ok */
    }
  }, []);
  const t = useCallback<Ctx['t']>(
    (k, vars) => {
      let texto: string = CATALOGS[lang][k];
      for (const [nome, valor] of Object.entries(vars ?? {})) texto = texto.replaceAll(`{${nome}}`, String(valor));
      return texto;
    },
    [lang],
  );
  const valor = useMemo(() => ({lang, setLang, t}), [lang, setLang, t]);
  return <I18nContext.Provider value={valor}>{children}</I18nContext.Provider>;
}

export function useI18n(): Ctx {
  const c = useContext(I18nContext);
  if (!c) throw new Error('useI18n fora do I18nProvider');
  return c;
}

export {CATALOGS};
