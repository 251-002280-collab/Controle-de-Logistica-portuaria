# Projeto Final - Estruturas de Dados
# Aluno: João Pedro de Medeiros
# Matricula: 251-002280
# Tema 4: Controle de Logística Portuária

#   Fila   -> Ordem de chegada de caminhões no pátio aguardando liberação para embarque.
#   Pilha  -> Controle de empilhamento físico de contêineres no navio ou pátio (o último a entrar é o primeiro a sair).
#   Lista  -> Registro geral da frota de veículos e transportadoras credenciadas.
#   Árvore ->  Árvore de rotas marítimas, portos intermediários e destinos finais.

"""CONTROLE DE LOGÍSTICA PORTUÁRIA - Projeto de Estruturas de Dados
Persistência: somente o arquivo de texto "dados_sistema.txt"."""
import os
from collections import deque
from datetime import datetime
# Caminho absoluto do arquivo de dados (fica na mesma pasta do script)
ARQUIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados_sistema.txt")
# Separador de campos no arquivo de texto (por isso é trocado por '/' nas entradas)
SEP = "|"
# Nome de cada nível da hierarquia da árvore (nível 0 a 3)
NIVEIS = ["Porto de origem", "Rota marítima", "Porto intermediário", "Destino final"]
frota = []      # LISTA: cada veículo é um dicionário
fila = deque()  # FILA: append() entra no final, popleft() sai do início (FIFO)
pilha = []      # PILHA: o topo é o último elemento; append() e pop() (LIFO)
arvore = {}     # ÁRVORE: {"nó": {"filho": {...}}}; nó sem filhos = {}
# FUNÇÕES AUXILIARES
# Imprime um título centralizado entre duas linhas de '='
def titulo(texto):
    print("\n" + "=" * 55 + "\n" + texto.center(55) + "\n" + "=" * 55)
# Lê um texto, remove espaços e troca o separador '|' por '/'.
# Se for obrigatório, repete até o usuário digitar algo
def ler_texto(mensagem, obrigatorio=True):
    while True:
        valor = input(mensagem).strip().replace(SEP, "/")
        if valor != "" or not obrigatorio: return valor
        print("Erro: este campo é obrigatório e não pode ficar vazio.")
# Converte texto em inteiro; devolve 0 se não for um número válido
def para_inteiro(texto):
    try:
        return int(texto.strip())
    except ValueError:
        return 0
# Pede um inteiro positivo, repetindo até a entrada ser válida
def ler_inteiro(mensagem):
    while True:
        numero = para_inteiro(input(mensagem))
        if numero > 0: return numero
        print("Erro: digite um número inteiro positivo.")
# Valida o peso: vazio é aceito (opcional); aceita vírgula decimal.
# Devolve o peso como texto com 2 casas decimais, ou None se for inválido
def validar_peso(texto):
    texto = texto.strip().replace(",", ".")
    if texto == "": return ""
    try:
        peso = float(texto)
    except ValueError:
        return None
    return f"{peso:.2f}" if 0 < peso < 1e9 else None
# Pede o peso até receber um valor válido ou vazio
def ler_peso(mensagem):
    while True:
        peso = validar_peso(input(mensagem))
        if peso is not None: return peso
        print("Erro: informe um peso maior que zero (ex.: 1500.5) ou deixe em branco.")
# Faz uma pergunta s/n e devolve True se a resposta for sim
def confirmar(mensagem):
    return input(mensagem + " (s/n): ").strip().lower() in ["s", "sim"]
# Busca sequencial genérica (ignora maiúsculas/minúsculas):
# devolve o primeiro registro cujo campo seja igual ao valor, ou None
def buscar(estrutura, campo, valor):
    for registro in estrutura:
        if str(registro[campo]).lower() == str(valor).lower(): return registro
    return None
# Imprime os dados de um veículo da frota
def mostrar_veiculo(v, prefixo="  "):
    print(f"{prefixo}ID: {v['id']} | Placa: {v['placa']} | Transportadora: {v['transportadora']} | Motorista: {v['motorista']} | Carga: {v['carga']}")
