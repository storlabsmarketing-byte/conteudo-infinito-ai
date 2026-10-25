# Motor editorial externo do Espúrio

Produção em GitHub Actions usando Gemini, pesquisa Google e geração de imagens, sem chamar o ChatGPT ou a API OpenAI.

## Estado e ativação
O motor e o receptor no Sites estão implementados. O teste integrado com a chave real é obrigatório antes de habilitar a agenda externa e desativar a rotina anterior. O workflow roda em modo verify no push da implementação para main. Verify gera o pacote completo e valida a identidade e o conteúdo no Sites, sem publicar um segundo artigo no mesmo dia.

## Configuração
Segredo obrigatório: ESPURIO_GEMINI_API_KEY.
Variáveis opcionais: ESPURIO_GEMINI_MODEL (default gemini-2.5-flash) e ESPURIO_IMAGE_MODEL (default gemini-2.5-flash-image).
Modelos, pesquisa, imagens e minutos do Actions têm cotas/custos próprios. Não há promessa de gratuidade.
A chave nunca entra no código, pacote ou logs. Credenciais temporárias do Sites não são copiadas ao GitHub.

## Fluxo
1. Ler estado público e RSS. Se já existe artigo do dia em modo publish, encerrar antes de gerar.
2. Pesquisar com grounding atual e exigir ao menos duas fontes.
3. Redigir JSON e auditar as afirmações contra as evidências.
4. Gerar capa usando o modelo visual aprovado como referência e duas imagens internas novas.
5. Otimizar JPEGs, incluir alt e legendas, slug e meta descrição.
6. Obter JWT OIDC temporário do GitHub. O Sites verifica assinatura, audiência, IDs do repositório e proprietário, branch main e caminho do workflow.
7. Validar o pacote. Em publish, inserir artigo e imagens atomicamente em D1.
8. Ler página, imagens, CTA, RSS e sitemap. Falha de leitura não declara sucesso; retry encontra o artigo já persistido.

## Publicação
Destino https://oespurio.com.br/api/blog/editorial.
O receptor só é habilitado com BLOG_EDITORIAL_ENABLED=true no Sites.
Permite um artigo por data de Brasília, sem substituir posts existentes. Push pode validar, mas não publicar.
As páginas mantêm tema branco, títulos dourados, texto preto, autoria O Espúrio.
Os artigos novos entram na listagem e nos metadados, RSS e sitemap sem novo deploy.
O envio de e-mail depende separadamente do provedor da newsletter.

## Execução
Workflow manual: verify ou publish.
Agenda preparada: 12:30 UTC, equivalente a 09:30 de Brasília. GitHub Actions pode atrasar; não garante horário exato.
A agenda será liberada após teste integrado. Não operar duas rotinas de geração simultaneamente.
Os artefatos incluem pacote, evidências, auditoria, imagens e resultado; são mantidos por 14 dias.
Não são enviados a redes sociais.

## Validação
Quatro testes Python validam metadados, estado, duplicatas, evidências e CTA.
No Sites, testes verificam assinatura OIDC, escopos, payload, inserção atômica, rollback e idempotência.
A auditoria por IA reduz erros, mas não garante veracidade: mantenha acompanhamento editorial e pause o envio se necessário.

Referências técnicas: https://docs.github.com/en/actions/reference/security/oidc
https://ai.google.dev/api/generate-content
https://ai.google.dev/gemini-api/docs/generate-content/google-search
https://ai.google.dev/gemini-api/docs/generate-content/image-generation
https://github.com/blader/humanizer
