# Rough Mockups - Perguntas sobre UI e Fluxo

## Sources

- [desc] Initial description: "Chatbot de RH com Amazon Bedrock AgentCore Runtime, Bedrock Knowledge Bases + S3 Vectors, Strands Agents SDK e Streamlit. Ver vision.md e tech-env.md na raiz do workspace."
- [scope] Workflow-selected scope: `mvp`.

## Q1. Alem do chat central, quais elementos devem aparecer na tela?

- A. Somente o chat (titulo + historico + input + spinner enquanto responde). Interface minima, como no exemplo de `tech-env.md`.
- B. Chat + botao de "Limpar conversa / nova sessao" na sidebar
- C. Chat + seletor de modelo de chat na sidebar (para experimentacao ao vivo, referente a B-5 do intent-backlog.md)
- D. Chat + botao de limpar + seletor de modelo (B + C)
- X. Other (please specify)

[Answer]:A, B, C, D

## Q2. Como o chatbot deve indicar o documento fonte na resposta?

- A. Ao final da resposta, em texto simples: "Fonte: employee_handbook.pdf".
- B. Como link/citacao inline no texto da resposta.
- C. Nao mostrar fonte na UI - deixar so no prompt de sistema (indicativo interno).
- D. Not yet defined.
- X. Other (please specify)

[Answer]:C

## Q3. Como tratar erros e casos limite na UI?

- A. Mensagem de erro amigavel na propria bolha do chat ("Nao consegui responder agora. Tente reformular ou contate o RH."); nao mostrar stack trace.
- B. Toast/banner de erro no topo da tela.
- C. Nao tratar - deixar o erro bruto do Streamlit aparecer.
- D. Not yet defined.
- X. Other (please specify)

[Answer]:A

## Q4. Qual form factor a interface deve suportar?

- A. Desktop (Chrome/Edge/Firefox modernos, resolucao >= 1024px) - suficiente para demo em notebook.
- B. Desktop + mobile responsive (Streamlit ja da isso por padrao mas com layout comprimido).
- C. Not yet defined.
- X. Other (please specify)

[Answer]:A

## Q5. Requisitos de acessibilidade?

- A. Streamlit padrao (HTML semantico basico, navegacao por teclado, contraste padrao). Sem certificacao WCAG formal para esta demo.
- B. Compliance WCAG 2.1 AA completo com screen reader.
- C. Sem requisito de acessibilidade especifico.
- D. Not yet defined.
- X. Other (please specify)

[Answer]:A

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
