from fastapi import FastAPI, Request
import psycopg2
import os

app = FastAPI()
DATA_FILE = "/data/notas.txt" 
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS notas(id SERIAL PRIMARY KEY, contenido TEXT)"
        )
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Tabla notas creada o ya existía")
    except Exception as e:
        print(str(e))


@app.post("/nota")
async def guardar_nota(request: Request):
    try:
        nota = (await request.body()).decode()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO notas (contenido) VALUES (%s) RETURNING id",
            (nota, )
        )
        nota_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        with open(DATA_FILE, "a", encoding="utf-8") as f:
            f.write(f"{nota.replace("\n", "\\n")}\n")

        return {"message": "Nota guardada correctamente", "id": nota_id}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def leer_notas():
    if not os.path.exists(DATA_FILE):
        return {"notas": []}

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        lineas = f.read().splitlines()

    notas = [linea.replace("\\n", "\n") for linea in lineas]
    return {"notas": notas}

@app.get("/notas-db")
async def leer_notas_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, contenido FROM notas ORDER BY id DESC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        notas = [{"id": row[0], "contenido": row[1]} for row in rows]
        return {"notas": notas}
    except Exception as e:
        return {"error": str(e)}


@app.get("/conteo")
def contar_notas():
    return len(leer_notas()["notas"])

@app.get("/autor")
def get_autor():
    return os.getenv('AUTOR')

@app.on_event("startup")
def startup_event():
    print("Starting up...")
    init_db()