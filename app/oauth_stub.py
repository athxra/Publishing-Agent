from fastapi import APIRouter

router = APIRouter()

@router.get('/oauth/google/authorize')
def google_authorize():
    return {"message": "Stub for OAuth - replace with actual implementation"}
