# Uso (desde esta carpeta):
#   setwd(".../shiny-dashboard-redirect")
#   source("deploy.R")
#
# Antes, una sola vez en este PC, ejecuta en R el bloque completo
# rsconnect::setAccountInfo(...) que copias de shinyapps.io → Account → Tokens.

if (!file.exists("app.R")) {
  stop("Ejecuta este script con setwd() en la carpeta shiny-dashboard-redirect (donde está app.R).")
}

if (!requireNamespace("rsconnect", quietly = TRUE)) {
  stop("Instala: install.packages('rsconnect')")
}

message("Desplegando a shinyapps.io (appName = Dashboard)...")
rsconnect::deployApp(
  appDir = ".",
  appName = "Dashboard",
  account = "guillermomartindeoliva"
)
message("Hecho.")
