import argparse
import logging
import difflib
import numpy as np
import dltk

from pprint import pprint,pformat

from scipy.optimize import linear_sum_assignment

from grouper import formatter,grouper
from predict import predict


class evaluator :
	def __init__(self,
		test_file_path,
		result_output_path=None,
		test_sentences_tag_file=None):

		self.test_file_path=test_file_path

		self.result_output_path=result_output_path
		self.test_sentences_tag_file=test_sentence_tag_file

		self.test_sentences=[]
		self.target_list=[]

		self.predict_list=[]

		self.result=None

		self.sim=difflib.SeuquenceMatcher()


	def _preprocess(self):

		'''
			Import test data and format those fact into
			special format string.

		'''

		with open(self.test_file_path,'r',encoding='utf-8') as f:
			buff=[eval(i) for i in f.read().split('\n')]
			for i in buff:
				self.test_sentences.append(i['natural'])
				self.target_list.append([_test_data_formatter(a) for a in i['logic']])


	def _data_formatter(self,a):

		return '('+'$'.join([a['subject'],a['predict'],a['object'],a['time'],a['place'],a['qulifier']])+')'

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
			with open(self.test_sentence_tag_file,'r',encoding='utf-8') as f:
				tags=[i.split(',') for i in f.read().split('\n') if i]

		g=grouper()

		for sentence,tag in zip(self.test_sentences,tags):

			tag=formatter(tag)

			g.sentence=sentence
			g.tag=tag

			g.group()

			r , _ =g.output()

			self.predict_list.append([_data_formatter(fact_) for fact_ in r])

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
				sim_matrix[t_index,p_index]=_similarity_one_string(t,p)

		sim_matrix=-sim_matrix

		x,y=linear_sum_assignment(sim_matrix)

		sim_matrix = -sim_matrix


		count=0
		for sim in sim_matrix[x,y]:
			if sim >=0.85:
				count+=1

		precision=round(count/len(predict_l),5)
		re_call=round(count/len(target_l),5)
		
		return precision,re_call


	def _similarity_one_string(self,str_1,str_2):

		self.sim.set_seqs(str_1,str_2)
		return round(self.sim.ratio(),5)

	def _f1(self,p,r):
		return 2*((p*r)/(p+r))

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
			assert self.test_sentence_tag_file is not None,\
			'Error: Need tag file! You haven\'t give the test sentences tag file!'

			self._get_predict_facts(mode=1)

		precision_list=[]
		re_call_list=[]

		short_sentence_list=[]
		middle_length_sentence_list=[]
		long_sentence_list=[]

		for target,predict_,sentence in zip(self.target_list,self.predict_l,self.test_sentences):
			p,r=_match(target,predict_)
			precision_list.append(p)
			re_call_list,append(r)

			if len(sentence)<=25:
				short_sentence_list.append((p,r))
			elif len(sentence)>=25 and len(sentence)<=60:
				middle_length_sentence_list.sppend((p,r))
			else:
				long_sentence_list.append((p,r))

		all_precision=self._mean(precision_list)
		all_recall=self._mean(re_call_list)
		all_f1=self._f1(all_precision,all_recall)

		short_p=self._mean([i[0] for i in short_sentence_list])
		short_r=self._mean([i[1] for i in short_sentence_list])
		short_f1=self._f1(short_p,short_r)

		middle_p=self._mean([i[0] for i in middle_length_sentence_list])
		middle_r=self._mean([i[1] for i in middle_length_sentence_list])
		middle_f1=self._f1(middle_p,middle_r)

		long_p=self._mean([i[0] for i in long_sentence_list])
		long_r=self._mean([i[1] for i in long_sentence_list])
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
			f.write(pformat(self.result),indent=4)

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
	e.evaluate(mode=1)

	e.evaluate()
	e._output()


