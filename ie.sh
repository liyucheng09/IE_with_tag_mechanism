#！/usr/bin/bash

INPUT_FILE=./input.txt

TAG_OUTPUT_FILE=./output.txt

FACT_OUTPUT_FILE=./facts.json

TEST_FILE=./test_set.json

TEST_SENTENCES_TAG_FILE=./output.txt

EVALUATE_RESULT=./result.txt

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
elif [ $1 = 'evaluate' ]; then
	echo 'Evaluating! Please wait!'
	python3 Evaluation.py --target_file $TEST_FILE \
		--test_sentences_tag_file $TEST_SENTENCES_TAG_FILE \
		--output_file $EVALUATE_RESULT
	echo 'Finsh evaluate!'
fi