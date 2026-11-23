"""Gera a capa e os cartões de projeto do perfil (SVG), nas versões clara e escura.

Uso: python3 scripts/cartoes_perfil.py
Baixa os ícones 3D (Fluent Emoji, licença MIT) e embute nas imagens, porque o GitHub
não carrega imagens externas de dentro de um SVG. Só usa a biblioteca padrão do Python.
"""
import base64
import os
import urllib.request
from html import escape

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "cartoes")
CDN = "https://cdn.jsdelivr.net/npm/@lobehub/fluent-emoji-3d@1.1.0/assets/"
FONTE = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
_cache = {}


def icone(emoji):
    """Ícone 3D como data URI (tenta com e sem o seletor de variação FE0F)."""
    if emoji in _cache:
        return _cache[emoji]
    cps = [f"{ord(c):x}" for c in emoji]
    for nome in dict.fromkeys(["-".join(cps), "-".join(c for c in cps if c != "fe0f")]):
        try:
            req = urllib.request.Request(CDN + nome + ".webp", headers={"User-Agent": "gerador-de-cartoes"})
            with urllib.request.urlopen(req, timeout=20) as r:
                _cache[emoji] = "data:image/webp;base64," + base64.b64encode(r.read()).decode()
                return _cache[emoji]
        except Exception:
            continue
    raise RuntimeError(f"ícone não encontrado: {emoji}")


def imagem_local(caminho, tipo="image/jpeg"):
    with open(caminho, "rb") as f:
        return f"data:{tipo};base64," + base64.b64encode(f.read()).decode()


TEMAS = {
    "claro": {"fundo": "#ffffff", "borda": "#e5e7eb", "titulo": "#0f172a", "texto": "#475569", "fraco": "#64748b", "chip": "#f1f5f9"},
    "escuro": {"fundo": "#161b22", "borda": "#30363d", "titulo": "#e6edf3", "texto": "#9da7b3", "fraco": "#8b949e", "chip": "#21262d"},
}


def salvar(nome, svg):
    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(SAIDA, nome), "w", encoding="utf-8") as f:
        f.write(svg)


