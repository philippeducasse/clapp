# TODOS

- Rotate some tags / status
- add color coding to orgs added by other users
- add season start/end logic
- add user deletion logic
- add invoices
- all emailing tasks on celery? -> io heavy
- check requests tab
  - dashboard queries entire data, but only count is needed
  - profiles/me is hit on every page load
  - optimise all of this

# building the image

docker build --build-arg NEXT_PUBLIC_BACKEND_URL=http://django:8000 -t clapp_frontend:latest .

# then export to dockerhub

docker tag clapp_frontend:latest pducasse/clapp_frontend:latest
docker push pducasse/clapp_frontend:latest
