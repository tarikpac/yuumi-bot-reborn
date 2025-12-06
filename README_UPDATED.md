# Yuumi Bot - Reforked & Updated

Este é um fork altamente modificado e atualizado do projeto [yuumi-bot original de SvetoslavDoychinov](https://github.com/SvetoslavDoychinov/yuumi-bot). Nosso objetivo foi trazer o bot de volta à vida, corrigindo incompatibilidades com a API atual do Client (LCU) e adicionando robustez para rodar de forma estável.

## 🚀 Principais Melhorias e Correções

### Estabilidade e API (Hardening)
*   **Correção de Crashes na API**: O bot agora lida graciosamente com falhas temporárias da API do LoL, como dados incompletos durante a tela de loading (`KeyError` em `summonerName`) ou retornos de erro (`TypeError` em listas de itens).
*   **Riot ID Suportado**: Corrigimos a detecção de jogador para funcionar corretamente com o novo sistema de Riot IDs (Ex: `Nome#TAG`), evitando que o bot não se reconheça na partida.
*   **Gestão de Processos**: A verificação `is_process_running` foi blindada contra encerramentos abruptos de processos (race conditions), impedindo o bot de fechar sozinho.

### Lógica de Jogo e Filas
*   **Sistema de Troca de Roles (Draft Pick)**: Implementada lógica inteligente para identificar a posição (Suporte/Utility). Se cair em outra role, o bot tenta trocar automaticamente ou aceita trocas recebidas, parando assim que consegue a posição desejada.
*   **Controle de Fases**: O bot agora detecta `PreEndOfGame` e sai do loop imediatamente, fechando o jogo de forma limpa e evitando erros de conexão com processos 'zumbis'.
*   **Modos de Fila**: IDs de fila atualizados para 2024/2025 (Intermediário, Intro, Draft Pick).

### Nova Interface Gráfica (GUI)
*   Adicionado um painel de controle visual (`gui.py`) moderno (Dark Theme) para facilitar o uso:
    *   **Seleção de Modo**: "Auto-Queue Only" (apenas entrar na partida) ou "Full Gameplay" (jogar como Yuumi).
    *   **Logs**: Visualização de status em tempo real.

---

## ⚠️ Disclaimer e Aviso Legal

**This bot isn’t endorsed by Riot Games and doesn’t reflect the views or opinions of Riot Games or anyone officially involved in producing or managing League of Legends. League of Legends and Riot Games are trademarks or registered trademarks of Riot Games, Inc. League of Legends © Riot Games, Inc.**

**PT-BR**: Este software funciona interagindo com programas de terceiros (League of Legends). Ao usá-lo, você assume total responsabilidade por violações dos Termos de Serviço da Riot Games e por qualquer consequência nas contas utilizadas (incluindo banimentos). **Use por sua conta e risco.**
