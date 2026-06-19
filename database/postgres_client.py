import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(os.getenv("NEON_DATABASE_URL"))

def initialize_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS requirements (
            id SERIAL PRIMARY KEY,
            mongo_id VARCHAR(100) UNIQUE,
            title VARCHAR(500),
            submitted_by VARCHAR(200),
            department VARCHAR(200),
            role VARCHAR(200),
            status VARCHAR(50) DEFAULT 'Submitted',
            priority VARCHAR(50),
            moscow VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_stories (
            id SERIAL PRIMARY KEY,
            requirement_id INTEGER REFERENCES requirements(id),
            story TEXT,
            acceptance_criteria TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS status_audit (
            id SERIAL PRIMARY KEY,
            requirement_id INTEGER REFERENCES requirements(id),
            old_status VARCHAR(50),
            new_status VARCHAR(50),
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS conflicts (
            id SERIAL PRIMARY KEY,
            requirement_id INTEGER REFERENCES requirements(id),
            conflicting_requirement_id INTEGER REFERENCES requirements(id),
            conflict_description TEXT,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

def insert_requirement(mongo_id, title, submitted_by, department, role, priority, moscow):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO requirements (mongo_id, title, submitted_by, department, role, priority, moscow)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (mongo_id, title, submitted_by, department, role, priority, moscow))
    req_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return req_id

def insert_user_stories(requirement_id, stories):
    conn = get_connection()
    cur = conn.cursor()
    for story in stories:
        cur.execute("""
            INSERT INTO user_stories (requirement_id, story, acceptance_criteria)
            VALUES (%s, %s, %s)
        """, (requirement_id, story["story"], story["acceptance_criteria"]))
    conn.commit()
    cur.close()
    conn.close()

def insert_conflict(requirement_id, conflicting_id, description):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO conflicts (requirement_id, conflicting_requirement_id, conflict_description)
        VALUES (%s, %s, %s)
    """, (requirement_id, conflicting_id, description))
    conn.commit()
    cur.close()
    conn.close()

def update_status(requirement_id, new_status, old_status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE requirements SET status = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
    """, (new_status, requirement_id))
    cur.execute("""
        INSERT INTO status_audit (requirement_id, old_status, new_status)
        VALUES (%s, %s, %s)
    """, (requirement_id, old_status, new_status))
    conn.commit()
    cur.close()
    conn.close()

def get_all_requirements():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.id, r.mongo_id, r.title, r.submitted_by, r.department,
               r.role, r.status, r.priority, r.moscow, r.created_at,
               COUNT(us.id) as story_count
        FROM requirements r
        LEFT JOIN user_stories us ON r.id = us.requirement_id
        GROUP BY r.id
        ORDER BY r.created_at DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_requirement_with_stories(requirement_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM requirements WHERE id = %s", (requirement_id,))
    req = cur.fetchone()
    cur.execute("SELECT * FROM user_stories WHERE requirement_id = %s", (requirement_id,))
    stories = cur.fetchall()
    cur.execute("SELECT * FROM status_audit WHERE requirement_id = %s ORDER BY changed_at DESC", (requirement_id,))
    audit = cur.fetchall()
    cur.close()
    conn.close()
    return req, stories, audit

def get_all_for_traceability():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.id, r.title, r.submitted_by, r.department, r.status,
               r.priority, r.moscow, us.story, us.acceptance_criteria
        FROM requirements r
        LEFT JOIN user_stories us ON r.id = us.requirement_id
        ORDER BY r.id
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows