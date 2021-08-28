# TestLoggingPractice
## Description
This repository contains the dataset and scripts for replicating our research regarding the logging practice in test code.

## RQ1

This directory contains the scripts for getting the data for rq1, includes logging statements number per file, dynamic variable numbers per logging statement and static text length per logging statement. 

How to run this script:

1. Install postgresql and python 3.6+.
2. Install libraries listed in [requirements](https://github.com/senseconcordia/TestLoggingPractice/blob/main/RQ2/mstracker/requirements.txt).
3. Install [cloc](https://github.com/AlDanial/cloc) and [srcML](https://www.srcml.org/).
4. Download the studied subjects (source code in head) to local.
5. Configure the database settings in config.py.
6. Run clone_and_save_project.py to initilize the database.
7. Run main.py to get log numbers per file, run log_util.py to get details about the dynamic variable numbers and static text lengths of the logging statements (you need to comment and comment out some source code lines indicated in file.py and log.py).

## RQ2

This directory contains the scripts that are used to analyze the histories of the studied repositories.

How to run this script:

1. Install postgresql and python 3.6+.
2. Install libraries listed in requirements.txt.
3. Install [cloc](https://github.com/AlDanial/cloc) and [srcML](https://www.srcml.org/).
4. Clone the studied repositories to a local path.
5. Configure the database settings in config.py.
6. Run clone_and_save_project.py to initilize the database.
7. Run main.py and enter *1* to detect all the commits in the repositories.

## RQ3

This directory contains the data regarding the firehouse email survey and the result of labelling of two of the researchers.

## RQ4

This directory contains the scripts about how we extarct the log lines from the outputs and sample the log lines. It also contains the data regarding all the extrated log lines, the results of labelling the relationship and usefulness of the test logs.

## Metrics Analysis

The scripts for analyzing the metrics with regard to RQ1 and RQ2 are presented in folder metrics_analysis.

Please refer to the filenames for the purpose of each script.

## Database data

Please refer to [here](https://drive.google.com/drive/folders/1hmMKE_k5f9nAv70ToqTPjx30TcwcBOAF?usp=sharing) for the generated database data for RQ1 and RQ2.