# Imprime os dados de um caminhão da fila
def mostrar_caminhao(c, prefixo="  "):
    print(f"{prefixo}ID: {c['id']} | Placa: {c['placa']} | Transportadora: {c['transportadora']} | Carga: {c['carga']} | Chegada: {c['chegada']}")
# Imprime os dados de um contêiner (peso vazio = 'não informado')
def mostrar_container(c, prefixo="  "):
    print(f"{prefixo}Código: {c['codigo']} | Contêiner: {c['numero']} | Carga: {c['descricao']} | Destino: {c['destino']} | "
          f"Peso: {c['peso'] + ' kg' if c['peso'] != '' else 'não informado'}")
#  VALIDAÇÕES (devolvem a mensagem de erro, ou '' se estiver tudo certo) 
# Veículo: campos preenchidos, ID positivo e ainda não existente
def validar_veiculo(v, existentes):
    if "" in [v["placa"], v["transportadora"], v["motorista"], v["carga"]]: return "campo obrigatório vazio"
    if v["id"] <= 0: return "ID inválido"
    if buscar(existentes, "id", v["id"]) is not None: return "ID duplicado"
    return ""
# Caminhão: campos preenchidos, veículo cadastrado na frota e ainda fora da fila
def validar_caminhao(c, existentes, frota_cadastrada):
    if "" in [c["placa"], c["transportadora"], c["carga"], c["chegada"]]: return "campo obrigatório vazio"
    if buscar(frota_cadastrada, "id", c["id"]) is None: return "veículo não cadastrado na frota"
    if buscar(existentes, "id", c["id"]) is not None: return "este caminhão já está na fila"
    return ""
# Contêiner: campos preenchidos, código e número únicos na pilha
def validar_container(c, existentes):
    if "" in [c["codigo"], c["numero"], c["descricao"], c["destino"]]: return "campo obrigatório vazio"
    if buscar(existentes, "codigo", c["codigo"]) is not None: return "código identificador duplicado"
    if buscar(existentes, "numero", c["numero"]) is not None: return "número de contêiner duplicado"
    return ""
# LISTA 
# Lê os dados do veículo, valida e adiciona ao final da lista
def cadastrar_veiculo():
    veiculo = {"id": ler_inteiro("ID do veículo (número): "), "placa": ler_texto("Placa do caminhão: ").upper(),
               "transportadora": ler_texto("Nome da transportadora: "), "motorista": ler_texto("Nome do motorista: "),
               "carga": ler_texto("Tipo de carga: ")}
    erro = validar_veiculo(veiculo, frota)
    if erro != "": print(f"Erro: {erro}.")
    else:
        frota.append(veiculo)
        print("Veículo cadastrado com sucesso!")
# Lista todos os veículos com sua posição (começando em 1)
def listar_veiculos():
    for posicao, veiculo in enumerate(frota, start=1):
        mostrar_veiculo(veiculo, f"  Posição {posicao} | ")
    print(f"\nTotal: {len(frota)} veículo(s).")
# Pesquisa um veículo por ID ou pela posição (índice) na lista
def pesquisar_veiculo():
    modo = input("1. Pesquisar por ID\n2. Consultar por posição (índice)\nEscolha uma opção: ").strip()
    veiculo = None
    if modo == "1": veiculo = buscar(frota, "id", ler_inteiro("ID do veículo: "))
    elif modo == "2":
        posicao = ler_inteiro(f"Posição (1 a {len(frota)}): ")
        # a posição digitada começa em 1, mas o índice da lista começa em 0
        if posicao <= len(frota): veiculo = frota[posicao - 1]
    else:
        print("Opção inválida!")
        return
    if veiculo is None: print("Veículo não encontrado.")
    else:
        mostrar_veiculo(veiculo)
# Edita os campos de um veículo (Enter mantém o valor atual)
def editar_veiculo():
    veiculo = buscar(frota, "id", ler_inteiro("ID do veículo a editar: "))
    if veiculo is None:
        print("Veículo não encontrado.")
        return
    mostrar_veiculo(veiculo)
    print("Digite o novo valor ou deixe em branco para manter o atual.")
    for campo in ["placa", "transportadora", "motorista", "carga"]:
        novo = ler_texto(f"{campo.capitalize()} [{veiculo[campo]}]: ", False)
        # a placa é sempre salva em maiúsculas
        if novo != "": veiculo[campo] = novo.upper() if campo == "placa" else novo
    caminhao = buscar(fila, "id", veiculo["id"])  # se está na fila, atualiza os dados de lá também
    if caminhao is not None:
        for campo in ["placa", "transportadora", "carga"]:
            caminhao[campo] = veiculo[campo]
    print("Veículo atualizado com sucesso!")
