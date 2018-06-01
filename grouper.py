import re
from pprint import pprint
import numpy as np
import argparse
import json

class fact:
	def __init__(self,predict,predict_position):
		self.subject=[]
		self.object=[]
		self.predict=predict
		self.place=None
		self.time=None
		self.qualifier=None

		self.predict_position=predict_position

	def _find_subj_in_the_same_subsentence(self,subj_posi,subs_posi):
		if self.predict_position[0]<subs_posi[1] and self.predict_position[1]>subs_posi[0] \
			and subj_posi[0]<subs_posi[1] and subj_posi[1]>subs_posi[0]:
			return True
		else:
			return False

	def is_in_predict(self,posi):
		if posi[0]>=self.predict_position[0] and \
			posi[1]<=self.predict_position[1] :
			return True
		else:
			return False

	def calculate_distance(self,posi):
		if posi[1]<=self.predict_position[0]:
			return self.predict_position[0]-posi[1]
		else:
			assert posi[0]>=self.predict_position[1]
			return posi[0]-self.predict_position[1]


class grouper :

	def __init__(self,sentence=None,tag=None):
		self.sentence=sentence
		self.tag=tag
		self.facts=[]

	def _generate_predict(self,sentence,tag):
		place_hodler_l=['X','Y','Z']
		pattern=re.compile('O*P{1,}O*P*O*P*')
		predict_tag_l=[[i.group(),i.span()] for i in pattern.finditer(tag)]

		predict_char_l=[sentence[predict[1][0]:predict[1][1]] \
									for predict in predict_tag_l]

		for index,predict in enumerate(predict_tag_l):
			subtag=predict[0]
			if 'O' in subtag:
				pattern2=re.compile('O*')
				for index2,obj in enumerate(\
							[i for i in pattern2.finditer(subtag) if i.group()]):
#					print(subtag,obj.group())
					obj_char=predict_char_l[index][obj.span()[0]:obj.span()[1]]
					predict_char_l[index]=\
						predict_char_l[index].replace(\
							obj_char,place_hodler_l[index2])
			predict_char_l[index]=(predict_char_l[index],predict[1])
		return predict_char_l

	def _subsentences(self):

		subsentences=re.split(',.!?，。！？',self.sentence)
		result=[]
		for subsentence in subsentences:
			s=self.sentence.find(subsentence)
			result.append((subsentence,(s,s+len(subsentence))))
		del subsentences
		return result


	def _find_section_in_sentence(self,tag_):
		re_str='('+tag_+'*)'

		pattern=re.compile(re_str)
		return [[self.sentence[i.span()[0]:i.span()[1]],i.span()] for i in pattern.finditer(self.tag) if i.group()]


	def _select_object(self,obj_l):

		#  As for each predict 
		#  we select object which is already contain in predict 
		#  where placeholder is.
		#  And for each predict which has no object already, we choice
		#  the most close object for him.

		flag=[0 for obj in obj_l]
		for fact_ in self.facts:
			for obj in obj_l:
				if fact_.is_in_predict(obj[1]):
					fact_.object.append(obj[0])
					flag[obj_l.index(obj)]=1
			if len(fact_.object)==0 and len(obj_l)!=0 :
				distance_l=[fact_.calculate_distance(obj[1]) for obj in obj_l]

				most_close_obj=obj_l[np.argmin(distance_l)]
				fact_.object.append(most_close_obj[0])
				flag[most_close_obj]=1



		rest_of_object=[obj for index,obj in enumerate(obj_l) if flag[index]!=1 ]
		if len(rest_of_object)!=0:
			for obj in rest_of_object:
				distance_l=[fact_.calculate_distance(obj[1]) for fact_ in self.facts]
				most_close_predict=np.argmin(distance_l)

				self.facts[most_close_predict].object.append(obj[0])


	def _select_object_with_delete(self,obj_l):

		#  As for each predict 
		#  we select object which is already contain in predict 
		#  where placeholder is.
		#  And for each predict which has no object already, we choice
		#  the most close object for him.
		#
		#  Warning!:
		#  The difference between this function and '_select_object'
		#  is this function will delete obj when he was chosen by 
		#  one predict.

		for fact_ in self.facts:
			for obj in obj_l:
				if fact_.is_in_predict(obj[1]):
					fact_.object.append(obj[0])
					obj_l.remove(obj)
		for fact_ in self.facts:
			if len(fact_.object)==0 and len(obj_l)!=0 :
				distance_l=[fact_.calculate_distance(obj[1]) for obj in obj_l]
				most_close_obj=obj_l[np.argmin(distance_l)]
				fact_.object.append(most_close_obj[0])
				obj_l.remove(most_close_objs)


	def _select_place_time_qualifier(self):
		'''

			We put each item(place/time/qualifier) to the 
			predict which is most close to.

		'''

		for tag_ in ['T','L','Q']:
			
			item_l=self._find_section_in_sentence(tag_)
			for item in item_l:
				distance_l=[fact_.calculate_distance(item[1]) for fact_ in self.facts]
				most_close_predict=np.argmin(distance_l)

				if tag_ == 'T':
					self.facts[most_close_predict].time=item[0]
				elif tag_ == 'L':
					self.facts[most_close_predict].place=item[0]
				else:
					self.facts[most_close_predict].qualifier=item[0]

	def _select_subject(self,sub_l):

		#  Delete after subject was chosen by a fact
		#

		subsentences=self._subsentences()
		flag=[0 for i in sub_l]

		for fact_ in self.facts:
			candidate=[]
			for index,subject in enumerate(sub_l):
				for subsentence in subsentences:
					if fact_._find_subj_in_the_same_subsentence(subject[1],subsentence[1]):
						candidate.append(subject)

			if len(candidate)!=0:
				distance_l=[fact_.calculate_distance(subject[1]) for subject in candidate]
				most_close_subject=np.argmin(distance_l)
				fact_.subject.append(candidate[most_close_subject][0])
				flag[sub_l.index(candidate[most_close_subject])]=1

		#  After the first round of matching, the rest of subject
		#  (which not be used already)
		#  will find the most close predict and be grouped together.
		#

		rest_of_subject=[subject for index,subject in enumerate(sub_l) if flag[index]!=1]
		if len(rest_of_subject)!=0 :
			for subject in rest_of_subject:
				distance_l=[fact_.calculate_distance(subject[1]) for fact_ in self.facts]
				most_close_predict=np.argmin(distance_l)

				self.facts[most_close_predict].subject.append(subject[0])



	def group(self):

		self.facts=[]

		#  First, Use all of predict as center, construct fact object.
		#  Fact object initalize with predict text and predict position.
		#

