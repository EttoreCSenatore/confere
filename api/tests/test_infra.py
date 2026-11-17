from confere.cache import CacheTTL
from confere.config import carregar
from confere.limite import LimiteTaxa


class Relogio:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def test_cache_expira_e_limita_tamanho():
    r = Relogio()
    c = CacheTTL(10, max_itens=2, relogio=r)
    c.guardar("a", 1)
    c.guardar("b", 2)
    c.guardar("c", 3)
    assert c.obter("a") is None and c.obter("c") == 3 and len(c) == 2
    r.t = 11
    assert c.obter("c") is None and len(c) == 1


def test_cache_ttl_zero_nao_guarda():
    c = CacheTTL(0)
    c.guardar("a", 1)
    assert c.obter("a") is None


def test_limite_janela_deslizante():
    r = Relogio()
    lim = LimiteTaxa(maximo=2, janela=60, relogio=r)
    assert lim.verificar("1.1.1.1") is None and lim.verificar("1.1.1.1") is None
    espera = lim.verificar("1.1.1.1")
    assert espera is not None and 1 <= espera <= 60
    assert lim.verificar("2.2.2.2") is None  # outra origem não é afetada
    r.t = 61
    assert lim.verificar("1.1.1.1") is None


def test_limite_nao_guarda_ip_em_claro_e_poda():
    r = Relogio()
    lim = LimiteTaxa(maximo=5, janela=60, max_chaves=3, relogio=r)
    for i in range(10):
        lim.verificar(f"10.0.0.{i}")
    assert len(lim._tentativas) <= 3
    assert all(isinstance(k, bytes) and b"10.0.0" not in k for k in lim._tentativas)


def test_config_padroes_seguros():
    c = carregar({})
    assert c.docs is False and c.cors_origens == () and c.confiar_proxy is False
    c2 = carregar({"CONFERE_DOCS": "true", "CONFERE_CORS_ORIGENS": "https://a.test, https://b.test"})
    assert c2.docs and c2.cors_origens == ("https://a.test", "https://b.test")
