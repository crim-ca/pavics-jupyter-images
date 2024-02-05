# Included custom configs change the value of MAKEFILE_LIST
# Extract the required reference beforehand so we can use it for help target
MAKEFILE_NAME := $(word $(words $(MAKEFILE_LIST)),$(MAKEFILE_LIST))
# Include custom config if it is available
-include Makefile.config

# Application
APP_ROOT    := $(abspath $(lastword $(MAKEFILE_NAME))/..)
APP_NAME    := $(shell basename $(APP_ROOT))
APP_DOMAINS ?= eo nlp
DOCKER_REPO ?= crim-ca/pavics-jupyter-images

DOCKER_BUILDS := $(addprefix docker-build-, $(APP_DOMAINS))
$(DOCKER_BUILDS): docker-build-%:
	docker build -t $(DOCKER_REPO)/$*:latest "$(APP_ROOT)/$(*)" 2>&1 | tee "$(APP_ROOT)/make-$@.log"

.PHONY: docker-build
docker-build: $(DOCKER_BUILDS)
