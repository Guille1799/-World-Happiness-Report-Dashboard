# Deploy the Shiny redirect (new PC or fresh R install)

The Streamlit app lives at **https://world-happiness-report-dash.streamlit.app/**.  
This tiny Shiny app only ensures the **legacy** shinyapps.io URL still works:

**https://guillermomartindeoliva.shinyapps.io/Dashboard/** → redirects to Streamlit.

## Prerequisites

1. **R** installed (on Windows, often under `C:\Program Files\R\R-x.x.x\`).
2. R packages **`shiny`** and **`rsconnect`**:

   ```r
   install.packages(c("shiny", "rsconnect"))
   ```

3. A [shinyapps.io](https://www.shinyapps.io/) account (**guillermomartindeoliva**).

## Step 1 — Register this computer (once per machine)

1. Sign in at [shinyapps.io](https://www.shinyapps.io/).
2. Top right: your name → **Account** → **Tokens** (or **Configure tokens**).
3. Copy the full block that looks like:

   `rsconnect::setAccountInfo(name=..., token=..., secret=...)`

4. Paste the **entire** block into the **R console** (not PowerShell) and press **Enter** once.

This stores credentials for future deploys.

## Step 2 — Set working directory

In R:

```r
setwd("C:/Users/Guille/Downloads/JOB Assist/shiny-dashboard-redirect")
```

Adjust the path if you moved the `JOB Assist` folder.

## Step 3 — Deploy

**Option A — from R:**

```r
source("deploy.R")
```

**Option B — PowerShell** (no R GUI):

```powershell
cd "C:\Users\Guille\Downloads\JOB Assist\shiny-dashboard-redirect"
& "C:\Program Files\R\R-4.5.3\bin\Rscript.exe" deploy.R
```

(Change the R version folder if yours differs.)

If prompted **“Discovered a previously deployed app named Dashboard”**, choose **`1`** to **update** the existing app and keep the same public URL.

## Step 4 — Verify

Open:

**https://guillermomartindeoliva.shinyapps.io/Dashboard/**

You should land on **world-happiness-report-dash.streamlit.app**.

## Troubleshooting

| Message | Action |
|--------|--------|
| `No accounts registered` | Repeat **Step 1** (`setAccountInfo` block). |
| App name conflict | Use option **1** to update **Dashboard** (do not create `Dashboard-1` if you need the old URL). |
| `403` / auth errors | Generate a new token on the website and run `setAccountInfo` again. |

**Never** commit tokens to GitHub. `app.R` only contains the public Streamlit URL.
