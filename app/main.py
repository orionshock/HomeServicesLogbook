from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root() -> str:
    return "Home Services Logbook running"
