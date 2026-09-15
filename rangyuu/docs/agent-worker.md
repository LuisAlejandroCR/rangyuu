# Worker autónomo (diseño futuro)

## Configuración

- `AGENT_PROVIDER_URL`: endpoint HTTPS del proveedor; no se acepta HTTP ni direcciones privadas.
- `AGENT_PROVIDER_TOKEN`: secreto del proveedor, inyectado desde Secret Manager.
- `RANGYUU_WORKER_TOKEN`: token entrante del worker, también desde Secret Manager.

No se guardan valores reales en el repositorio, imágenes ni logs.

## Permisos mínimos

Usar un token GitHub fine-grained limitado al repositorio: `Contents: Read and write` y
`Pull requests: Read and write`. No conceder administración, secrets ni acceso a otros repositorios.
En Cloud Run, restringir invocación mediante IAM/OIDC (`roles/run.invoker`).

## Contrato y operación

El endpoint recibe un objeto JSON con `objective` (máximo 2.000 caracteres) y archivos permitidos;
el cuerpo máximo es 1 MB. El worker responde con un parche y abre una PR en una rama efímera; nunca
fusiona directamente a `main`. Un cron diario puede disparar el trabajo, con timeout y reintentos
limitados. La autenticación HMAC queda para proveedores externos sin OIDC.

## Checklist antes de producción

- [ ] Secretos en Secret Manager y rotación definida.
- [ ] HTTPS, allowlist y bloqueo de SSRF verificados.
- [ ] Límites y timeout probados con payloads inválidos.
- [ ] PR generada en rama efímera y revisión automática ejecutada.
- [ ] Merge manual después de auditoría y suite verde.
