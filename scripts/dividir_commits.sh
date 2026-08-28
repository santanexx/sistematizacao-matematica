#!/usr/bin/env bash
#
# dividir_commits.sh
# ==================
#
# Reconstrói o histórico do repositório em 26 commits pequenos e temáticos,
# distribuídos entre os três integrantes da equipe.
#
# COMO FUNCIONA
# O conteúdo final do projeto NÃO muda. O script cria um branch órfão
# (sem histórico), adiciona os arquivos em ordem de dependência — um
# commit por assunto — e no final CONFERE que a árvore resultante é
# idêntica à do branch original. Se houver qualquer diferença, ele aborta
# e não mexe em nada.
#
# O branch antigo é preservado com o nome `historico-monolitico`, para o
# caso de você querer voltar atrás.
#
# DOIS MODOS DE USO
#
# 1) MODO REVEZAMENTO (recomendado)  ./scripts/dividir_commits.sh --pausar
#
# O script para toda vez que a trilha muda de pessoa e espera ENTER.
# A ideia é que cada integrante sente na máquina, LEIA os arquivos da
# própria trilha e só então libere os commits. O commit sai com o nome
# dessa pessoa como autora E como committer, porque foi ela quem
# executou.
#
# 2) MODO DIRETO                     ./scripts/dividir_commits.sh
#
# Roda tudo de uma vez, atribuindo a autoria de cada commit pela
# tabela abaixo (`--author`). Mais rápido, mas quem executa fica
# registrado como committer de tudo.
#
# --sem-scripts  não publica a pasta `scripts/` no histórico novo. Os
# arquivos continuam no disco (como não rastreados) e
# seguem utilizáveis; eles simplesmente não vão para o
# repositório entregue. Sem essa opção, a ferramenta é
# versionada junto — o que é transparente e defensável.
#
# O barema prevê arguição individual: cada integrante precisa saber
# explicar qualquer parte da solução. As trilhas abaixo foram montadas
# para que a divisão faça sentido temático — cada pessoa fica com um
# bloco coerente (núcleo + testes + página da interface do mesmo assunto).
#
# PRÉ-REQUISITOS
# - `scripts/equipe.conf` preenchido com nome e e-mail de cada um
# - árvore de trabalho limpa (`git status` sem alterações pendentes)
#
set -euo pipefail

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"

# shellcheck source=equipe.conf
source "scripts/equipe.conf"

BRANCH_NOVO="main"
BRANCH_ANTIGO="historico-monolitico"

PAUSAR=0
INCLUIR_SCRIPTS=1

for arg in "$@"; do
    case "$arg" in
        --pausar)       PAUSAR=1 ;;
        --sem-scripts)  INCLUIR_SCRIPTS=0 ;;
        -h|--help)
            sed -n '3,50p' "${BASH_SOURCE[0]}" | sed 's/^# \?//'
            exit 0 ;;
        *)
            echo "ERRO: Argumento desconhecido: $arg"
            echo "Use: $0 [--pausar] [--sem-scripts]"
            exit 1 ;;
    esac
done

# ---------------------------------------------------------------------------
# Verificações de segurança
# ---------------------------------------------------------------------------

if [[ -n "$(git status --porcelain)" ]]; then
    echo "ERRO: A árvore de trabalho tem alterações pendentes."
    echo "Faça commit ou stash antes de reescrever o histórico."
    exit 1
fi

for var in EMAIL_G EMAIL_PR EMAIL_PF; do
    if [[ "${!var}" == *PREENCHER* ]]; then
        echo "ERRO: $var ainda está com o valor de exemplo em scripts/equipe.conf."
        echo "Preencha o e-mail de cada integrante antes de rodar."
        exit 1
    fi
done

if git show-ref --verify --quiet "refs/heads/$BRANCH_ANTIGO"; then
    echo "ERRO: O branch '$BRANCH_ANTIGO' já existe — parece que o script já rodou."
    echo "Se quiser rodar de novo: git branch -D $BRANCH_ANTIGO"
    exit 1
fi

BRANCH_ORIGINAL="$(git branch --show-current)"
COMMIT_ORIGINAL="$(git rev-parse HEAD)"

echo "Branch atual: $BRANCH_ORIGINAL ($(git rev-list --count HEAD) commits)"
echo "Árvore final que será preservada: $COMMIT_ORIGINAL"
echo

