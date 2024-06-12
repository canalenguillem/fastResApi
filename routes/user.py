from fastapi import APIRouter

user=APIRouter()


@user.get("/users")
def helloWorld():
    return {"message": "Hello users"}