## PAVICS NLP Docker Image

This image contains all the nlp notebook dependencies.


To build and run the project :

### 1. Build docker image
```bash
docker build -t crim-jupyter-nlp .
```
### 2. Run the docker image 
```bash
docker run -it --rm crim-jupyter-nlp bash
```
### 2.1 File execution inside the running image
```bash
source activate birdy
python <python_file.py>
```
