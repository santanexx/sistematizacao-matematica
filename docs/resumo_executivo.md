# Resumo Executivo — Laboratório Estatístico Interativo

**Disciplina:** Matemática e Estatística para Computação — Sistematização
**Nome do grupo:** Grupo Sigma
**Integrantes:** Gustavo Santana (72650214), Pedro Oliveira Rocha
(72650213), Pedro Falcão (72650212)

**Dataset:** Bike Sharing Dataset — UCI Machine Learning Repository
<https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset>
17.379 registros horários · 10 variáveis numéricas · 7 categóricas

**Repositório:** <https://github.com/santanexx/sistematizacao-matematica>
**Vídeo:** `[PREENCHER]`

---

## O que foi construído

Uma aplicação Streamlit em que **nenhuma medida exibida ao usuário vem de
biblioteca pronta**. O pacote `minhastats/` implementa todo o núcleo estatístico
em Python puro — importando apenas `math` e `random` — e é validado contra
NumPy, SciPy e `statistics` por **518 testes automatizados**, com tolerância
relativa de $10^{-9}$ justificada pela análise de erro de ponto flutuante.

Cuidado adicional: `plt.hist` e `plt.boxplot` **calculariam** as classes e os
quartis. Por isso o histograma é desenhado com `ax.bar` sobre a nossa tabela de
frequências e o boxplot com `ax.bxp`, alimentado com os quartis e outliers já
calculados pelo núcleo.

## Módulos implementados

| Módulo | Entregue |
|---|---|
| **0 — Dados reais** | Dataset com 17.379 registros, conferência automática dos requisitos, dicionário de variáveis, desnormalização para °C / % / km/h |
| **1 — Núcleo próprio** | Média, mediana, moda, amplitude, variância e desvio padrão (amostral e populacional), percentis, quartis, IQR, coeficiente de variação, covariância, Pearson, assimetria e curtose — todos com testes contra NumPy/SciPy |
| **2 — Descritiva interativa** | Tabelas de frequência (classes e categorias), todas as medidas, histograma, boxplot, barras, pizza, outliers por IQR e interpretação textual automática |
| **3 — Simulação** | Lei dos Grandes Números (moeda, dado, estimativa de π) e Teorema Central do Limite, com nº de repetições, tamanho da amostra e semente controlados pelo usuário |
| **4 — Distribuições teóricas** | Normal, Uniforme, Exponencial, Poisson e Binomial sobrepostas ao histograma, com parâmetros estimados dos dados e χ² comparativo |
| **5 — Correlação e regressão** | Dispersão, r de Pearson, mínimos quadrados implementados por nós, equação, R², predição interativa com alerta de extrapolação, resíduos e o alerta de causalidade |
| **6 — Descobertas** | As três descobertas abaixo, recalculadas ao vivo pelo núcleo |

## As três principais descobertas

**1. A temperatura importa — mas explica menos de 17% dos aluguéis.**
$r = 0{,}4048$ e reta $\hat{y} = 9{,}30x - 0{,}04$ (cada +1 °C ⇒ +9,3
aluguéis/hora). Mas $R^2 = 0{,}1638$: **83,6% da variação ficam de fora** — não
por falta de relação, e sim porque a relação **não é linear**. A demanda tem dois
picos diários (média de 359 aluguéis às 8h e 461 às 17h, contra 6,35 às 4h) que
nenhuma reta em função da temperatura captura. O gráfico de resíduos mostra um
funil (heterocedasticidade), confirmando a inadequação do modelo linear.

**2. Dois públicos opostos escondidos no mesmo total.**
Do dia útil para o fim de semana, usuários **casuais sobem +124,7%** (25,6 → 57,4
aluguéis/hora) enquanto **registrados caem −26,1%** (167,7 → 124,0). No agregado
os efeitos quase se cancelam: o total varia apenas −6,1%. São dois fenômenos
distintos — lazer e deslocamento pendular — e olhar só `cnt` levaria à conclusão
errada de que o calendário quase não afeta a demanda. É o **paradoxo da
agregação**. A assinatura estatística confirma: CV de 138,2% contra 98,4%,
curtose 7,57 contra 2,75, e 1.192 outliers (6,86%) no público casual.

**3. Os dados violam a Poisson por um fator de 174× — e o TCL não se abala.**
Aluguéis são contagens, mas o índice de dispersão $s^2/\bar{x}$ vale **173,66**
para `cnt` (na Poisson vale exatamente 1): sobredispersão extrema, modelo
descartado. Ainda assim, partindo de `casual` — assimetria 2,499, curtose 7,569 —
o **Teorema Central do Limite funciona exatamente como prometido**: a assimetria
das médias amostrais cai para 0,132 com $n = 200$ (redução de 94,7%) e o desvio
padrão observado reproduz $\sigma/\sqrt{n}$ com erro inferior a 2% em todos os
tamanhos testados. Não é preciso assumir normalidade da população para trabalhar
com a média dela.

---

## Reprodutibilidade

```bash
git clone https://github.com/santanexx/sistematizacao-matematica.git  &&  cd sistematizacao-matematica
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest              # 518 testes
streamlit run app.py
```

As simulações usam sementes fixas (42, 2024 e 21), então todos os números deste
resumo são reproduzíveis em qualquer máquina.
