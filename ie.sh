#！/usr/bin/bash

INPUT_FILE=./input.txt

TAG_OUTPUT_FILE=./output.txt

FACT_OUTPUT_FILE=./facts.json

######################


if [ $1 = 'tag' ]; then
	echo 'Predicting! Please Wait!'
	python3 predict.py --sentence_file $INPUT_FILE --output_path $TAG_OUTPUT_FILE
	echo 'Finsh tag!'
elif [ $1 = 'ie' ]; then
	echo 'Grouping! Please wait!'
	python3 grouper.py --sentences_file $INPUT_FILE \
		--tags_file $TAG_OUTPUT_FILE --result_path $FACT_OUTPUT_FILE
	echo 'Finsh group!'
fi