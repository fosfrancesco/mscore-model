*(this repository is currently under development)* 

# Music-score Model

Set of classes for Python3 to efficiently model musical scores in order to easily extract information from them. 
It uses the library music21 for musicxml import and export.

The model of the score is organized in two layers:
- musical content
- engraving

For more details on the model see the chapter 2 of my thesis: "The Musical Score: a challenging goal for automatic music transcription"

## Install mscore-model
It can be easily installed from git by running

    python -m pip install git+https://github.com/fosfrancesco/mscore-model
    
or if you have also python 2 installed

    python3 -m pip install git+https://github.com/fosfrancesco/mscore-model
