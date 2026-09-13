# Roteiro do vídeo (4 min 30 s)

**Quem grava:** Gustavo e Rocha.
**Como:** gravação de tela com áudio. Tudo acontece dentro da aplicação — não precisa abrir editor nem terminal.

---

## Antes de apertar REC

1. Abrir um terminal na pasta do projeto e rodar:
   ```bash
   source .venv/bin/activate
   streamlit run app.py
   ```
   Tem que aparecer `(.venv)` no prompt. Sem isso a aplicação não abre.
2. O navegador abre em `http://localhost:8501`. Deixar em **tela cheia** (F11) e o menu lateral visível.
3. Clicar uma vez em cada módulo da barra lateral **antes de gravar** — o primeiro carregamento demora uns segundos e o cache resolve.
4. Deixar o Módulo 0 aberto. Testar o microfone.
5. Gravador de tela: OBS, o gravador nativo do sistema, ou o do Google Meet — qualquer um serve.

---

## Bloco 1 — Abertura · 0:00 a 0:20 · **Gustavo**

**Tela:** Módulo 0 — Dados Reais (já aberto).

**Fala:**
> Olá, professor. Somos o Grupo Sigma: Gustavo Santana, Pedro Rocha e Pedro Falcão.
> Nosso laboratório usa o dataset Bike Sharing, do repositório UCI: 17 mil registros de aluguel de bicicleta em Washington, com clima, calendário e quantidade de aluguéis por hora.

**Mostrar:** os três cartões grandes (17.379 registros, 10 numéricas, 7 categóricas) e a lista "Conferência dos requisitos" com os ATENDE.

---

## Bloco 2 — O núcleo e os testes · 0:20 a 1:20 · **Rocha**

**Tela:** clicar em **Módulo 1 — Núcleo Estatístico Próprio** na barra lateral.

**Passo a passo:**
1. Apontar a tabela "Regra de ouro: o que o núcleo importa".
2. Rolar até "Código-fonte". No seletor **Função**, escolher `variancia_amostral`.
3. Depois rolar até o fim e clicar em **Rodar os testes de validação agora**. Esperar uns 5 segundos.

**Fala (enquanto mostra a tabela):**
> A regra do trabalho é que nenhuma medida venha de biblioteca pronta. Essa tabela é lida do código na hora: o pacote `minhastats` importa só `math` e `random`. Nada de NumPy, nada de SciPy.

**Fala (com o código da variância na tela):**
> Aqui está a variância amostral. Primeiro calculamos a média. Depois, para cada valor, o desvio em relação à média, elevado ao quadrado, e somamos. Dividimos por n menos 1 — essa é a correção de Bessel.
>
> Existe uma fórmula que faz tudo numa passada só: soma dos quadrados menos n vezes a média ao quadrado. A gente não usou. Quando a média é grande, esses dois números ficam enormes e quase iguais, e ao subtrair um do outro os dígitos se cancelam — sobra ruído. Em dois passos é mais lento, mas o resultado é estável.

**Fala (depois de clicar no botão, com o resultado verde na tela):**
> São 504 testes só do núcleo. Cada função nossa é comparada com o NumPy ou o SciPy com tolerância de um bilionésimo. Todos passando.

---

## Bloco 3 — Estatística descritiva · 1:20 a 1:55 · **Gustavo**

**Tela:** clicar em **Módulo 2 — Estatística Descritiva**.

**Passo a passo:**
1. No seletor **Variável**, escolher **Aluguéis de usuários casuais**.
2. Rolar devagar: cartões de medidas → histograma → boxplot → "Detecção de outliers" → "Interpretação automática".

**Fala:**
> No Módulo 2 o usuário escolhe uma variável e recebe tudo: as medidas, o histograma, o boxplot, a tabela de classes.
>
> Um detalhe importante: o boxplot não é o do Matplotlib pronto, porque ele calcularia os quartis sozinho. A gente calcula os quartis e os outliers no nosso pacote e só manda o Matplotlib desenhar.
>
> E aqui embaixo a aplicação interpreta sozinha: diz que a distribuição é assimétrica à direita, que a mediana descreve melhor que a média, e quantos outliers a regra do IQR encontrou.

---

## Bloco 4 — Teorema Central do Limite · 1:55 a 2:40 · **Gustavo**

**Tela:** clicar em **Módulo 3 — Probabilidade e Simulação**, depois na aba **(b) Teorema Central do Limite**.

**Passo a passo:**
1. Conferir que a variável é **Aluguéis de usuários casuais**.
2. No controle **Tamanho de cada amostra**, arrastar para **2**. Rolar até o segundo histograma (o das médias).
3. Voltar ao controle e arrastar para **200**. Rolar de novo até o histograma das médias.

