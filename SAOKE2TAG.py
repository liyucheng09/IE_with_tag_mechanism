import argparse
import re



def tagging(keyword,sentence,tags_of_sentence,tag):

	all_keywords=[ i.span() for i in re.finditer(keyword,sentence)]

	for k in all_keywords:
		for i in range(k[0],k[1]):
			tags_of_sentence[i]=tag

	return tags_of_sentence

def has_placeholder(s):
	for i in ['X','Y','Z']:
		if(i in s):
			return True
	return False

def has_special_character(s):
	for i in ['[',']','|']:
		if(i in s):
			return True
	return False

def tag_object(obj,sentence,tags_of_sentence,tag):

	o=obj
	if isinstance(o,list):
		o=obj[0]

	'''
		If object has special character replace them and 
		parse them with moudle re.

		Else, tag directly.
	'''
	if(has_special_character(o)):
		o=obj_re_str(o)

		all_keyword=[i.span() for i in re.finditer(o,sentence)]
		for k in all_keyword:
			for i in range(k[0],k[1]):
				tags_of_sentence[i]=tag
	else:
		tagging(obj,sentence,tags_of_sentence,tag)

def tag_predicate_has_placehodler(predicate,sentence,tags_of_sentence,tag):

	predicate_origin=predicate
	predicate=predicate.replace('X','.*').replace('Y','.*').replace('Z','.*')
	l=re.findall(predicate,sentence)
	if len(l)==0:
		return
	l=l[0]
	start=sentence.find(l)

	for i in re.split('X|Y|Z',predicate_origin):
		if(i):
			for a in range(l.find(i)+start,start+l.find(i)+len(i)):
				tags_of_sentence[a]=tag

def obj_re_str(obj):

	return obj.replace('[','').replace(']','').replace('|','.{0,5}')

def tag_object_with_placeholder(predicate,obj,sentence,tags_of_sentence,tag):

	predicate_origin=predicate
	predicate=predicate.replace('X','.*').replace('Y','.*').replace('Z','.*')

	predicate=re.findall(predicate,sentence)

	if len(predicate)==0:
		return
	else:
		predicate=predicate[0]
	predicate_start=sentence.find(predicate)

	p=predicate_origin.replace('X','(.*)').replace('Y','(.*)').replace('Z','(.*)')
	object_tuple=re.findall(p,predicate)[0]

	if isinstance(object_tuple,str):
		object_tuple=[object_tuple]
	for place,obj_ in zip(object_tuple,obj):

		place_start=predicate.find(place)
		keyword=[i.span() for i in re.finditer(obj_re_str(obj_),place)]

		for k in keyword:
			for i in range(k[0],k[1]):
				tags_of_sentence[predicate_start+place_start+i]=tag


def main(data):

	sentence=data['natural']
	tags=['N' for i in sentence]

	for logic in data['logic']:
		m={
			'time':'T',
			'place':'L',
			'qualifier':'Q',
			'subject':'S',
			'predicate':'P',
			'object':'O'
		}
		
		for i in ['time','place','qualifier']:
			keyword=logic[i]
			tagging(keyword,sentence,tags,m[i])
		if logic['subject']!='_':
			tag_object(logic['subject'],sentence,tags,'S')

		'''
			

		'''
		if has_placeholder(logic['predicate']):
			tag_predicate_has_placehodler(logic['predicate'],sentence,tags,'P')
			tag_object_with_placeholder(logic['predicate'],logic['object'],sentence,tags,'O')
		else:
			tag_object(logic['predicate'],sentence,tags,'P')
			tag_object(logic['object'][0],sentence,tags,'O')

	return tags




if __name__ == '__main__':
	parser=argparse.ArgumentParser()

	parser.add_argument('--SAOKE',required=False)
	parser.add_argument('--output',required=True)

	args=parser.parse_args()

	with open(args.SAOKE,'r',encoding='utf-8') as f:
		data=f.read().split('\n')


	tags=[]
	for s in data:
		tag=main(eval(s))
		tags.append(tag)

	with open(args.output,'w',encoding='utf-8') as f:
		for tag in tags:
			f.write(''.join(tag)+'\n')

	print('Generate tag Done!\n*************\n')


