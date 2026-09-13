"""
Gera o PDF de entrega da Sistematizacao.

    python docs/gerar_pdf.py                      # com o link do video em aberto
    python docs/gerar_pdf.py --video https://...  # com o link preenchido

Saida: docs/SISTEMATIZACAO_MEC_GrupoSigma.pdf

Conteudo, na ordem exigida pelo enunciado:
  1. Identificacao (nome, matricula, grupo)
  2. Link dos dados crus
  3. Link da solucao (repositorio)
  4. Link do video
  5. Resumo executivo de 1 pagina

Renderizacao: HTML + CSS de impressao, convertido pelo Chrome em modo
headless. Nao depende de LaTeX nem de pandoc.
"""

import argparse
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA_PDF = os.path.join(AQUI, "SISTEMATIZACAO_MEC_GrupoSigma.pdf")
SAIDA_HTML = os.path.join(AQUI, "_entrega.html")

URL_DADOS = "https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset"
URL_REPO = "https://github.com/santanexx/sistematizacao-matematica"

CSS = """
@page { size: A4; margin: 18mm 20mm 16mm 20mm; }
* { box-sizing: border-box; }
body {
  font-family: "Liberation Serif", "DejaVu Serif", Georgia, serif;
  font-size: 10.5pt; line-height: 1.36; color: #111; margin: 0;
}
h1 { font-size: 19pt; margin: 0 0 2px 0; letter-spacing: -0.2px; }
h2 { font-size: 13pt; margin: 18px 0 6px 0; border-bottom: 1px solid #999; padding-bottom: 3px; }
h3 { font-size: 11pt; margin: 12px 0 4px 0; }
p { margin: 0 0 7px 0; text-align: justify; }
.sub { font-size: 11.5pt; color: #333; margin-bottom: 14px; }
.meta { color: #444; font-size: 10pt; margin-bottom: 18px; }
table { border-collapse: collapse; width: 100%; margin: 6px 0 10px 0; font-size: 10pt; }
th, td { border: 1px solid #bbb; padding: 4px 7px; vertical-align: top; text-align: left; }
th { background: #efefef; font-weight: 600; }
.mono { font-family: "Liberation Mono", "DejaVu Sans Mono", monospace; font-size: 9.5pt; }
a { color: #0b4a8b; text-decoration: none; }
.link-row { margin: 4px 0 8px 0; }
.link-row .rotulo { display: inline-block; width: 150px; font-weight: 600; }
.pendente { color: #9a2c2c; font-weight: 600; }
.quebra { page-break-before: always; }
.compacto { font-size: 9.8pt; line-height: 1.3; }
.compacto p { margin-bottom: 4px; }
.compacto h3 { margin: 9px 0 3px 0; font-size: 10.5pt; }
.compacto table { font-size: 9.2pt; margin: 4px 0 6px 0; }
.compacto th, .compacto td { padding: 2.5px 6px; }
.compacto .descoberta { margin-bottom: 6px; }
.mono-bloco { font-family: "Liberation Mono", "DejaVu Sans Mono", monospace; font-size: 8.4pt;
  text-align: left; white-space: nowrap; margin: 2px 0 3px 0; }
.descoberta { margin-bottom: 8px; }
.descoberta b { display: block; margin-bottom: 1px; }
.rodape { margin-top: 14px; font-size: 9pt; color: #555; border-top: 1px solid #ccc; padding-top: 5px; }
ul { margin: 2px 0 7px 18px; padding: 0; }
li { margin-bottom: 2px; }
"""


def html_entrega(link_video):
    video = (
        f'<a href="{link_video}">{link_video}</a>'
        if link_video
        else '<span class="pendente">[link a ser inserido antes do envio]</span>'
    )

    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<title>Sistematização MEC — Grupo Sigma</title>
<style>{CSS}</style></head>
<body>

<h1>Sistematização — Matemática e Estatística para Computação</h1>
<div class="sub">Laboratório Estatístico Interativo</div>
<div class="meta">Entrega do <b>Grupo Sigma</b> · Prof. Romes</div>

