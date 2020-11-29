heroku.push:
	heroku container:push web -a py-shorten --recursive

heroku.release:
	heroku container:release web -a py-shorten

heroku.deploy:
	make heroku.push
	make heroku.release