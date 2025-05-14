#!/bin/bash

echo "📤 Criando evento..."
curl -s -X POST http://localhost:8000/api/v1/eventos \
-H "Content-Type: application/json" \
-d '{
  "title": "Festival de Tecnologia",
  "description": "Evento com oficinas e palestras.",
  "event_date": "2025-06-12T19:00:00",
  "participants": ["Alice", "Bob"],
  "local_info": {
    "location_name": "auditório central",
    "capacity": 200,
    "venue_type": "AUDITORIO",
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
echo -e "\n✅ Evento criado"

echo "📚 Listando eventos:"
curl -s http://localhost:8000/api/v1/eventos
echo

echo "🔍 Buscando evento por ID:"
curl -s http://localhost:8000/api/v1/eventos/1
echo

echo "✏️ Atualizando evento:"
curl -s -X PUT http://localhost:8000/api/v1/eventos/1 \
-H "Content-Type: application/json" \
-d '{
  "title": "Festival Atualizado",
  "description": "Descrição atualizada",
  "event_date": "2025-06-13T20:00:00",
  "participants": ["Alice", "Carlos"],
  "local_info": {
    "location_name": "auditório central",
    "capacity": 250,
    "venue_type": "AUDITORIO",
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
echo -e "\n✅ Evento atualizado"

echo "🗑️ Removendo evento:"
curl -s -X DELETE http://localhost:8000/api/v1/eventos/1
echo -e "\n✅ Evento removido"