# Exclui um veículo, mas só se ele não estiver na fila
def excluir_veiculo():
    veiculo = buscar(frota, "id", ler_inteiro("ID do veículo a excluir: "))
    if veiculo is None: print("Veículo não encontrado.")
    elif buscar(fila, "id", veiculo["id"]) is not None: print("Erro: o veículo está na fila. Remova-o da fila antes de excluir.")
    else:
        mostrar_veiculo(veiculo)
        if confirmar("Confirma a exclusão?"):
            frota.remove(veiculo)
            print("Veículo excluído com sucesso!")
        else:
            print("Exclusão cancelada.")
# MENUS 
# recebe {número: (descrição, função)}, mostra as opções e
# executa a função escolhida; a última opção sempre é 'Voltar'
def submenu(nome, opcoes):
    while True:
        titulo(nome)
        for numero, (descricao, _) in opcoes.items():
            print(f"{numero}. {descricao}")
        print(f"{len(opcoes) + 1}. Voltar")
        opcao = input("\nEscolha uma opção: ").strip()
        if opcao == str(len(opcoes) + 1):
            return
        if opcao in opcoes:
            opcoes[opcao][1]()
        else:
            print("Opção inválida! Tente novamente.")
# Submenu da frota
def menu_frota():
    submenu("GERENCIAR FROTA (LISTA)", {
        "1": ("Cadastrar veículo", cadastrar_veiculo),
        "2": ("Listar veículos", listar_veiculos),
        "3": ("Pesquisar veículo", pesquisar_veiculo),
        "4": ("Editar veículo", editar_veiculo),
        "5": ("Excluir veículo", excluir_veiculo),
    })
# FILA - CAMINHÕES (FIFO) 
# Coloca no final da fila um veículo já cadastrado na frota
def adicionar_caminhao_fila():
    veiculo = buscar(frota, "id", ler_inteiro("ID do caminhão (da frota): "))
    if veiculo is None:
        print("Erro: veículo não cadastrado na frota. Cadastre-o primeiro.")
        return
    chegada = ler_texto("Horário/informação de chegada (Enter = agora): ", False)
    if chegada == "":
        chegada = datetime.now().strftime("%d/%m/%Y %H:%M")
    caminhao = {"id": veiculo["id"], "placa": veiculo["placa"], "transportadora": veiculo["transportadora"],
                "carga": veiculo["carga"], "chegada": chegada}
    erro = validar_caminhao(caminhao, fila, frota)
    if erro != "":
        print(f"Erro: {erro}.")
    else:
        fila.append(caminhao)  # FIFO: entra no final
        print("Caminhão adicionado ao final da fila.")
# Mostra a fila do primeiro (próximo a sair) ao último
def visualizar_fila():
    for posicao, caminhao in enumerate(fila, start=1):
        mostrar_caminhao(caminhao, f"  Posição {posicao} | ")
    print(f"\nTotal aguardando: {len(fila)}. (Posição 1 = próximo a ser liberado)")
# Mostra o primeiro da fila sem removê-lo
def consultar_proximo_caminhao():
    if len(fila) == 0:
        print("A fila está vazia.")
    else: mostrar_caminhao(fila[0])  # só consulta, não remove
# Remove e exibe o primeiro da fila (libera para embarque)
def liberar_proximo_caminhao():
    if len(fila) == 0:
        print("A fila está vazia. Não há caminhão para liberar.")
    else:
        mostrar_caminhao(fila.popleft())  # FIFO: sai quem está no início
        print("Próximo caminhão liberado para embarque.")
# Procura na fila por ID exato ou por trecho da placa (pode haver vários resultados)
def pesquisar_caminhao_fila():
    termo = ler_texto("Digite o ID ou a placa: ").upper()
    encontrou = False
    for posicao, caminhao in enumerate(fila, start=1):
        if termo == str(caminhao["id"]) or termo in caminhao["placa"]:
            mostrar_caminhao(caminhao, f"  Posição {posicao} | ")
            encontrou = True
    if not encontrou:
        print("Caminhão não encontrado na fila.")