<h2>1. Identificação</h2>
<table>
  <tr><th style="width:55%">Nome completo</th><th>Matrícula</th></tr>
  <tr><td>Gustavo Santana</td><td class="mono">72650214</td></tr>
  <tr><td>Pedro Oliveira Rocha</td><td class="mono">72650213</td></tr>
  <tr><td>Pedro Falcão</td><td class="mono">72650212</td></tr>
</table>
<p><b>Nome do grupo:</b> Grupo Sigma</p>

<h2>2. Link dos dados crus</h2>
<div class="link-row"><span class="rotulo">Fonte original:</span>
  <a href="{URL_DADOS}">{URL_DADOS}</a></div>
<p>Bike Sharing Dataset — UCI Machine Learning Repository. Arquivo <span class="mono">hour.csv</span>:
17.379 registros horários (2011–2012) do sistema Capital Bikeshare, Washington D.C.,
com condições climáticas, calendário e contagem de aluguéis.</p>

<h2>3. Link da solução</h2>
<div class="link-row"><span class="rotulo">Repositório público:</span>
  <a href="{URL_REPO}">{URL_REPO}</a></div>
<p>Contém o código-fonte completo (núcleo estatístico separado da interface), o arquivo de testes
automatizados, o <span class="mono">README.md</span> com os nomes dos componentes e instruções de
execução, e o <span class="mono">RELATORIO.md</span> da atividade. Histórico com 31 commits
assinados, distribuídos entre os três integrantes.</p>

<h2>4. Link do vídeo de demonstração</h2>
<div class="link-row"><span class="rotulo">Vídeo (3–5 min):</span> {video}</div>

<div class="rodape">
Links testados em janela anônima antes do envio. Repositório público; dataset em fonte aberta.
</div>

<!-- ===================== PÁGINA 2: RESUMO EXECUTIVO ===================== -->
<div class="quebra compacto">

<h1 style="font-size:16pt">5. Resumo executivo</h1>
<div class="meta">Grupo Sigma · Gustavo Santana (72650214) · Pedro Oliveira Rocha (72650213) · Pedro Falcão (72650212)</div>

<h3>O que foi construído</h3>
<p>Uma aplicação Streamlit em que <b>nenhuma medida exibida ao usuário vem de biblioteca pronta</b>.
O pacote próprio <span class="mono">minhastats/</span> implementa todo o núcleo estatístico em Python puro
— importando apenas <span class="mono">math</span> e <span class="mono">random</span> — e é validado contra
NumPy, SciPy e <span class="mono">statistics</span> por <b>518 testes automatizados</b>, com tolerância relativa
de 10<sup>−9</sup> justificada pela análise de erro de ponto flutuante. Até os gráficos respeitam a regra:
histograma via <span class="mono">ax.bar</span> sobre a nossa tabela de classes e boxplot via
<span class="mono">ax.bxp</span> com os nossos quartis, porque <span class="mono">plt.hist</span> e
<span class="mono">plt.boxplot</span> calculariam eles mesmos.</p>

<h3>Dataset</h3>
<p>Bike Sharing Dataset (UCI): 17.379 registros, 10 variáveis numéricas e 7 categóricas na aplicação.
As variáveis meteorológicas, normalizadas no original, foram convertidas para °C, % e km/h pela
transformação inversa documentada pelos autores.</p>

<h3>Módulos implementados</h3>
<table>
<tr><th style="width:24%">Módulo</th><th>Entregue</th></tr>
<tr><td>0 — Dados reais</td><td>Dataset, conferência automática dos requisitos, dicionário de variáveis.</td></tr>
<tr><td>1 — Núcleo próprio</td><td>Média, mediana, moda, amplitude, variância e desvio padrão (amostral e populacional),
  percentis, quartis, IQR, CV, covariância, Pearson, assimetria e curtose — todos testados contra NumPy/SciPy.</td></tr>
<tr><td>2 — Descritiva</td><td>Tabelas de frequência, medidas, histograma, boxplot, barras, pizza, outliers por IQR
  e interpretação textual automática.</td></tr>