# ---------------------------------------------------------------------------
# Motor de commits
# ---------------------------------------------------------------------------

ULTIMO_AUTOR=""
CONTADOR=0

# commitar <inicial-do-autor> <arquivos...> -- <<< mensagem via stdin
commitar() {
    local sigla="$1"; shift
    local nome email

    case "$sigla" in
        G)  nome="$NOME_G";  email="$EMAIL_G"  ;;
        PR) nome="$NOME_PR"; email="$EMAIL_PR" ;;
        PF) nome="$NOME_PF"; email="$EMAIL_PF" ;;
        *)  echo "ERRO: Sigla de autor desconhecida: $sigla"; exit 1 ;;
    esac

    local mensagem
    mensagem="$(cat)"          # a mensagem vem pelo stdin (heredoc)

    # Pausa quando a trilha troca de pessoa
    if [[ $PAUSAR -eq 1 && "$sigla" != "$ULTIMO_AUTOR" ]]; then
        echo
        echo "══════════════════════════════════════════════════════════════"
        echo "Agora é a vez de: $nome"
        echo "Revise os arquivos desta trilha antes de continuar."
        echo "══════════════════════════════════════════════════════════════"
        read -r -p "Pressione ENTER quando $nome estiver no teclado... "
        echo
    fi
    ULTIMO_AUTOR="$sigla"

    git add -- "$@"

    if [[ $PAUSAR -eq 1 ]]; then
        # quem executa é a própria pessoa: autor E committer são ela
        GIT_AUTHOR_NAME="$nome"GIT_AUTHOR_EMAIL="$email" \
        GIT_COMMITTER_NAME="$nome" GIT_COMMITTER_EMAIL="$email" \
            git commit -q -m "$mensagem"
    else
        git commit -q --author="$nome <$email>" -m "$mensagem"
    fi

    CONTADOR=$((CONTADOR + 1))
    printf "  [%02d] %-22s %s\n" "$CONTADOR" "($nome)" "$(echo "$mensagem" | head -1)"
}

# ---------------------------------------------------------------------------
# Cria o branch órfão e esvazia o índice (a árvore de trabalho permanece)
# ---------------------------------------------------------------------------

echo "Criando histórico novo..."
git checkout -q --orphan "__reconstrucao__"
git rm -rq --cached .

# ===========================================================================
# TRILHA A — Gustavo Santana
# Estatística descritiva (o alicerce do núcleo), simulação de Monte Carlo,
# carregamento dos dados e a montagem da aplicação.
#
# TRILHA B — Pedro Oliveira Rocha
# Associação entre variáveis: covariância, correlação, mínimos quadrados,
# a página de regressão, a das descobertas e o relatório.
#
# TRILHA C — Pedro Falcão
# Frequências, outliers, distribuições teóricas, toda a camada de gráficos
# e as páginas descritiva e de distribuições.
# ===========================================================================

commitar G .gitignore .vscode/settings.json requirements.txt pytest.ini data/hour.csv data/Readme_UCI.txt <<'MSG'
chore: estrutura inicial do projeto e dataset

Esqueleto do repositorio, dependencias fixadas e o dataset escolhido.

Dataset: Bike Sharing Dataset (UCI Machine Learning Repository)
https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset
17.379 registros horarios de 2011-2012, com clima, calendario e contagem
de alugueis. Atende com folga ao Modulo 0: minimo de 1.000 registros,
4 variaveis numericas e 2 categoricas.

O CSV vai versionado (1,1 MB) para que um `git clone` seguido de
`pip install -r requirements.txt` ja permita rodar tudo, sem download
manual nem chave de API.
MSG

commitar G minhastats/descritiva.py <<'MSG'
feat(nucleo): medidas descritivas em Python puro

Primeira peca do Modulo 1. Media, mediana, moda (multimodal), amplitude,
variancia e desvio padrao nas versoes amostral e populacional, percentis
por interpolacao linear, quartis, IQR, coeficiente de variacao, erro
padrao da media, assimetria (Pearson e momento) e curtose.

Decisoes de implementacao:

- Variancia calculada em DOIS PASSOS (media primeiro, depois os desvios).
  A forma equivalente `soma(x^2) - n*media^2` faria tudo numa passada,
  mas sofre cancelamento catastrofico quando a media e grande frente ao
  desvio: os dois termos ficam enormes e quase iguais, e a subtracao
  aniquila os digitos significativos.

