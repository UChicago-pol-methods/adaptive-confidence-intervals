<h1 align="center">Non Contextual Replication of Adaptive Confidence Intervals</h1>

# R Package Adaptation

We have adjusted the simulation code originally provided by [Hadad, Vitor, et al. (2021)](https://arxiv.org/abs/1911.02768) to focus on only on the estimation methods relevant to our `banditsCI` R package: uniform and two-point estimators. The original Python simulation code is accessible [here](https://github.com/gsbDBI/adaptive-confidence-intervals/blob/master/experiments/main/simulations.ipynb).

Our updated version of Python simulation code is accessible here:
- [experiments/main/simulation.ipynb](https://github.com/UChicago-pol-methods/adaptive-confidence-intervals/blob/non_contextual_replication/experiments/main/simulations.ipynb)
We simulate the experimental data in python, analyze it using the original python code, and then export identical data to be analyzed in R. 

Our analysis script in R can be reviewed here:
- R Markdown: [experiments/main/results/Simulation_with_Python_experiment_data.Rmd](https://github.com/UChicago-pol-methods/adaptive-confidence-intervals/blob/non_contextual_replication/experiments/main/results/Simulation_with_Python_experiment_data.Rmd)
- Rendered PDF: [experiments/main/results/Simulation_with_Python_experiment_data.pdf](https://github.com/UChicago-pol-methods/adaptive-confidence-intervals/blob/non_contextual_replication/experiments/main/results/Simulation_with_Python_experiment_data.pdf)

The objective is to compare the estimates produced in the [python notebook](https://github.com/UChicago-pol-methods/adaptive-confidence-intervals/blob/non_contextual_replication/experiments/main/simulations.ipynb) (cells 8 and 9) to those in the R script, reported below:

|method                  |  estimate| std_error|contrasts   |policy |
|:-----------------------|---------:|---------:|:-----------|:------|
|non_contextual_twopoint | 0.8267759| 0.1125030|main effect |0      |
|non_contextual_twopoint | 0.9138038| 0.0580545|main effect |1      |
|non_contextual_twopoint | 1.1012259| 0.0104059|main effect |2      |
|non_contextual_twopoint | 0.3891761| 0.2723742|combined    |(0,1)  |
|non_contextual_twopoint | 0.4351515| 0.2386683|combined    |(0,2)  |
|non_contextual_twopoint | 0.2744500| 0.1129833|separate    |(0,1)  |
|non_contextual_twopoint | 0.1874221| 0.0589797|separate    |(0,2)  |
|uniform                 | 0.7198237| 0.2557261|main effect |0      |
|uniform                 | 0.7106815| 0.2011189|main effect |1      |
|uniform                 | 1.1055150| 0.0106840|main effect |2      |
|uniform                 | 0.3856913| 0.2559502|combined    |(0,1)  |
|uniform                 | 0.3948335| 0.2014011|combined    |(0,2)  |
|uniform                 | 0.3856913| 0.2559491|separate    |(0,1)  |
|uniform                 | 0.3948335| 0.2014024|separate    |(0,2)  |

We do find that the estimates are identical. 


---------------------------------------------
The following is the original README.md:

# Overview

Models for paper [_Confidence Intervals for Policy Evaluation in Adaptive Experiments_](https://arxiv.org/abs/1911.02768).

*Note: For any questions, please file an issue.*

Adaptive experimental designs can dramatically improve efficiency in randomized trials. But adaptivity also makes offline policy inference challenging. In the paper [_Confidence Intervals for Policy Evaluation in Adaptive Experiments_](https://arxiv.org/abs/1911.02768), we propose a class of estimators that lead to asymptotically normal and consistent policy evaluation. This repo contains reproducible code for the results shown in the paper. 

We organize the code into two directories:
- [./adaptive_CI](https://github.com/gsbDBI/adaptive-confidence-intervals/tree/master/adaptive_CI) is a Python module for doing adaptive inference developed in the paper. This directory also contains other methods for developing confidence intervals using adaptive data that are compared in the paper, including:
   - naive sample mean using the usual variance estimate;
   - non-asymptotic confidence intervals for the sample mean, based on the method of time-uniform confidence sequences described in [Howard et al. (2021)](https://arxiv.org/pdf/1810.08240.pdf);
   - w-decorrelation confidence intervals, based on method described in [Deshpande et al. (2017)](https://arxiv.org/pdf/1712.06695.pdf).

- [./experiments](https://github.com/gsbDBI/adaptive-confidence-intervals/tree/master/experiments) contains python scripts to run experiments and make plots shown in the paper, including:
   - collecting multi-armed bandits data with a Thompson sampling agent;
   - doing adaptive inference using collected data;
   - saving results and making plots. 

# Development setup

We recommend creating the following conda environment for computation.
```bash
conda create --name adaptive_CI python=3.7
conda activate adaptive_CI
python setup.py develop
```

# Acknowledgements
We are grateful for the generous financial support provided by the Sloan Foundation, Office of Naval Research grant N00014-17-1-2131, National Science Foundation grant DMS-1916163, Schmidt Futures, Golub Capital Social Impact Lab, and the Stanford Institute for Human-Centered Artificial Intelligence. Ruohan Zhan acknowledges generous support from the Total Innovation fellowship and the PayPal Innovation fellowship. In addition, we thank Steve Howard, Sylvia Klosin, Sanath Kumar Krishnamurthy and Aaditya Ramdas for helpful advice.

For reference, please cite the paper: [_Confidence Intervals for Policy Evaluation in Adaptive Experiments_](https://arxiv.org/abs/1911.02768).
