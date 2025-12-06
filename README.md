# 🐱 Yuumi Bot Reborn (Minha versão corrigida)

Salve! Resolvi pegar esse projeto antigo do [yuumi-bot](https://github.com/SvetoslavDoychinov/yuumi-bot) pra dar uma atualizada, já que ele não estava nem abrindo mais com o Client novo do LoL (2025).

Basicamente, eu queria algo que funcionasse sem ficar crashando toda hora, então fiz várias correções e melhorias no código "por baixo do capô" pra deixar ele estável. Tô subindo aqui pra deixar documentado e caso sirva pra mais algúem.

## 🛠️ O que eu arrumei (Changelog Pessoal)

O código original era bom, mas a API do LoL mudou muito. Aqui o que eu tive que mexer:

*   **API Hardening (Blindagem)**: O bot original adorava fechar sozinho se a API do LoL demorasse 1 segundo a mais pra responder. Enchi de proteções (`try/catch`) nas chamadas de rede. Agora se o LoL engasgar na tela de loading, o bot espera de boa em vez de crashar com `KeyError`.
*   **Troca de Roles (Draft Pick)**: Eu queria usar isso em Draft, mas o bot as vezes caía Jungle ou Top e ficava lá parado. Implementei uma lógica nova: se eu não cair Suporte, ele automaticamente spamma pedido de troca ou aceita qualquer troca que mandarem, até cair na role certa.
*   **Riot ID**: Tive que arrumar a detecção de nomes. O bot não reconhecia o próprio jogador por causa das tags (`Nome#BR1`). Agora ele ignora a tag e acha o boneco certo.
*   **Adeus, Processos Zumbis**: Arrumei um bug chato onde o bot tentava ler memória de um jogo que já tinha fechado, o que travava o script.
*   **GUI (Interface)**: Cansei de ficar editando o `config.py` ou `constants.py` toda vez que queria mudar de fila. Fiz uma interfacezinha rápida (`gui.py`) com tema escuro pra selecionar o modo e dar Play.
*   **Filas**: Atualizei os IDs das filas (Co-op vs AI Intermediário mudou de ID, tive que caçar o novo).

## 🚀 Como botar pra rodar

É Python puro.
1.  Clona o repo.
2.  Instala as libs: `pip install -r requirements.txt`
3.  Roda a interface: `python gui.py`

**Dica de amigo**: Deixa o LoL em 1024x768 (Janela). O bot usa reconhecimento de imagem pra aceitar fila e tals, se mudar a resolução ele fica cego.

## ⚙️ Sobre o Gameplay

Eu deixei dois modos na interface:
1.  **Auto-Fila**: Só aceita a partida, picka e ajeita a role. Qunado o jogo começa, ele para. (É o que eu uso pra não tomar ban de script).
2.  **Gameplay Full**: A lógica original da Yuumi (ficar no ADC, curar, ultar). Eu **comentei** essa parte no código por segurança, mas se você quiser ativar, é só descomentar no `yuumi.py`. A estrutura tá toda lá funcionando.

## ⚠️ Aviso Legal (Disclaimer)

**Este projeto não é endossado pela Riot Games e não reflete as opiniões ou visões da Riot Games ou de qualquer pessoa oficialmente envolvida na produção ou gerenciamento do League of Legends. League of Legends e Riot Games são marcas comerciais ou marcas registradas da Riot Games, Inc. League of Legends © Riot Games, Inc.**

Este software interage com outros programas e serviços (League of Legends). Ao utilizá-lo, você assume total responsabilidade por quaisquer violações dos Termos de Serviço da Riot Games e por quaisquer consequências às contas utilizadas (incluindo suspensões ou banimentos permanentes). Você concorda em utilizar este software estritamente por sua própria conta e risco.

*Fork mantido por [TarikPac](https://github.com/tarikpac).*
