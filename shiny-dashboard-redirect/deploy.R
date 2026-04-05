# Usage (from this directory):
#   setwd(".../shiny-dashboard-redirect")
#   source("deploy.R")
#
# First time on this machine: run the full rsconnect::setAccountInfo(...) block
# copied from shinyapps.io → Account → Tokens.

if (!file.exists("app.R")) {
  stop("Run this script with setwd() pointing at shiny-dashboard-redirect (where app.R lives).")
}

if (!requireNamespace("rsconnect", quietly = TRUE)) {
  stop("Install: install.packages('rsconnect')")
}

message("Deploying to shinyapps.io (appName = Dashboard)...")
rsconnect::deployApp(
  appDir = ".",
  appName = "Dashboard",
  account = "guillermomartindeoliva"
)
message("Done.")
