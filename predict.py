import sys
import dltk
import argparse
from grouper import formatter

if __name__ == '__main__':

	parser=argparse.ArgumentParser()

	parser.add_argument('--sentence_file',\
		help='The file which contain sentences which you want to tag.\
			Noted that the coding of the file must be utf-8',required=True)
	parser.add_argument('--output_path',\
		help='Where you want to write result in.',\
		required=True)

	args=parser.parse_args()

	dic_path=sys.path[0]
	model_file=dic_path+'/model/model.pb'
	map_file=dic_path+'/model/maps.pkl'

	model=dltk.load_model(map_file=map_file,model_file=model_file)

	print(args.sentence_file)

	with open(args.sentence_file,'r',encoding='utf-8') as f:
		sentences=[sentence for sentence in f.read().split('\n') if sentence]

	tags=model.predict(sentences)

	tags=[formatter(tag) for tag in tags]

	with open(args.output_path,'w',encoding='utf-8') as f:
		for tag in tags:
			f.write(tag+'\n')

	print('%d sentences were tagged! Done! ' %len(sentences))



