# db.py
import os
import json
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager

DATABASE_URL = os.getenv("DATABASE_URL")

# Cria pool de conexões
pool = SimpleConnectionPool(1, 10, dsn=DATABASE_URL)

@contextmanager
def get_conn():
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)

class CommitRepository:
    @staticmethod
    def insert_commit(conn, commit_sha, repo, author):
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO public.commits (commit_sha, repo, author_hkey, committed_at)
                VALUES (%s, %s, %s, now())
                ON CONFLICT (commit_sha) DO NOTHING
                """,
                (commit_sha, repo, author)
            )

class ScoreRepository:
    @staticmethod
    def upsert_score(conn, commit_sha, repo, author, sqc, subnotes, rationale):
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO public.scores (commit_sha, repo, author_hkey, sqc, subnotes, rationale, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, now())
                ON CONFLICT (commit_sha) DO UPDATE
                SET sqc = EXCLUDED.sqc,
                    subnotes = EXCLUDED.subnotes,
                    rationale = EXCLUDED.rationale,
                    created_at = now()
                """,
                (commit_sha, repo, author, sqc, json.dumps(subnotes), rationale)
            )

def save_score(commit_sha, repo, author, subnotes, rationale, sqc):
    with get_conn() as conn:
        try:
            CommitRepository.insert_commit(conn, commit_sha, repo, author)
            ScoreRepository.upsert_score(conn, commit_sha, repo, author, sqc, subnotes, rationale)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
