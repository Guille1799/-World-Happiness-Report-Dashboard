# Security policy

## Supported versions

We address security issues affecting the **default branch** (`main`) and the deployed Streamlit app configuration.

## Reporting a vulnerability

**Do not** open a public issue for undisclosed security problems (especially leaked tokens or secrets).

1. Use GitHub **private vulnerability reporting** if enabled on the repository, or  
2. Contact the repository owner via a **private** channel (e.g. email listed on their GitHub profile).

Include:

- Description of the issue and impact  
- Steps to reproduce (if applicable)  
- Whether you believe credentials or user data are at risk  

## Secrets

- Never commit `.env`, Streamlit **Secrets**, or API keys.  
- If a secret was ever pushed to git history, **rotate** it immediately and consider history cleanup or repo rotation for severe cases.

## Data

This app loads public WHR-style data and optional downloads. Do not use it to store or transmit regulated personal data without proper compliance review.