#		print(self._generate_predict(self.sentence,self.tag))
		for fact_,fact_position in self._generate_predict(self.sentence,self.tag):
			self.facts.append(fact(fact_,fact_position))

		obj_l=self._find_section_in_sentence('O')
		self._select_object(obj_l)

		self._select_place_time_qualifier()

		sub_l=self._find_section_in_sentence('S')
		self._select_subject(sub_l)

	def print(self):

		pprint(self.sentence)
		for i in self.facts:
			pprint([
				i.subject,
				i.predict,
				i.object,
				i.time,
				i.place,
				i.qualifier])

	def output(self):

		result=[]
		for fact_ in self.facts:

			fact_l=[i if i!=None else '_' for i in [fact_.subject,fact_.predict,\
					fact_.object,fact_.time,fact_.place,fact_.qualifier]]

			result.append(
				{
					'subject':fact_l[0],
					'predict':fact_l[1],
					'object':fact_l[2],
					'time':fact_l[3],
					'place':fact_l[4],
					'qualifier':fact_l[5]
				})

		return json.dumps(result,ensure_ascii=False),len(result)

def formatter(old_tag):

	'''
		Replace tag 'NA' with 'N', 'PL' with 'L'.

	'''

	tag_new=[]
	for item in old_tag:
		if item =='NA':
			tag_new.append('N')
			continue
		if item == 'PL':
			tag_new.append('L')
			continue
		tag_new.append(item)

	tag=''.join(tag_new)
	del old_tag,tag_new

	return tag


if __name__ == '__main__':

	parser=argparse.ArgumentParser()

	parser.add_argument('--sentences_file', \
		help='The path of sentences file ready \
		for information extraction, noted that the coding of \
		the file must be utf-8',required=True)

	parser.add_argument('--tags_file',\
		help='The corresponding tags which predct by tag model, \
		noted that the coding of \
		the file must be utf-8',\
		required=True)

	parser.add_argument('--result_path',\
		help='Where do you want to write result at. \
		The result format will be Json file.',\
		required=True)

	args=parser.parse_args()


	with open(args.sentences_file,'r',encoding='utf-8') as f:
		sentences=[sentence for sentence in f.read().split('\n') if sentence]

	with open(args.tags_file,'r',encoding='utf-8') as f:
		tags=[tag for tag in f.read().split('\n') if tag]

	assert len(sentences)==len(tags) , 'Input error: the number of input sentences\
		and tags are not same!'

	g=grouper()
	result=[]
	all_count=0
	for sentence,tag in zip(sentences,tags):

		tag=formatter(tag)

		g.sentence=sentence
		g.tag=tag

#		print(g.sentence,g.tag)
		g.group()

		r,count=g.output()
		all_count+=count
		result.append(r)

	with open(args.result_path,'w',encoding='utf-8') as f:
		for fact_ in result:
			f.write(fact_+'\n')

	print('%d facts were found in %d sentences! \n \
			The result save at %s.'  %(all_count,len(sentences),args.result_path))



