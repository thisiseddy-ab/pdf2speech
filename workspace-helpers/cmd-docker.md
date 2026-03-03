#### ====== Docker Compose Helper Commands ===== ####
# === docker ompose down === #
docker-compose down 
# === start services (in foreground) === #
docker-compose -f docker-compose-17.yml up
# === start and rebuild (after code/addons change) === #
docker-compose -f docker-compose-17.yml up --build
# === start in detached mode (run in background) === #
docker-compose -f docker-compose-17.yml up -d
# === stop services (without removing containers) === #
docker-compose -f docker-compose-17.yml stop
# === stop and remove containers, networks, volumes === #
docker-compose -f docker-compose-17.yml down
# === restart services === #
docker-compose -f docker-compose-17.yml restart

#### ====== Docker Image Commands ===== ####
# === pull image === #
docker pull odoo:17.0
docker run --pull always odoo:17.0
# === list images === #
docker images
# === inspect image === #
docker image inspect odoo:17.0
docker image inspect odoo:17.0 --format '{{.Created}}'
# === remove image === #
docker rmi odoo:17.0
docker rmi -f odoo:17.0
# === prune unused images === #
docker image prune -f           # remove dangling images
docker image prune -a -f        # remove all unused images
# === build image === #
docker build -t my-odoo:custom .
docker build -f Dockerfile.odoo -t odoo:custom .
# === tag image === #
docker tag odoo:17.0 myrepo/odoo:prod
# === run image === #
docker run -it odoo:17.0 bash
docker run -v /my/addons:/mnt/extra-addons odoo:17.0
# === search images on Docker Hub === #
docker search odoo
# === view image history === #
docker history odoo:17.0

#### ====== Inspecting Containers & Logs ===== ####
# === View real-time logs === #
docker-compose -f docker-compose-17.yml logs
docker-compose -f docker-compose-17.yml logs -f odoo  # only odoo container
# === see running containers === #
docker ps
# === exec into running container === #
docker exec -it <container_id_or_name> bash
docker exec -it odoo17 bash  # if your service is named "odoo17"

#### ====== Development Helpers ===== ####
# === run Odoo shell inside container === #
docker exec -it odoo17 odoo shell -d your_db
# === manually upgrade a module === #
docker exec -it odoo17 odoo -u your_module -d your_db --stop-after-init
# === drop to psql inside PostgreSQL container === #
docker exec -it db-odoo psql -U odoo -d your_db

#### ====== Docker Volume Commands ===== ####
# === list all volumes === #
docker volume ls
# === inspect a specific volume (see mountpoint, usage) === #
docker volume inspect <volume_name>
# === prune volumes === #
docker volume prune -f
# === remove all unused volumes (not attached to any container) === #
docker volume prune -f
# === remove a specific volume === #
docker volume rm <volume_name>
# === remove multiple volumes === #
docker volume rm volume1 volume2