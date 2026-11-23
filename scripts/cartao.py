"""Gera o cartão de estatísticas do perfil (SVG) a partir da resposta do GraphQL do GitHub.

Uso: python3 cartao.py dados.json saida.svg
Só usa a biblioteca padrão do Python.
"""
import json
import sys
from datetime import date, timedelta
from html import escape


def sequencias(dias):
    """Devolve (sequência atual, maior sequência) de dias seguidos com contribuição.

    Um dia de hoje ainda sem commit não quebra a sequência atual.
    """
    maior = corrida = 0
    for d in dias:
        corrida = corrida + 1 if d["contributionCount"] > 0 else 0
        maior = max(maior, corrida)
    atual = 0
    pendentes = list(reversed(dias))
    if pendentes and pendentes[0]["contributionCount"] == 0 and pendentes[0]["date"] == date.today().isoformat():
        pendentes = pendentes[1:]
    for d in pendentes:
        if d["contributionCount"] == 0:
            break
        atual += 1
    return atual, maior


def numero(n):
    return f"{n:,}".replace(",", ".")


def svg(stats):
    blocos = [
        ("🔥", numero(stats["atual"]), "dias seguidos", "#ff7a59"),
        ("🏆", numero(stats["maior"]), "maior sequência", "#f5b301"),
        ("✅", numero(stats["contribuicoes"]), "contribuições no ano", "#2fbf71"),
        ("📦", numero(stats["repos"]), "projetos públicos", "#5b8def"),
        ("⭐", numero(stats["estrelas"]), "estrelas", "#a66bff"),
    ]
    largura, altura, margem = 840, 190, 24
    w = (largura - 2 * margem - 4 * 12) / 5
    partes = []
    for i, (emoji, valor, rotulo, cor) in enumerate(blocos):
        x = margem + i * (w + 12)
        partes.append(f"""
    <g>
      <rect x="{x:.1f}" y="62" width="{w:.1f}" height="106" rx="18" fill="#ffffff" fill-opacity=".14"/>
      <rect x="{x + 14:.1f}" y="76" width="34" height="34" rx="11" fill="{cor}"/>
      <text x="{x + 31:.1f}" y="99" font-size="17" text-anchor="middle">{emoji}</text>
      <text x="{x + 14:.1f}" y="140" class="valor">{escape(valor)}</text>
      <text x="{x + 14:.1f}" y="158" class="rotulo">{escape(rotulo)}</text>
    </g>""")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" viewBox="0 0 {largura} {altura}" role="img" aria-label="Estatísticas do GitHub">
  <defs>
    <linearGradient id="fundo" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#22b877"/>
      <stop offset=".55" stop-color="#13804a"/>
      <stop offset="1" stop-color="#0b5e35"/>
    </linearGradient>
  </defs>
  <style>
    text {{ font-family: 'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif; fill: #ffffff; }}
    .titulo {{ font-size: 19px; font-weight: 700; }}
    .sub {{ font-size: 12px; fill-opacity: .8; }}
    .valor {{ font-size: 24px; font-weight: 800; }}
    .rotulo {{ font-size: 11px; fill-opacity: .85; }}
  </style>
  <rect width="{largura}" height="{altura}" rx="24" fill="url(#fundo)"/>
  <circle cx="{largura - 40}" cy="10" r="90" fill="#ffffff" fill-opacity=".07"/>
  <text x="{margem}" y="40" class="titulo">Meu GitHub em números</text>
  <text x="{largura - margem}" y="40" class="sub" text-anchor="end">atualizado em {escape(stats["data"])}</text>{"".join(partes)}
</svg>
"""


def main():
    entrada, saida = sys.argv[1], sys.argv[2]
    with open(entrada, encoding="utf-8") as f:
        usuario = json.load(f)["data"]["user"]
    calendario = usuario["contributionsCollection"]["contributionCalendar"]
    dias = [d for semana in calendario["weeks"] for d in semana["contributionDays"]]
    atual, maior = sequencias(dias)
    stats = {
        "atual": atual,
        "maior": maior,
        "contribuicoes": calendario["totalContributions"],
        "repos": usuario["repositories"]["totalCount"],
        "estrelas": sum(r["stargazerCount"] for r in usuario["repositories"]["nodes"]),
        "data": date.today().strftime("%d/%m/%Y"),
    }
    with open(saida, "w", encoding="utf-8") as f:
        f.write(svg(stats))
    print(json.dumps(stats, ensure_ascii=False))


def _autoteste():
    hoje = date.today()
    dia = lambda delta, n: {"date": (hoje - timedelta(days=delta)).isoformat(), "contributionCount": n}
    assert sequencias([dia(3, 1), dia(2, 0), dia(1, 2), dia(0, 1)]) == (2, 2)
    assert sequencias([dia(3, 1), dia(2, 1), dia(1, 1), dia(0, 0)]) == (3, 3)  # hoje sem commit não quebra
    assert sequencias([dia(2, 1), dia(1, 0), dia(0, 0)]) == (0, 1)
    assert sequencias([]) == (0, 0)
    assert numero(1234) == "1.234"


if __name__ == "__main__":
    _autoteste()
    main()
