# Redirección shinyapps.io → Streamlit

Esta carpeta contiene un **Shiny mínimo** que solo envía al usuario a la URL de tu app **Streamlit**.

1. Edita `app.R` y pon tu URL en `STREAMLIT_URL`.
2. En R, desde esta carpeta:

```r
setwd("ruta/a/shiny-dashboard-redirect")
library(rsconnect)
rsconnect::deployApp(
  appDir = ".",
  appName = "Dashboard",
  account = "guillermomartindeoliva"
)
```

El nombre `Dashboard` debe coincidir con la app en shinyapps.io para conservar  
`https://guillermomartindeoliva.shinyapps.io/Dashboard/`.
