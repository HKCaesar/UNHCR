#!/bin/bash


##############################################################
## GET BATCHES OF LANDSAT IMAGE(S) FROM GOOGLE CLOUD
##############################################################


usage=$'[-h] -- program to retrieve landsat images from Google Storage  \n where: -h  show this help text \n 1st Argument: full path to gsutil instalation directory (ex: /home/gsutil_folder )  \n 2nd Argument: image repository path (ex: gs://gcp-public-data-landsat ) \n 3rd Argument: image path (ex:164) \n 4th Argument: image row (ex: 058) \n 5th Argument: Landsat version (ex: 8) \n 6th Argument: time window (ex: 2017-2019) \n 7th Argument: output dir (full path) '


if [ $1 == '-h' ]; then
echo "${usage}"
exit 0
fi


GSUTIL_HOME=$1
IMAGE_REPO=$2
IMAGE_PATH=$3
IMAGE_ROW=$4
LANDSAT_VERSION=$5
TIMEFRAME=$6
OUTPUT_DIR=$7


if [ ! -d "$OUTPUT_DIR" ]; then
mkdir -p ${OUTPUT_DIR}
fi

START_YEAR="$(echo ${TIMEFRAME} | cut -d'-' -f1)"
END_YEAR="$(echo ${TIMEFRAME} | cut -d'-' -f2)"

COUNT=0

YEARS_TO_LOAD=$[${END_YEAR}-${START_YEAR}]


echo "[INFO] GETTING LANDSAT IMAGE:"
echo "[INFO] PATH: "${IMAGE_PATH}
echo "[INFO] ROW: "${IMAGE_ROW}
echo "[INFO] TIME WINDOW: "${TIMEFRAME}

while [ $COUNT -lt $[${YEARS_TO_LOAD} +1] ]
do
CURR_YEAR=$[${START_YEAR}+${COUNT}]
${GSUTIL_HOME}/gsutil/gsutil -m cp -r ${IMAGE_REPO}/LC0${LANDSAT_VERSION}/01/${IMAGE_PATH}/${IMAGE_ROW}/LC0${LANDSAT_VERSION}_L1TP_${IMAGE_PATH}${IMAGE_ROW}_${CURR_YEAR}* ${OUTPUT_DIR}/
COUNT=$[$COUNT+1]
done

echo "[INFO] Images downloaded."
