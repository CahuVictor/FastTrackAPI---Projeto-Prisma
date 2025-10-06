# app\api\v1\endpoints\users.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from structlog import get_logger

from app.repositories.user import AbstractUserRepo
from app.schemas.user import UserInDB, UserCreate
from app.core.security import get_password_hash
from app.core.rate_limit_config import limiter
from app.utils.security import require_roles, auth_dep
from app.deps import provide_user_repo

_provide_user_repo = Depends(provide_user_repo)

logger = get_logger().bind(module="eventos")

router = APIRouter(
#     dependencies=[auth_dep]
    prefix="/users",
    tags=["users"],
)

@router.get(
    "/",
    summary="Lista todos os usuários",
    response_model=list[UserInDB],
    dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={
        200: {"description": "Usuários encontrados"},
        404: {"description": "Lista vazia"}
    },
)
@limiter.limit("10/minute")
def listar_usuarios(
    request: Request,  # ← Necessário para funcionar com @limiter.limit,
    repo: AbstractUserRepo = _provide_user_repo
):
    return repo.list_all()

@router.get(
    "/{username}",
    summary="Lista usuário específico",
    response_model=UserInDB,  # TODO Se tiver dois usuários com o mesmo nome, deveria retornar os 2?
    dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={
        200: {"description": "Usuário encontrado"},
        404: {"description": "Usuário não encontrado"}
    },
)
@limiter.limit("20/minute")
def buscar_usuario(
    request: Request,  # ← Necessário para funcionar com @limiter.limit,
    username: str,
    repo: AbstractUserRepo = _provide_user_repo
):
    user = repo.get_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@router.post(
    "/",
    summary="Adiciona usuário",
    response_model=UserInDB,
    dependencies=[auth_dep, Depends(require_roles("admin"))],
    responses={
        200: {"description": "Usuário adicionado"},
        400: {"description": "Usuário já existe"}
    },
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("20/minute")
def criar_usuario(
    request: Request,  # ← Necessário para funcionar com @limiter.limit,
    novo: UserCreate,
    repo: AbstractUserRepo = _provide_user_repo
):
    if repo.get_by_username(novo.username):
        raise HTTPException(status_code=400, detail="Usuário já existe")
    user = UserInDB(
        username=novo.username,
        full_name=novo.full_name,
        hashed_password=get_password_hash(novo.password),
        roles=novo.roles,
    )
    return repo.add(user)

@router.delete(
    "/{username}",
    summary="Adiciona usuário",
    dependencies=[auth_dep, Depends(require_roles("admin"))],
    responses={
        200: {"description": "Usuário deletado"},
        404: {"description": "Usuário não encontrado"}
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.limit("20/minute")
def remover_usuario(
    request: Request,  # ← Necessário para funcionar com @limiter.limit,
    username: str,
    repo: AbstractUserRepo = _provide_user_repo
):
    if not repo.delete_by_username(username):
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return None
