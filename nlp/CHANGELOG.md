Changes
=======

Unreleased (latest)
===================

- n/a

0.5.0 (2023-12-13)
===================

Changes:
--------
- Update NLU demo notebook with latest pipeline improvements and a STAC wrapper to convert NL queries to STAC requests.
- Add `duckling` installation in the Docker to allow running it as child process rather than sibling Docker service.
- Update base image version in Dockerfile
- Add `mamba` cache cleanup to reduce image size

Fixes:
------
- Fix dependencies to make them functional across multiple Python versions.

0.4.0 (2022-12-23)
===================

Changes:
--------
- Use `mamba` instead of `conda` for environment installation

Fixes:
------
- na

0.3.3 (2022-12-13)
===================

Changes:
--------
- Update base image version in Dockerfile

Fixes:
------
- na

0.3.2 (2022-02-17)
===================

Changes:
--------
- Added `notebooks/stac_wrapper` folder

Fixes:
------
- na

0.3.1 (2021-09-14)
===================

Changes:
--------
- Update base image version in Dockerfile

Fixes:
------
- na

0.3.0 (2021-07-21)
===================

Changes:
--------
- Dockerfile with the tree-tagger installation has been added
- environment.yml has been updated to contain the necessary dependencies.
- nl2query contains all the nlp notebook dependencies.
- Added tutorial notebook to showcase nl2query.
- Added nl2q_eval folder and files
- Added tests

Fixes:
------
- na

0.2.1 (2021-06-01)
===================

Changes:
--------
- na, test of renovate bot from `pavics-jupyter-base` master commit

Fixes:
------
- na
 
0.2.0 (2021-05-11)
===================

Changes:
--------
- Custom notebooks specific to the environment can now be added to the docker image

Fixes:
------
- na

0.1.0 (2021-02-22)
===================

Changes:
--------
- Updated basic Dockerfile and added basic environment.yml

Fixes:
------
- na

0.0.2 (2020-12-09)
===================

Changes:
--------
- Updated tag, only for cascading build test purposes

Fixes:
------
- na

0.0.1 (2020-12-04)
===================

Changes:
--------
- Added dummy `Dockerfile`

Fixes:
------
- na
