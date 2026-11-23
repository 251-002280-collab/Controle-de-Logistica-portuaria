# Controle de Logística Portuária

Projeto final da disciplina Teoria das Estruturas de Dados. Sistema em Python, executado pelo terminal (CLI), que integra Fila, Pilha, Lista e Árvore para simular o núcleo lógico de um sistema de logística portuária, com persistência em arquivo texto.

## 1. Como executar

**Requisitos:** Python 3.6 ou superior (o programa usa f-strings). Nenhuma biblioteca externa é necessária.

```bash
python main.py
```

(em alguns sistemas, `python3 main.py`)

O sistema inicia totalmente vazio. Para guardar o que foi cadastrado, use a opção **5 - Salvar Dados**, que cria o arquivo `dados_sistema.txt`. Em uma execução futura, use **6 - Carregar Dados** para restaurar tudo.

### Roteiro rápido de teste

1. Menu 1 (Frota) → 1 Cadastrar veículo → cadastre alguns veículos → 2 Listar.
2. Menu 2 (Fila) → 1 Adicionar caminhão, usando o ID de um veículo da frota → 2 Visualizar fila.
3. Menu 3 (Pilha) → insira contêineres e visualize (o topo aparece marcado).
4. Menu 4 (Árvore) → adicione um porto de origem (o primeiro nó), depois filhos usando o nome do nó pai, por exemplo `Santos` → `Rota Atlântico Norte` → `Roterdã`.
5. Menu 5 para salvar, feche o programa, abra novamente e use 6 para carregar.

## 2. Visão geral do funcionamento

O programa tem um menu principal com seis opções de trabalho e a saída:

| Opção | Ação |
|-------|------|
| 1 | Frota de Veículos (Lista) |
| 2 | Fila de Caminhões |
| 3 | Pilha de Contêineres |
| 4 | Rotas Marítimas (Árvore) |
| 5 | Salvar Dados |
| 6 | Carregar Dados |
| 7 | Sair |

As opções 1 a 4 abrem um submenu com as operações de cada estrutura e, como última opção, Voltar. Cada estrutura tem suas próprias funções, que respeitam as regras conceituais dela.

Todos os dados ficam em memória em quatro variáveis globais. O arquivo só é lido ou escrito quando o usuário escolhe Salvar ou Carregar.

| Estrutura | Variável | Tipo Python | Papel no porto |
|-----------|----------|-------------|----------------|
| Fila | `fila` | `collections.deque` | Ordem de chegada dos caminhões no pátio |
| Pilha | `pilha` | `list` | Empilhamento de contêineres no navio ou pátio |
| Lista | `frota` | `list` | Frota de veículos e transportadoras |
| Árvore | `arvore` | `dict` aninhado | Rotas marítimas, portos intermediários e destinos finais |

## 3. Justificativa técnica das estruturas

### Fila (FIFO) - Caminhões aguardando embarque

No pátio, o caminhão que chegou primeiro deve ser liberado primeiro. Isso é exatamente o comportamento FIFO (First In, First Out): a inserção ocorre sempre no fim e a liberação sempre no início. Usamos `collections.deque` porque `popleft()` remove do início em tempo O(1), enquanto `list.pop(0)` seria O(n), pois desloca todos os elementos restantes. Em um porto com muitos caminhões, essa diferença importa.

### Pilha (LIFO) - Empilhamento de contêineres

Contêineres empilhados fisicamente só podem ser retirados pelo topo: o último a entrar é o primeiro a sair. Isso é o comportamento LIFO (Last In, First Out). Usamos `list` com `append()` (empilhar) e `pop()` (desempilhar), ambos O(1) no fim da lista, que funciona como o topo. Para chegar a um contêiner mais abaixo, é preciso desempilhar os que estão acima dele, e o sistema avisa quantos são.

### Lista - Frota de veículos

A frota não segue ordem de atendimento: é preciso consultar, alterar ou excluir qualquer veículo, a qualquer momento. A lista permite acesso por posição (índice) e por ID. É a estrutura adequada para um cadastro dinâmico que cresce e diminui sem regra de ordem.

### Árvore - Rotas marítimas

Rotas são naturalmente hierárquicas (porto de origem → rota marítima → porto intermediário → destino final). Uma estrutura linear não representaria essa relação de "pertence a". A árvore permite navegar do geral para o específico. Como o Python não tem árvore nativa, foi usado dicionário aninhado, em que cada chave é um nó e o valor é um dicionário com os filhos.

## 4. Como cada estrutura foi implementada

### 4.1 Fila (`deque`)

```python
fila = deque()
```

Cada caminhão é um dicionário `{"id", "placa", "transportadora", "carga", "chegada"}`. Só entram na fila veículos já cadastrados na frota.

