#!/bin/bash
set -e

cd "$HOME" || exit 1

# Install bench CLI
pip install frappe-bench

# Fetch Frappe framework v16 directly with depth 1
mkdir -p "$HOME/frappe"
pushd "$HOME/frappe"
git init
git remote add origin "https://github.com/frappe/frappe"
git fetch origin "version-16" --depth 1
git checkout FETCH_HEAD
popd

# Initialize bench using local frappe path
bench init --skip-redis-config-generation --skip-assets \
  --frappe-path "$HOME/frappe" --python "$(which python)" "$HOME/frappe-bench"

# Ensure UTF8mb4 on MariaDB service container
mysql --host 127.0.0.1 --port 3306 -u root -proot -e "SET GLOBAL character_set_server = 'utf8mb4'" || true
mysql --host 127.0.0.1 --port 3306 -u root -proot -e "SET GLOBAL collation_server = 'utf8mb4_unicode_ci'" || true

cd "$HOME/frappe-bench" || exit 1

# Install brokerage_module from checked out workspace
bench get-app brokerage_module "${GITHUB_WORKSPACE}"
bench new-site --db-root-password root --admin-password admin \
  --no-mariadb-socket --install-app brokerage_module test_site
bench --site test_site set-config allow_tests true
