# TODOS

- table pagination
- breadcrumbs
- Add update button to editfestival page
- Rotate some tags / status
- add reminders

# building the image

docker build --build-arg NEXT_PUBLIC_BACKEND_URL=http://django:8000 -t clapp_frontend:latest .

then export to dockerhub
