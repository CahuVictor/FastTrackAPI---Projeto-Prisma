# app\api\v1\api_router.py
from fastapi import APIRouter

from app.controllers import event_controller # , auth, events, users, admin_urls

router = APIRouter(prefix="/api/v1")

# router.include_router(auth.router)
router.include_router(event_controller.router)
# router.include_router(users.router)
# router.include_router(admin_urls.router)

# app.include_router(
#     eventos.router,
#     prefix="/api/v1",
#     dependencies=[Depends(get_current_user)],   #  ←  proteção em bloco
# )