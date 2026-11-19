#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
mkdir -p build/classes results
find src/main/java src/test/java -name '*.java' | sort > build/sources.txt
if command -v javac >/dev/null 2>&1; then
  javac --release 17 -encoding UTF-8 -d build/classes @build/sources.txt
elif [ -n "${ECJ_JAR:-}" ]; then
  java -jar "$ECJ_JAR" -17 -encoding UTF-8 -d build/classes @build/sources.txt
else
  echo 'Install JDK 17 or newer (not only a JRE), and put javac on PATH.' >&2
  exit 1
fi
case "${1:-serve}" in
  serve) if [ "$#" -gt 0 ]; then shift; fi; exec java -cp build/classes studio.Server "$@" ;;
  test) exec java -cp build/classes studio.AlgorithmTests ;;
  benchmark) exec java -cp build/classes studio.Benchmark ;;
  *) echo 'Usage: ./run.sh [serve|test|benchmark]' >&2; exit 1 ;;
esac
