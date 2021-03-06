test:
	docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py test"

migrations:
	docker-compose run --rm app sh -c "python manage.py makemigrations"

up:
	docker-compose up

down:
	docker-compose down

lint:
	flake8 .

format:
	black .

build:
	docker-compose build

dependencies:
	pip install -r requirements.txt