**Fala (com n = 2):**
> Essa variável é muito torta — assimetria de 2,5. Sorteando amostras de tamanho 2 e tirando a média, a distribuição das médias ainda é torta.

**Fala (com n = 200):**
> Com amostras de 200, vira um sino. A curva vermelha é a Normal que o teorema prevê, e ela encaixa. A assimetria caiu de 2,5 para 0,13.
>
> E não é só no desenho: o desvio padrão das médias bate com sigma sobre raiz de n com menos de 2% de erro. O usuário controla o tamanho da amostra e o número de repetições.

---

## Bloco 5 — Distribuições teóricas · 2:40 a 3:00 · **Gustavo**

**Tela:** clicar em **Módulo 4 — Distribuições Teóricas**. Deixar a variável em **Temperatura (°C)** e as candidatas **Normal** e **Uniforme** (já vêm marcadas).

**Passo a passo:** rolar até o histograma com a curva sobreposta; passar pela aba Normal e pela aba Uniforme.

**Fala:**
> No Módulo 4 a gente sobrepõe uma distribuição teórica ao histograma, com parâmetros estimados dos próprios dados. Para a temperatura, a Normal ajusta quase quatro vezes melhor que a Uniforme, mas nenhuma ajusta perfeito: a curtose é negativa, a distribuição é mais achatada que a Normal. A forma real fica entre as duas.

---

## Bloco 6 — Regressão · 3:00 a 3:40 · **Rocha**

**Tela:** clicar em **Módulo 5 — Correlação e Regressão**. Deixar X = **Temperatura (°C)** e Y = **Total de aluguéis** (já vêm assim).

**Passo a passo:**
1. Apontar os cartões: r, R², a equação da reta em verde.
2. No campo **Digite um valor de X**, apagar e digitar `30`. Mostrar o Ŷ mudando e o X laranja no gráfico.
3. Digitar `60`. Mostrar o aviso amarelo de extrapolação.
4. Rolar até o gráfico de resíduos e a caixa vermelha do alerta.

**Fala:**
> Correlação de 0,40 entre temperatura e aluguéis. A reta é calculada pelos mínimos quadrados que a gente implementou: cada grau a mais, mais nove aluguéis por hora.
>
> Se eu digito 30 graus, a aplicação prevê o Y. Se eu digito 60, ela avisa que isso está fora dos dados — extrapolação.
>
> Mas o R² é só 0,16: a temperatura explica 16% da variação. E o gráfico de resíduos mostra um funil, sinal de que a reta não captura tudo. E o alerta obrigatório: correlação não implica causalidade. Temperatura e demanda também variam com a estação e com o horário.

---

## Bloco 7 — Descobertas · 3:40 a 4:15 · **Rocha**

**Tela:** clicar em **Módulo 6 — Descobertas**. Rolar até a **descoberta 2** (a tabela com "Casual" e "Registrado").

**Fala:**
> A descoberta que mais gostamos. Separando por tipo de usuário, os dois públicos vão em direções opostas no fim de semana: os casuais sobem 125%, os registrados caem 26%. No total isso quase se cancela — cai só 6%.
>
> Quem olha só o total conclui que o dia da semana não importa. Está errado. É o paradoxo da agregação: lazer e deslocamento para o trabalho são dois fenômenos diferentes escondidos no mesmo número.

---

## Bloco 8 — Fechamento · 4:15 a 4:30 · **Gustavo**

**Tela:** voltar ao **Módulo 1** e deixar parado na tabela da regra de ouro.

**Fala:**
> Tudo isso está no repositório público: código, 521 testes, README com as instruções e o relatório com todas as fórmulas. Obrigado, professor.

Parar a gravação.

---

## Depois de gravar

- [ ] Duração entre 3 e 5 minutos
- [ ] Subir no YouTube como **Não listado** (não é "Privado" — privado o professor não abre)
- [ ] Abrir o link numa **janela anônima** e conferir que o vídeo carrega
- [ ] Mandar o link para fechar o PDF e o README

---

## Se travar na hora

- **A aplicação não abre / erro de módulo:** o venv não está ativo. Fechar o terminal, abrir outro, `source .venv/bin/activate`, rodar de novo.
- **Um módulo demora para carregar:** normal na primeira vez. Por isso o passo 3 de "Antes de apertar REC".
- **Errou a fala:** parar, respirar, começar o bloco de novo. Cortar depois é fácil; gravar em blocos separados e juntar também vale.
- **O botão dos testes não terminou em 5 s:** continuar falando; ele termina em até 15 s.
