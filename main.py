"""
Simulador e Minimizador de AFD por preenchimento de tabela (Myhill-Nerode / Moore)
"""
import json
import os
from itertools import combinations
from collections import defaultdict

class AFD:
    def __init__(self, estados, alfabeto, transicoes, estado_inicial, estados_finais):
        self.estados = sorted(list(set(estados)))
        self.alfabeto = sorted(list(set(alfabeto)))
        self.transicoes = transicoes  # (estado, simbolo) -> proximo_estado
        self.estado_inicial = estado_inicial
        self.estados_finais = set(estados_finais)

    def processar_cadeia(self, cadeia):
        estado_atual = self.estado_inicial
        historico = [estado_atual]

        if cadeia in ("", "e", "epsilon", "ε"):
            aceita = estado_atual in self.estados_finais
            tipo = "ESTADO DE ACEITACAO" if aceita else "ESTADO DE REJEICAO"
            msg = f"Cadeia vazia terminada em '{estado_atual}' ({tipo}) -> {'ACEITA' if aceita else 'REJEITADA'}"
            return aceita, historico, estado_atual, msg

        for simbolo in cadeia:
            if simbolo not in self.alfabeto:
                return False, historico, estado_atual, f"Erro: Simbolo '{simbolo}' nao pertence ao alfabeto {self.alfabeto}."
            chave = (estado_atual, simbolo)
            if chave not in self.transicoes:
                return False, historico, estado_atual, f"Erro: Transicao indefinida para ({estado_atual}, '{simbolo}')."
            estado_atual = self.transicoes[chave]
            historico.append(estado_atual)

        aceita = estado_atual in self.estados_finais
        tipo = "ESTADO DE ACEITACAO" if aceita else "ESTADO DE REJEICAO"
        msg = f"Cadeia terminada em '{estado_atual}' ({tipo}) -> {'ACEITA' if aceita else 'REJEITADA'}"
        return aceita, historico, estado_atual, msg

    def remover_inalcancaveis(self):
        """Remove estados que nao podem ser alcancados a partir do inicial."""
        alcancaveis = set()
        fila = [self.estado_inicial]

        while fila:
            atual = fila.pop(0)
            if atual not in alcancaveis:
                alcancaveis.add(atual)
                for simbolo in self.alfabeto:
                    prox = self.transicoes.get((atual, simbolo))
                    if prox and prox not in alcancaveis:
                        fila.append(prox)

        self.estados = sorted(list(alcancaveis))
        self.estados_finais = self.estados_finais.intersection(alcancaveis)
        self.transicoes = {
            (e, s): d for (e, s), d in self.transicoes.items()
            if e in alcancaveis and d in alcancaveis
        }

    def minimizar(self):
        """Executa a minimizacao por preenchimento de tabela e lista de dependencias."""
        self.remover_inalcancaveis()
        estados = self.estados
        n = len(estados)
        if n <= 1:
            return self

        pares = list(combinations(estados, 2))
        marcado = {par: False for par in pares}
        lista_dependencias = defaultdict(list)

        def get_par(p, q):
            return (p, q) if estados.index(p) < estados.index(q) else (q, p)

        # 1. Marcar pares (Final, Nao-Final)
        for p, q in pares:
            p_final = p in self.estados_finais
            q_final = q in self.estados_finais
            if p_final != q_final:
                marcado[(p, q)] = True

        def propagar_marcacao(par):
            for dep in lista_dependencias[par]:
                if not marcado[dep]:
                    marcado[dep] = True
                    propagar_marcacao(dep)
            lista_dependencias[par] = []

        # 2. Analisar transicoes e alimentar "listas encadeadas"
        for p, q in pares:
            if marcado[(p, q)]:
                continue

            for simbolo in self.alfabeto:
                dest_p = self.transicoes.get((p, simbolo))
                dest_q = self.transicoes.get((q, simbolo))

                if not dest_p or not dest_q or dest_p == dest_q:
                    continue

                par_dest = get_par(dest_p, dest_q)

                if marcado[par_dest]:
                    marcado[(p, q)] = True
                    propagar_marcacao((p, q))
                    break
                else:
                    if (p, q) not in lista_dependencias[par_dest] and (p, q) != par_dest:
                        lista_dependencias[par_dest].append((p, q))

        
        
        # 3. Unir estados equivalentes
        equivalentes = {e: e for e in estados}
        for p, q in pares:
            if not marcado[(p, q)]:
                raiz_p = equivalentes[p]
                antigo_q = equivalentes[q]
                for est, raiz in equivalentes.items():
                    if raiz == antigo_q:
                        equivalentes[est] = raiz_p



        grupos = defaultdict(list)
        for est, raiz in equivalentes.items():
            grupos[raiz].append(est)

        mapeamento = {}
        novos_estados = []
        for grupo in grupos.values():
            nome_unificado = "[" + ",".join(sorted(grupo)) + "]"
            novos_estados.append(nome_unificado)
            for est in grupo:
                mapeamento[est] = nome_unificado

        novo_inicial = mapeamento[self.estado_inicial]
        novos_finais = {mapeamento[e] for e in self.estados_finais}
        novas_transicoes = {}

        for (est, simb), dest in self.transicoes.items():
            origem_unificada = mapeamento[est]
            dest_unificado = mapeamento[dest]
            novas_transicoes[(origem_unificada, simb)] = dest_unificado

        return AFD(novos_estados, self.alfabeto, novas_transicoes, novo_inicial, novos_finais)

    def exibir_informacoes(self):
        print(f"• Conjunto de Estados ({len(self.estados)}): {self.estados}")
        print(f"• Alfabeto de Entrada: {self.alfabeto}")
        print(f"• Estado Inicial (q0): {self.estado_inicial}")
        print(f"• Estado(s) de Aceitacao (F): {list(self.estados_finais) if self.estados_finais else 'Nenhum'}")
        print("\n• Tabela de Transicoes delta(origem, simbolo) -> destino:")
        for (e, s), d in sorted(self.transicoes.items()):
            tag_aceitacao = " [ACEITACAO]" if e in self.estados_finais else ""
            print(f"    delta({e}{tag_aceitacao}, '{s}') -> {d}")


