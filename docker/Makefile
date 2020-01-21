migrate:
	docker-compose -f docker/docker-compose.yml run rapidpro python manage.py migrate

########## DEV COMMANDS ##########

build.dev:
	docker-compose -f docker/docker-compose.dev.yml build

migrate.dev:
	docker-compose -f docker-compose.dev.yml run rapidpro python manage.py migrate

dev:
	make migrate.dev
	docker-compose -f docker-compose.dev.yml up

superuser.dev:
	docker-compose -f docker-compose.dev.yml run rapidpro python manage.py createsuperuser