import {NavLink, Route, Routes} from 'react-router';

import {useI18n, type Lang} from './i18n';
import {ApiCli} from './pages/ApiCli';
import {Conferir} from './pages/Conferir';
import {Explorar} from './pages/Explorar';
import {Privacidade} from './pages/Privacidade';

export function App() {
  const {t, lang, setLang} = useI18n();
  return (
    <>
      <a className="skip" href="#conteudo">
        {t('app.skip')}
      </a>
      <header className="topo">
        <div className="contido topo-in">
          <NavLink to="/" className="marca" aria-label="Confere">
            <img src="/favicon.svg" alt="" width="28" height="28" />
            <span>Confere</span>
          </NavLink>
          <nav aria-label="principal" className="menu">
            <NavLink to="/" end>
              {t('nav.check')}
            </NavLink>
            <NavLink to="/explorar">{t('nav.explore')}</NavLink>
            <NavLink to="/api">{t('nav.api')}</NavLink>
            <NavLink to="/privacidade">{t('nav.privacy')}</NavLink>
          </nav>
          <label className="idioma">
            <span className="so-leitor">{t('nav.lang')}</span>
            <select value={lang} onChange={(e) => setLang(e.target.value as Lang)}>
              <option value="pt-BR">Português</option>
              <option value="en">English</option>
            </select>
          </label>
        </div>
      </header>
      <main id="conteudo" className="contido">
        <Routes>
          <Route path="/" element={<Conferir />} />
          <Route path="/explorar" element={<Explorar />} />
          <Route path="/api" element={<ApiCli />} />
          <Route path="/privacidade" element={<Privacidade />} />
          <Route path="*" element={<Conferir />} />
        </Routes>
      </main>
      <footer className="rodape">
        <div className="contido">
          <p>{t('footer.notice')}</p>
          <p>
            <strong>{t('footer.nostore')}</strong> ·{' '}
            <a href="https://github.com/EttoreCSenatore/confere" rel="noopener noreferrer">
              {t('footer.code')}
            </a>
          </p>
        </div>
      </footer>
    </>
  );
}
