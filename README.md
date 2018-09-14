# neuro/anat datatype validator

Brainlife uses this code to validate and normalize input datasets uploaded by users to make sure that the content and format of the data matches the specified Brainlife datatype.

Currently this App performs following checks

* check to see if .tck header can be parsed
* check fiber count is non-0.

This service is not meant to be executed outside Brainlife.

In the future, this repo might be incooporated into to [brain-life/datatypes repo](https://github.com/brain-life/datatypes)

### Authors
- Soichi Hayashi (hayashis@iu.edu)

### Project directors
- Franco Pestilli (franpest@indiana.edu)

### Funding 
[![NSF-BCS-1734853](https://img.shields.io/badge/NSF_BCS-1734853-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1734853)
[![NSF-BCS-1636893](https://img.shields.io/badge/NSF_BCS-1636893-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1636893)
