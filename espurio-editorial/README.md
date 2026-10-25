# Espúrio Editorial Externo

Estado: implementação de preparação editorial. NÃO é uma substituição ativa da publicação diária.

## O que está implementado
- Execução fora do ChatGPT, em GitHub Actions, com Python sem dependências externas.
- Pesquisa atual com Google Search grounding, geração estruturada com Gemini e auditoria separada.
- Consulta do RSS real para evitar títulos e slugs duplicados. Falha de leitura interrompe execução.
- Autoria O Espúrio, Investidor Legionário, linha editorial e CTA do projeto.
- Slug, título SEO, meta descrição, fontes, corpo em blocos compatíveis com o Site e direção de três imagens.
- Validações e quatro testes automatizados.
- Saída sempre draft. Nenhuma escrita no site, nenhum envio de email, nenhuma credencial no repositório.

## Ativação da preparação
1. Mesclar esta branch após revisão.
2. Em GitHub Settings / Secrets and variables / Actions, cadastrar o segredo ESPURIO_GEMINI_API_KEY.
3. Cadastrar a variável ESPURIO_GEMINI_MODEL com um modelo habilitado nessa conta que suporte generateContent e Google Search.
4. Cadastrar ESPURIO_EXTERNAL_ENABLED=true.
5. Executar manualmente o workflow e conferir o artefato. Nenhuma chamada paga foi executada durante a implementação.

Agendamento preparado: 12:30 UTC, equivalente a 09:30 em Brasília. GitHub Actions pode atrasar execuções, não garante horário exato. A chave do Site não é copiada nem reaproveitada aqui.
As chamadas Gemini, pesquisa e minutos de Actions dependem das cotas e preços das respectivas contas. Não consomem o plano ChatGPT quando executadas externamente. Não há promessa de gratuidade.

## O que falta para substituir a rotina atual
- Credencial Gemini cadastrada no GitHub e teste real da geração.
- Geração/exportação das imagens finais com o modelo aprovado, incluindo moeda original.
  Os prompts de imagem não substituem arquivos finais.
- Integração autenticada de importação/publicação no Sites. A hospedagem atual usa um repositório gerenciado,
  não este GitHub. Um commit aqui não publica o Site.
- Persistência de publicação por data/slug no destino, teste de retries e leitura da página pública, imagens,
  CTA, RSS e sitemap.
- Somente após o fluxo completo ser testado, desativar a automação ChatGPT para evitar publicações duplas.

Não persistir as credenciais curtas do Sites como segredo permanente. Não criar endpoint de escrita público.
Não ativar publicação baseada apenas na aprovação do modelo. A auditoria reduz erros, não garante veracidade.
A evidência completa fica no artefato para revisão; dados de clientes e segredos nunca entram no pacote.

## Testes locais
python -m unittest discover -s espurio-editorial -p test_engine.py

## Referências consultadas
https://docs.github.com/en/actions/how-tos/troubleshoot-workflows
https://ai.google.dev/gemini-api/docs/generate-content/google-search
https://ai.google.dev/api/generate-content
https://github.com/blader/humanizer

Consulta técnica: 25 de outubro de 2026. Humanizer orienta revisão editorial; não é um modelo de IA nem elimina custos de inferência.
