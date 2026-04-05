# Redirección: mismo nombre de app en shinyapps.io → misma URL pública.
# 1) Edita STREAMLIT_URL abajo con la URL definitiva de tu app Streamlit.
# 2) En R: setwd(".../shiny-dashboard-redirect")
# 3) rsconnect::deployApp(appDir = ".", appName = "Dashboard", account = "guillermomartindeoliva")
#    (appName debe coincidir con "Dashboard" para conservar el enlace antiguo.)

library(shiny)

# === Edita solo esto ===
STREAMLIT_URL <- "https://world-happiness-report-dash.streamlit.app/"
# =======================

ui <- fluidPage(
  tags$head(
    tags$title("Redirigiendo…"),
    tags$meta(http_equiv = "refresh", content = paste0("0;url=", STREAMLIT_URL)),
    tags$script(HTML(paste0("window.location.replace('", STREAMLIT_URL, "');")))
  ),
  fluidRow(
    column(
      12,
      style = "margin-top: 2rem; font-family: system-ui, sans-serif;",
      h3("Redirigiendo al dashboard actual…"),
      p(
        "Si no te lleva solo en unos segundos, ",
        tags$a(href = STREAMLIT_URL, target = "_blank", "abre el enlace nuevo"),
        "."
      )
    )
  )
)

server <- function(input, output, session) {}

shinyApp(ui, server)
