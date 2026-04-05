# Redirección shinyapps.io → Streamlit

La URL de destino está en `app.R` (`STREAMLIT_URL` → Streamlit en producción).

**Guía detallada (PC nuevo, token, etc.):** [GUIA-DESPLEGUE.md](GUIA-DESPLEGUE.md)

Resumen: en shinyapps.io → **Account → Tokens**, ejecuta **una vez** el `rsconnect::setAccountInfo(...)` que te dan. Luego, en esta carpeta:

```r
setwd("ruta/a/shiny-dashboard-redirect")
source("deploy.R")
```

El nombre `Dashboard` debe coincidir con la app en shinyapps.io para conservar  
`https://guillermomartindeoliva.shinyapps.io/Dashboard/`.
