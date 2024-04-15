library(banditsCI)
setwd(dirname(rstudioapi::getSourceEditorContext()$path))
gammahat <- as.matrix(read.csv('scores.csv', header = FALSE))
probs_array <- as.matrix(read.csv('probs.csv', header = FALSE))

## import arms and rewards as well, check the sample mean naive.

set.seed(123)

policy1_main <- list(
  matrix(
    c(rep(1, nrow(gammahat)), rep(0, nrow(gammahat)), rep(0, nrow(gammahat))),
    nrow = nrow(gammahat)),
  matrix(
    c(rep(0, nrow(gammahat)), rep(1, nrow(gammahat)), rep(0, nrow(gammahat))),
    nrow = nrow(gammahat)),
  matrix(
    c(rep(0, nrow(gammahat)*(ncol(gammahat)-1)), rep(1, nrow(gammahat))),
    nrow = nrow(gammahat)))

policy1 <- list(
  matrix(
    c(rep(1, nrow(gammahat)), rep(0, nrow(gammahat)), rep(0, nrow(gammahat))),
    nrow = nrow(gammahat)),
  matrix(
    c(rep(0, nrow(gammahat)), rep(1, nrow(gammahat)), rep(0, nrow(gammahat))),
    nrow = nrow(gammahat))
  )

policy0 <- matrix(
    c(rep(0, nrow(gammahat)*(ncol(gammahat)-1)), 
      rep(1, nrow(gammahat))),
    nrow = nrow(gammahat))

# main effects
output_estimates(policy1 = policy1_main,
                 gammahat = gammahat,
                 probs_array = probs_array,
                 floor_decay = 0.7)

output_estimates(policy1 = policy1,
                 gammahat = gammahat,
                 probs_array = probs_array,
                 floor_decay = 0.7)

# Get estimates for treatment effects of policies as contrast to control
# \delta(w_1, w_2) = E[Y_t(w_1) - Y_t(w_2)].
# In Hadad et al. (2021) there are two approaches.
## The first approach: use the difference in AIPW scores as the unbiased scoring
## rule for \delta (w_1, w_2)
### The following function implements the first approach by subtracting policy0,
### the control arm, from all the arms in policy1, except for the control arm
### itself.
out_full_te1 <- output_estimates(
  policy0 = policy0,
  policy1 = policy1,
  contrasts = "combined",
  gammahat = gammahat,
  probs_array = probs_array,
  floor_decay = 0.7)

## The second approach takes asymptotically normal inference about
## \delta(w_1, w_2): \delta ^ hat (w_1, w_2) = Q ^ hat (w_1) - Q ^ hat (w_2)
out_full_te2.1 <- output_estimates(
  policy0 = policy1_main[[1]],
  policy1 = list(policy1_main[[3]]),
  contrasts = "separate",
  gammahat = gammahat,
  probs_array = probs_array,
  floor_decay = 0.7)
out_full_te2.1

out_full_te2.2 <- output_estimates(
  policy0 = policy1_main[[2]],
  policy1 = list(policy1_main[[3]]),
  contrasts = "separate",
  gammahat = gammahat,
  probs_array = probs_array,
  floor_decay = 0.7)
out_full_te2.2

# Compare the two approaches for uniform and non_contextual_two_point
compare_methods <- function(out_full_te1, out_full_te2) {
  # Initialize an empty data frame to hold the comparison data
  comparison_df <- data.frame(method = character(),
                              estimate = numeric(),
                              std_error = numeric(),
                              contrasts = character(),
                              policy = integer(),
                              from = character(),
                              stringsAsFactors = FALSE)

  # Function to process and append data
  process_data <- function(data, policy_num, contrasts, from) {
    for (method in c("uniform", "non_contextual_twopoint")) {
      if (method %in% rownames(data)) {
        row <- data.frame(
          method = method,
          estimate = data[method, "estimate"],
          std_error = data[method, "std.error"],
          contrasts = contrasts,
          policy = policy_num,
          from = from,
          stringsAsFactors = FALSE
        )
        comparison_df <<- rbind(comparison_df, row)
      }
    }
  }

  # Process and append data for each subset and condition
  process_data(out_full_te1[[1]], 1, "combined", "out_full_te1[[1]]")
  process_data(out_full_te1[[2]], 2, "combined", "out_full_te1[[2]]")
  process_data(out_full_te2[[1]], 1, "separate", "out_full_te2[[1]]")
  process_data(out_full_te2[[2]], 2, "separate", "out_full_te2[[2]]")

  return(comparison_df)
}


comparison_df <- compare_methods(out_full_te1, out_full_te2)
print(comparison_df)



