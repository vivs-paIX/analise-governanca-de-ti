import csv
import os
import random
from dataclasses import dataclass
from typing import List
from faker import Faker
import psycopg2
from psycopg2.extras import execute_values


@dataclass
class UserSecurityRecord:
    name: str
    department: str
    account_status: str
    sharepoint_access: str
    antivirus_status: str


class SyntheticDataGenerator:
    DEPARTMENTS = ["TI", "RH", "Financeiro", "Operações", "Marketing", "Vendas"]
    ACCOUNT_STATUSES = ["Ativo", "Inativo"]
    SHAREPOINT_ACCESS_LEVELS = ["Visitante", "Membro", "Owner"]
    ANTIVIRUS_STATUSES = ["Atualizado", "Quarentena"]

    def __init__(self, locale: str = "pt_BR"):
        self.faker = Faker(locale)

    def generate_records(self, count: int = 500, anomaly_rate: float = 0.08) -> List[UserSecurityRecord]:
        records = []
        for _ in range(count):
            status = random.choice(self.ACCOUNT_STATUSES)
            
            if status == "Inativo" and random.random() < anomaly_rate:
                access = "Owner"
                av_status = random.choice(self.ANTIVIRUS_STATUSES)
            elif status == "Inativo":
                access = random.choice(["Visitante", "Membro"])
                av_status = random.choice(self.ANTIVIRUS_STATUSES)
            else:
                access = random.choice(self.SHAREPOINT_ACCESS_LEVELS)
                av_status = random.choice(self.ANTIVIRUS_STATUSES)

            record = UserSecurityRecord(
                name=self.faker.name(),
                department=random.choice(self.DEPARTMENTS),
                account_status=status,
                sharepoint_access=access,
                antivirus_status=av_status
            )
            records.append(record)
        return records


class CsvRepository:
    FIELDNAMES = ["name", "department", "account_status", "sharepoint_access", "antivirus_status"]

    @classmethod
    def export(cls, records: List[UserSecurityRecord], file_path: str) -> None:
        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=cls.FIELDNAMES)
            writer.writeheader()
            for record in records:
                writer.writerow(record.__dict__)

    @classmethod
    def import_records(cls, file_path: str) -> List[UserSecurityRecord]:
        records = []
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                records.append(UserSecurityRecord(**row))
        return records


class PostgresDatabaseManager:
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

    def initialize_schema(self) -> None:
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_security_audits (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            department VARCHAR(100) NOT NULL,
            account_status VARCHAR(50) NOT NULL,
            sharepoint_access VARCHAR(50) NOT NULL,
            antivirus_status VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_table_query)

    def insert_records(self, records: List[UserSecurityRecord]) -> None:
        insert_query = """
        INSERT INTO user_security_audits (name, department, account_status, sharepoint_access, antivirus_status)
        VALUES %s
        """
        values = [
            (r.name, r.department, r.account_status, r.sharepoint_access, r.antivirus_status)
            for r in records
        ]
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                execute_values(cursor, insert_query, values)


class GovernanceDataPipeline:
    def __init__(self, csv_file_path: str = "it_governance_audit.csv"):
        self.csv_file_path = csv_file_path
        self.generator = SyntheticDataGenerator()
        self.db_manager = PostgresDatabaseManager()

    def run(self, record_count: int = 1000) -> None:
        records = self.generator.generate_records(count=record_count)
        CsvRepository.export(records, self.csv_file_path)
        imported_records = CsvRepository.import_records(self.csv_file_path)
        self.db_manager.initialize_schema()
        self.db_manager.insert_records(imported_records)


if __name__ == "__main__":
    pipeline = GovernanceDataPipeline()
    pipeline.run(record_count=1000)