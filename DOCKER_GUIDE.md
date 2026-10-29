# Docker Deployment & Execution Guide for Brokerage Module

This guide explains how to run the Docker image for **Brokerage Module** (`brokerage_module`), including both the Frappe/ERPNext backend and the Vue 3 / Vite Single Page Application (SPA).

---

## Architecture Overview: Why `docker run` Alone Isn't Enough

Unlike standalone microservices (Node/Express, Flask), **Frappe/ERPNext** is a multi-tenant enterprise framework. When someone runs your Docker image, it requires:

1. **MariaDB Database (`db`)**: To store tables, DocTypes (`Brokers`, `Broker Purchase Entry`, `Broker Sales Entry`, `Stock Group`, etc.), and transactions.
2. **Redis Services (`redis-cache`, `redis-queue`)**: For session caching and background queue execution.
3. **A Frappe Site (`bench new-site`)**: In Frappe, apps are not executed directly against the database; they are installed into an isolated **Site** (e.g., `brokerage.local` or `sugar.local`).
4. **Persistent Volumes (`sites/`)**: To persist site configurations, private keys, database credentials, and uploaded files.

To run everything seamlessly without configuring databases manually, use the included **`docker-compose.yml`**.

---

## Method 1: Running with Docker Compose (Recommended)

### Step 1: Start Supporting Services & Brokerage Container
From the `brokerage_module` directory, start the stack:

```bash
docker compose up -d
```

This starts:
- `db` (MariaDB 10.6)
- `redis-cache` (Redis 6.2)
- `redis-queue` (Redis 6.2)
- `configurator` (Sets global database and redis connection strings)
- `backend` (Frappe + ERPNext + Brokerage Module web server exposed on port `8006`)
- `worker` (Background jobs)
- `scheduler` (Cron scheduler)

Check running containers:
```bash
docker compose ps
```

---

### Step 2: Create a Site & Install Brokerage Module (First Time Only)

Run `bench new-site` inside the `backend` container to initialize your database and install both ERPNext and Brokerage Module:

```bash
docker compose exec backend bench new-site brokerage.localhost \
  --admin-password admin \
  --db-root-password admin \
  --install-app erpnext \
  --install-app brokerage_module
```

Set this site as the default site:
```bash
docker compose exec backend bench use brokerage.localhost
```

---

### Step 3: Access the Application

Once the site is created, open your browser:

| Interface | URL | Credentials |
| :--- | :--- | :--- |
| **Brokerage Desk (Vue SPA)** | `http://localhost:8006/brokerage-desk#/` | Log in as Administrator |
| **Desk Admin / ERPNext** | `http://localhost:8006/app` | `Administrator` / `admin` |
| **Direct Login Page** | `http://localhost:8006/login` | `Administrator` / `admin` |

---

## Method 2: Running Without Docker Compose (Connecting to Existing MariaDB & Redis)

If someone already has MariaDB and Redis running on their host or network:

```bash
docker run -d \
  --name brokerage-app \
  -p 8006:8000 \
  -e DB_HOST=172.17.0.1 \
  -e DB_PORT=3306 \
  -e REDIS_CACHE=redis://172.17.0.1:6379 \
  -e REDIS_QUEUE=redis://172.17.0.1:6379 \
  -v brokerage_sites:/home/frappe/frappe-bench/sites \
  0sapkale070rohan0/brokerage-module:latest
```

Then create the site:
```bash
docker exec -it brokerage-app bench new-site brokerage.localhost \
  --admin-password admin \
  --db-root-password <your-mariadb-root-password> \
  --install-app erpnext \
  --install-app brokerage_module
```

---

## How to Share Your Docker Image on Docker Hub

If someone else needs to `docker pull` this image directly from Docker Hub:

### 1. Log In to Docker Hub
```bash
docker login
```

### 2. Push the Image
```bash
docker push 0sapkale070rohan0/brokerage-module:latest
```

Once pushed, anyone in the world can run:
```bash
docker pull 0sapkale070rohan0/brokerage-module:latest
```
and spin it up using the steps above!