<tr><td>3 — Simulação</td><td>Lei dos Grandes Números (moeda, dado, π) e Teorema Central do Limite, com repetições,
  tamanho da amostra e semente controlados pelo usuário.</td></tr>
<tr><td>4 — Distribuições</td><td>Normal, Uniforme, Exponencial, Poisson e Binomial sobrepostas ao histograma, parâmetros
  estimados dos dados, χ² comparativo.</td></tr>
<tr><td>5 — Regressão</td><td>Dispersão, r, mínimos quadrados próprios, equação, R², predição interativa com alerta de
  extrapolação, resíduos e alerta de causalidade.</td></tr>
<tr><td>6 — Descobertas</td><td>As três descobertas abaixo, recalculadas ao vivo pelo núcleo.</td></tr>
</table>

<h3>As três principais descobertas</h3>

<div class="descoberta"><b>1. A temperatura importa — mas explica menos de 17% dos aluguéis.</b>
r = 0,4048 e reta ŷ = 9,30x − 0,04 (cada +1 °C ⇒ +9,3 aluguéis/hora). Mas R² = 0,1638: 83,6% da variação
ficam de fora — não por falta de relação, e sim porque a relação não é linear. A demanda tem dois picos
diários (359 aluguéis às 8h, 461 às 17h, contra 6,35 às 4h) que nenhuma reta em função da temperatura
captura. O gráfico de resíduos mostra um funil (heterocedasticidade).</div>

<div class="descoberta"><b>2. Dois públicos opostos escondidos no mesmo total.</b>
Do dia útil para o fim de semana, usuários casuais sobem +124,7% (25,6 → 57,4 aluguéis/h) enquanto
registrados caem −26,1% (167,7 → 124,0). No agregado os efeitos quase se cancelam (−6,1%): olhar só o total
levaria à conclusão errada de que o calendário não afeta a demanda. É o paradoxo da agregação — lazer contra
deslocamento pendular. CV de 138% contra 98%, curtose 7,57 contra 2,75 e 1.192 outliers no público casual.</div>

<div class="descoberta"><b>3. Os dados violam a Poisson por um fator de 174× — e o TCL não se abala.</b>
Aluguéis são contagens, mas o índice de dispersão s²/x̄ vale 173,66 (na Poisson vale 1): sobredispersão
extrema, modelo descartado. Ainda assim, partindo de uma variável com assimetria 2,499 e curtose 7,569, o
TCL funciona como prometido: a assimetria das médias amostrais cai para 0,132 com n = 200 (−94,7%) e o
desvio observado reproduz σ/√n com erro inferior a 2% em todos os tamanhos testados.</div>

<h3>Reprodutibilidade</h3>
<div class="mono-bloco">git clone {URL_REPO}.git &amp;&amp; cd sistematizacao-matematica<br>
python3 -m venv .venv &amp;&amp; source .venv/bin/activate &amp;&amp; pip install -r requirements.txt<br>
pytest &nbsp;# 518 testes &nbsp;&nbsp;·&nbsp;&nbsp; streamlit run app.py</div>
<p style="font-size:9pt">Sementes fixas (42, 2024, 21) tornam todos os números acima reproduzíveis em qualquer máquina.</p>

</div>
</body></html>"""


def gerar(link_video):
    with open(SAIDA_HTML, "w", encoding="utf-8") as f:
        f.write(html_entrega(link_video))

    comando = [
        "google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox",
        "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={SAIDA_PDF}", f"file://{SAIDA_HTML}",
    ]
    resultado = subprocess.run(comando, capture_output=True, text=True, timeout=120)
    os.remove(SAIDA_HTML)

    if not os.path.exists(SAIDA_PDF):
        print("Falha ao gerar o PDF:", resultado.stderr[-800:], file=sys.stderr)
        sys.exit(1)

    tamanho = os.path.getsize(SAIDA_PDF) // 1024
    print(f"PDF gerado: {SAIDA_PDF} ({tamanho} KB)")
    if not link_video:
        print("AVISO: o link do video ficou em aberto. Regere com --video <URL> antes de enviar.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--video", default="", help="URL do video de demonstracao")
    gerar(parser.parse_args().video)
