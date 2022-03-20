test:
	docker-compose run app sh -c "python manage.py test"

lint:
	flake8 app/

format:
	black .

dependencies:
	pip install -r requirements.txt
