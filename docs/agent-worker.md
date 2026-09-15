# Worker autónomo (diseño)

Esta es una especificación, no una afirmación de despliegue existente.

## Workflow de GitHub Actions

`.github/workflows/agent-worker.yml` invoca el orquestador cada seis horas o manualmente.
Usa `AGENT_PROVIDER_URL` y, opcionalmente, `AGENT_PROVIDER_TOKEN` desde Secrets; nunca imprime
el token. Rechaza URLs que no sean HTTPS, limita el objetivo a 2.000 caracteres y solicita al
orquestador un único PR con un máximo de tres iteraciones y 800 líneas modificadas.

El job tiene `contents: read` y `id-token: write`, sin permiso de escritura ni de merge en GitHub.
La concurrencia impide dos workers simultáneos. El endpoint debe validar el token/OIDC, aplicar
allowlist de repositorio, crear una rama efímera y abrir un PR; el merge queda fuera del worker y
requiere branch protection y revisión humana.

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
