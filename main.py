from fastapi import FastAPI

APP = FastAPI()

@APP.get("/")
def index():
    return "Olá mundo !!!"