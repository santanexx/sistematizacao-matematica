# Roteiro do vídeo de demonstração (3 a 5 minutos)

> **Formato:** compartilhamento de tela com áudio. Todos os integrantes falam.
> **Antes de gravar:** `streamlit run app.py` já aberto no navegador,
> terminal em outra aba com o projeto, e o arquivo `minhastats/descritiva.py`
> aberto no editor.

---

## 0:00 – 0:25 — Abertura e identificação

**Quem fala:** Gustavo

> "Olá, professor. Somos o grupo `[NOME]`: Gustavo Santana, Pedro Oliveira Rocha
> e Pedro Falcão. Este é o nosso Laboratório Estatístico Interativo.
> Usamos o **Bike Sharing Dataset** do UCI, com **17.379 registros horários** de
> aluguel de bicicletas em Washington, com clima, calendário e contagem de
> aluguéis."

**Mostrar:** Módulo 0, com os três cartões de conferência (registros, numéricas,
categóricas).

---

## 0:25 – 1:15 — O núcleo estatístico (a parte que mais vale nota)

**Quem fala:** Pedro Oliveira Rocha
**Mostrar:** o editor com `minhastats/descritiva.py` aberto.

> "A regra de ouro do projeto: o pacote `minhastats` importa **apenas `math` e
> `random`** da biblioteca padrão. Nada de NumPy, SciPy ou statistics."

**Rolar até `variancia_amostral` e explicar o trecho:**

```python
def variancia_amostral(dados):
    x = _validar(dados, minimo=2)
    xbar = media(x)
    soma_quadrados = 0.0
    for valor in x:
        desvio = valor - xbar
        soma_quadrados += desvio * desvio
    return soma_quadrados / (len(x) - 1)
```

> "Esta é a variância amostral: soma dos quadrados dos desvios em relação à
> média, dividida por n−1 — a correção de Bessel.
>
> **A decisão importante está no que a gente NÃO fez.** Existe uma forma
> algebricamente equivalente, `soma de x² menos n vezes x-barra ao quadrado`,
> que faz tudo numa passada só. Ela é mais rápida, mas quando a média é grande
> comparada ao desvio, esses dois números ficam enormes e quase iguais — e
> subtrair um do outro provoca **cancelamento catastrófico**: os dígitos
> significativos se anulam e sobra ruído.
>
> Por isso calculamos a média primeiro e só depois acumulamos os desvios: duas
> passadas, mas numericamente estável. E temos um teste que prova isso, com
> valores da ordem de 10⁶ e desvio de 10⁴."

---

## 1:15 – 1:50 — A validação

**Quem fala:** Pedro Oliveira Rocha
**Mostrar:** terminal, rodar `pytest`.

> "São **521 testes automatizados**. Cada função nossa é comparada com NumPy,
> SciPy ou statistics em três frentes: casos calculados à mão, o dataset real com
> 17 mil linhas, e amostras aleatórias em escalas hostis.
>
> A tolerância é **1e-9**, e ela é justificada: o float de 64 bits tem 16 dígitos
> significativos, o erro acumulado com 17 mil parcelas chega à ordem de 1e-12, e
> o NumPy ainda usa somatório pareado, que muda a ORDEM das operações — e soma em
> ponto flutuante não é associativa. Então 1e-9 fica acima do ruído esperado e
> muito abaixo de qualquer erro de fórmula."

**Se der tempo, mencionar o bug real:**

> "Esses testes pegaram um bug de verdade: no histograma, `int((x - li)/h)`
> colocava 5 registros na classe errada, porque a borda 0,85 na verdade vale
> 0,8500000000000001 em binário. Era invisível no gráfico."

---

## 1:50 – 2:30 — Módulo 2: descritiva e interpretação automática

**Quem fala:** Pedro Falcão
**Mostrar:** Módulo 2 com `Aluguéis de usuários casuais`.

> "Aqui o usuário escolhe a variável e recebe todas as medidas — todas calculadas
> pelo nosso pacote. Tabela de frequências, histograma, boxplot e detecção de
> outliers pelo IQR."

