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
conda init 
. ~/.bashrc
conda activate birdy
python <python_file.py>
```

# Model flair
The "ner-large" flair model is included in the image build. This means that the models will not be updated to the latest.
If the latest is needed, the image will have to be rebuilt with --no-cache. 
