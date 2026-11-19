@echo off
cd /d "%~dp0"
if not exist build\classes mkdir build\classes
if not exist results mkdir results
(for %%f in (src\main\java\studio\*.java src\test\java\studio\*.java) do @echo %%f) > build\sources.txt
javac --release 17 -encoding UTF-8 -d build\classes @build\sources.txt
if errorlevel 1 exit /b 1
if "%1"=="test" (java -cp build\classes studio.AlgorithmTests) else if "%1"=="benchmark" (java -cp build\classes studio.Benchmark) else (java -cp build\classes studio.Server)