# Remove da fila um caminhão específico, em qualquer posição
def remover_caminhao_especifico():
    caminhao = buscar(fila, "id", ler_inteiro("ID do caminhão a remover: "))
    if caminhao is None:
        print("Caminhão não encontrado na fila.")
        return
    mostrar_caminhao(caminhao)
    if confirmar("Confirma a remoção?"):
        fila.remove(caminhao)
        print("Caminhão removido da fila.")
    else:
        print("Remoção cancelada.")
# Submenu da fila
def menu_fila():
    submenu("GERENCIAR FILA DE CAMINHÕES", {
        "1": ("Adicionar caminhão à fila", adicionar_caminhao_fila),
        "2": ("Visualizar fila", visualizar_fila),
        "3": ("Consultar próximo caminhão", consultar_proximo_caminhao),
        "4": ("Liberar próximo caminhão", liberar_proximo_caminhao),
        "5": ("Pesquisar caminhão", pesquisar_caminhao_fila),
        "6": ("Remover caminhão específico", remover_caminhao_especifico),
    })
#  PILHA - CONTÊINERES (LIFO)
# Lê os dados, valida e coloca o contêiner no topo da pilha
def empilhar_container():
    container = {"codigo": ler_texto("Código identificador: "), "numero": ler_texto("Número/código do contêiner: ").upper(),
                 "descricao": ler_texto("Descrição da carga: "), "destino": ler_texto("Destino: "),
                 "peso": ler_peso("Peso em kg (opcional): ")}
    erro = validar_container(container, pilha)
    if erro != "":
        print(f"Erro: {erro}.")
    else:
        pilha.append(container)  # LIFO: entra no topo
        print("Contêiner empilhado com sucesso.")
# reversed(): mostra do topo (último elemento) até a base
def visualizar_pilha():
    for posicao, container in enumerate(reversed(pilha), start=1):
        mostrar_container(container, f"  [{posicao}º a partir do topo]{' (TOPO)' if posicao == 1 else ''} ")
    print(f"\nTotal empilhado: {len(pilha)}.")
# Consulta o contêiner do topo sem removê-lo
def consultar_topo():
    if len(pilha) == 0:
        print("A pilha está vazia.")
    else: mostrar_container(pilha[-1])  # só consulta, não remove
# Remove e exibe apenas o contêiner do topo
def desempilhar_container():
    if len(pilha) == 0:
        print("A pilha está vazia. Não há contêiner para retirar.")
    else:
        mostrar_container(pilha.pop())  # LIFO: remove apenas o topo
        print("Contêiner do topo removido.")
# Procura por código ou número; avisa quantos contêineres estão acima dele
def pesquisar_container():
    termo = ler_texto("Digite o código identificador ou número do contêiner: ").lower()
    for posicao, container in enumerate(reversed(pilha), start=1):
        if termo == container["codigo"].lower() or termo == container["numero"].lower():
            mostrar_container(container, f"  [{posicao}º a partir do topo] ")
            if posicao > 1:
                print(f"  Atenção: há {posicao - 1} contêiner(es) acima dele. Só é possível retirá-lo após desempilhar os de cima.")
            return
    print("Contêiner não encontrado na pilha.")
# Submenu da pilha
def menu_pilha():
    submenu("GERENCIAR PILHA DE CONTÊINERES", {
        "1": ("Empilhar contêiner", empilhar_container),
        "2": ("Visualizar pilha", visualizar_pilha),
        "3": ("Consultar contêiner do topo", consultar_topo),
        "4": ("Desempilhar contêiner", desempilhar_container),
        "5": ("Pesquisar contêiner", pesquisar_container),
    })
#  ÁRVORE - ROTAS (dicionários aninhados + recursividade) 
# Devolve o dicionário (nó) indicado pelo caminho, descendo nível por nível
def obter_no(caminho):
    no = arvore  # desce pelo caminho; caminho vazio = raiz
    for nome in caminho:
        no = no[nome]
    return no
