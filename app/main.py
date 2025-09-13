from fastapi import FastAPI, Request
import os

app = FastAPI()
DATA_FILE = "/data/notas.txt"

@app.post("/nota")
async def guardar_nota(request: Request):
    nota = await request.body()
    with open(DATA_FILE, "a") as f:
        f.write(nota.decode().replace("\n", "\\n") + "\n")
    return {"status": "Nota saved"}

@app.get("/")
def leer_notas():
    if not os.path.exists(DATA_FILE):
        return {"notas": []}

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        lineas = f.read().splitlines()

    notas = [linea.replace("\\n", "\n") for linea in lineas]
    return {"notas": notas}

@app.get("/conteo")
def contar_notas():
    return len(leer_notas()["notas"])
