import os

import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)


def get_secret(secret_name, default=None):
    """
    Read a secret from a Podman/Kubernetes-style secret file.

    Falls back to an environment variable for local development.
    """
    secret_path = f"/run/secrets/{secret_name}"

    if os.path.exists(secret_path):
        with open(secret_path, "r", encoding="utf-8") as secret_file:
            return secret_file.read().strip()

    return os.getenv(secret_name.upper(), default)


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "mydb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = get_secret("db_password", os.getenv("DB_PASS", "password"))


def get_db_connection():
    """Create a PostgreSQL connection."""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        connect_timeout=5,
    )


@app.route("/")
def index():
    return jsonify(
        {
            "status": "OK",
            "service": "secure-flask-microservice",
            "message": "Flask Microservice Running",
        }
    )


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "healthy",
            "service": "secure-flask-microservice",
        }
    )


@app.route("/ready")
def readiness():
    """
    Verify that the application can reach PostgreSQL.
    """
    try:
        conn = get_db_connection()
        conn.close()

        return jsonify(
            {
                "status": "ready",
                "database": "available",
            }
        ), 200

    except Exception:
        return jsonify(
            {
                "status": "not_ready",
                "database": "unavailable",
            }
        ), 503


@app.route("/data")
def database_info():
    """
    Return PostgreSQL version information.
    """
    conn = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return jsonify(
            {
                "status": "OK",
                "database": db_version,
            }
        )

    except Exception as error:
        if conn:
            conn.close()

        app.logger.error("Database request failed: %s", error)

        return jsonify(
            {
                "status": "error",
                "message": "Database connection failed",
            }
        ), 503


@app.route("/users")
def users():
    """
    Return application users stored in PostgreSQL.
    """
    conn = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, username, email, created_at
            FROM users
            ORDER BY id;
            """
        )

        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(
            {
                "status": "OK",
                "count": len(rows),
                "users": [
                    {
                        "id": row[0],
                        "username": row[1],
                        "email": row[2],
                        "created_at": row[3].isoformat(),
                    }
                    for row in rows
                ],
            }
        )

    except Exception as error:
        if conn:
            conn.close()

        app.logger.error("User query failed: %s", error)

        return jsonify(
            {
                "status": "error",
                "message": "Unable to retrieve users",
            }
        ), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
