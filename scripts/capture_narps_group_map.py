#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Center for Open Neuroscience
# SPDX-License-Identifier: Apache-2.0
"""Capture the current example together with its matched R2/R3 spatial inputs.

Accepts the same explicit retained-capture arguments as extract_narps_spatial.py.
The example cannot be refreshed independently of its shared provenance binding.
"""
from extract_narps_spatial import main

if __name__ == '__main__':
    main()
