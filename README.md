# Bluenet ERPNext

ERPNext deployment for Bluenet — LAN-only on port 80.

## Setup

1. **On the server**, install Docker and Docker Compose v2.
2. Clone this repo and `frappe_docker` side by side:
   ```
   ~/source/repos/
   ├── frappe_docker/
   └── bluenetERP/
   ```
3. Copy `.env.example` to `.env` and set `DB_PASSWORD`:
   ```
   cp .env.example .env
   nano .env
   ```
4. Generate the compose file:
   ```
   ./generate.sh
   ```
5. Start containers:
   ```
   docker compose -p bluenet -f compose.yaml up -d
   ```
6. Create the site:
   ```
   docker compose -p bluenet exec backend \
     bench new-site --mariadb-user-host-login-scope=% \
       --db-root-password changeit \
       --install-app erpnext \
       --admin-password changeit \
       erpnext.site.com
   ```

## Client access

Add to each client's hosts file:
```
<server-ip>  erpnext.site.com
```
Access at `http://erpnext.site.com`

## Adding custom apps

1. Create `apps.json` in this directory.
2. Run from `frappe_docker/`:
   ```
   docker build \
     --build-arg=FRAPPE_PATH=https://github.com/frappe/frappe \
     --build-arg=FRAPPE_BRANCH=version-16 \
     --secret=id=apps_json,src=../bluenetERP/apps.json \
     --tag=my-erpnext:16.0.0 \
     --file=images/layered/Containerfile .
   ```
3. Add `CUSTOM_IMAGE=my-erpnext` and `CUSTOM_TAG=16.0.0` to `.env`.
4. Regenerate and restart.
