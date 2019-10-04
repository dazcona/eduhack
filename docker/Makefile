run:
	@docker-compose up -d --build
dev:
	@docker exec -it edu_container bash
build:
	@docker-compose build
down:
	@docker-compose down -v
status:
	@docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
logs:
	@docker logs edu_container -f
yolo:
	@docker-compose up -d --build yolo
dev-yolo:
	@docker exec -it yolo bash