| Operação | Função | Implementação |
|----------|--------|---------------|
| Inserir | `adicionar_caminhao_fila()` | `fila.append(caminhao)` adiciona no fim; a chegada é preenchida com data e hora atuais se ficar vazia |
| Listar | `visualizar_fila()` | percorre com `enumerate`, mostrando a posição (1 = próximo a ser liberado) |
| Consultar | `consultar_proximo_caminhao()` | `fila[0]`, sem remover |
| Remover | `liberar_proximo_caminhao()` | `fila.popleft()` remove e retorna o primeiro (caminhão liberado) |
| Pesquisar | `pesquisar_caminhao_fila()` | busca por ID ou trecho da placa |
| Remover específico | `remover_caminhao_especifico()` | `fila.remove()` em qualquer posição, com confirmação |
| Atualizar | `editar_veiculo()` | ao editar um veículo da frota, o caminhão correspondente na fila também é atualizado |

No fluxo normal, a regra "insere no fim, remove no início" é garantida: só existe uma função de entrada e uma de liberação. A remoção específica é uma exceção deliberada, para o caso de um caminhão desistir ou ser cancelado antes da liberação; ela não altera a ordem dos demais e exige confirmação.

### 4.2 Pilha (`list`)

```python
pilha = []
```

Cada contêiner é um dicionário `{"codigo", "numero", "descricao", "destino", "peso"}`. O topo é o último elemento da lista. O peso é opcional.

| Operação | Função | Implementação |
|----------|--------|---------------|
| Inserir (empilhar) | `empilhar_container()` | valida (código e número únicos) e faz `pilha.append(container)` |
| Listar | `visualizar_pilha()` | `reversed(...)` mostra do topo para a base e marca o topo |
| Consultar | `consultar_topo()` | `pilha[-1]`, sem remover |
| Remover (desempilhar) | `desempilhar_container()` | `pilha.pop()` remove o topo |
| Pesquisar | `pesquisar_container()` | busca por código ou número e avisa quantos contêineres estão acima |

Em uma pilha só o topo é acessível, por isso o sistema não permite alterar nem retirar um contêiner do meio dela.

### 4.3 Lista (`list`)

```python
frota = []
```

Cada veículo é um dicionário `{"id", "placa", "transportadora", "motorista", "carga"}`.

| Operação | Função | Implementação |
|----------|--------|---------------|
| Buscar | `buscar(frota, "id", valor)` | percorre a lista comparando o campo; retorna o registro ou `None` |
| Inserir | `cadastrar_veiculo()` | recusa ID repetido e faz `append()` |
| Listar | `listar_veiculos()` | percorre com `enumerate`, mostrando a posição |
| Pesquisar | `pesquisar_veiculo()` | busca por ID ou consulta por posição (índice) |
| Atualizar | `editar_veiculo()` | localiza pelo ID e altera os campos (Enter mantém o atual) |
| Remover | `excluir_veiculo()` | localiza pelo ID e usa `remove()`; bloqueado se o veículo estiver na fila |

### 4.4 Árvore (dicionários aninhados)

```python
arvore = {}
```

Exemplo de conteúdo em memória:

```python
{
  "Santos": {
      "Rota Atlântico Norte": {
          "Roterdã": {"Hamburgo": {}, "Antuérpia": {}}
      },
      "Rota Pacífico": {
          "Cingapura": {"Xangai": {}}
      }
  }
}
```

- Cada chave é o nome de um nó.
- Cada valor é outro dicionário com os filhos daquele nó.
- Um dicionário vazio `{}` indica um nó folha.
- A raiz é o próprio dicionário `arvore` (pode ter vários portos de origem no primeiro nível).
- Os níveis são fixos: Porto de origem, Rota marítima, Porto intermediário e Destino final. Um destino final não aceita filhos.

O usuário informa a posição de um nó pelo nome (ou parte dele). Se houver mais de um nó com o mesmo nome em lugares diferentes, o sistema lista os caminhos completos e pede que o usuário escolha.

| Função | O que faz |
|--------|-----------|
| `obter_no(caminho)` | começa em `arvore` e desce uma chave por vez; retorna o dicionário do nó (caminho vazio = raiz) |
| `buscar_filho(no, nome)` | procura um filho pelo nome, ignorando maiúsculas e minúsculas |
| `escolher_no(termo)` | localiza o nó pelo nome e resolve ambiguidades; retorna o caminho |
| `adicionar_no_arvore()` | localiza o pai e cria o filho com `filhos[nome] = {}` |
| `listar_hierarquia()` | recursiva: imprime o nome, depois chama a si mesma para os filhos com um nível a mais de indentação |
| `buscar_nos()` | recursiva: devolve o caminho de todos os nós cujo nome contém o termo |
| `caminhos_completos()` | recursiva: gera o caminho da raiz até cada folha |
| `contar_nos()` | recursiva: conta todos os descendentes de um nó |
| `navegar_niveis()` | navegação interativa: entrar em um nó, voltar um nível ou sair |
| `remover_no_arvore()` | `del` remove o nó e toda a sua subárvore, com confirmação |

## 5. Persistência em arquivo texto

Todo o estado é gravado em um único arquivo, `dados_sistema.txt`, sem banco de dados, JSON, CSV ou pickle. Cada linha começa com um identificador da estrutura e os campos são separados por pipe (`|`):

