migrate:
	docker-compose -f docker/docker-compose.yml run rapidpro python manage.py migrate

########## DEV COMMANDS ##########

build:
	docker-compose -f docker/docker-compose.yml build

migrate:
	docker-compose -f docker-compose.dev.yml run rapidpro python manage.py migrate

dev:
	make migrate.dev
	docker-compose -f docker-compose.yml up

superuser:
	docker-compose -f docker-compose.yml run rapidpro python manage.py createsuperuser