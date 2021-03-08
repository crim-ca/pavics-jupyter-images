# pavics-jupyter-images

This repo contains the different Dockerfiles used to create the images available in JupyterHub for DACCS.
These images will be available as image choices when starting a new instance of JupyterLab from the JupyterHub interface.

All Dockerfiles (eo, nlp, etc.) are derived from the 'base' image found on the repo
[bird-house/pavics-jupyter-base](https://github.com/bird-house/pavics-jupyter-base).
Any packages required only for a specific image can be added to its corresponding environment.yml file.

These images were first initialized with the packages listed on this
[Confluence page](https://www.crim.ca/confluence/pages/viewpage.action?pageId=58625163).

The Docker image builds can be found on Docker Hub : 
* [eo](https://hub.docker.com/repository/docker/pavics/crim-jupyter-eo)
* [nlp](https://hub.docker.com/repository/docker/pavics/crim-jupyter-nlp)
