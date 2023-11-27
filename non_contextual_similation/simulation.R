library(reticulate)
use_condaenv("adaptive_CI", required = TRUE)

setwd(dirname(rstudioapi::getSourceEditorContext()$path))
gammahat <- read.csv('../experiments/main/results/scores.csv')  # make sure gammahat is scores
ys <- read.csv('../experiments/main/results/ys.csv')
xs <- read.csv('../experiments/main/results/arms.csv')
muhat <- read.csv('../experiments/main/results/muhat.csv')
probs <- read.csv('../experiments/main/results/probs.csv') # is this the correct probs we want?
rewards <- read.csv('../experiments/main/results/rewards.csv') # what's the difference between rewards and muhat?

A <- dim(gammahat)[1]
K <- dim(gammahat)[2]

## Functions
#source('adaptive_utils.R')