# ==============================================================================
# ENTRADAS E MENU
# ==============================================================================

def criar_automato_manualmente():
    print("\n" + "-" * 45)
    print("        CRIACAO MANUAL DE AUTOMATO")
    print("-" * 45)
    estados = input("1. Estados separados por espaco (ex: q0 q1 q2): ").split()
    alfabeto = input("2. Alfabeto separado por espaco (ex: 0 1): ").split()

    estado_inicial = input("3. Estado inicial (ex: q0): ").strip()
    while estado_inicial not in estados:
        print(f"   Erro: O estado inicial precisa estar entre {estados}.")
        estado_inicial = input("   Estado inicial valido: ").strip()

    finais_input = input("4. Estado(s) de aceitacao/finais (ex: q1 q2): ").split()
    estados_finais = [e for e in finais_input if e in estados]

    print("\n5. Preencha as transicoes delta(origem, simbolo) = destino:")
    transicoes = {}
    for est in estados:
        for simb in alfabeto:
            while True:
                dest = input(f"   delta({est}, {simb}) -> ").strip()
                if dest in estados:
                    transicoes[(est, simb)] = dest
                    break
                print(f"   Destino '{dest}' invalido. Escolha entre: {estados}")

    return AFD(estados, alfabeto, transicoes, estado_inicial, estados_finais)


def carregar_de_arquivo_json():
    caminho = input("\nCaminho do arquivo JSON (ex: automato.json): ").strip()
    if not os.path.exists(caminho):
        print(f"Erro: Arquivo '{caminho}' nao encontrado.")
        return None

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)

        transicoes = {}
        for t in dados["transicoes"]:
            transicoes[(t[0], t[1])] = t[2]

        return AFD(
            estados=dados["estados"],
            alfabeto=dados["alfabeto"],
            transicoes=transicoes,
            estado_inicial=dados["estado_inicial"],
            estados_finais=dados["estados_finais"]
        )
    except Exception as e:
        print(f"Erro ao ler JSON: {e}")
        return None


