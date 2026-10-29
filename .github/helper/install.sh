#!/bin/bash
set -ex

cd "$HOME" || exit 1

echo "=== 1. Installing frappe-bench ==="
pip install --upgrade pip
pip install frappe-bench

echo "=== 2. Fetching Frappe Framework v16 ==="
rm -rf "$HOME/frappe"
mkdir -p "$HOME/frappe"
pushd "$HOME/frappe"
git init
git remote add origin "https://github.com/frappe/frappe"
git fetch origin "version-16" --depth 1
git checkout FETCH_HEAD
popd

echo "=== 3. Initializing Bench ==="
bench init --skip-redis-config-generation --skip-assets \
  --frappe-path "$HOME/frappe" --python "$(which python)" "$HOME/frappe-bench"

echo "=== 4. Setting up MariaDB connection ==="
for i in {1..30}; do
  if mariadb -h 127.0.0.1 -P 3306 -u root -proot -e "SELECT 1" >/dev/null 2>&1; then
    echo "MariaDB is ready!"
    break
  elif mysql -h 127.0.0.1 -P 3306 -u root -proot -e "SELECT 1" >/dev/null 2>&1; then
    echo "MySQL is ready!"
    break
  fi
  echo "Waiting for MariaDB... ($i/30)"
  sleep 2
done

mariadb -h 127.0.0.1 -P 3306 -u root -proot -e "SET GLOBAL character_set_server = 'utf8mb4'; SET GLOBAL collation_server = 'utf8mb4_unicode_ci';" 2>/dev/null || \
mysql -h 127.0.0.1 -P 3306 -u root -proot -e "SET GLOBAL character_set_server = 'utf8mb4'; SET GLOBAL collation_server = 'utf8mb4_unicode_ci';" 2>/dev/null || true

cd "$HOME/frappe-bench" || exit 1

echo "=== 5. Installing brokerage_module ==="
bench get-app brokerage_module "${GITHUB_WORKSPACE}"

echo "=== 6. Creating test_site ==="
bench new-site --db-root-password root --admin-password admin \
  --no-mariadb-socket --install-app brokerage_module test_site

bench --site test_site set-config allow_tests true
