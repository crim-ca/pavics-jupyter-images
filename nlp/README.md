## DACCS - NLP docker image

This image is able tu run all the python files required for the nlp notbooks.
It has an installation of tree-tagger and java librarie needed for tree-tagger by download and extraction.

To build and run the project :

### 1 .Build docker image
```bash
cd path/to/nlp
docker build -t nlp .
```
### 2. Run the docker image 
```bash
sudo docker run -it --rm nlp bash
```
### 2.1 File execution after running the image
```bash
source active birdy
cd nl2query 
python3 <python_file.py>
```
