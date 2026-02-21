#!/bin/bash
set -e

ZIP_NAME=lambda_function.zip
BUILD_DIR=build

echo "== Clean build directory =="
rm ${ZIP_NAME} 2>/dev/null || true
rm -rf ${BUILD_DIR}
mkdir ${BUILD_DIR}
mkdir ${BUILD_DIR}/src

echo "== Install dependencies =="
pip install -r requirements.txt -t ${BUILD_DIR}

echo "== Copy source files =="
cp main.py ${BUILD_DIR}
cp src/logging_config.py ${BUILD_DIR}/src

echo "== Remove unnecessary files =="
find ${BUILD_DIR} -type d -name "__pycache__" -exec rm -rf {} +
find ${BUILD_DIR} -type f -name "*.pyc" -delete
rm -rf ${BUILD_DIR}/bin

echo "== Create zip =="
cd ${BUILD_DIR}
zip -r ../${ZIP_NAME} .
cd ..

echo "== Done =="
ls -lh ${ZIP_NAME}