def submenu_operacoes(automato):
    automato_trabalho = automato

    while True:
        print("\n" + "=" * 50)
        print("                 MENU DO AUTOMATO")
        print("=" * 50)
        print("1. Exibir estrutura formal atual e estados de aceitacao")
        print("2. Testar palavras/cadeias de entrada")
        print("3. Minimizar este automato (Myhill-Nerode / Moore)")
        print("4. Voltar ao menu principal")

        op = input("\nEscolha uma opcao: ").strip()

        if op == "1":
            print("\n--- Estrutura Formal do AFD ---")
            automato_trabalho.exibir_informacoes()

        elif op == "2":
            print("\n--- Modo de Teste de Cadeias ---")
            print(f"Estado(s) de Aceitacao: {list(automato_trabalho.estados_finais)}")
            print("Dica: Digite 'sair' para voltar ao menu ou aperte Enter para testar a cadeia vazia.")
            while True:
                cadeia = input("\nDigite a cadeia para testar: ").strip()
                if cadeia.lower() == "sair":
                    break
                aceita, caminho, est_final, msg = automato_trabalho.processar_cadeia(cadeia)
                print("\n--- Rastreamento de Estados ---")

                print(" -> ".join(caminho))

                print(f"Estado Final Alcancado: {est_final}")


                print(f"Status do Estado: {'Pertence aos Estados de Aceitacao' if aceita else 'NAO e Estado de Aceitacao'}")
                print(f"Resultado: {msg}")
                print("-" * 35)

        elif op == "3":

            print("\nExecutando minimizacao...")
            qtd_antes = len(automato_trabalho.estados)
            automato_trabalho = automato_trabalho.minimizar()
            qtd_depois = len(automato_trabalho.estados)
            print(f"\nSucesso! Automato reduzido de {qtd_antes} para {qtd_depois} estados.")
            print("\n--- Automato Minimo Gerado ---")
            automato_trabalho.exibir_informacoes()

        elif op == "4":
            break

        else:
            print("Opcao invalida.")


def main():

    while True:

        print("\n" + "=" * 55)
        print("   SIMULADOR E MINIMIZADOR UNIVERSAL DE AFD (LFA)")
        print("=" * 55)
        print("1. Digitar um automato do zero no terminal")
        print("2. Carregar definicao de automato via JSON")
        print("3. Carregar exemplo padrao com equivalencias")
        print("4. Sair")

        opcao = input("\nEscolha uma opcao: ").strip()
        if opcao == "1":

            automato = criar_automato_manualmente()
            submenu_operacoes(automato)

        elif opcao == "2":

            automato = carregar_de_arquivo_json()
            if automato:
                submenu_operacoes(automato)

        elif opcao == "3":

            estados = ["A", "B", "C", "D", "E", "F"]
            alfabeto = ["0", "1"]
            transicoes = {
                ("A", "0"): "B", ("A", "1"): "C",
                ("B", "0"): "A", ("B", "1"): "D",
                ("C", "0"): "E", ("C", "1"): "F",
                ("D", "0"): "E", ("D", "1"): "F",
                ("E", "0"): "E", ("E", "1"): "F",
                ("F", "0"): "F", ("F", "1"): "F",
            }

            # Estados C, D e E são os estados de aceitação


            automato = AFD(estados, alfabeto, transicoes, "A", ["C", "D", "E"])
            print("\nExemplo carregado com sucesso!")
            submenu_operacoes(automato)

        elif opcao == "4":
            print("\nEncerrando o simulador. Ate logo!")
            break

        else:
            print("Opcao invalida. Tente novamente.")


if __name__ == "__main__":
    main()