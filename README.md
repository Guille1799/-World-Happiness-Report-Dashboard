# JOB Assist — World Happiness Intelligence

Monorepo con el **dashboard Streamlit** de exploración del *World Happiness Report* y, en paralelo, la **app R mínima** para redirigir desde un enlace antiguo en [shinyapps.io](https://shinyapps.io).

## Contenido del repositorio

| Carpeta | Descripción |
|--------|-------------|
| [`world-happiness-streamlit/`](world-happiness-streamlit/) | App principal **Streamlit** (`app.py`), tests, Docker, `requirements.txt`. |
| [`shiny-dashboard-redirect/`](shiny-dashboard-redirect/) | Shiny mínimo que solo **redirige** a la URL de Streamlit (misma URL pública en shinyapps.io). |

## Requisitos

- **Python 3.11+** recomendado (coincide con el `Dockerfile`).
- Cuenta **GitHub** para desplegar en [Streamlit Community Cloud](https://share.streamlit.io).
- **No subas** el archivo `.env` (está en `.gitignore`). Usa [`.env.example`](.env.example) como plantilla.

## Puesta en marcha local (Streamlit)

```bash
cd world-happiness-streamlit
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Más detalle: [`world-happiness-streamlit/README.md`](world-happiness-streamlit/README.md).

## Desplegar en Streamlit Cloud (después del `git push`)

1. Crea un repositorio vacío en GitHub y sube **este repo** (`main`).
2. En [share.streamlit.io](https://share.streamlit.io) → **New app** → conecta el repo.
3. **Main file path:** `world-happiness-streamlit/app.py`
4. **Branch:** `main` (o la que uses).
5. Si hace falta, en **Secrets** añade variables (mismo criterio que `.env.example`).

La URL pública será del estilo `https://<nombre>.streamlit.app`.

## Redirección desde Shiny (cuando tengas la URL de Streamlit)

Instrucciones en [`shiny-dashboard-redirect/README.md`](shiny-dashboard-redirect/README.md).

## Seguridad

- **Nunca** subas `.env` con tokens o claves. Si alguna vez quedó expuesta, **revócala** en BotFather / el servicio correspondiente y genera otra.
- El repositorio solo incluye [`.env.example`](.env.example) como plantilla.

## Licencia y datos

Código bajo [LICENSE](LICENSE) (MIT). Los **datos del World Happiness Report** y **Gallup** siguen sus condiciones de uso; esta UI no está afiliada al WHR.
