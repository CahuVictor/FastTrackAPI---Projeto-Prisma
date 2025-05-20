# app/services/mock_local_info.py
from app.schemas.local_info import LocalInfo

MOCKED_LOCAL_INFOS = [
    LocalInfo(location_name="cesar", capacity=200, venue_type="Auditorio", is_accessible=True, address="Rua Bione, 220", past_events=["Recn'n Play 2018", "Recn'n Play 2019"], manually_edited=False),
    LocalInfo(location_name="auditorio central", capacity=350, venue_type="Auditorio", is_accessible=True, address="Av. Central, 123", past_events=["Evento A", "Evento B"], manually_edited=False),
    LocalInfo(location_name="salao azul", capacity=100, venue_type="Salao", is_accessible=False, address="Rua Azul, 10", past_events=["Evento C", "Evento D"], manually_edited=False),
    LocalInfo(location_name="teatro municipal", capacity=500, venue_type="Auditorio", is_accessible=True, address="Praça Matriz, 5", past_events=["Festival de Dança"], manually_edited=False),
    LocalInfo(location_name="espaço verde", capacity=150, venue_type="Salao", is_accessible=False, address="Rua das Palmeiras, 200", past_events=["Feira Agroecológica"], manually_edited=False),
    LocalInfo(location_name="galpão criativo", capacity=80, venue_type="Salao", is_accessible=True, address="Rua do Comércio, 45", past_events=["Oficina Maker"], manually_edited=False),
    LocalInfo(location_name="centro cultural", capacity=400, venue_type="Auditorio", is_accessible=True, address="Av. Cultura, 555", past_events=["Festival de Música"], manually_edited=False),
    LocalInfo(location_name="biblioteca", capacity=60, venue_type="Salao", is_accessible=True, address="Rua do Saber, 77", past_events=["Clube do Livro"], manually_edited=False),
    LocalInfo(location_name="sala amarela", capacity=40, venue_type="Salao", is_accessible=False, address="Rua Sol, 33", past_events=["Reunião Anual"], manually_edited=False),
    LocalInfo(location_name="auditorio beta", capacity=220, venue_type="Auditorio", is_accessible=True, address="Av. Beta, 101", past_events=["Workshop Python"], manually_edited=False),
]

def get_local_info_by_name(location_name: str) -> LocalInfo | None:
    name = location_name.strip().lower()
    for item in MOCKED_LOCAL_INFOS:
        if item.location_name == name:
            return item
    return None
