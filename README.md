# Análise de Governança de TI
Projeto de BI e Governança de TI - Análise de gestão de identidades e acessos.

### AC1: Extração e Ingestão (Concluída)
- Script (`governance_pipeline.py`) construído para simular a extração de logs de infraestrutura (identidades, acessos e endpoints).
- Ingestão automatizada e estruturada em banco de dados PostgreSQL.

## AC2: Limpeza e Modelagem Relacional (Concluído)
* **Script (`governance_pipeline_ac2.py`):** Desenvolvido para realizar a limpeza automatizada dos dados brutos, incluindo remoção de duplicatas por nome e tratamento de registros inválidos.
* **Modelagem Relacional (PostgreSQL):** Criação de um esquema normalizado contendo tabelas dimensionais (`dim_departments`, `dim_account_statuses`, `dim_sharepoint_access`, `dim_antivirus_statuses`) e a tabela fato (`fact_user_security_audits`) interligadas por **Chaves Primárias e Estrangeiras (PK/FK)**.
* **Regra de Governança e Conformidade:** Identificação automatizada de anomalias críticas (ex: contas inativas que mantêm privilégios de acesso `Owner` no SharePoint) para auditoria de segurança.

## AC3: Dashboard MVP - Gestão de Identidades (Concluído)
* **Integração BI e SGBD:** Conexão direta do Power BI ao PostgreSQL utilizando uma View otimizada (`vw_dashboard_identidades`) para performance e agilidade.
* **Indicadores Executivos (KPI Cards):** Cartões de resumo evidenciando o *Total de Usuários*, *Usuários Ativos* e *Usuários Inativos*.
* **Análise Demográfica e Organizacional:** Gráfico de barras horizontais apresentando a distribuição volumétrica de colaboradores por departamento.
* **Monitoramento do Ciclo de Vida:** Gráfico de rosca segmentando o status das contas corporativas.
* **Painel de Auditoria de Acessos (SharePoint Owners):** Tabela interativa dedicada à listagem de administradores de coleções de sites, permitindo a verificação rápida de privilégios elevados.

## Entrega Final: Matriz de Risco, Alertas e Documentação Arquitetural (Concluído)
- **Score e Nível de Risco de Governança:** Cruzamento de status de conta, privilégios no SharePoint e saúde de endpoint para calcular a pontuação de risco e classificar os registros por severidade.
- **Matriz de Risco e Alertas de Conformidade:** Visualizações analíticas e alertas para identificar departamentos e usuários com maior exposição a falhas de conformidade e privilégios excessivos.
- **Diagrama de Arquitetura:** Representação visual do fluxo ponta a ponta, da geração de dados sintéticos e limpeza/modelagem em Python até o armazenamento no PostgreSQL e a visualização no Power BI.
- **Diagrama Entidade-Relacionamento (MER):** Mapeamento da estrutura relacional do banco com chaves primárias (`PK`), chaves estrangeiras (`FK`) e cardinalidades entre a tabela fato e as tabelas dimensão.
