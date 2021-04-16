.PHONY: help
help: ## Prints help for targets with comments
	@grep -E '^[a-zA-Z._-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


.PHONY: jupyter
jupyter: ## Launch Jupyter notebook, bound to port 8888 on the host system
	docker run -it --rm -v `pwd`:/app -p 8888:8888 detritus:dev

.PHONY: test
test: ## Test the detector notebook
	 docker run -it --rm -v `pwd`:/app detritus:dev \
	  jupyter-nbconvert  /app/detector/detector.ipynb --to python --execute --stdout

.PHONY: download
download: ## Test the detector notebook
	 docker run -it --rm -v `pwd`:/app -e /bin/bash detritus:dev \
	  python /app/download.py

.PHONY: shell
shell: ## Run a new container and execute bash
	 docker run -it --rm -v `pwd`:/app detritus:dev /bin/bash

.PHONY: build
build: ## Build the detritus container
	docker build -t detritus:dev -f docker/Dockerfile .

.PHONY: nbstripout
nbstripout: ## Strip output from all Jupyter notebooks
	 docker run -it --rm -v `pwd`:/app detritus:dev /bin/bash -c 'find /app -name "*.ipynb" -exec nbstripout {} \;'
