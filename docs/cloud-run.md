# Despliegue en Cloud Run

Construir y desplegar con `gcloud run deploy rangyuu-orchestrator --source . --region REGION`.
Guardar `RANGYUU_WEBHOOK_SECRET` en Secret Manager y enlazarlo con `--set-secrets`; no incluirlo en
la imagen ni en logs. Cloud Run proporciona autenticación OIDC para invocadores IAM; el endpoint
además acepta HMAC cuando se integra un proveedor externo. `/health` sirve para la comprobación de
salud. El servicio limita cuerpos a 1 MB y objetivos a 2.000 caracteres. Para OIDC, restringir el
invocador con IAM (`roles/run.invoker`) y usar tokens Google; HMAC queda para integraciones externas.