# Procura um filho pelo nome (ignorando maiúsculas); devolve o nome original ou None
def buscar_filho(no, nome):
    for filho in no:
        if filho.lower() == nome.lower():
            return filho
    return None
# Imprime a árvore com indentação proporcional ao nível
def listar_hierarquia(no, nivel=0):  
    for nome in no:
        print("    " * nivel + f"└─ {nome}  [{NIVEIS[nivel]}]")
        listar_hierarquia(no[nome], nivel + 1)
# Procura nós cujo nome contém o termo 
def buscar_nos(no, termo, caminho=None):  
    if caminho is None:
        caminho = []
    achados = []
    for nome in no:
        if termo.lower() in nome.lower():
            achados.append(caminho + [nome])
        achados.extend(buscar_nos(no[nome], termo, caminho + [nome]))
    return achados
# Lista os caminhos completos, da raiz até cada folha
def caminhos_completos(no, caminho=None):
    if caminho is None:
        caminho = []
    resultado = []
    for nome in no:
        if len(no[nome]) > 0:
            resultado.extend(caminhos_completos(no[nome], caminho + [nome]))
        else:
            resultado.append(caminho + [nome])
    return resultado
# Conta todos os nós (descendentes) de um nó
def contar_nos(no):  
    total = 0
    for nome in no:
        total += 1 + contar_nos(no[nome])
    return total
# Localiza um nó pelo nome; se houver ambiguidade, o usuário escolhe
# entre os caminhos encontrados. Devolve o caminho ou None
def escolher_no(termo):
    achados = buscar_nos(arvore, termo)
    exatos = []
    for caminho in achados:
        if caminho[-1].lower() == termo.lower():
            exatos.append(caminho)
    if len(exatos) > 0:
        achados = exatos
    if len(achados) == 0:
        print("Nó não encontrado na árvore.")
        return None
    if len(achados) == 1:
        return achados[0]
    print("Foram encontrados vários nós:")
    for numero, caminho in enumerate(achados, start=1):
        print(f"  {numero}. {' > '.join(caminho)}  [{NIVEIS[len(caminho) - 1]}]")
    escolha = ler_inteiro("Escolha o número do nó desejado: ")
    if escolha > len(achados):
        print("Opção inválida.")
        return None
    return achados[escolha - 1]
# Adiciona um novo nó (porto ou rota) abaixo de um pai, ou como porto de origem
def adicionar_no_arvore():
    pai = []
    if len(arvore) == 0:
        print("A árvore está vazia: o primeiro nó será um Porto de origem.")
    else:
        termo = ler_texto("Nome do nó pai (Enter = novo Porto de origem): ", False)
        if termo != "":
            pai = escolher_no(termo)
            if pai is None:
                return
    # o último nível (destino final) não pode ter filhos
    if len(pai) >= len(NIVEIS):
        print("Erro: um Destino final não pode ter nós filhos.")
        return
    nome = ler_texto(f"Nome do novo nó ({NIVEIS[len(pai)]}): ")
    filhos = obter_no(pai)
    if buscar_filho(filhos, nome) is not None:
        print("Erro: já existe um nó com esse nome neste mesmo local.")
    else:
        filhos[nome] = {}
        print(f"Nó adicionado com sucesso como {NIVEIS[len(pai)]}.")
# Mostra a hierarquia completa e o total de nós
def listar_arvore():
    listar_hierarquia(arvore)
    print(f"\nTotal de nós: {contar_nos(arvore)}.")
# Pesquisa nós pelo nome (ou parte dele) e mostra caminho e nível
def pesquisar_no_arvore():
    achados = buscar_nos(arvore, ler_texto("Digite o nome (ou parte do nome): "))
    if len(achados) == 0:
        print("Nenhum porto ou rota encontrado.")
    for caminho in achados:
        print(f"  {' > '.join(caminho)}  [{NIVEIS[len(caminho) - 1]}] - {len(obter_no(caminho))} filho(s) direto(s)")
