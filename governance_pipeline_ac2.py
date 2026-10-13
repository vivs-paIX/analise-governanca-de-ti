import csv
import os
from typing import List
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd


class DatabaseRelationalManager:
    """conexão do DB relacional, postgre nesse caso"""
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "5432"))
        self.database = os.getenv("DB_NAME", "it_governance_db")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "admin")

    def get_connection(self):
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.database,
            user=self.user,
            password=self.password
        )

    def initialize_relational_schema(self) -> None:
        """Chaves primárias e estrageiras para limpar os dados"""
        schema_query = """
        -- Tabela Dimensão: Departamentos
        CREATE TABLE IF NOT EXISTS dim_departments (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL
        );

        -- Tabela Dimensão: Status da Conta
        CREATE TABLE IF NOT EXISTS dim_account_statuses (
            id SERIAL PRIMARY KEY,
            status VARCHAR(50) UNIQUE NOT NULL
        );

        -- Tabela Dimensão: Níveis de Acesso SharePoint
        CREATE TABLE IF NOT EXISTS dim_sharepoint_access (
            id SERIAL PRIMARY KEY,
            access_level VARCHAR(50) UNIQUE NOT NULL
        );

        -- Tabela Dimensão: Status do Antivírus
        CREATE TABLE IF NOT EXISTS dim_antivirus_statuses (
            id SERIAL PRIMARY KEY,
            status VARCHAR(50) UNIQUE NOT NULL
        );

        -- Tabela Fato: Auditoria de Usuários Relacionada (AC2)
        CREATE TABLE IF NOT EXISTS fact_user_security_audits (
            id SERIAL PRIMARY KEY,
            user_name VARCHAR(255) NOT NULL,
            department_id INT REFERENCES dim_departments(id),
            account_status_id INT REFERENCES dim_account_statuses(id),
            sharepoint_access_id INT REFERENCES dim_sharepoint_access(id),
            antivirus_status_id INT REFERENCES dim_antivirus_statuses(id),
            is_governance_anomaly BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(schema_query)
        print("[INFO] Schema relacional normalizado inicializado com sucesso!")


class DataCleaningAndModelingPipeline:
    """Executa a limpeza e a carga."""
    def __init__(self, csv_file_path: str = "it_governance_audit.csv"):
        self.csv_file_path = csv_file_path
        self.db_manager = DatabaseRelationalManager()

    def clean_and_transform(self) -> pd.DataFrame:
        """remove duplicatas e trata registros com anomalias."""
        print("[INFO] Iniciando limpeza e tratamento dos dados...")
        df = pd.read_csv(self.csv_file_path)

        initial_count = len(df)
        df = df.drop_duplicates(subset=["name"]).reset_index(drop=True)
        print(f"[CLEAN] Removidas {initial_count - len(df)} duplicatas.")

        df = df.dropna(subset=["name", "department", "account_status", "sharepoint_access", "antivirus_status"])

        df['is_governance_anomaly'] = (df['account_status'] == 'Inativo') & (df['sharepoint_access'] == 'Owner')
        
        print(f"[CLEAN] Total de registros limpos e válidos para carga: {len(df)}")
        return df

    def load_to_relational_db(self, df: pd.DataFrame) -> None:
        """Insere os dados utilizando as chaves estrangeiras."""
        self.db_manager.initialize_relational_schema()
        
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                # Inserir Dimensões e mapear IDs
                def get_or_create_dimension(table, column, value):
                    cursor.execute(f"SELECT id FROM {table} WHERE {column} = %s", (value,))
                    res = cursor.fetchone()
                    if res:
                        return res[0]
                    cursor.execute(f"INSERT INTO {table} ({column}) VALUES (%s) RETURNING id", (value,))
                    return cursor.fetchone()[0]

                print("[INFO] Inserindo dados nas tabelas dimensionais e fato...")
                for _, row in df.iterrows():
                    dept_id = get_or_create_dimension("dim_departments", "name", row["department"])
                    acc_status_id = get_or_create_dimension("dim_account_statuses", "status", row["account_status"])
                    sp_access_id = get_or_create_dimension("dim_sharepoint_access", "access_level", row["sharepoint_access"])
                    av_status_id = get_or_create_dimension("dim_antivirus_statuses", "status", row["antivirus_status"])

                    insert_fact_query = """
                    INSERT INTO fact_user_security_audits 
                    (user_name, department_id, account_status_id, sharepoint_access_id, antivirus_status_id, is_governance_anomaly)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_fact_query, (
                        row["name"],
                        dept_id,
                        acc_status_id,
                        sp_access_id,
                        av_status_id,
                        row["is_governance_anomaly"]
                    ))
        print("[SUCCESS] Carga concluída com sucesso!")

    def run(self):
        df_cleaned = self.clean_and_transform()
        self.load_to_relational_db(df_cleaned)


if __name__ == "__main__":
    pipeline = DataCleaningAndModelingPipeline()
    pipeline.run()
