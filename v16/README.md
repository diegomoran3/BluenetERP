# Bluenet ERPNext v16

Docker deployment for ERPNext 16.34.1 + KLiK PoS + POS-Awesome (all baked into one custom image).

- Compose project: `bluenet`
- Port: `8080`
- Site: `localhost`

## Layout

```
repos/
├── frappe_docker/          # clone of https://github.com/frappe/frappe_docker
└── BluenetERP/
    └── v16/                # this directory
```

## Setup (fresh machine)

1. Prereqs: Docker Engine (Linux) or Docker Desktop with WSL2 (Windows). On Windows, clone with WSL git into the WSL filesystem (`~/repos`), not `/mnt/c` — see `scripts/fix-crlf.sh` if files ever get CRLF line endings.

2. Create env:

   ```
   cp .env.example .env
   nano .env          # set DB_PASSWORD
   ```

3. Generate compose.yaml:

   ```
   ./generate.sh
   ```

4. Build the image (only if `docker images` has no `my-erpnext:16.34.1`; takes ~30 min):

   ```
   cd ../../frappe_docker
   docker build \
     --build-arg=FRAPPE_PATH=https://github.com/frappe/frappe \
     --build-arg=FRAPPE_BRANCH=version-16 \
     --build-arg=CACHE_BUST=$(date +%s) \
     --secret=id=apps_json,src=../BluenetERP/v16/apps.json \
     --tag=my-erpnext:16.34.1 \
     --file=images/layered/Containerfile .
   cd ../BluenetERP/v16
   ```

5. Start:

   ```
   docker compose -p bluenet -f compose.yaml up -d
   ```

6. Create the site:

   ```
   docker compose -p bluenet -f compose.yaml exec backend \
     bench new-site --mariadb-user-host-login-scope=% \
       --db-root-password <DB_PASSWORD from .env> \
       --install-app erpnext \
       --admin-password admin \
       localhost
   ```

7. Open `http://localhost:8080` — `Administrator` / `admin`

## Post-setup

1. Import customizations (custom field + scripts):

   ```
   ./customizations/import.sh
   docker compose -p bluenet -f compose.yaml exec backend \
     bench --site localhost set-config server_script_enabled 1
   ```

2. Install a POS app (both are baked in, switchable anytime):

   ```
   ./pos-switcher.py                       # interactive
   # or
   ./scripts/switch-to-klik.sh             # KLiK PoS → /klik_pos
   ./scripts/switch-to-posawesome.sh       # POS-Awesome → workspace
   ```

3. POS Profile: `docker compose -p bluenet -f compose.yaml exec -T backend bash -c "cat scripts/setup_pos_profile.py | bench --site localhost console"` (copy script into container first).

4. Data import tooling lives in the repo root: `generate_import.py`, `scripts/*`, `import/*` (items, customers, warehouses, stock reconciliation).

## Upgrade ERPNext version

1. Edit `apps.json` → new branch (e.g. `v16.34.1`)
2. Update `.env`: `ERPNEXT_VERSION`, `CUSTOM_TAG`
3. Rebuild image (step 4 above, new tag), `./generate.sh`, `up -d`
4. `docker compose -p bluenet -f compose.yaml exec backend bench --site localhost migrate`
