note:
	mkdir -p ./docs/notebooks/
	rm -rf ./docs/notebooks/*.ipynb
	cp -rf *.ipynb ./docs/notebooks/

contents:
	mkdir -p ./docs/_build/html/media_content/
	cp -rf ./html_builders/*/*.html ./docs/media_content/
	cp -rf ./html_builders/*/*.css ./docs/media_content/

dash_content:
	cp -rf ./html_builders/*/*.html ./dash/content/