- Ordenacao propria por merge sort. `sorted()` seria permitido, mas
  mediana e percentis dependem inteiramente dela -- se afirmamos que o
  calculo e nosso, o passo do qual ele depende tambem deve ser.

- Percentil pelo metodo dos postos (tipo 7), o mesmo default do
  numpy.percentile, escolhido justamente para permitir validacao direta.

- `_validar()` descarta NaN e valores nao numericos, e levanta ValueError
  explicito quando a amostra e pequena demais.

O modulo importa apenas `math`.
MSG

commitar G tests/conftest.py tests/test_descritiva.py <<'MSG'
test(descritiva): 200 testes contra NumPy, SciPy e statistics

Valida cada funcao descritiva em tres frentes: casos calculados a mao,
o dataset real com 17.379 registros e amostras aleatorias com semente
fixa em escalas hostis (ordem de 10^6, de 10^-6, negativas, com muitos
empates).

O cenario "grande_escala" e o teste critico da estabilidade numerica:
valores ~10^6 com desvio ~10^4, onde a formula ingenua de variancia
perderia precisao e a nossa nao perde.

Tolerancia relativa de 1e-9, justificada em detalhe no conftest: o float
de 64 bits carrega ~16 digitos significativos, o erro acumulado com
n=17.379 parcelas chega a ordem de 1e-12, e o NumPy usa somatorio pareado
-- ordem de operacoes diferente da nossa, e soma em ponto flutuante nao e
associativa. Um erro de FORMULA apareceria ja na segunda casa decimal.

Inclui testes de identidade matematica: s^2 = sigma^2 * n/(n-1) e Q2 = Md.
MSG

commitar PR minhastats/associacao.py <<'MSG'
feat(nucleo): covariancia, Pearson e minimos quadrados

Segunda peca do Modulo 1 e base do Modulo 5.

- covariancia amostral e populacional
- coeficiente de correlacao de Pearson, com clamp explicito em [-1, 1]
  (erro de arredondamento chega a produzir 1.0000000000000002, que
  quebraria quem consumisse o valor, por exemplo em math.acos)
- regressao linear simples pelo metodo dos minimos quadrados, resolvendo
  as equacoes normais: b = Sxy/Sxx e a = ybar - b*xbar
- decomposicao SQtot = SQreg + SQres, R^2, erro padrao da estimativa,
  predicao e residuos
- interpretacao textual da forca e do sentido da correlacao

`_validar_pares` descarta o PAR inteiro quando qualquer um dos lados e
invalido -- descartar so um lado quebraria o emparelhamento e produziria
uma correlacao sem sentido.
MSG

commitar PR tests/test_associacao.py <<'MSG'
test(associacao): 54 testes contra SciPy e NumPy

Compara covariancia com numpy.cov, correlacao com scipy.stats.pearsonr e
numpy.corrcoef, e a regressao com numpy.polyfit e scipy.stats.linregress,
tanto em pares sinteticos de relacao conhecida (linear perfeita, linear
com ruido, independente, quadratica) quanto nos pares reais do dataset.

Alem da comparacao numerica, verifica propriedades teoricas que pegam
erros que a comparacao sozinha deixaria passar:

- Cov(X,X) = Var(X) e Cov(X,Y) = Cov(Y,X)
- r invariante a transformacao linear de Y
- R^2 = r^2 na regressao simples
- SQtot = SQreg + SQres
- a reta passa por (xbar, ybar)
- a soma dos residuos e nula
MSG

commitar PF minhastats/frequencias.py <<'MSG'
feat(nucleo): tabelas de frequencia, Sturges e outliers por IQR

Motor do Modulo 2.

- tabela de frequencias categorica com fi, fr, percentual e acumuladas
- tabela em classes de igual amplitude para variaveis continuas, com o
  numero de classes pela regra de Sturges (k = teto de 1 + log2(n))
- deteccao de outliers pela regra de Tukey: LI = Q1 - f*IQR e
  LS = Q3 + f*IQR, com f configuravel (1,5 moderados / 3,0 extremos)
- interpretacao textual automatica que combina quatro leituras:
  assimetria, dispersao relativa pelo CV, achatamento pela curtose e
  presenca de outliers

