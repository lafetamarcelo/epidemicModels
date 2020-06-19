note:
	mkdir -p ./docs/notebooks/
	rm -rf ./docs/notebooks/*.ipynb
	cp -rf *.ipynb ./docs/notebooks/

html:
	cd ./docs && make html && cd ..

contents:
	mkdir -p ./docs/_build/html/media_content/
	cp -rf ./html_builders/*/*.html ./docs/media_content/
	cp -rf ./html_builders/*/*.css ./docs/media_content/

authors_contents:
	cd ./docs/authors && make contents && cd ../..

dash_contents:
	cp -rf ./html_builders/*/*.html ./dash/content/
