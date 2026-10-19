from fastapi import APIRouter

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/broken")
def broken_endpoint():
    return 1 / 0