A regra do IQR usa quartis, e nao media e desvio padrao, justamente
porque quartis sao robustos: um valor absurdo nao desloca Q1 e Q3, mas
envenena a media e o desvio.
MSG

commitar PF tests/test_frequencias.py <<'MSG'
test(frequencias): 63 testes, e a correcao de um bug real de borda

As contagens por classe sao comparadas com numpy.histogram para varias
colunas e varios valores de k. Foi esse teste que pegou um bug que era
invisivel a olho nu.

Sintoma: coluna 'hum' com k=20, cinco registros na classe errada.

Causa: a atribuicao era `indice = int((valor - li) / h)`. Com h = 0,05, a
borda da classe 17 vale 0,8500000000000001 e nao 0,85 -- porque 0,05 nao
tem representacao binaria exata. O valor 0,85 e MENOR que essa borda,
logo pertence a classe 16; mas int(0,85 / 0,05) devolve 17, ja que a
divisao resulta em 17,000000000000004.

Correcao: as bordas passam a ser calculadas explicitamente e o indice e
corrigido comparando com elas -- exatamente o que o np.histogram faz
internamente.

O episodio e a melhor justificativa que temos para a exigencia de
validacao automatizada: o histograma parecia perfeitamente normal.
MSG

commitar PF minhastats/distribuicoes.py <<'MSG'
feat(nucleo): distribuicoes teoricas e qualidade do ajuste

Base do Modulo 4. Normal (densidade e acumulada), Uniforme, Exponencial,
Binomial e Poisson, cada uma com o estimador dos parametros a partir dos
dados, mais o indice de dispersao e uma medida de qualidade do ajuste.

Duas decisoes numericas:

- A acumulada da Normal usa math.erf, porque a integral da Normal nao tem
  primitiva elementar. erf e funcao matematica da biblioteca padrao, nao
  uma funcao estatistica.

- A Poisson e calculada em ESCALA LOGARITMICA:
  ln P = -lambda + k*ln(lambda) - lgamma(k+1).
  O calculo direto estoura o float para valores modestos: com lambda=189
  (a media de 'cnt') e k=189, lambda^k tem mais de 400 digitos.

A qualidade do ajuste devolve o qui-quadrado como MEDIDA DESCRITIVA
comparativa entre candidatas -- nao e teste de hipotese: nao calculamos
p-valor nem corrigimos graus de liberdade pelos parametros estimados.
Isso esta documentado na propria docstring e no RELATORIO.
MSG

commitar PF tests/test_distribuicoes.py <<'MSG'
test(distribuicoes): 140 testes contra scipy.stats

Cada densidade e comparada ponto a ponto com a referencia do SciPy
(norm, uniform, expon, binom, poisson) para varios conjuntos de
parametros, e o coeficiente binomial com math.comb.

Testes de propriedade:
- soma das pmf da Binomial e da Poisson converge para 1
- regra empirica 68-95-99,7 da Normal
- F(mu) = 0,5 e monotonicidade da acumulada
- ajuste Normal melhor que Uniforme em dados gerados de uma Normal

test_poisson_lambda_grande_nao_estoura verifica lambda = k = 500, caso em
que a formula ingenua levantaria OverflowError -- e a prova de que a
escala logaritmica resolveu.
MSG

commitar G minhastats/simulacao.py <<'MSG'
feat(nucleo): Monte Carlo -- Lei dos Grandes Numeros e TCL

Motor do Modulo 3.

(a) LGN: lancamento de moeda com frequencia relativa acumulada passo a
    passo, lancamento de dado de f faces com media acumulada e frequencia
    por face, e a estimativa classica de pi por pontos no quadrado
    unitario. Mais uma tabela do erro em marcos de n, que deixa numerico
    o que o grafico mostra: o erro cai na ordem de 1/raiz(n), nao
    linearmente.

(b) TCL: sorteia amostras repetidas de uma variavel do dataset e devolve
    as medias amostrais junto com a previsao teorica (mu e sigma/raiz(n))
    e o que a simulacao efetivamente produziu.

`random` entra apenas como GERADOR de numeros aleatorios; toda medida
calculada sobre os resultados vem do proprio nucleo. Todas as funcoes
aceitam semente, para que os resultados sejam reproduziveis.
MSG

