from fastapi.params import Body
from worker.tasks import send_verification_mail
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from rejson import Path, Client
from utils.client import get_redis_client
import os


class User(BaseModel):
    '''
    Model representing one user json document.
    '''
    email: str
    district: int
    verified: Optional[bool] = False
    code: Optional[str] = None
    session_ids: Optional[List[int]]


app = FastAPI()

@app.post("/users/register")
async def register_users(user: User):
    '''
    Register users and push a task to send a verfication mail.
    '''
    redis_client = get_redis_client()
    code = os.urandom(3).hex()
    user.code = code
    district = str(user.district)
    user.session_ids = []
    obj = dict(user)
    path = f'["{user.email}"]'
    redis_client.jsonset('users', Path(path), obj)
    send_verification_mail.delay(user.email, code)
    # Populate the district to users mapping accordingly.
    if redis_client.jsontype("districts", Path(f'["{district}"]')) is None:
        redis_client.jsonset("districts", Path(f'["{district}"]'), [])
    redis_client.jsonarrappend("districts", Path(f'["{district}"]'), user.email)
    return JSONResponse({"success": True}, status_code=201)


@app.post("/users/verify")
async def verify_user(code: str = Body(...), email: str = Body(...)):
    '''
    Verify the code for a user.
    '''
    redis_client = get_redis_client()
    user = redis_client.jsonget('users', Path(f'["{email}"]'))
    if user['code'] == code:
        redis_client.jsonset('users', Path(f'["{email}"]["verified"]'), True)
        return {"verified": True}
    return JSONResponse({"verified": False}, status_code=401)
