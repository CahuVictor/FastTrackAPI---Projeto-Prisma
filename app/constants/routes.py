# app/constants/routes.py

API_V1_PREFIX = "/api/v1"

# Eventos
EVENTS_PREFIX = f"{API_V1_PREFIX}/events"
EVENTS_LOCAL_INFO_ROUTE = f"{EVENTS_PREFIX}/local_info"
EVENTS_FORECAST_INFO_ROUTE = f"{EVENTS_PREFIX}/forecast_info"
EVENTS_UPLOAD_CSV_ROUTE = f"{EVENTS_PREFIX}/upload"

# Rotas diretas (sem parâmetros dinâmicos)
EVENTS_ALL_ROUTE = f"{EVENTS_PREFIX}/all"
EVENTS_TOP_SOON_ROUTE = f"{EVENTS_PREFIX}/top/soon"
EVENTS_TOP_MOST_VIEWED_ROUTE = f"{EVENTS_PREFIX}/top/most-viewed"
EVENTS_LOTE_ROUTE = f"{EVENTS_PREFIX}/lote"

# Rota de detalhe de um evento
EVENTS_DETAIL_ROUTE = lambda event_id: f"{EVENTS_PREFIX}/{event_id}"

# Rota para info local de um evento específico
EVENTS_DETAIL_LOCAL_INFO_ROUTE = lambda event_id: f"{EVENTS_PREFIX}/{event_id}/local_info"

# Rota com paginação (você pode passar os parâmetros via `params`, mas se quiser gerar direto como string):
EVENTS_PAGINATED_ROUTE = lambda skip, limit: f"{EVENTS_PREFIX}?skip={skip}&limit={limit}"

# Autenticação (se existir)
AUTH_PREFIX = f"{API_V1_PREFIX}/auth"
LOGIN_ROUTE = f"{AUTH_PREFIX}/login"

# Forecast geral (ex: /api/v1/forecast)
FORECAST_PREFIX = f"{API_V1_PREFIX}/forecast"

# Rota com query param dinâmico
EVENTS_LOCAL_INFO_BY_NAME_ROUTE = lambda location_name: f"{EVENTS_LOCAL_INFO_ROUTE}?location_name={location_name}"

# Outros exemplos possíveis
USER_PREFIX = f"{API_V1_PREFIX}/users"
USER_DETAIL_ROUTE = lambda user_id: f"{USER_PREFIX}/{user_id}"
