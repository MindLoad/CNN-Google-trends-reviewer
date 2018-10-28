sh:
	docker-compose exec web sh

shell:
	docker-compose exec web python3 manage.py shell_plus

worker:
	docker-compose exec web celery -A cnn worker -l info

beat:
	docker-compose exec web celery -A cnn beat -l info

flower:
	docker-compose exec -it web flower -A cnn --port=5555
