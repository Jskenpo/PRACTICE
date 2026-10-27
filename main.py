from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from time import perf_counter

#from routes import testrouter, conversation_router, agents_router, admin_router, users_router

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




app.include_router(testrouter.router, prefix="/test", tags=["test"])

app.include_router(conversation_router, prefix="/conversations", tags=["conversations"])

app.include_router(agents_router, prefix="/agents", tags=["agents"])

app.include_router(admin_router, prefix="/admin", tags=["admin"])

app.include_router(users_router, prefix="/users", tags=["users"])




if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )