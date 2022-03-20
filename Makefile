test:
	docker-compose run app sh -c "python manage.py test"

lint:
	flake8 app/
