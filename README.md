# pavics-jupyter-images

## Description

This repo contains the different `Dockerfile` used to create images available in JupyterHub for DACCS.
These images will be available as image choices when starting a new instance of JupyterLab from the JupyterHub interface.

Every `Dockerfile` (`eo`, `nlp`, etc.) are derived from the `base` image found on the repo
[bird-house/pavics-jupyter-base](https://github.com/bird-house/pavics-jupyter-base).
Any packages required only for a specific image can be added to its corresponding `environment.yml` file.

These images were first initialized with the packages listed on this
[Confluence page](https://www.crim.ca/confluence/pages/viewpage.action?pageId=58625163).

The Docker image builds can be found on Docker Hub :

* [eo](https://hub.docker.com/repository/docker/pavics/crim-jupyter-eo)
* [nlp](https://hub.docker.com/repository/docker/pavics/crim-jupyter-nlp)

The notebooks associated to each specific image are found on this repo, on their corresponding notebook sub-folder.

Also, a YAML configuration file can be found for each image, containing a list of parameters used 
by the [deploy_data_specific_image script](https://github.com/bird-house/pavics-jupyter-base/blob/master/scheduler-jobs/deploy_data_specific_image)
on the [bird-house/pavics-jupyter-base repo](https://github.com/bird-house/pavics-jupyter-base). 
This script is used to download and update the image's associated notebooks that should be available on 
the JupyterLab environment for DACCS.

## Release Procedure

1. Update the relevant `CHANGELOG.md` file with added/removed/updated features and/or fixes.
   - The title should correspond to an appropriate semantic version for applied changes.
   - Ensure that the date corresponds to when the PR will be merged.
2. Merge the PR once approved by reviewers.
3. Tag the new version with the appropriate image prefix.
   - ex: if the `type` is `eo` image updated to `x.y.z`, the tag should be `eo-x.y.z`.
4. Validate that the build was auto-triggered on [DockerHub](https://hub.docker.com/repositories/pavics).
   - the build should be under the appropriate `pavics/crim-jupyter-[type]` repository with the specified `x.y.z` tag.
   - the `latest` tag should also be updated from merging the PR
5. Add the new entries 
   (i.e.: [here](https://github.com/bird-house/birdhouse-deploy/blob/8218166d5c8c7163293a656930ff85762eff4b60/birdhouse/env.local.example#L265-L280))
   for the relevant [`env.local`](https://github.com/bird-house/birdhouse-deploy/blob/master/birdhouse/env.local.example)
   file of the specific server instance that should offer new versions.
   - Add the `DOCKER_NOTEBOOK_IMAGES` entry as `pavics/crim-jupyter-[type]:[x.y.z]`.
   - Add the `JUPYTERHUB_IMAGE_SELECTION_NAMES` shortcut name for the image (note: must be the same index position).
6. Follow the specific server instance's release procedure to make the images available.

## Internal References

Relevant CRIM Confluence pages:

- [UC10 - Notebooks](https://crim-ca.atlassian.net/wiki/spaces/DAC/pages/9962723)
  - [Flavours and minimum notebook environment](https://crim-ca.atlassian.net/wiki/spaces/DAC/pages/9962214)
  - [Installing additional libraries](https://crim-ca.atlassian.net/wiki/spaces/DAC/pages/9962205)
  - [Jupyter images build flow](https://crim-ca.atlassian.net/wiki/spaces/DAC/pages/9963140)
  - [Jupyter images hierarchy](https://crim-ca.atlassian.net/wiki/spaces/DAC/pages/9962529)