```text
LISTA|101|ABC1D23|Transportes Atlântico|Carlos Silva|Soja
FILA|101|ABC1D23|Transportes Atlântico|Soja|22/11/2026 08:30
PILHA|C-001|MSKU1234567|Café em grãos|Roterdã|18500.00
ARVORE|Santos|Rota Atlântico Norte|Roterdã|Hamburgo
```

### Salvar (`salvar_dados`)

- Abre o arquivo em modo escrita (`"w"`), sobrescrevendo o conteúdo anterior.
- Grava `LISTA`, `FILA` (na ordem atual da fila) e `PILHA` (da base ao topo, para que ao recarregar o topo continue sendo o último elemento).
- Para a árvore, a função recursiva `caminhos_completos` gera um caminho para cada folha; cada caminho vira uma linha `ARVORE|...`. Como todo nó pertence a algum caminho até uma folha, a árvore inteira é preservada.
- Erros de gravação são tratados e informados ao usuário.

### Carregar (`carregar_dados`)

- Se o arquivo não existir, avisa o usuário e não altera nada.
- Lê o arquivo linha a linha, separa cada linha com `split("|")` e usa o primeiro campo para decidir em qual estrutura inserir (`interpretar_linha`).
- Monta os registros em estruturas temporárias e só substitui os dados em memória no final. Se o arquivo tiver linhas, mas nenhuma válida, os dados atuais são mantidos. Se já houver dados em memória, pede confirmação.
- Carrega a frota antes da fila, porque um caminhão só entra se o veículo existir na frota.
- Para `ARVORE`, desce pelos nomes usando `buscar_filho`, que cria o nó caso ainda não exista e reaproveita nós já criados por outras linhas.
- Linhas inválidas (campos faltando, ID duplicado, caminhão fora da frota, peso inválido) são ignoradas com aviso, sem derrubar o programa.

### Proteção do delimitador

A função `ler_texto` troca qualquer `|` digitado pelo usuário por `/`, evitando que o texto quebre o formato do arquivo.

## 6. Organização do código (`main.py`)

O arquivo está dividido em blocos, cada um com funções de responsabilidade única:

- **Estruturas em memória:** as quatro variáveis globais (iniciam vazias).
- **Funções de entrada e auxiliares:** `ler_texto` (texto não vazio), `ler_inteiro` (repete até receber um número válido), `para_inteiro`, `ler_peso`, `validar_peso`, `confirmar`, `buscar` (busca genérica por campo) e `titulo`.
- **Exibição e validação:** `mostrar_veiculo`, `mostrar_caminhao`, `mostrar_container`, `validar_veiculo`, `validar_caminhao`, `validar_container`.
- **Fila:** `adicionar_caminhao_fila`, `visualizar_fila`, `consultar_proximo_caminhao`, `liberar_proximo_caminhao`, `pesquisar_caminhao_fila`, `remover_caminhao_especifico`.
- **Pilha:** `empilhar_container`, `visualizar_pilha`, `consultar_topo`, `desempilhar_container`, `pesquisar_container`.
- **Lista:** `cadastrar_veiculo`, `listar_veiculos`, `pesquisar_veiculo`, `editar_veiculo`, `excluir_veiculo`.
- **Árvore:** `obter_no`, `buscar_filho`, `listar_hierarquia`, `buscar_nos`, `caminhos_completos`, `contar_nos`, `escolher_no`, `adicionar_no_arvore`, `listar_arvore`, `pesquisar_no_arvore`, `navegar_niveis`, `consultar_caminhos`, `remover_no_arvore`.
- **Persistência:** `salvar_dados`, `interpretar_linha`, `carregar_dados`.
- **Menus:** `submenu`, `menu_frota`, `menu_fila`, `menu_pilha`, `menu_arvore` e `menu_principal`.

### Fluxo de execução

1. `if __name__ == "__main__"` chama `menu_principal()`, protegido contra `Ctrl+C` e `Ctrl+D`.
2. O menu principal roda em um laço `while True`, lê a opção e chama a função correspondente.
3. As opções 1 a 4 chamam `menu_frota`, `menu_fila`, `menu_pilha` e `menu_arvore`, que usam o mesmo `submenu`. Ele recebe o nome do menu e um dicionário `{número: (descrição, função)}`. Assim, um único submenu serve para as quatro estruturas, sem repetir código.
4. A opção 7 encerra o laço, oferece salvar os dados e finaliza o programa. Opções inválidas exibem uma mensagem e o menu é mostrado novamente.

## 7. Resumo

O sistema mantém quatro estruturas em memória: uma fila (`deque`) para os caminhões aguardando embarque, uma pilha (`list`) para os contêineres, uma lista (`list`) para a frota de veículos e uma árvore (dicionários aninhados) para as rotas marítimas. O usuário opera todas por menus numéricos, respeitando as regras de cada estrutura: a fila insere no fim e libera no início, a pilha opera só no topo, a lista acessa por ID ou posição e a árvore navega e insere de forma hierárquica. Os dados são salvos e carregados explicitamente em um único arquivo `dados_sistema.txt`, com um identificador por linha e campos separados por `|`.