**Apontar o rodapé do boxplot:**

> "Detalhe: `plt.hist` e `plt.boxplot` **calculam** as classes e os quartis. Se a
> gente usasse, os números na tela viriam do Matplotlib. Então desenhamos o
> histograma com `ax.bar` e o boxplot com `ax.bxp`, passando os quartis já
> calculados pelo `minhastats`."

**Rolar até a interpretação automática e ler o texto gerado.**

---

## 2:30 – 3:15 — Módulo 3: LGN e TCL

**Quem fala:** Gustavo
**Mostrar:** aba da Lei dos Grandes Números; mexer no slider de repetições.

> "O usuário controla o número de repetições e a semente. Note o eixo x
> logarítmico — a convergência é da ordem de 1 sobre raiz de n, então em escala
> linear os primeiros lançamentos, os mais instáveis, ficariam espremidos."

**Trocar para a aba do TCL, com `casual`, e variar o tamanho da amostra de 2 → 200.**

> "Aqui é a demonstração mais bonita: `casual` tem assimetria de **2,5**, é
> violentamente torta. Com amostras de tamanho 2, a distribuição das médias ainda
> é torta. Aumentando para 200… vira um sino, com assimetria 0,13 — queda de 95%.
>
> E não é só visual: o desvio padrão observado bate com sigma sobre raiz de n com
> menos de 2% de erro."

---

## 3:15 – 3:50 — Módulos 4 e 5

**Quem fala:** Pedro Falcão
**Mostrar:** Módulo 4 com `temp_c`, Normal e Uniforme selecionadas.

> "Sobrepomos a curva teórica com parâmetros estimados dos dados. A Normal ajusta
> 3,8 vezes melhor que a Uniforme, mas nenhuma ajusta bem — a curtose é −0,94,
> platicúrtica, a forma real está entre as duas."

**Ir para o Módulo 5, temperatura × total de aluguéis.**

> "Correlação de 0,40, reta pelos mínimos quadrados: a cada grau a mais, +9,3
> aluguéis por hora. Mas o R² é só **0,16** — a temperatura explica 16% da
> variação. E o gráfico de resíduos mostra um **funil**: heterocedasticidade, a
> reta não dá conta."

**Digitar um valor no campo de predição e mostrar o Ŷ mudando; digitar um valor
fora da faixa para mostrar o alerta de extrapolação.**

> "E o alerta obrigatório: correlação não implica causalidade. Temperatura e
> demanda também variam com a estação e o horário."

---

## 3:50 – 4:30 — Módulo 6: as descobertas

**Quem fala:** Gustavo
**Mostrar:** Módulo 6, descoberta 2 (a tabela dos dois perfis).

> "A descoberta que mais gostamos: separando por tipo de usuário, os dois
> públicos reagem ao calendário em **direções opostas**. Casuais sobem 125% no fim
> de semana; registrados caem 26%. No total, isso quase se cancela — a média cai
> só 6%.
>
> Se a gente olhasse só o agregado, concluiria que o dia da semana quase não
> importa. É o paradoxo da agregação."

**Mencionar a descoberta 3:**

> "E a terceira: o índice de dispersão de `cnt` é **174**, sendo que na Poisson
> ele vale 1. Sobredispersão extrema — Poisson descartada. Mas o TCL continua
> funcionando perfeitamente mesmo assim."

---

## 4:30 – 5:00 — Fechamento

**Quem fala:** todos, brevemente

> "Repositório público com histórico de commits, README com instruções de
> execução e RELATORIO.md com todas as fórmulas em notação matemática, a
> justificativa da tolerância e as limitações que reconhecemos. Obrigado!"

---

## Checklist antes de publicar

- [ ] Vídeo entre 3 e 5 minutos
- [ ] Todos os integrantes falaram
- [ ] Um trecho de código do núcleo foi explicado (não só mostrado)
- [ ] A aplicação apareceu **funcionando** (interações reais, não prints)
- [ ] Upload como **YouTube não listado** ou **Drive com acesso liberado**
- [ ] Link testado em **janela anônima**
- [ ] Link colado no README.md e no PDF de entrega
