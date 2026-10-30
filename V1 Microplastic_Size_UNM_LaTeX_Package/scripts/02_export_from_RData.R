# Helper for Windows RStudio. NOT EXECUTED in ChatGPT's Python-only runtime.
# Purpose: identify the correct 10,833-record data frame in your Bibliometrix_Filtered.RData.
# Usage in RStudio:
#   source("scripts/02_export_from_RData.R")
#   export_mp_candidates("C:/Users/SIVI/Documents/Y3/Group Project/Case studies/Combined/Bibliometrix_Filtered.RData", "Include_Candidates.csv")
# If multiple 10,833-row dataframes exist, specify object_name to avoid a guess.
export_mp_candidates <- function(rdata_path, output_path = "Include_Candidates.csv", object_name = NULL) {
  env <- new.env(parent = baseenv())
  loaded <- load(rdata_path, envir = env)
  message("Loaded objects: ", paste(loaded, collapse = ", "))
  for (nm in loaded) {
    item <- get(nm, envir = env)
    message(nm, ": ", paste(class(item), collapse = ", "),
            if (is.data.frame(item)) paste0(" | rows=", nrow(item), " cols=", ncol(item)) else "")
  }
  if (is.null(object_name)) {
    hits <- loaded[vapply(loaded, function(nm) {
      z <- get(nm, envir = env)
      is.data.frame(z) && nrow(z) == 10833L && all(c("TI", "AB", "DI") %in% names(z))
    }, logical(1))]
    if (length(hits) != 1L) {
      stop("Found ", length(hits), " eligible 10,833-row objects. Inspect `loaded` and specify object_name explicitly; do not guess.")
    }
    object_name <- hits[[1L]]
  }
  if (!object_name %in% loaded) stop("Unknown object_name: ", object_name)
  tab <- get(object_name, envir = env)
  stopifnot(is.data.frame(tab), nrow(tab) == 10833L)
  need <- c("TI", "AB", "PY", "AU", "DI", "DT", "SO", "C1", "affiliations", "AU_UN", "AU1_UN", "RP")
  absent <- setdiff(need, names(tab))
  if (length(absent)) stop("Required columns missing: ", paste(absent, collapse = ", "),
                           ". Check the original screening export used in the project; columns must not be silently fabricated.")
  utils::write.csv(tab, file = output_path, row.names = FALSE, na = "", fileEncoding = "UTF-8")
  message("Saved ", nrow(tab), " rows to ", normalizePath(output_path, mustWork = FALSE))
  invisible(output_path)
}
