# Worker autónomo (diseño)

Esta es una especificación, no una afirmación de despliegue existente.

## Configuración y límites

- `AGENT_PROVIDER_URL`: URL HTTPS validada; `AGENT_PROVIDER_TOKEN` y `RANGYUU_WORKER_TOKEN` se
  inyectan desde Secret Manager y nunca se versionan.
- Entrada: objeto JSON con `objective` (1–2.000 caracteres) y `files` (rutas relativas, máximo 100,
  cada ruta 256 caracteres). Cuerpo máximo: 1 MiB; respuestas máximo: 1 MiB.
- Un solo trabajo activo por repositorio mediante una clave idempotente `request_id`; duplicados
  devuelven el resultado anterior. Timeout sugerido: 20 s por llamada y 10 min por job.

## GitHub y control

Token fine-grained limitado al repositorio: `Contents: Read and write` y `Pull requests: Read and
write`; sin permisos de administración, secrets o repositorios adicionales. El worker crea una rama
efímera `agent/<request_id>`, abre PR y no hace merge. `main` debe tener branch protection, revisión
obligatoria y aprobación manual del merge. Cloud Run debe restringir invocación mediante IAM/OIDC;
HMAC se reserva para integraciones externas.

## Cron y checklist

El cron diario debe ser explícito, registrar solo metadatos no sensibles y limitar reintentos.

- [ ] Secret Manager configurado y rotación definida.
- [ ] Validación de rutas, tamaño, HTTPS y SSRF probada.
- [ ] Idempotencia y concurrencia probadas.
- [ ] PR efímera revisada automáticamente y manualmente.
- [ ] Suite verde y merge aprobado manualmente.
