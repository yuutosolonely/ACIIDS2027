"""Cross-fitted conditional evidence for unsupervised cell-level error detection.

Detectors receive only the observed (dirty) table. Clean values and error masks are
loaded separately and are consumed only by `cced.metrics` and explicitly labelled
oracle diagnostics.
"""