commitar G tests/test_simulacao.py <<'MSG'
test(simulacao): 28 testes de reprodutibilidade e convergencia

Simulacao nao tem valor de referencia exato como uma media, entao o que
se valida aqui e outra coisa:

1. Reprodutibilidade: a mesma semente produz exatamente o mesmo resultado.
2. Convergencia da LGN: o erro medio cai quando n cresce, e a estimativa
   fica dentro do intervalo previsto pela teoria (4 erros padrao).
3. TCL: a media das medias recupera mu, o desvio das medias reproduz
   sigma/raiz(n) com menos de 10% de folga, e a assimetria da
   distribuicao das medias cai monotonicamente conforme n cresce.

Os limites das assercoes vem da teoria (erro padrao da proporcao, desvio
de um dado honesto), nao de valores chutados.

Confirmacao independente: com n=200, scipy.stats.normaltest aplicado as
medias amostrais devolve p > 0,05 -- elas ja nao sao distinguiveis de
uma Normal.
MSG

commitar PR minhastats/__init__.py <<'MSG'
feat(nucleo): API publica do pacote minhastats

Reexporta as 45 funcoes dos cinco modulos para que a interface possa
escrever `from minhastats import media` em vez de navegar a estrutura
interna, e documenta a regra de ouro no docstring do pacote.

Com isso o Modulo 1 esta completo: media, mediana, moda, amplitude,
variancia e desvio padrao (amostral e populacional), quartis/percentis,
coeficiente de variacao, covariancia e correlacao de Pearson -- todos
exigidos pelo enunciado -- mais assimetria, curtose, minimos quadrados,
distribuicoes teoricas e simulacao.
MSG

commitar G app/__init__.py app/carregador.py <<'MSG'
feat(app): carregamento dos dados e catalogo das variaveis

Esta e a UNICA parte da aplicacao que fala com o pandas -- e mesmo aqui
ele so LE o CSV e organiza as colunas.

A funcao `coluna_como_lista()` e a fronteira do projeto: dali em diante
os dados sao listas Python comuns e todo calculo passa por minhastats.
Nenhum metodo estatistico do pandas atravessa essa linha.

Inclui a desnormalizacao das variaveis meteorologicas para unidades
reais, aplicando a transformacao inversa documentada pelos autores do
dataset (temp x 41, atemp x 50, hum x 100, windspeed x 67). Dizer que "a
temperatura media e 0,497" nao comunica nada; 20,4 C sim. Como sao
transformacoes lineares, correlacao, R^2 e CV sao identicos nas duas
escalas -- so a leitura melhora.

As categoricas ganham rotulos legiveis, e `periodo` e derivada da hora
para dar uma quinta variavel categorica.
MSG

commitar PF app/graficos.py <<'MSG'
feat(app): camada de graficos que nao calcula nada

Ponto sutil da regra de ouro: `plt.hist` CALCULA as classes e
`plt.boxplot` CALCULA os quartis. Usa-los violaria a regra em silencio --
os numeros na tela viriam do Matplotlib, nao de minhastats.

Por isso:
- o histograma e desenhado com ax.bar, a partir da nossa tabela de
  classes;
- o boxplot e desenhado com ax.bxp, que recebe um dicionario de
  estatisticas PRONTAS: quartis, limites de Tukey e a lista de outliers,
  todos vindos do nucleo.

O Matplotlib so pinta.

Inclui ainda dispersao com reta ajustada, grafico de residuos, barras e
pizza para categoricas, grafico de convergencia da LGN (com eixo x
logaritmico, porque a convergencia e da ordem de 1/raiz(n) e em escala
linear os primeiros lancamentos ficariam espremidos na origem) e a
visualizacao do Monte Carlo de pi. Paleta unica para os graficos
parecerem um sistema so.
MSG

commitar G app/paginas/__init__.py app/paginas/m0_dados.py <<'MSG'
feat(app): Modulo 0 -- apresentacao do dataset

Pagina com a fonte original, conferencia AUTOMATICA dos requisitos do
enunciado (numero de registros, de variaveis numericas e de categoricas),
amostra dos dados, dicionario completo das variaveis, verificacao de
valores ausentes e a distribuicao de cada variavel categorica -- esta
ultima ja calculada por minhastats.frequencias.
MSG

