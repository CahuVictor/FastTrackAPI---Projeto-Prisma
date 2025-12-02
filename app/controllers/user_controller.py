# app\api\v1\endpoints\user_controller.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status, Request
from structlog import get_logger

from app.core.rate_limit_config import limiter

from app.core.deps import provide_user_service
from app.schemas.user.user_create import UserCreate
from app.schemas.user.user_update import UserUpdate
from app.schemas.user.user_view import UserView
from app.schemas.common.common import MessageResponse
from app.models.user import User
from app.services.user_service import ( # user_service
    UserService,
    UserAlreadyExistsError,
    UserNotFoundError,
)

from app.utils.security import require_roles, auth_dep # TODO Essas funções deveriam estar em úteis, elas usam classes da camada service

_provide_user_service = Depends(provide_user_service)

logger = get_logger().bind(module="users")

router = APIRouter(
    prefix="/users",
    tags=["users"],
    # dependencies=[auth_dep]
)


# ------------------------------------------------------------------ #
# Helper methods for common actions
# ------------------------------------------------------------------ #
def _to_user_view(user: User) -> UserView:
    """
    Convert a domain User entity into a UserView response model.

    If audit timestamps are not available (e.g., in-memory repository),
    they are filled with the current UTC timestamp.
    """
    return UserView(
        id=user.id,  # type: ignore[arg-type]
        username=user.username,
        full_name=user.full_name,
        hashed_password=user.hashed_password,
        roles=user.roles,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
    
def _from_user_view(view: UserView) -> User:
    """
    Convert a UserView (typically from the HTTP layer) back to a
    domain User entity.

    This helper is not being used yet, but can be helpful if, in the
    future, we accept user payloads in this format on write operations.
    """
    return User(
        id=view.id,  # ID will be enforced by the service/repository layer.
        username=view.username,
        full_name=view.full_name,
        hashed_password=view.hashed_password,
        roles=view.roles,
        created_at=view.created_at,
        updated_at=view.updated_at,
    )


@router.get(
    "/",
    summary="Lista todos os usuários",
    response_model=list[UserView],
    dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={
        200: {"description": "Usuários encontrados"},
        404: {"description": "Lista vazia"},
    },
)
# @limiter.limit("10/minute")
def listar_usuarios(
    request: Request,  # Necessário para funcionar com @limiter.limit
    service: UserService = _provide_user_service,
) -> UserView:
    """
    Endpoint que lista todos os usuários cadastrados.

    Delegamos a lógica de negócio para o UserService, mantendo o
    controller focado apenas em HTTP (status codes, respostas, etc.).
    """
    users = service.list_users()
    if not users:
        # Opcional: você pode optar por retornar [] com 200, dependendo da sua API.
        logger.info("Nenhum usuário encontrado")
    return [_to_user_view(user) for user in users]


@router.get(
    "/{username}",
    summary="Lista usuário específico",
    response_model=UserView,  # TODO Se tiver dois usuários com o mesmo nome, deveria retornar os 2?
    dependencies=[auth_dep, Depends(require_roles("admin", "editor"))],
    responses={
        200: {"description": "Usuário encontrado"},
        404: {"description": "Usuário não encontrado"},
    },
)
# @limiter.limit("20/minute")
def buscar_usuario(
    request: Request,  # Necessário para funcionar com @limiter.limit
    username: str,
    service: UserService = _provide_user_service,
) -> UserView:
    """
    Endpoint que busca um usuário a partir do username.

    O service levanta UserNotFoundError, que aqui é traduzido para
    um HTTP 404 (HTTPException).
    """
    try:
        user=service.get_user_by_username(username)
        return _to_user_view(user)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="Usuário não encontrado") from None
    


@router.post(
    "/",
    summary="Adiciona usuário",
    response_model=UserView,
    dependencies=[auth_dep, Depends(require_roles("admin"))],
    responses={
        201: {"description": "Usuário adicionado"},
        400: {"description": "Usuário já existe"},
    },
    status_code=status.HTTP_201_CREATED,
)
# @limiter.limit("20/minute")
def criar_usuario(
    request: Request,  # Necessário para funcionar com @limiter.limit
    payload: UserCreate,
    service: UserService = _provide_user_service,
) -> UserView:
    """
    Endpoint responsável por criar um novo usuário.

    Regras de negócio (verificação de duplicidade, hash de senha) são
    aplicadas no UserService.
    """
    try:
        user = service.create_user(payload)
        return _to_user_view(user)
    except UserAlreadyExistsError:
        raise HTTPException(status_code=400, detail="Usuário já existe") from None


@router.delete(
    "/{username}",
    summary="Remove usuário",
    dependencies=[auth_dep, Depends(require_roles("admin"))],
    responses={
        204: {"description": "Usuário deletado"},
        404: {"description": "Usuário não encontrado"},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
# @limiter.limit("20/minute")
def remover_usuario(
    request: Request,  # Necessário para funcionar com @limiter.limit
    username: str,
    service: UserService = _provide_user_service,
):
    """
    Endpoint que remove um usuário pelo username.

    Se o usuário não for encontrado, retornamos 404.
    """
    try:
        service.delete_user(username)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="Usuário não encontrado") from None
    return None
