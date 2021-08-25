# mstracker
Characterizing monitoring statement practice for testing

# Motivation 
Prior work studied the characteristics of logging practices in C/C++ projects (Yuan et al., 2012), Java projects (Chen et al., 2017; Li et al., 2017a, 2017b), and Android projects (Zeng et al., 2019). Such projects usually ignore the difference between production and test logging (Yuan et al., 2012; Chen et al., 2017; Zeng et al., 2019), or only consider production logging (Li et al., 2017a, 2017b). 

Test logging provides important testing runtime information to help developers understand the status of test results and debug test failures. Production logging and testing logging may have different purposes (e.g., to spot test failures), thus they may follow different practices of development and maintenance. Therefore, this work aims to understand the characteristics of logging practices in the testing code.

# Research Questions:
## RQ1: What are the differences between the monitoring statements in the test and production code?
- Log number/density (overall & per-file distribution)
- Difference between unit test and source code for the same classes (per-file comparison)
- Log level (overall distribution)
- Log length, number of log variables (overall distribution)
- Other logging characteristics (logging guard, containing block, etc.)

## RQ2: What are the differences between the maintenance efforts of the monitoring statements in the test and production code?
- Change frequency (add/modify/delete)
- Changed content (text/variable/level)
- Consistent log changes (change with other code) or after-thought changes (independent log changes)
- Change rate compared to lines of code / lines of logging code
- Change rate compared to other code changes

## RQ3: How does test logging complement/overlap/co-evolve with production logging?
- Would test logging duplicate with production logging?
- What additional information can test logging provide?

## RQ4: Why do developers use test logging?
- Survey developers who added test logging statements.

# References
Yuan, Ding, Soyeon Park, and Yuanyuan Zhou. "Characterizing logging practices in open-source software." Proceedings of the 34th International Conference on Software Engineering. IEEE Press, 2012.

Chen, Boyuan, and Zhen Ming Jack Jiang. "Characterizing logging practices in Java-based open source software projects–a replication study in Apache Software Foundation." Empirical Software Engineering 22.1 (2017): 330-374.

Zeng, Yi, et al. "Studying the characteristics of logging practices in mobile apps: a case study on F-Droid." Empirical Software Engineering (2019): 1-41.

Li, Heng, et al. "Towards just-in-time suggestions for log changes." Empirical Software Engineering 22.4 (2017a): 1831-1865.

Li, Heng, Weiyi Shang, and Ahmed E. Hassan. "Which log level should developers choose for a new logging statement?." Empirical Software Engineering 22.4 (2017b): 1684-1716.