def capa():
    icones = [("🛒", 905, 70), ("🐷", 1040, 40), ("🛡️", 1150, 120), ("🐛", 960, 190), ("🍬", 1090, 215)]
    chips = ["HTML", "CSS", "JavaScript", "Python", "Machine Learning"]
    x, partes_chips = 64, []
    for c in chips:
        w = 22 + len(c) * 9.6
        partes_chips.append(f'<rect x="{x}" y="232" width="{w:.0f}" height="34" rx="17" fill="#ffffff" fill-opacity=".1" stroke="#ffffff" stroke-opacity=".18"/>'
                            f'<text x="{x + w / 2:.0f}" y="254" class="chip" text-anchor="middle">{c}</text>')
        x += w + 10
    flutuando = "".join(
        f'<g class="flutua" style="animation-delay:{i * .5:.1f}s"><circle cx="{cx}" cy="{cy}" r="46" fill="#ffffff" fill-opacity=".08" stroke="#ffffff" stroke-opacity=".14"/>'
        f'<image href="{icone(e)}" x="{cx - 30}" y="{cy - 30}" width="60" height="60"/></g>'
        for i, (e, cx, cy) in enumerate(icones))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="320" viewBox="0 0 1280 320" role="img" aria-label="Ricardo: apps web, jogos e IA aplicada a pagamentos">
  <defs>
    <linearGradient id="f" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1020"/><stop offset=".55" stop-color="#1a1f4d"/><stop offset="1" stop-color="#2b1a5e"/></linearGradient>
    <radialGradient id="brilho" cx=".82" cy=".45" r=".5"><stop offset="0" stop-color="#7c5cf5" stop-opacity=".55"/><stop offset="1" stop-color="#7c5cf5" stop-opacity="0"/></radialGradient>
    <linearGradient id="nome" x1="0" x2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#c4b5fd"/></linearGradient>
    <pattern id="pontos" width="26" height="26" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="#ffffff" fill-opacity=".09"/></pattern>
  </defs>
  <style>
    text {{ font-family: {FONTE}; }}
    .ola {{ font-size: 16px; font-weight: 700; letter-spacing: 5px; fill: #a5b4fc; }}
    .nome {{ font-size: 86px; font-weight: 800; letter-spacing: -3px; }}
    .sub {{ font-size: 24px; fill: #c7d2fe; }}
    .chip {{ font-size: 15px; font-weight: 600; fill: #e0e7ff; }}
    .flutua {{ animation: flutua 4s ease-in-out infinite; }}
    @keyframes flutua {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-8px); }} }}
  </style>
  <rect width="1280" height="320" rx="24" fill="url(#f)"/>
  <rect width="1280" height="320" rx="24" fill="url(#pontos)"/>
  <rect width="1280" height="320" rx="24" fill="url(#brilho)"/>
  <text x="64" y="86" class="ola">OLÁ, EU SOU</text>
  <text x="60" y="170" class="nome" fill="url(#nome)">Ricardo</text>
  <text x="64" y="210" class="sub">Crio apps web, jogos e projetos de IA aplicada a pagamentos</text>
  {"".join(partes_chips)}
  {flutuando}
</svg>
"""


def cartao(p, tema):
    t = TEMAS[tema]
    linhas = "".join(f'<text x="118" y="{76 + i * 20}" class="desc">{escape(l)}</text>' for i, l in enumerate(p["desc"]))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="440" height="160" viewBox="0 0 440 160" role="img" aria-label="{escape(p['nome'])}">
  <style>
    text {{ font-family: {FONTE}; }}
    .titulo {{ font-size: 20px; font-weight: 700; fill: {t['titulo']}; }}
    .desc {{ font-size: 13.5px; fill: {t['texto']}; }}
    .tags {{ font-size: 12px; font-weight: 600; fill: {t['fraco']}; }}
    .acao {{ font-size: 13px; font-weight: 700; fill: {p['cor']}; }}
  </style>
  <rect x=".5" y=".5" width="439" height="159" rx="16" fill="{t['fundo']}" stroke="{t['borda']}"/>
  <rect x="22" y="24" width="80" height="80" rx="20" fill="{p['cor']}" fill-opacity="{'.14' if tema == 'claro' else '.22'}"/>
  <image href="{icone(p['emoji'])}" x="34" y="36" width="56" height="56"/>
  <text x="118" y="50" class="titulo">{escape(p['nome'])}</text>
  {linhas}
  <rect x="22" y="122" width="{14 + len(p['tags']) * 6.6:.0f}" height="24" rx="12" fill="{t['chip']}"/>
  <text x="{29}" y="138" class="tags">{escape(p['tags'])}</text>
  <text x="418" y="139" class="acao" text-anchor="end">{escape(p['acao'])} →</text>
</svg>
"""


def destaque(tema):
    t = TEMAS[tema]
    thumb = imagem_local(os.path.join(RAIZ, "scripts", "radar.jpg"))
    chips = [("AUC 0,92", "#6d5cf5"), ("11 testes automáticos", "#16a34a"), ("0 dependências", "#0ea5e9")]
    x, partes = 36, []
    for txt, cor in chips:
        w = 26 + len(txt) * 7.6
        partes.append(f'<rect x="{x}" y="196" width="{w:.0f}" height="30" rx="15" fill="{cor}" fill-opacity=".14"/>'
                      f'<text x="{x + w / 2:.0f}" y="216" class="chip" fill="{cor}" text-anchor="middle">{txt}</text>')
        x += w + 8
    desc = ["Uma IA que aprende a detectar pagamentos suspeitos,",
            "treinada direto no navegador. Regressão logística do zero,",
            "métricas de negócio, curva ROC e um simulador que",
            "explica o porquê de cada decisão."]
    linhas = "".join(f'<text x="36" y="{110 + i * 21}" class="desc">{escape(l)}</text>' for i, l in enumerate(desc))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="260" viewBox="0 0 900 260" role="img" aria-label="Radar de Fraude: IA que detecta pagamentos suspeitos">
  <defs><clipPath id="c"><rect x="486" y="22" width="392" height="216" rx="14"/></clipPath></defs>
  <style>
    text {{ font-family: {FONTE}; }}
    .rot {{ font-size: 12px; font-weight: 700; letter-spacing: 2px; fill: #6d5cf5; }}
    .titulo {{ font-size: 32px; font-weight: 800; letter-spacing: -1px; fill: {t['titulo']}; }}
    .desc {{ font-size: 14.5px; fill: {t['texto']}; }}
    .chip {{ font-size: 12.5px; font-weight: 700; }}
  </style>
  <rect x=".5" y=".5" width="899" height="259" rx="20" fill="{t['fundo']}" stroke="{t['borda']}"/>
  <text x="36" y="44" class="rot">PROJETO EM DESTAQUE · INTELIGÊNCIA ARTIFICIAL</text>
  <image href="{icone('🛡️')}" x="34" y="54" width="36" height="36"/>
  <text x="80" y="84" class="titulo">Radar de Fraude</text>
  {linhas}
  {"".join(partes)}
  <image href="{thumb}" x="486" y="22" width="392" height="248" preserveAspectRatio="xMidYMin slice" clip-path="url(#c)"/>
  <rect x="486.5" y="22.5" width="391" height="215" rx="14" fill="none" stroke="{t['borda']}"/>
</svg>
"""


PROJETOS = [
    {"slug": "lista-compras", "emoji": "🛒", "nome": "Lista da Família", "cor": "#1e9e57", "acao": "Abrir app",
     "desc": ["Lista de compras com categorias, marcas,", "sugestões e um cardápio com o que tem."], "tags": "HTML · CSS · JavaScript"},
    {"slug": "controle-gastos", "emoji": "🐷", "nome": "Controle de Gastos", "cor": "#16a066", "acao": "Abrir app",
     "desc": ["Orçamento do mês, gráficos e um medidor", "de quanto vai embora em besteira."], "tags": "HTML · CSS · JavaScript"},
    {"slug": "minhoca-faminta", "emoji": "🐛", "nome": "Minhoca Faminta", "cor": "#ff5f8f", "acao": "Jogar",
     "desc": ["Jogo da minhoca com frutas 3D, recorde", "e controle por toque no celular."], "tags": "Canvas · JavaScript"},
    {"slug": "empilha", "emoji": "🍬", "nome": "Empilha!", "cor": "#7c5cf5", "acao": "Jogar",
     "desc": ["Encaixe os doces que caem e limpe as", "linhas. Fica mais rápido a cada nível."], "tags": "Canvas · JavaScript"},
]


def main():
    salvar("capa.svg", capa())
    for tema in TEMAS:
        salvar(f"radar-fraude-{tema}.svg", destaque(tema))
        for p in PROJETOS:
            salvar(f"{p['slug']}-{tema}.svg", cartao(p, tema))
    print("ok:", sorted(os.listdir(SAIDA)))


if __name__ == "__main__":
    main()
