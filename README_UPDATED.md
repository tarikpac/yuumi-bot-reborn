# 🐱 Yuumi Bot Reborn

> **Nota**: Este projeto é um fork modernizado e corrigido do original [yuumi-bot](https://github.com/SvetoslavDoychinov/yuumi-bot). Nosso foco foi reviver o bot para funcionar no Client atual do League of Legends (2025), corrigindo interações quebradas com a API.

## 📖 O que é isso?

O **Yuumi Bot Reborn** é uma ferramenta de automação desenvolvida em Python para League of Legends. Ele foi projetado para simular um jogador de suporte (especificamente com a campeã Yuumi), automatizando desde a criação do lobby até as ações dentro da partida.

Ao contrário de scripts complexos de injeção direta na memória (que dão banimento rápido), este bot foca em usar a **LCU API** (a API local oficial do cliente do LoL) e reconhecimento visual simples, tornando-o mais uma "ferramenta de auxílio" do que um hack agressivo.

## ✨ O que há de novo? (Nossas Melhorias)

O projeto original estava abandonado e não funcionava mais nas versões recentes do jogo. Nós implementamos:

*   **🛡️ Blindagem de API (Anti-Crash)**: O bot não fecha mais sozinho quando o LoL demora para carregar ou retorna dados incompletos. Tratamos erros como `KeyError` em nomes de invocador e falhas de conexão durante telas de carregamento.
*   **🔄 Troca de Roles Inteligente**: Em filas Draft, o bot identifica se caiu como Suporte. Se cair em outra posição (ex: Jungle), ele automaticamente pede troca com o suporte ou aceita trocas recebidas.
*   **🆔 Suporte a Riot ID**: Corrigido o bug onde o bot não reconhecia o próprio jogador devido às novas tags (`#BR1`) nos nomes.
*   **🖥️ Nova Interface Gráfica**: Adicionamos um painel de controle (`gui.py`) com tema escuro para você não precisar ficar editando código para mudar entre Fila Ranqueada ou Bot.
*   **Co-op vs AI Atualizado**: IDs das filas de bot (Intro/Intermediário) atualizados para os padrões de 2025.

## 🚀 Como Usar

### Pré-requisitos
*   Python 3.10+ instalado.
*   Cliente do League of Legends aberto e logado.
*   Resolução do jogo deve estar em **1024x768** e modo **Janela** (Windowed) para o reconhecimento visual funcionar perfeitamente.

### Instalação
1.  Clone este repositório:
    ```bash
    git clone https://github.com/tarikpac/yuumi-bot-reborn.git
    cd yuumi-bot-reborn
    ```
2.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

### Rodando
Execute a nova interface gráfica:
```bash
python gui.py
```
Selecione o tipo de fila (ex: "Draft Pick" ou "Intermediate Bot") e clique em **INICIAR BOT**.

## ⚙️ Modos de Operação

O bot possui dois modos principais (selecionáveis na GUI):

1.  **Somente Auto-Fila**: O bot fará todo o trabalho chato de criar sala, aceitar partida, escolher campeão e trocar de role se necessário. Quando o jogo começar, ele para e deixa você jogar.
2.  **Yuumi In-Game Completo**: O bot joga a partida inteira. Ele se conecta ao ADC (ou aliado mais forte), cura, usa ultimate, compra itens e volta base se estiver com pouca vida. *(Nota: Por padrão, a lógica in-game está desativada no código para segurança, mas pode ser reativada facilmente).*

## ⚠️ Aviso Legal e Responsabilidade

**Este bot não é endossado pela Riot Games e não reflete as opiniões da Riot Games ou de qualquer pessoa oficialmente envolvida na produção ou gerenciamento do League of Legends.**

O uso de programas de automação ("bots") viola os Termos de Serviço do League of Legends.
*   **Use por sua conta e risco.**
*   Não nos responsabilizamos por banimentos ou suspensões de contas.
*   Este projeto é puramente educacional, demonstrando como interagir com a API LCU e automação de GUI.