commitar PF app/paginas/m2_descritiva.py <<'MSG'
feat(app): Modulo 2 -- estatistica descritiva interativa

O usuario escolhe uma variavel e recebe:

- todas as medidas de tendencia central e dispersao, nas versoes amostral
  E populacional, vindas de minhastats.descritiva.resumo()
- tabela de frequencias em classes (com k ajustavel, sugerido por
  Sturges) para continuas, ou por categoria para qualitativas
- histograma e boxplot para numericas; barras e pizza para categoricas
- deteccao de outliers pela regra do IQR, com os limites explicitos
- interpretacao textual automatica da distribuicao

Inclui tambem o cruzamento de uma numerica com uma categorica: media,
mediana, desvio padrao e CV calculados DENTRO de cada categoria, com list
comprehension e minhastats -- sem groupby().mean().
MSG

commitar G app/paginas/m3_simulacao.py <<'MSG'
feat(app): Modulo 3 -- probabilidade e simulacao

Duas abas, com todos os parametros controlaveis pelo usuario, como o
enunciado exige.

(a) Lei dos Grandes Numeros: moeda (com p ajustavel), dado (com numero de
    faces ajustavel) e estimativa de pi. Numero de repeticoes e semente
    controlados por widget. Alem do grafico de convergencia, uma tabela
    do erro em marcos de n e o confronto com a Binomial teorica.

(b) Teorema Central do Limite: o usuario escolhe a variavel do dataset, o
    tamanho da amostra e o numero de repeticoes. A pagina mostra lado a
    lado a distribuicao original e a das medias amostrais, com a Normal
    prevista pelo TCL sobreposta, e uma tabela comparando a previsao
    (mu e sigma/raiz(n)) com o que a simulacao produziu.

A interpretacao automatica quantifica a queda da assimetria e a
discrepancia percentual entre o erro padrao teorico e o observado.
MSG

commitar PF app/paginas/m4_distribuicoes.py <<'MSG'
feat(app): Modulo 4 -- distribuicoes teoricas sobrepostas

O usuario escolhe a variavel e uma ou mais candidatas entre Normal,
Uniforme, Exponencial, Poisson e Binomial. A aplicacao estima os
parametros A PARTIR DOS DADOS, sobrepoe a curva ao histograma e calcula o
qui-quadrado comparativo, com a tabela de frequencia observada contra
esperada por classe.

A discussao da qualidade do ajuste e gerada automaticamente e combina
assimetria, curtose e -- para variaveis de contagem -- o indice de
dispersao s^2/xbar, que na Poisson vale exatamente 1.

Traz o aviso metodologico explicito de que o qui-quadrado esta sendo
usado como medida descritiva comparativa, e nao como teste de aderencia
formal.
MSG

commitar PR app/paginas/m5_regressao.py <<'MSG'
feat(app): Modulo 5 -- correlacao e regressao linear

O usuario escolhe X e Y e recebe: diagrama de dispersao, correlacao de
Pearson (da nossa biblioteca), reta por minimos quadrados implementados
por nos, equacao formatada, R^2, erro padrao da estimativa e o campo de
predicao interativa -- digita X, recebe Y-chapeu, com o ponto destacado
no grafico.

Cuidados que valem a discussao na arguicao:

- alerta de EXTRAPOLACAO quando o X digitado sai da faixa observada;
- o intercepto so e interpretado como valor real quando X = 0 esta dentro
  da faixa dos dados; fora dela, e apontado como mero parametro de ajuste;
- tabela de decomposicao da variacao (SQtot = SQreg + SQres);
- grafico de residuos, com a leitura de que um formato de funil indica
  heterocedasticidade e portanto inadequacao do modelo linear;
- o alerta obrigatorio de que correlacao nao implica causalidade, com o
  exemplo concreto das confundidoras deste dataset (estacao, horario e
  dia da semana afetam tanto a temperatura quanto a demanda).
MSG

commitar PR app/paginas/m6_descobertas.py <<'MSG'
feat(app): Modulo 6 -- as tres descobertas

Nenhum numero desta pagina esta escrito a mao: todos sao recalculados ao
vivo pelo nucleo a cada carregamento, inclusive as simulacoes do TCL.

1. A temperatura importa, mas explica menos de 17% dos alugueis
   (r = 0,40 e R^2 = 0,16) -- e nao por falta de relacao, e sim porque a
   relacao nao e uma reta.

