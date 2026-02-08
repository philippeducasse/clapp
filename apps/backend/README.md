# switching from gemini to mistral search would shave off a lot in disk space:

django@6d8a3cbddea5:/$ du -sh /app/.venv/lib/python3.12/site-packages/\* | sort -rh | head -20
87M /app/.venv/lib/python3.12/site-packages/googleapiclient
44M /app/.venv/lib/python3.12/site-packages/pandas
39M /app/.venv/lib/python3.12/site-packages/django
38M /app/.venv/lib/python3.12/site-packages/numpy.libs
31M /app/.venv/lib/python3.12/site-packages/numpy
23M /app/.venv/lib/python3.12/site-packages/phonenumbers
15M /app/.venv/lib/python3.12/site-packages/grpc
15M /app/.venv/lib/python3.12/site-packages/google
11M /app/.venv/lib/python3.12/site-packages/psycopg2_binary.libs
4.8M /app/.venv/lib/python3.12/site-packages/pydantic_core
4.2M /app/.venv/lib/python3.12/site-packages/rest_framework
2.7M /app/.venv/lib/python3.12/site-packages/tzdata
2.7M /app/.venv/lib/python3.12/site-packages/pytz
1.9M /app/.venv/lib/python3.12/site-packages/pydantic
1.8M /app/.venv/lib/python3.12/site-packages/mistralai
1.8M /app/.venv/lib/python3.12/site-packages/celery
1.7M /app/.venv/lib/python3.12/site-packages/redis
1.7M /app/.venv/lib/python3.12/site-packages/prompt_toolkit
1016K /app/.venv/lib/python3.12/site-packages/pyasn1_modules
900K /app/.venv/lib/python3.12/site-packages/kombu

# build image

docker build -f docker/dockerfile -t pducasse/clapp_backend:latest .

# Push to Docker Hub

docker push pducasse/clapp_backend:latest

# loading postgres into container:

docker cp data_dump.json clapp-django-1:/app/data_dump.json
docker compose exec django python manage.py loaddata /app/data_dump.json