# Navegação interativa: entrar em um nó, voltar um nível ou sair
def navegar_niveis():
    atual = []  # caminho do nó onde o usuário está
    while True:
        filhos = list(obter_no(atual).keys())
        print("\nLocal atual: " + (" > ".join(atual) if len(atual) > 0 else "(raiz)"))
        if len(filhos) == 0:
            print("Este nó não possui filhos.")
        else:
            print(f"Itens do nível '{NIVEIS[len(atual)]}':")
            for numero, nome in enumerate(filhos, start=1):
                print(f"  {numero}. {nome}")
        escolha = input("Número para entrar | V = voltar um nível | S = sair: ").strip().lower()
        numero = para_inteiro(escolha)
        if escolha == "s":
            return
        elif escolha == "v" and len(atual) > 0:
            atual.pop()
        elif escolha == "v":
            print("Você já está na raiz.")
        elif 1 <= numero <= len(filhos):
            atual.append(filhos[numero - 1])
        else: print("Opção inválida.")
# Mostra todos os caminhos completos ou permite navegar pelos níveis
def consultar_caminhos():
    opcao = input("1. Listar todos os caminhos completos\n2. Navegar pelos níveis da hierarquia\nEscolha uma opção: ").strip()
    if opcao == "1":
        for caminho in caminhos_completos(arvore):
            print("  " + " > ".join(caminho))
    elif opcao == "2":
        navegar_niveis()
    else:
        print("Opção inválida!")
# Remove um nó e todos os seus descendentes, com confirmação
def remover_no_arvore():
    caminho = escolher_no(ler_texto("Nome do nó a remover: "))
    if caminho is None:
        return
    descendentes = contar_nos(obter_no(caminho))
    print(f"Nó: {' > '.join(caminho)}")
    if descendentes > 0:
        print(f"Atenção: {descendentes} descendente(s) também serão removido(s).")
    if confirmar("Confirma a remoção?"):
        del obter_no(caminho[:-1])[caminho[-1]]  # remove o nó com todos os filhos
        print("Nó removido com sucesso.")
    else:
        print("Remoção cancelada.")
# Submenu da árvore
def menu_arvore():
    submenu("GERENCIAR ÁRVORE DE ROTAS", {
        "1": ("Adicionar porto ou rota", adicionar_no_arvore),
        "2": ("Listar hierarquia", listar_arvore),
        "3": ("Pesquisar porto ou rota", pesquisar_no_arvore),
        "4": ("Consultar caminhos", consultar_caminhos),
        "5": ("Remover porto ou rota", remover_no_arvore),
    })
#  PERSISTÊNCIA (dados_sistema.txt)
# Grava uma linha por registro no formato TIPO|campo1|campo2|...
# A árvore é salva apenas pelos caminhos completos (raiz até as folhas)
def salvar_dados():
    linhas = []
    for v in frota:
        linhas.append(SEP.join(["LISTA", str(v["id"]), v["placa"], v["transportadora"], v["motorista"], v["carga"]]))
    for c in fila:
        linhas.append(SEP.join(["FILA", str(c["id"]), c["placa"], c["transportadora"], c["carga"], c["chegada"]]))
    for c in pilha:
        linhas.append(SEP.join(["PILHA", c["codigo"], c["numero"], c["descricao"], c["destino"], c["peso"]]))
    for caminho in caminhos_completos(arvore):
        linhas.append(SEP.join(["ARVORE"] + caminho))
    try:
        with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
            arquivo.write("\n".join(linhas) + "\n")
        print("Dados salvos com sucesso!")
    except OSError as erro:
        print(f"Erro ao gravar o arquivo: {erro}")
# Converte uma linha do arquivo em registro e o adiciona em 'novos'.
# Devolve '' se deu certo ou a mensagem de erro
def interpretar_linha(campos, novos):
    tipo, v = campos[0], campos[1:]
    # ARVORE: cada campo é um nível do caminho; cria os nós que ainda não existem
    if tipo == "ARVORE":
        if len(v) == 0 or len(v) > len(NIVEIS) or "" in v:
            return "caminho da árvore inválido"
        no = novos["arvore"]
        for nome in v:
            filho = buscar_filho(no, nome)
            if filho is None:
                no[nome] = {}
                filho = nome
            no = no[filho]
        return ""
    # os demais tipos (LISTA, FILA, PILHA) têm exatamente 5 campos
    if len(v) != 5:
        return "quantidade de campos incorreta"
    if tipo == "LISTA":
        registro = {"id": para_inteiro(v[0]), "placa": v[1].upper(), "transportadora": v[2], "motorista": v[3], "carga": v[4]}
        erro = validar_veiculo(registro, novos["frota"])
        destino = novos["frota"]
    elif tipo == "FILA":
        registro = {"id": para_inteiro(v[0]), "placa": v[1].upper(), "transportadora": v[2], "carga": v[3], "chegada": v[4]}
        erro = validar_caminhao(registro, novos["fila"], novos["frota"])
        destino = novos["fila"]
    else:
        peso = validar_peso(v[4])
        if peso is None:
            return "peso deve ser número maior que zero"
        registro = {"codigo": v[0], "numero": v[1].upper(), "descricao": v[2], "destino": v[3], "peso": peso}
        erro = validar_container(registro, novos["pilha"])
        destino = novos["pilha"]
    if erro == "":
        destino.append(registro)
    return erro
