# Desplegar el redirect en shinyapps.io (PC nuevo)

Tu app Streamlit ya está en **https://world-happiness-report-dash.streamlit.app/**.  
Este mini-proyecto Shiny solo hace que el enlace **antiguo** (`…shinyapps.io/Dashboard/`) lleve ahí.

## Qué necesitas

1. **R** instalado (en tu PC: suele estar en `C:\Program Files\R\R-x.x.x\`).
2. Paquetes **`shiny`** y **`rsconnect`** (si no los tienes, en R: `install.packages(c("shiny","rsconnect"))`).
3. Cuenta en [shinyapps.io](https://www.shinyapps.io/) (la misma que usaste antes: **guillermomartindeoliva**).

## Paso 1 — Token de shinyapps.io (solo la primera vez en este PC)

1. Entra en [https://www.shinyapps.io/](https://www.shinyapps.io/) e inicia sesión.
2. Arriba a la derecha: tu nombre → **Account** → pestaña **Tokens** / **Configure tokens**.
3. Verás un bloque de código que pone algo como:

   `rsconnect::setAccountInfo(name=..., token=..., secret=...)`

4. **Copia ese bloque entero**, ábrelo en **R** o **RStudio**, pégalo y pulsa **Enter** (una sola vez).  
   Eso guarda la credencial en tu usuario de Windows para futuros despliegues.

Si no ves el comando, busca **“Show secret”** o **“Copy”** junto al token.

## Paso 2 — Abrir la carpeta correcta

En R:

```r
setwd("C:/Users/Guille/Downloads/JOB Assist/shiny-dashboard-redirect")
```

(Ajusta la ruta si moviste la carpeta `JOB Assist`.)

## Paso 3 — Desplegar

**Opción A — desde R:**

```r
source("deploy.R")
```

**Opción B — desde PowerShell** (sin abrir R a mano):

```powershell
cd "C:\Users\Guille\Downloads\JOB Assist\shiny-dashboard-redirect"
& "C:\Program Files\R\R-4.5.3\bin\Rscript.exe" deploy.R
```

(Si tu versión de R no es 4.5.3, cambia la ruta a la carpeta `bin\Rscript.exe` que tengas.)

## Paso 4 — Probar

Abre en el navegador:

**https://guillermomartindeoliva.shinyapps.io/Dashboard/**

Debería redirigir a **world-happiness-report-dash.streamlit.app**.

## Si algo falla

| Mensaje | Qué hacer |
|--------|-----------|
| `No accounts registered` | Repite el **Paso 1** (`setAccountInfo` completo). |
| Error de nombre de app | Asegúrate de que en shinyapps.io la app se llama **Dashboard** (como antes). |
| `403` / credenciales | Vuelve a generar un token nuevo en la web y ejecuta de nuevo `setAccountInfo`. |

## Nota

No subas tokens a GitHub. El archivo `app.R` solo contiene la URL pública de Streamlit, no secretos.
