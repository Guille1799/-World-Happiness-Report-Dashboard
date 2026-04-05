# Shiny → Streamlit redirect

Minimal **R/Shiny** app that **HTTP-redirects** visitors from a legacy [shinyapps.io](https://www.shinyapps.io/) deployment to the current **Streamlit** app.

The target URL is set in `app.R` as `STREAMLIT_URL` (production Streamlit).

**Full deploy guide:** [DEPLOY-SHINY.md](DEPLOY-SHINY.md)

**Quick deploy** (after `rsconnect::setAccountInfo(...)` has been run once on this PC):

```r
setwd("path/to/shiny-dashboard-redirect")
source("deploy.R")
```

Keep **`appName = "Dashboard"`** so the public URL remains:

`https://guillermomartindeoliva.shinyapps.io/Dashboard/`
