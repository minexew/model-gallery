import csv
import sqlite3

from pathlib import Path


def upsert(conn, table, key, kv):
    query = (
        f"INSERT INTO {table} ({', '.join(kv.keys())}) "
        f"VALUES ({', '.join(['?' for i in range(len(kv))])}) "
        f"ON CONFLICT({key}) DO UPDATE SET {', '.join([f'{key} = excluded.{key}' for key in kv.keys()])}"
    )
    # print(query)
    c = conn.cursor()
    c.execute(query, tuple(kv.values()))


class DB:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row

        c = self.conn.cursor()

        c.execute(
            """
            CREATE TABLE IF NOT EXISTS resource (
                    sha1 TEXT PRIMARY KEY,
                    path TEXT,
                    type TEXT
                    )
            """
        )

        self.conn.commit()

    def add_resource(self, **kwargs):
        kwargs["path"] = str(kwargs["path"])
        upsert(self.conn, "resource", "sha1", kwargs)

    def close(self):
        self.conn.commit()
        self.conn.close()

    def resources(self):
        c = self.conn.cursor()
        c.execute("SELECT DISTINCT resource.* FROM resource ORDER BY resource.path ASC")
        return c.fetchall()


class PreviewsDB:
    def __init__(self, path):
        self.conn = sqlite3.connect(str(path))
        self.conn.row_factory = sqlite3.Row

        c = self.conn.cursor()

        c.execute(
            """
            CREATE TABLE IF NOT EXISTS mbac_preview (
                    source TEXT NOT NULL,
                    filename TEXT,
                    width INT,
                    height INT,
                    thumb INT,
                    version INT NOT NULL,
                    axis_forward TEXT NOT NULL,
                    axis_up TEXT NOT NULL,
                    PRIMARY KEY (source, thumb)
                    )
            """
        )

        try:
            c.execute("ALTER TABLE mbac_preview ADD COLUMN axis_forward INT DEFAULT '-Z'")
            c.execute("ALTER TABLE mbac_preview ADD COLUMN axis_up INT DEFAULT 'Y'")
        except sqlite3.OperationalError:
            pass

        try:
            c.execute("ALTER TABLE mbac_preview ADD COLUMN filename TEXT DEFAULT NULL")
            c.execute("ALTER TABLE mbac_preview ADD COLUMN width INT DEFAULT NULL")
            c.execute("ALTER TABLE mbac_preview ADD COLUMN height INT DEFAULT NULL")
        except sqlite3.OperationalError:
            pass

        self.conn.commit()

    def add_mbac_preview(self, **kwargs):
        upsert(self.conn, "mbac_preview", "source, thumb", kwargs)
        self.conn.commit()

    def close(self):
        self.conn.commit()
        self.conn.close()

    def get_mbac_preview(self, source, thumb):
        c = self.conn.cursor()
        c.execute("SELECT * FROM mbac_preview WHERE source = ? AND thumb = ?", (source, thumb))
        return c.fetchone()
