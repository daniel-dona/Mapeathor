 [![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)  
 [![Generic badge](https://img.shields.io/badge/Status-Developing-yellow)](https://shields.io/)
 [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/oeg-upm/Mapeathor/blob/master/LICENSE)
 [![version](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/release/python-360/)

<p align="center"> 
 <img src="./imgs/Square_logo_mapeathor.png" alt="workflow" width="150"/> 
</p>


# Mapeathor
#### Mapeathor translates your mapping rules specified in spreadsheets to a mapping language.  

## How it works:  
Mapeathor is a simple spreadsheet parser able to generate mapping rules in three mapping languages: R2RML, RML (with extension to functions from FnO) and YARRRML. It takes the mapping rules expressed in a spreadsheet and transforms them into the desired language. The spreadsheet template is designed to facilitate the mapping rules' writting, with the aim of being language independent, and thus, lowering the barrier of generating mappings for non-expert users. 

<p align="center"> 
 <img src="./imgs/general_schema.png" alt="workflow" width="600"/> 
</p>

## Example:    
### First Step: Fill the xlsx template with your own information.  
The template has five mandatory sheets, *Prefixes, Source, Subject PredicateObjectMap* and *Functions*. The last one can be left blank in case there are no functions.
#### Prefixes:   
<p align="center"> 
 <img src="./imgs/sheet_prefix.png" alt="prefixes" width="300"/> 
</p>

#### Source:  
<p align="center"> 
 <img src="./imgs/sheet_source.png" alt="source" width="370"/> 
</p>
 
#### Subject:    
<p align="center"> 
 <img src="./imgs/sheet_subject.png" alt="subject" width="460"/> 
</p>

#### PredicateObjectMaps:    
<p align="center"> 
 <img src="./imgs/sheet_pom.png" alt="pom" width="800"/> 
</p>

#### Functions:
<p align="center"> 
 <img src="./imgs/sheet_function.png" alt="function" width="400"/> 
</p>

### Second Step: Choose the output language that you prefer. 
Here you can see the [Available Languages](./templates).

### Third Step: Execute these commands:
With python:
```BASH
# Clone the repository
$ git clone https://github.com/oeg-upm/Mapeathor

# Install the needed packages
$ cd Mapeathor/code/
$ pip3 install -r requirements.txt

# How to execute it
$ python3 main.py -i /Mapeathor/data/YOURFILE -l [RML | R2RML | YARRRML]

# Help Menu
$ python3 main.py -h 

# Example
$ python3 main.py -i /Mapeathor/data/default.xlsx -l yarrrml
```
With docker:
```BASH
# Clone the repository
$ git clone https://github.com/oeg-upm/Mapeathor

# Install the docker image with docker-compose
$ docker-compose up -d

# Copy the XLSX files to data repository
$ cp yourfiles ./data/

# Execute it
$ docker exec -it mapeathor ./run.sh /Mapeathor/data/YOURFILE [RML | R2RML | YARRRML]

# Results will appear in result folder
```
### Publications
Iglesias-Molina, A., Chaves-Fraga, D., Priyatna, F., & Corcho, O. (2019). Towards the Definition of a Language-Independent Mapping Template for Knowledge Graph Creation. *In Proceedings of the Third International Workshop on Capturing Scientific Knowledge co-located with the 10th International Conference on Knowledge Capture (K-CAP 2019)* (pp. 33-36). [Online version](https://sciknow.github.io/sciknow2019/papers/SciKnow_2019_paper_4.pdf)

### Authors and contact
- [Ana Iglesias-Molina](https://github.com/anaigmo) (ana.iglesiasm@upm.es)
- [Luis Pozo](https://github.com/w0xter) (luis.pozo@upm.es)
