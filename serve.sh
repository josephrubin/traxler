#!/bin/bash

# Serve the website locally.
_main() {
    (cd website && python3 -m http.server)
}

_main
