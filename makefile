

note:
	mkdir -p ./docs/notebooks/
	rm -rf ./docs/notebooks/*.ipynb
	cp -r *.ipynb ./docs/notebooks/

contents:
	mkdir -p ./docs/_build/html/media_content/
	cp ./html_builders/UK_results/*.html ./docs/_build/html/media_content/

