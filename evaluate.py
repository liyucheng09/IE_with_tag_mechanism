import argparse
import logging
import difflib
import numpy as np
#import dltk

from pprint import pprint,pformat

from scipy.optimize import linear_sum_assignment

from grouper import formatter,grouper


class evaluator :
	def __init__(self,
		test_file_path,
		result_output_path=None,
		test_sentences_tag_file=None):

		self.test_file_path=test_file_path

		self.result_output_path=result_output_path
		self.test_sentences_tag_file=test_sentences_tag_file

		self.test_sentences=[]
		self.target_list=[]

		self.predict_list=[]

		self.result=None

		self.sim=difflib.SequenceMatcher()
		self.replace_map=str.maketrans({'[':'',']':'','|':''})


	def _preprocess(self):

		'''
			Import test data and format those fact into
			special format string.

		'''

		with open(self.test_file_path,'r',encoding='utf-8') as f:
			buff=[eval(i) for i in f.read().split('\n')]
			for i in buff:
				self.test_sentences.append(i['natural'])
				self.target_list.append([self._data_formatter(a) for a in i['logic']])


	def _data_formatter(self,a):

		if isinstance(a['object'],list):
			a['object']='|'.join(a['object'])
		if isinstance(a['subject'],list):
			a['subject']='|'.join(a['subject'])
		return '('+'$'.join([a['subject'],a['predicate'],a['object'],a['time'],a['place'],a['qualifier']])+')'

	def _get_predict_facts(self,mode=0):

		'''
			Use tag model and group algorithm generate facts.

			Argument:
				mode: 1 means evaluate grouping algorithm. 0 means evaluate
						entire model.
		'''

		self.predict_list=[]


		if mode == 0:
			tags=predict(self.test_sentences)
		elif mode == 1:
			with open(self.test_sentences_tag_file,'r',encoding='utf-8') as f:
				tags=[i.split(',') for i in f.read().split('\n') if i]

		g=grouper()

		for sentence,tag in zip(self.test_sentences,tags):

			tag=formatter(tag)

			g.sentence=sentence
			g.tag=tag

			g.group()
			r , _ =g.output()

			self.predict_list.append([self._data_formatter(fact_) for fact_ in r])

	def _match(self,target_l,predict_l):

		'''
			Use patent matching algorithm calculate similarity between target
			fact string and predict fact string.
			And then solve Assignment problem use Hungarian Algorithm.
			Finally calculate precision and re-call score for a single sentence.

			argument:
				target_l: 1-D List,
					len(target_l)=num_of_fact_each_sentence
				predict_l: 1-D List, 
						len(predict_l)=num_of_fact_each_sentence_predicted

		'''

		sim_matrix=np.zeros((len(target_l),len(predict_l)))

		for t_index,t in enumerate(target_l):
			for p_index,p in enumerate(predict_l):
				sim_matrix[t_index,p_index]=self._similarity_one_string(t,p)

		sim_matrix=-sim_matrix

		x,y=linear_sum_assignment(sim_matrix)
		sim_matrix = -sim_matrix

		count=0
		for sim,x_,y_ in zip(sim_matrix[x,y],x,y):
			if sim >=0.85:
				
				print(target_l[x_])
				print(predict_l[y_])
				print('------'+'\n')
				
				count+=1

		return count,len(predict_l),len(target_l)

	def _p_r(self,t):

		'''
			Argument:
				tuple: (count, len_p, len_t)

		'''
		#print(t)

		if t[1]*t[2]==0:
			if t[0] == t[1] == t[2] ==0:
				return 1,1
			else:
				return 0,0
		else:
			precision=round(t[0]/t[1],5)
			re_call=round(t[0]/t[2],5)
			
			return precision,re_call

	def _similarity_one_string(self,str_1,str_2):

		str_1=str_1.translate(self.replace_map)
		str_2=str_2.translate(self.replace_map)
		
		self.sim.set_seqs(str_1,str_2)
		return round(self.sim.ratio(),5)

	def _f1(self,p,r):

		if p == r ==0:
			return 0
		else:
			return round(2*((p*r)/(p+r)),5)

	def _mean(self,l):
		return round(np.mean(l),5)


	def evaluate(self,mode=0):

		'''
			Calculate precision and re_call for all sentences and then
			return mean of them.

			Argument:
				mode: 1 means evaluate grouping algorithm. 0 means evaluate
						entire model.

		'''

		self.result=None

		self._preprocess()

		if mode == 0:
			self._get_predict_facts()
		elif mode == 1:
			assert self.test_sentences_tag_file is not None,\
			'Error: Need tag file! You haven\'t give the test sentences tag file!'

			self._get_predict_facts(mode=1)

		overall=[0,0,0]

		short_sentence=[0,0,0]
		middle_length_sentence=[0,0,0]
		long_sentence=[0,0,0]

		for target,predict_,sentence in zip(self.target_list,self.predict_list,self.test_sentences):
			#print(target,predict_)
			count,len_p,len_t=self._match(target,predict_)
			#print(count,len_p,len_t)
			overall[0]+=count
			overall[1]+=len_p
			overall[2]+=len_t

			'''
			pprint(target)
			pprint(predict_)
			print('------')
			p,r=self._p_r([count,len_p,len_t])
			print(self._f1(p,r))
			print('\n\n')
			'''

			if len(sentence)<=25:
				short_sentence[0]+=count
				short_sentence[1]+=len_p
				short_sentence[2]+=len_t
			elif len(sentence)>=25 and len(sentence)<=60:
				middle_length_sentence[0]+=count
				middle_length_sentence[1]+=len_p
				middle_length_sentence[2]+=len_t
			else:
				long_sentence[0]+=count
				long_sentence[1]+=len_p
				long_sentence[2]+=len_t

		all_precision,all_recall=self._p_r(overall)
		all_f1=self._f1(all_precision,all_recall)

		short_p,short_r=self._p_r(short_sentence)
		short_f1=self._f1(short_p,short_r)

		middle_p,middle_r=self._p_r(middle_length_sentence)
		middle_f1=self._f1(middle_p,middle_r)

		long_p,long_r=self._p_r(long_sentence)
		long_f1=self._f1(long_p,long_r)

		self.result={
			'all_precision':all_precision,
			'all_recall':all_recall,
			'all_f1':all_f1,
			'short_precision':short_p,
			'short_recall':short_r,
			'short_f1':short_f1,

			'middle_length_precison':middle_p,
			'middle_length_recall':middle_r,
			'middle_length_f1':middle_f1,

			'long_precision':long_p,
			'long_recall':long_r,
			'long_f1':long_f1
		}

		pprint(self.result)

	def _output(self):

		assert self.result_output_path is not None , \
			'You have not give the path where you want save the result in.'

		with open(self.result_output_path,'w',encoding='utf-8') as f:
			f.write(pformat(self.result,indent=4))

		print('Result save done!')



if __name__ == '__main__':
	parser=argparse.ArgumentParser()

	parser.add_argument('--target_file',required=True,\
		help='test file path')
	parser.add_argument('--output_file',required=False,\
		help='where the result write to')
	parser.add_argument('--test_sentences_tag_file',required=False,\
		help='For evaluate grouping alogithm we use target tag and group them\
		and then compare with target facts.')


	args=parser.parse_args()

	e=evaluator(args.target_file,args.output_file,args.test_sentences_tag_file)
	if args.test_sentences_tag_file is not None:
		e.evaluate(mode=1)
	else:
		from predict import predict
		e.evaluate()
	if args.output_file is not None:
		e._output()


