library(banditsCI)
gammahat <- as.matrix(read.csv('scores.csv', header = FALSE))
probs_array <- as.matrix(read.csv('probs.csv', header = FALSE))

policy1 <- list(
  matrix(
    c(rep(0, nrow(gammahat)), rep(1, nrow(gammahat)), rep(0, nrow(gammahat))),
    nrow = nrow(gammahat)),
  matrix(
  c(rep(0, nrow(gammahat)*(ncol(gammahat)-1)), rep(1, nrow(gammahat))),
  nrow = nrow(gammahat)))

policy0 <- matrix(
    c(rep(1, nrow(gammahat)), rep(0, nrow(gammahat)*(ncol(gammahat)-1)) ),
    nrow = nrow(gammahat))

output_estimates(policy1 = policy1,
                 gammahat = gammahat,
                 probs_array = probs_array,
                 floor_decay = 0.7)
