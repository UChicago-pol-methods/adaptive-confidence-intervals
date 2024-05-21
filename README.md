<h1 align="center">Adaptive Confidence Intervals</h1>

Models for paper [_Confidence Intervals for Policy Evaluation in Adaptive Experiments_](https://arxiv.org/abs/1911.02768).

# R Package Adaptation

We have adjusted and extended the simulation originally provided by [Hadad, Vitor, et al. (2021)](https://arxiv.org/abs/1911.02768) to focus on the methods relevant to our `banditsCI` R package: uniform and two-point estimators. The original Python simulation code is accessible [here](https://github.com/gsbDBI/adaptive-confidence-intervals/blob/master/experiments/main/simulations.ipynb).

Our updated version of Python simulation code is accessible here:
- [experiments/main/simulation.ipynb](https://github.com/UChicago-pol-methods/adaptive-confidence-intervals/blob/non_contextual_replication/experiments/main/simulations.ipynb)

Our replication in R can be reviewed here:
- [Simulation with Python Experiment Data - R Markdown: experiments/main/results/Simulation_with_Python_experiment_data.Rmd](https://github.com/UChicago-pol-methods/adaptive-confidence-intervals/blob/non_contextual_replication/experiments/main/results/Simulation_with_Python_experiment_data.Rmd)
- [R Script for Simulation: experiments/main/results/Simulation_with_Python_experiment_data.R](https://github.com/UChicago-pol-methods/adaptive-confidence-intervals/blob/non_contextual_replication/experiments/main/results/Simulation_with_Python_experiment_data.R)
- [Rendered PDF of R Simulation Results: experiments/main/results/Simulation_with_Python_experiment_data.pdf](https://github.com/UChicago-pol-methods/adaptive-confidence-intervals/blob/non_contextual_replication/experiments/main/results/Simulation_with_Python_experiment_data.pdf)

Our R simulations have confirmed that the results are consistent with those generated by the original Python code, specifically in terms of the main effect and contrasts using the separate method. It should be noted that the Python code does not include contrasts using a combined method, and thus comparisons in this aspect are not applicable.

---------------------------------------------
The following is the original README.md:

# Overview

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
