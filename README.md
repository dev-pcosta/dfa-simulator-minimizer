# Simulador e Minimizador de AFD (DFA Simulator & Minimizer)

Este projeto é um ferramenta desenvolvida em Python (CLI) para simulação, validação de cadeias e minimização de **Autômatos Finitos Determinísticos (AFD / DFA)**. O projeto aplica na prática conceitos formais de Linguagens Formais e Autômatos (LFA), utilizando o **Algoritmo de Preenchimento de Tabela** (*Table-Filling Algorithm*) baseado no Teorema de Myhill-Nerode e algoritmo de Moore.


## Funcionalidades do Minimizador

- **Simulação interativa de cadeias:** Rastreamento passo a passo da transição entre estados para qualquer palavra de entrada (incluindo tratamento de cadeia vazia $\varepsilon$).
- **Minimização de um AFD:**
  - Remoção automática de estados inalcançáveis a partir do estado inicial ($q_0$).
  - Construção da tabela triangular de pares de estados.
  - Propagação de distinguibilidade usando listas de dependências encadeadas.
  - Fusão de classes de equivalência gerando o autômato mínimo equivalente.
- **Entrada dinâmica:** Suporte à definição manual via terminal ou importação via arquivos `.json`.


## Fundamentação Teórica

Um Autômato Finito Determinístico é definido formalmente como uma 5-tupla:

$$M = (Q, \Sigma, \delta, q_0, F)$$

Tal que:
* $Q$: Conjunto finito de estados.
* $\Sigma$: Alfabeto finito de símbolos de entrada.
* $\delta$: Função de transição total $\delta: Q \times \Sigma \rightarrow Q$.
* $q_0$: Estado inicial ($q_0 \in Q$).
* $F$: Conjunto de estados de aceitação/finais ($F \subseteq Q$).


## Como executar:

### Pré-requisitos
* Python 3.8 ou superior instalado.

### Execução
1. Clone o repositório ou baixe os arquivos:
```
git clone https://github.com/dev-pcosta/dfa-simulator-minimizer.git

cd dfa-simulator-minimizer
```

2. Execute o arquivo principal no terminal:
```
python main.py
```
