# Análise de Governança de TI
Projeto de BI e Governança de TI - Análise de gestão de identidades e acessos.

### AC1: Extração e Ingestão (Concluída)
- Script (`governance_pipeline.py`) construído para simular a extração de logs de infraestrutura (identidades, acessos e endpoints).
- Ingestão automatizada e estruturada em banco de dados PostgreSQL.

## AC2: Limpeza e Modelagem Relacional (Concluído)
* **Script (`governance_pipeline_ac2.py`):** Desenvolvido para realizar a limpeza automatizada dos dados brutos, incluindo remoção de duplicatas por nome e tratamento de registros inválidos.
* **Modelagem Relacional (PostgreSQL):** Criação de um esquema normalizado contendo tabelas dimensionais (`dim_departments`, `dim_account_statuses`, `dim_sharepoint_access`, `dim_antivirus_statuses`) e a tabela fato (`fact_user_security_audits`) interligadas por **Chaves Primárias e Estrangeiras (PK/FK)**.
* **Regra de Governança e Conformidade:** Identificação automatizada de anomalias críticas (ex: contas inativas que mantêm privilégios de acesso `Owner` no SharePoint) para auditoria de segurança.
