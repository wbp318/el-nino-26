# correlate.R — relationships among the three drivers (NAO, ENSO, sunspots).
#
# Works today, no target needed: correlation matrix + lead/lag cross-correlation,
# reported on BOTH the full record and the clean 1950+ window (they can differ
# because pre-1950 NAO/ENSO are reconstructed).
#
# Base R only. Run:  Rscript R/correlate.R
# Outputs: results/correlation_full.csv, results/correlation_1950plus.csv,
#          results/ccf_<pair>.png

root <- normalizePath(file.path(dirname(sub("^--file=", "",
          grep("^--file=", commandArgs(FALSE), value = TRUE)[1])), ".."),
          mustWork = FALSE)
if (is.na(root) || root == "") root <- normalizePath("..", mustWork = FALSE)

panel_path <- file.path(root, "data", "processed", "panel_monthly.csv")
out_dir    <- file.path(root, "results")
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

df <- read.csv(panel_path, stringsAsFactors = FALSE)
df$date <- as.Date(df$date)

drivers <- c("nao_cpc", "nao_station", "enso_oni", "enso_nino34", "ssn_monthly")
drivers <- drivers[drivers %in% names(df)]

corr_report <- function(data, label, file) {
  cm <- cor(data[, drivers], use = "pairwise.complete.obs")
  cat("\n== Correlation matrix (", label, ") ==\n", sep = "")
  print(round(cm, 3))
  write.csv(round(cm, 4), file)
  invisible(cm)
}

corr_report(df, "full record", file.path(out_dir, "correlation_full.csv"))
corr_report(df[df$clean_1950plus == "True" | df$clean_1950plus == TRUE, ],
            "1950+ window", file.path(out_dir, "correlation_1950plus.csv"))

# --- lead/lag cross-correlation for the three conceptual pairs ----------------
# NAO uses the live CPC series; ENSO uses ONI; sunspots monthly.
pairs <- list(
  c("nao_cpc",     "ssn_monthly"),
  c("enso_oni",    "ssn_monthly"),
  c("nao_cpc",     "enso_oni")
)
maxlag <- 24  # months

for (p in pairs) {
  a <- df[[p[1]]]; b <- df[[p[2]]]
  ok <- is.finite(a) & is.finite(b)
  if (sum(ok) < 3 * maxlag) next
  fname <- file.path(out_dir, sprintf("ccf_%s_vs_%s.png", p[1], p[2]))
  png(fname, width = 900, height = 600, res = 110)
  cc <- ccf(a[ok], b[ok], lag.max = maxlag, plot = TRUE,
            main = sprintf("CCF: %s vs %s", p[1], p[2]),
            na.action = na.pass)
  dev.off()
  best <- cc$lag[which.max(abs(cc$acf))]
  cat(sprintf("CCF %-12s vs %-12s : peak |r|=%.3f at lag %+d months  -> %s\n",
              p[1], p[2], max(abs(cc$acf)), best, basename(fname)))
}

cat("\nDone. Matrices + CCF plots written to:", out_dir, "\n")
cat("Note: the NAO<->sunspot link is known to be weak; treat outputs as a\n",
    "sanity gate, not a result claim, until a target variable is set.\n")
