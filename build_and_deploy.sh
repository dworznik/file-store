#!/usr/bin/env bash

set -x
set -e 

RUNTIME=python312
REGION=us-central1
SERVICE_ACCOUNT=veri-dao@appspot.gserviceaccount.com

if [ "$#" -ne 2 ]; then
    echo "Usage: ./build_and_deploy.sh <function_directory> <function_name>"
    exit 1
fi

SCRIPT_DIR=$(dirname $(realpath $0))
FUNCTION_DIR=$1
FUNCTION_NAME=$2
TARGET_DIR=$FUNCTION_DIR/target

rm -rf $TARGET_DIR

mkdir -p $TARGET_DIR/file_store
cp -r $SCRIPT_DIR/file_store/*  $TARGET_DIR/file_store/
cp $FUNCTION_DIR/main.py $TARGET_DIR/

cat .env | grep -v '^#' | grep -v '^$' | awk -F= '{print $1 ": \"" $2 "\""}' > $TARGET_DIR/env.yaml
poetry export -f requirements.txt --without-hashes --output $TARGET_DIR/requirements.txt

cd $TARGET_DIR

gcloud functions deploy $FUNCTION_NAME --gen2 --runtime=$RUNTIME --region=$REGION --service-account=$SERVICE_ACCOUNT --source=. --entry-point=handler --trigger-http --allow-unauthenticated --env-vars-file env.yaml
