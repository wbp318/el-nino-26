# model.R — predictive scaffold for whenever a target variable lands.
#
# The three drivers are predictors; the predictand ("target") is undecided
# (Amelia's numbers, or a named weather series). This file provides:
#   - build_design(): adds lagged predictors to the monthly panel
#   - fit_model():    time-ordered train/test fit of target ~ lagged drivers
# Until `target` is populated (via Python build_panel.merge_target or by editing
# the CSV), main() just reports that the target is empty and exits cleanly.
#
# Base R only. Run:  Rscript R/model.R

root <- normalizePath(file.path(dirname(sub("^--file=", "",
          grep("^--file=", commandArgs(FALSE), value = TRUE)[1])), ".."),
          mustWork = FALSE)
if (is.na(root) || root == "") root <- normalizePath("..", mustWork = FALSE)

panel_path <- file.path(root, "data", "processed", "panel_monthly.csv")

load_panel <- function() {
  df <- read.csv(panel_path, stringsAsFactors = FALSE)
  df$date <- as.Date(df$date)
  df
}

lag_vec <- function(x, k) c(rep(NA, k), head(x, -k))

# Add lags 0..maxlag for each predictor (drivers lead the target).
build_design <- function(df, predictors, maxlag = 6) {
  for (p in predictors) {
    for (k in 0:maxlag) {
      df[[sprintf("%s_l%d", p, k)]] <- lag_vec(df[[p]], k)
    }
  }
  df
}

# Time-ordered fit: first `train_frac` of rows train, remainder tests.
fit_model <- function(df, target_col = "target",
                      predictors = c("nao_cpc", "enso_oni", "ssn_monthly"),
                      maxlag = 6, train_frac = 0.8) {
  stopifnot(target_col %in% names(df))
  d <- build_design(df, predictors, maxlag)
  feat <- grep("_l[0-9]+$", names(d), value = TRUE)
  d <- d[stats::complete.cases(d[, c(target_col, feat)]), ]
  if (nrow(d) < 2 * length(feat)) stop("not enough complete rows to fit")

  n <- nrow(d); cut <- floor(n * train_frac)
  train <- d[seq_len(cut), ]; test <- d[(cut + 1):n, ]
  f <- stats::as.formula(paste(target_col, "~",
                               paste(feat, collapse = " + ")))
  fit <- stats::lm(f, data = train)
  pred <- stats::predict(fit, newdata = test)
  rmse <- sqrt(mean((test[[target_col]] - pred)^2))
  list(fit = fit, rmse_test = rmse, n_train = nrow(train), n_test = nrow(test))
}

main <- function() {
  df <- load_panel()
  if (all(is.na(df$target))) {
    cat("`target` column is empty — no predictand set yet.\n",
        "Populate it (Python: build_panel.merge_target, or edit the CSV) then\n",
        "re-run. Scaffold is ready: fit_model(load_panel()).\n", sep = "")
    return(invisible(NULL))
  }
  res <- fit_model(df)
  cat(sprintf("Fitted target ~ lagged drivers. train n=%d, test n=%d, test RMSE=%.4f\n",
              res$n_train, res$n_test, res$rmse_test))
  print(summary(res$fit))
}

if (sys.nframe() == 0) main()
