

note:
	mkdir -p ./docs/notebooks/
	rm -rf ./docs/notebooks/*.ipynb
	cp -r *.ipynb ./docs/notebooks/

contents:
	mkdir -p ./docs/_build/html/media_content/
	cp ./html_builders/*/*.html ./docs/media_content/
	cp ./html_builders/*/*.css ./docs/media_content/

authors_contents:
	cd ./docs/authors && make contents && cd ../..

dash_content:
	cp ./html_builders/*/*.html ./dash/content/