FROM birdhouse/pavics-jupyter-base:0.1.0

# must update as root, because of a permission error with pip
USER root

COPY environment.yml /environment.yml

# update env "birdy"
# use umask 0000 so that the files for the updated environment are usable by the user for the jupyter-conda-extension
RUN umask 0000 && conda env update -f /environment.yml

# specify user because of problem running start-notebook.sh when being root
USER jenkins

# start notebook in conda environment to have working jupyter extensions
CMD ["conda", "run", "-n", "birdy", "/usr/local/bin/start-notebook.sh"]
