FROM birdhouse/pavics-jupyter-base:0.1.0

COPY environment.yml /environment.yml

# update env "birdy"
RUN conda env update -f /environment.yml
