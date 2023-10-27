#!/usr/bin/env python

import argparse
import sys
import os
from os.path import relpath
import subprocess
import time

RUNTIMES_DIR = os.path.join('runtimes')
RUNTIMES_DIR = relpath(RUNTIMES_DIR).replace("\\", "/")
BENCHMARK_DIR = os.path.join('benchmarks')
BENCHMARK_DIR = relpath(BENCHMARK_DIR).replace("\\", "/")

NUM_TRIALS = 10

RUNTIMES = []
BENCHMARKS = []

TRIALS = []

def BENCHMARK(name):
  BENCHMARKS.append([name])

BENCHMARK("hello_world")
BENCHMARK("fibonacci")
BENCHMARK("for")

if sys.platform == 'win32':
  GREEN = NORMAL = RED = YELLOW = ''
else:
  GREEN = '\033[92m'
  NORMAL = '\033[0m'
  RED = '\033[91m'
  YELLOW = '\033[93m'

def green(text):
  return GREEN + text + NORMAL

def red(text):
  return RED + text + NORMAL

def yellow(text):
  return YELLOW + text + NORMAL

def get_ghost_runtimes():
  # Get the list of Ghost runtimes in alphabetical order
  for runtime in sorted(os.listdir(RUNTIMES_DIR)):
      RUNTIMES.append(os.path.join(RUNTIMES_DIR, runtime))

def run_benchmark(benchmark):
  print("Running benchmark: " + benchmark[0])

  # For each version of Ghost, run the benchmark
  # and print the results
  for runtime in RUNTIMES:
    # extract version from runtime: runtimes/ghost_v0.19.0 -> v0.19.0
    version = os.path.basename(runtime)[6:]

    print("  Ghost: " + version)
    print("  -----------------")

    # Run the benchmark NUM_TRIALS times
    for i in range(0, NUM_TRIALS):
      print("    Trial " + str(i + 1) + ": ", end='')
      sys.stdout.flush()

      # Run the benchmark
      time_start = time.time()
      result = subprocess.run([runtime, os.path.join(BENCHMARK_DIR, benchmark[0] + ".ghost")], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      time_end = time.time()

      # Calculate the elapsed time and round to 2 decimal places
      elapsed_time = round(time_end - time_start, 4)

      # Store benchmark test, runtime, and elapsed time
      TRIALS.append([benchmark[0], runtime, elapsed_time])

      # Print the result
      if result.returncode == 0:
        print(green("PASSED") + "  " + str(elapsed_time) + "s")
      else:
        print(red("FAILED"))
        print(result.stdout.decode('utf-8'))
        print(result.stderr.decode('utf-8'))
    sys.stdout.flush()
    print()

def main():
  get_ghost_runtimes()

  parser = argparse.ArgumentParser(description="Run the benchmarks")
  parser.add_argument("benchmark", nargs='?',
    default="all",
    help="The benchmark to run")
  
  args = parser.parse_args()

  # Run the benchmarks
  for benchmark in BENCHMARKS:
    if benchmark[0] == args.benchmark or args.benchmark == "all":
      run_benchmark(benchmark)

  # Generate table for each runtime and benchmark combination
  print("Version | Benchmark | Average Runtime")
  print("--------|-----------|----------------")

  for benchmark in BENCHMARKS:
    # for each benchmark, in alphabetical order, print the average runtime for each runtime
    for runtime in RUNTIMES:
      version = os.path.basename(runtime)[6:]

      total_time = 0
      for trial in TRIALS:
        if trial[0] == benchmark[0] and trial[1] == runtime:
          total_time += trial[2]
      average_time = round(total_time / NUM_TRIALS, 4)

      print(version + " | " + benchmark[0] + " | " + str(average_time) + "s")
  print()
main()