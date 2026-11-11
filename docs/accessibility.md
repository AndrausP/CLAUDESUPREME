# Acessibilidade e compatibilidade de terminal

## Contraste e cor

O tema parte de `#0C0C0C`. `#BAF3DB` tem contraste alto e pode ser texto/acento. `#C9372C` é obrigatório como sinal de erro, mas não deve ser usado como único texto pequeno sobre o fundo: combine borda/token vermelho com `#F2F2F2` e o rótulo `FALHA`.

Tokens:

- texto primário: `#F2F2F2`;
- texto secundário: `#A7A7A7`;
- borda funcional: `#6B6B6B`;
- foco/acento/sucesso: `#BAF3DB`;
- erro: `#C9372C` + texto primário;
- alerta: `#F5C35B`;
- informação: `#8AB4F8`.

Nenhuma informação depende de cor. Status sempre inclui token ASCII e rótulo.

## Teclado

| Tecla | Comportamento |
|---|---|
| `Tab` / `Shift+Tab` | próximo/anterior controle interativo |
| setas ou `j`/`k` | mover seleção em listas |
| `Enter` | abrir detalhe/confirmar ação não destrutiva |
| `Esc` | limpar busca ou voltar um nível |
| `/` | focar busca |
| `?` | abrir ajuda contextual |
| `1`–`7` | navegar para seção |
| `q` | sair da TUI; nunca cancelar task |

Ações destrutivas não possuem atalho de uma tecla. O foco inicial de diálogo fica em `Cancelar`.

## Leitores de tela

- Preferir renderer estático quando `ORCHESTRA_ACCESSIBLE=1` ou quando o usuário solicitar `--plain`.
- Títulos precedem conteúdo e não dependem de posição visual.
- Atualizações assíncronas são linhas textuais estáveis; não redesenhar a tela inteira em alta frequência.
- Tabelas têm versão linear `campo: valor` em `--plain`.
- Indicadores visuais usam rótulos completos (`Bloqueado`, `Falha`, `Concluído`).
- Não usar arte ASCII decorativa, emojis ou animação como informação.

## Redução de movimento

Não há animações obrigatórias. Textual pode atualizar estado sem transições. Em `ORCHESTRA_REDUCE_MOTION=1`, desabilitar spinner e refresh periódico visual; atualizar somente em evento ou comando explícito.

## Encoding

- Arquivos, banco e JSONL: UTF-8.
- `--json`: UTF-8 válido, sem transliteração de conteúdo.
- Console interativa CP850: renderer baseline usa ASCII nos tokens e deve substituir apenas glifos não renderizáveis na apresentação.
- Não alterar `chcp` globalmente nem exigir Windows Terminal.
- Dados originais permanecem íntegros mesmo quando a console mostra fallback.

## Resize e overflow

- >=120 colunas: três regiões.
- 80–119: lista ou detalhe, nunca ambos comprimidos.
- <80 ou altura <24: snapshot estático paginável pelo terminal.
- Textos longos truncados visualmente têm acesso ao conteúdo integral no detalhe e em `--json`.
- Status, motivo de bloqueio, próxima ação e ID nunca são colunas descartáveis.

## Checklist de QA

- Testar PowerShell, CMD, Windows Terminal e stdout redirecionado.
- Testar `TERM=dumb`, `NO_COLOR=1`, `ORCHESTRA_ACCESSIBLE=1` e `ORCHESTRA_REDUCE_MOTION=1`.
- Testar teclado sem mouse, inclusive retorno de diálogo.
- Validar foco após atualização, erro e fechamento de detalhe.
- Verificar que códigos ANSI não aparecem em logs/JSON.
- Verificar significado dos status em escala de cinza.
- Validar microcopy de persistência: solicitado != gravado != validado != concluído.