# Lê o arquivo para estruturas temporárias e só substitui os dados em memória
# se houver registros válidos (e o usuário confirmar, quando já houver dados)
def carregar_dados():
    if not os.path.exists(ARQUIVO):
        print("Arquivo de dados não encontrado. Nenhum dado foi carregado.")
        return
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
            linhas = arquivo.readlines()
    except (OSError, UnicodeDecodeError) as erro:
        print(f"Erro ao ler o arquivo: {erro}")
        return
    registros = []
    for linha in linhas:
        if linha.strip() != "":
            registros.append([campo.strip() for campo in linha.split(SEP)])
    # estruturas temporárias: os dados atuais só são trocados no final
    novos = {"frota": [], "fila": deque(), "pilha": [], "arvore": {}}
    aceitas = 0
    for tipo in ["LISTA", "FILA", "PILHA", "ARVORE"]:  # a frota vem antes da fila, que depende dela
        for campos in registros:
            if campos[0] == tipo:
                erro = interpretar_linha(campos, novos)
                if erro == "":
                    aceitas += 1
                else:
                    print(f"  Linha ignorada ({erro}): {SEP.join(campos)}")
    # linhas que não foram aceitas (inválidas ou duplicadas)
    invalidas = len(registros) - aceitas
    if aceitas == 0 and invalidas > 0:
        print("Nenhum registro válido encontrado. Os dados atuais foram mantidos.")
        return
    if (len(frota) > 0 or len(fila) > 0 or len(pilha) > 0 or len(arvore) > 0) and not confirmar("Os dados atuais em memória serão substituídos. Continuar?"):
        print("Carregamento cancelado.")
        return
    # atualiza os objetos globais no lugar (sem recriá-los)
    frota[:] = novos["frota"]
    fila.clear()
    fila.extend(novos["fila"])
    pilha[:] = novos["pilha"]
    arvore.clear()
    arvore.update(novos["arvore"])
    print("Dados carregados com sucesso!")
    print(f"  Veículos: {len(frota)} | Fila: {len(fila)} | Contêineres: {len(pilha)} | Nós da árvore: {contar_nos(arvore)}")
    if invalidas > 0:
        print(f"Aviso: {invalidas} linha(s) inválida(s) ou incompleta(s) foram ignoradas.")
#  MENU PRINCIPAL 
# Loop do menu principal; ao sair, oferece salvar os dados
def menu_principal():
    while True:
        titulo("CONTROLE DE LOGÍSTICA PORTUÁRIA")
        print("1. Gerenciar Lista\n2. Gerenciar Fila de Caminhões\n3. Gerenciar Pilha de Contêineres\n"
              "4. Gerenciar Rotas\n5. Salvar Dados\n6. Carregar Dados\n7. Sair")
        opcao = input("\nEscolha uma opção: ").strip()
        if opcao == "1": menu_frota()
        elif opcao == "2": menu_fila()
        elif opcao == "3": menu_pilha()
        elif opcao == "4": menu_arvore()
        elif opcao == "5": salvar_dados()
        elif opcao == "6": carregar_dados()
        elif opcao == "7": break
        else: print("Opção inválida! Tente novamente.")
    if confirmar("Deseja salvar os dados antes de sair?"): salvar_dados()
    print("Programa encerrado. Até logo!")
if __name__ == "__main__":
    try:
        menu_principal()
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma encerrado.")
