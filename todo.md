
## to-do:

- app / active learning
    - general
        - [x] handle different column names
    - learn
        - [x] labelled samples dataframe interactive table
        - [x] previous / next / edit options for learning samples
        - [x] reformat active learning sample cards to be text instead of json
        - [x] show which dataset is being used    
        - [x] link to cards from dataframe
            - [x] ability to pass parameter to learn/<idl>-<idr> route
        - [x] if previous submit is revised, update json
        - [x] re-implenet active-dict to not relearn from already-learned samples
        - [ ] prettier presentation of counter in learn page
        - [x] ignore label="unknown" 
    - datasets
        - [x] show cached files on load page
        - [x] if no file is selected, use first in glob
    - plots
        - [ ] ability to select features
        - [x] axis labels
    - data 
        - [ ] handling multiple csv files
        - [x] select previously uploaded file
    - labels
        - [ ] on labels page, ability to hover of comparison to see names/addresses/etc
    - cached labelled samples
        - [ ] cache file name should be hash of dataset name
        - [x] clear cache option
        - [ ] upload labels option
        - [ ] download labels option
    - bugs
        - [x] retrain requires at least one sample in each class
        - [x] with each hard refresh, cached samples is popped
        - [x] redirect to load page if dataset is not loaded
        - [x] if user attempts to go to different page when dataset is not loaded, show warning
        - [] if user does not select a file in /load, then submit errors; it should alert that file was not selected
        - [] if user does not select an option in /learn, then submit errors; it should alert that file was not selected
        - [x] make sure order of labels is consistent between .predict() and .predict_proba() and that probabilities 
        are always probability of "Yes"

    - dockerize
        - [x] create dockerfile / .dockerignore
    - misc
        - [x] flask api logging
        - [x] linting
    - refactor
- algos
    - [x] add more blocking algos
    - [ ] add other ML algos
- sql
    - [ ] mysql database
- parallelize (ray / dask)
    - [ ] parallelize blocks? 
- output
    - [x] predictions page
    - [x] download option
- record linkage option
- make sure readme quickstart works


## Run Flask APP with Docker

```
# First, clone the repo
1. git clone https://github.com/chansooligans/deduper.git
2. cd deduper

# Build Docker image
3. docker build -t deduper:latest .

# Run
4. docker run -t -d --rm --name deduper -p 8080:8081 deduper 
5. Go to http://127.0.0.1:8080/load

(test dataset will be pre-loaded)
```

## quickstart dashboard without docker

run `make serve`