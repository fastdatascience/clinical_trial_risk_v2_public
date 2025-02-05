#!/bin/bash

# This function runs when the -test argument is provided
run_tests() {
  echo "Running tests..."
  python tests/test.py
}

# This function runs when the -build argument is provided
build_project() {
  echo "Building project..."
  pip install .
}

build_and_run() {
    build_project
    run_tests
}

# Check the first argument passed to the script
case "$1" in
  -test)
    run_tests
    ;;
  -build)
    build_project
    ;;
  *)
    build_and_run
    ;;
esac
