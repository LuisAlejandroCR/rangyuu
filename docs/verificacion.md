<!-- docs/verificacion.md: qué está comprobado, con qué comando, y qué sigue sin comprobar.
     Una fila pasa a ✅ solo cuando alguien que no la escribió puede repetir la comprobación.
     No es el plan (docs/plan.md) ni la bitácora (docs/memoria.md): es la evidencia.
     Toda corrección a un dato ya documentado entra aquí, fechada. -->

# Verificación

## Comprobado

| Qué | Cómo se repite | Estado | Fecha |
|---|---|---|---|
| Suite completa del núcleo, 57 pruebas | `python -m pytest -q` → `57 passed` | ✅ | 2026-09-15 |
| Cliente de Ring sin red: token del Playground, intercambio de refresh, expiración y rotación | `python -m pytest tests/test_ring_client.py` | ✅ | 2026-09-15 |
| El cliente rechaza `http://`, ids de dispositivo con `/` o `?`, y no filtra el token en el error | `python -m pytest tests/test_ring_client.py` | ✅ | 2026-09-15 |
| Precedencia de configuración: la variable de entorno gana sobre `.env.local` | `python -m pytest tests/test_config.py` | ✅ | 2026-09-15 |
| Demo sin credenciales: libre → ocupado → duplicado rechazado → caducado | `python -m rangyuu` | ✅ | 2026-09-15 |
| DLT normalizado: correspondencias degeneradas y punto al infinito fallan en vez de adivinar | `python -m pytest tests/test_geometry.py` | ✅ | 2026-09-15 |
| Firma HMAC-SHA256 sobre los bytes originales del cuerpo; alterada rechaza con 401 | `python -m pytest tests/test_security.py tests/test_api_contract.py` | ✅ | 2026-09-15 |
| Contrato de degradación: sin evidencia explícita no hay `PROCEED` | `python -m pytest tests/test_core.py` | ✅ | 2026-09-15 |
| Caducidad: celda más vieja que `max_age` responde `cell stale` | `python -m pytest tests/test_spatial.py::test_lifecycle_unknown_stale_and_occupied` | ✅ | 2026-09-15 |
| Oclusión: una celda ocluida vuelve a desconocida, nunca a libre | `python -m pytest tests/test_spatial.py::test_occlusion_returns_a_cell_to_unknown_never_to_free` | ✅ | 2026-09-15 |
| Un evento repetido no vuelve a entrar; dos dispositivos no comparten celdas | `python -m pytest tests/test_spatial.py` | ✅ | 2026-09-15 |

## Correcciones a datos ya documentados

- **2026-09-15 — `pytest` sí está instalado.** La bitácora del 2026-09-14 dice que no lo estaba y que
  las funciones de prueba se ejecutaron a mano. `python -m pytest --version` devuelve `pytest 9.1.1`
  en este entorno; la suite corre formalmente.

## Sin comprobar — ⏳ pendiente

| Qué | Por qué no se pudo | Bloque |
|---|---|---|
| Cualquier llamada a la API real de Ring | No hay `RANGYUU_ACCESS_TOKEN` ni `client_id` en el entorno | B1, B2, B3 |
| Error métrico de la homografía en centímetros a una distancia dada | Requiere cuatro correspondencias medidas contra una escena real | B8 |
| Las seis mediciones de `docs/perception.md` §7 | Requieren sesión WHEP viva | B3, B10 |
| La ruta real del endpoint de token OAuth | No está en el sample ni se pudo leer la doc oficial; queda en `RANGYUU_TOKEN_URL`, configurable, sin valor por defecto | B1, B2 |
| Sesión WHEP fuera del navegador | Nada escrito todavía; es el riesgo técnico mayor | B10 |
| Oclusión derivada del frame | `mark_occluded` existe y tiene pruebas, pero hoy la oclusión se declara desde fuera, no se detecta | B8 |
| Persistencia de la deduplicación entre reinicios | El registro de eventos vive en memoria | B10 |
