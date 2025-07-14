up:
	docker-compose -f compose/docker-compose.yml up --build -d

down:
	docker-compose -f compose/docker-compose.yml down

logs:
	docker-compose -f compose/docker-compose.yml logs -f

rebuild:
	docker-compose -f compose/docker-compose.yml build --no-cache

compile-locales:
	poetry run compile-locales