2. Dois publicos com comportamentos opostos escondidos no mesmo total:
   casuais sobem 125% no fim de semana enquanto registrados caem 26%; no
   agregado os efeitos quase se cancelam. Paradoxo da agregacao.

3. Os dados violam a Poisson por um fator de 174 (indice de dispersao
   173,66 contra 1) -- e mesmo assim o TCL funciona exatamente como
   prometido, partindo de uma variavel com assimetria 2,5.

A separacao por dia util e feita com list comprehension sobre listas
puras, para nao recorrer ao groupby do pandas.
MSG

commitar G app.py <<'MSG'
feat(app): ponto de entrada e navegacao entre os modulos

Monta a barra lateral, carrega o dataset uma unica vez (com cache do
Streamlit, para nao reler 17.379 linhas a cada movimento de slider) e
delega para a pagina de cada modulo.

A barra lateral documenta a regra de ouro para quem estiver usando a
aplicacao: de onde vem cada numero e para que servem NumPy, SciPy e
Pandas neste projeto.

    streamlit run app.py
MSG

commitar PR tests/test_app.py <<'MSG'
test(app): 15 testes de ponta a ponta da interface

Usa o AppTest do proprio Streamlit para EXECUTAR a aplicacao inteira sem
abrir navegador. Nao valida numeros -- isso e papel dos testes do nucleo
-- e sim que a aplicacao sobe, que cada um dos seis modulos renderiza sem
excecao e que os elementos exigidos pelo enunciado existem de fato:

- os controles de numero de repeticoes e tamanho da amostra do Modulo 3;
- o campo de predicao interativa do Modulo 5, que responde a um valor
  digitado;
- o alerta de que correlacao nao implica causalidade;
- a rejeicao de X igual a Y na regressao.
MSG

commitar PF tests/test_regra_de_ouro.py <<'MSG'
test(regra-de-ouro): a separacao nucleo/bibliotecas virou teste

Confiar que ninguem vai escrever um df['cnt'].mean() num ajuste de ultima
hora e ingenuo. Este arquivo LE o codigo fonte com o modulo ast e falha
automaticamente se:

- algum arquivo de minhastats/ importar qualquer coisa alem de math e
  random;
- algum arquivo de app/ (ou o proprio app.py) chamar .mean(), .median(),
  .std(), .var(), .corr(), .cov(), .quantile(), .describe(), .skew(),
  .kurtosis() ou .percentile().

Ha ainda um teste que sobe um subprocesso com numpy, scipy, pandas e
statistics BLOQUEADOS em sys.modules e verifica que `import minhastats`
funciona e produz resultados corretos.

Esse ultimo teste ja rendeu um achado: a assercao original comparava
correlacao_pearson([1,2,3],[2,4,6]) == 1.0 e falhou, porque o valor
retornado e 0.9999999999999998. Correlacao perfeita, mas nao exatamente 1
em ponto flutuante. Corrigida para usar folga numerica, que e como
comparacoes de float devem ser escritas.

Total do projeto: 518 testes.
MSG

commitar G README.md <<'MSG'
docs: README com instrucoes de execucao e capturas

Identificacao da equipe, descricao do projeto, link da fonte original do
dataset, passo a passo de instalacao e execucao a partir do zero,
capturas de tela de todos os modulos funcionando, estrutura comentada do
repositorio e o mapa completo de correspondencia entre cada funcao nossa
e a referencia usada para valida-la.
MSG

commitar PR RELATORIO.md <<'MSG'
docs: RELATORIO completo da atividade

Documenta:

- dataset escolhido e a justificativa da escolha (tem todos os tipos
  estatisticos ao mesmo tempo, a relacao entre variaveis e interessante
  justamente por ser imperfeita, e o download nao exige login);
- arquitetura, com a fronteira explicita entre nucleo e interface;
- TODAS as formulas em notacao matematica, incluindo a deducao dos
  minimos quadrados a partir das equacoes normais;
- as decisoes de implementacao e o que elas custaram: variancia em dois
  passos, Poisson em escala logaritmica, o bug de borda do histograma e a
  ordenacao propria;
- a justificativa numerica da tolerancia de 1e-9;
- resultados da validacao, com o mapa de correspondencias e os testes de
  propriedade matematica;
