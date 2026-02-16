# TODOS

- Rotate some tags / status
- add color coding to orgs added by other users
- add confirmation mail logic
- add user deletion logic
- add invoices

# building the image

docker build --build-arg NEXT_PUBLIC_BACKEND_URL=http://django:8000 -t clapp_frontend:latest .

# then export to dockerhub

docker tag clapp_frontend:latest pducasse/clapp_frontend:latest
docker push pducasse/clapp_frontend:latest
