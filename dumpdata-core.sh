set -a
source .env.dev-local
set +a

python ./app/manage.py dumpdata core --indent 2 --output "$HOME/$(date -I)-postgres-data--core.json"