- a explicacao de cada modulo com os numeros efetivamente obtidos;
- as 3 descobertas do Modulo 6, com tabelas;
- as limitacoes reconhecidas, listadas honestamente.
MSG

commitar PF docs/resumo_executivo.md docs/roteiro_video.md docs/capturar_telas.py docs/imagens <<'MSG'
docs: resumo executivo, roteiro do video e capturas reproduziveis

- resumo_executivo.md: a pagina exigida no PDF de entrega, com dataset,
  modulos implementados e as 3 descobertas.
- roteiro_video.md: roteiro minutado de 3 a 5 minutos, com a fala
  dividida entre os tres integrantes e o trecho do nucleo a ser explicado
  (a variancia em dois passos e o porque de nao usar a formula de uma
  passada so).
- capturar_telas.py: script que sobe o navegador, percorre cada modulo e
  regenera as capturas do README -- assim as imagens nao ficam
  desatualizadas em relacao a aplicacao.
- imagens/: as capturas geradas por ele.
MSG

if [[ $INCLUIR_SCRIPTS -eq 1 ]]; then
commitar G scripts/dividir_commits.sh scripts/equipe.conf <<'MSG'
chore(scripts): ferramenta de organizacao do historico da equipe

scripts/dividir_commits.sh reconstroi o historico do projeto em commits
pequenos e tematicos, agrupados em tres trilhas -- uma por integrante --
para que cada um assuma um bloco coerente: nucleo, testes e pagina da
interface do mesmo assunto.

O script confere ao final que a arvore resultante e IDENTICA a anterior;
se houver qualquer diferenca, aborta sem alterar nada e preserva o branch
antigo. Foi essa conferencia que pegou, no primeiro teste, que a propria
pasta scripts/ havia ficado de fora.

O modo --pausar interrompe a cada troca de trilha para que o integrante
correspondente revise os arquivos antes de liberar os proprios commits.
MSG
fi

# ---------------------------------------------------------------------------
# Conferencia: a arvore final tem de ser IDENTICA a original
# ---------------------------------------------------------------------------

echo
echo "Conferindo se o conteudo final ficou identico ao original..."

if [[ $INCLUIR_SCRIPTS -eq 1 ]]; then
    ESCOPO_DIFF=(.)
else
    # com --sem-scripts, a pasta scripts/ nao entra no historico novo de
    # proposito -- entao ela fica de fora tambem da conferencia
    ESCOPO_DIFF=(. ":(exclude)scripts")
fi

if ! git diff --quiet "$COMMIT_ORIGINAL" HEAD -- "${ESCOPO_DIFF[@]}"; then
    echo "ERRO: DIFERENCA DETECTADA entre o historico novo e o original."
    echo "Nada foi perdido: o branch '$BRANCH_ORIGINAL' continua intacto."
    echo
    git diff --stat "$COMMIT_ORIGINAL" HEAD -- "${ESCOPO_DIFF[@]}"
    echo
    echo "Abortando. Volte com:  git checkout $BRANCH_ORIGINAL"
    exit 1
fi

echo "OK: arvore identica — nenhum arquivo foi perdido ou alterado."

# ---------------------------------------------------------------------------
# Troca os branches de lugar
# ---------------------------------------------------------------------------

git branch -m "$BRANCH_ORIGINAL" "$BRANCH_ANTIGO"
git branch -m "__reconstrucao__" "$BRANCH_NOVO"

echo
echo "══════════════════════════════════════════════════════════════"
echo "Historico reconstruido em $CONTADOR commits"
echo "══════════════════════════════════════════════════════════════"
echo
git shortlog -sne "$BRANCH_NOVO"
echo
echo "Branch novo   : $BRANCH_NOVO"
echo "Branch antigo : $BRANCH_ANTIGO (preservado; apague quando quiser"
echo "com 'git branch -D $BRANCH_ANTIGO')"
echo
if [[ $INCLUIR_SCRIPTS -eq 0 ]]; then
    echo "AVISO: a pasta scripts/ NAO entrou no historico novo (--sem-scripts)."
    echo "Os arquivos continuam no disco, agora como nao rastreados."
    echo "Confirme com: git status --short"
    echo
fi

echo "Confira antes de publicar:"
echo "git log --pretty=format:'%h %an %ad %s' --date=short"
echo "pytest"
