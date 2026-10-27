from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from time import perf_counter

from app.routes import auth_routes, products_routes
load_dotenv()

app = FastAPI(
    title="AI Agent, Backend Documentation",
)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(products_routes.router, prefix="/products", tags=["Products"])
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )
