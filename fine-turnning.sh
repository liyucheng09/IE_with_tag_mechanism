TEST_SET=./test_set_totally_honest_2.json

TAG_GENERATE=./output_1.txt
#tag_generate.txt

EVALUATE_RESULT=./result_3_verison_3.txt


#python3 SAOKE2TAG.py --SAOKE $TEST_SET \
#	--output $TAG_GENERATE


python3 evaluate.py --target_file $TEST_SET \
	--output_file $EVALUATE_RESULT \
	--test_sentences_tag_file $TAG_GENERATE