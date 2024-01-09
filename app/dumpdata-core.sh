set -a
source .env.dev-local
set +a

python manage.py dumpdata core --indent 2 --output "$HOME/$(date -I)-postgres-data--core.json"
