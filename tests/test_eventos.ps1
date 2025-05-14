Write-Host "Criando evento..."
Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/eventos" -ContentType "application/json" -Body '{
  "title": "Festival de Tecnologia",
  "description": "Evento com oficinas e palestras.",
  "event_date": "2025-06-12T19:00:00",
  "participants": ["Alice", "Bob"],
  "local_info": {
    "location_name": "auditório central",
    "capacity": 200,
    "venue_type": "Auditorio",
    "is_accessible": true,
    "address": "Rua Principal, 123",
    "past_events": ["evento 1", "evento 2"]
  },
  "forecast_info": {
    "forecast_datetime": "2025-06-12T15:00:00",
    "temperature": 27.5,
    "weather_main": "Clear",
    "weather_desc": "céu limpo",
    "humidity": 40,
    "wind_speed": 3.5
  }
}'

Write-Host "`nEvento criado"

Write-Host "`nListando eventos:"
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/eventos"

Write-Host "`nBuscando evento por ID:"
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/eventos/1"

Write-Host "`nAtualizando evento:"
Invoke-RestMethod -Method PUT -Uri "http://localhost:8000/api/v1/eventos/1" -ContentType "application/json" -Body '{
  "title": "Festival Atualizado",
  "description": "Descrição atualizada",
  "event_date": "2025-06-13T20:00:00",
  "participants": ["Alice", "Carlos"],
  "local_info": {
    "location_name": "auditório central",
    "capacity": 250,
    "venue_type": "Auditorio",
    "is_accessible": false,
    "address": "Rua Nova, 456",
    "past_events": []
  },
  "forecast_info": {
    "forecast_datetime": "2025-06-13T16:00:00",
    "temperature": 25.0,
    "weather_main": "Clouds",
    "weather_desc": "nublado",
    "humidity": 60,
    "wind_speed": 2.0
  }
}'

Write-Host "`nEvento atualizado"

Write-Host "`nRemovendo evento:"
Invoke-RestMethod -Method DELETE -Uri "http://localhost:8000/api/v1/eventos/1"
Write-Host "`nEvento removido"
