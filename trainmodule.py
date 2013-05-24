#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os
import re
import collections
from splitwords import SplitWords
#from splitwords_trie import SplitWords

class TrainModules:
	"""
		use given mails to train the module
	"""

	def __init__(self):
		self.wordlist = {'normal' : [], 'spam' : []}
		self.mail_count = {'normal' : 0, 'spam' : 0}
		self.dic_word_freq = {}
		self.PRE_DEFINED_WORD_FREQ = 0.01

	def build_word_list(self, mail_dir):
		for dirt in os.listdir(mail_dir): # 'normal', 'spam'
			d = mail_dir + '/' + dirt + '/'
			print 'scanning directory: ', d
			for filename in os.listdir(d):
				fp = open(d + filename).read()
				mail_content = fp[fp.index('\n\n')::]

				try:
					mail_content = mail_content.decode('gbk')
				except:
					print 'ERROR: ', filename
					continue

				mail_content = re.sub('\s+',' ', mail_content)
				res_list = SplitWords(mail_content).get_word_list()
				word_list = list(set(res_list))
				self.wordlist[dirt].extend(word_list)
				self.mail_count[dirt] += 1

	def calc_word_freq(self, mail_type):
		counter = collections.Counter(self.wordlist[mail_type])
		dic = collections.defaultdict(list)
		for word in list(counter):
			dic[word].append(counter[word])

		for key in dic:
			dic[key][0] *= 1.0 / self.mail_count[mail_type]

		return dic

	def build_freq_dict(self):
		dic_word_freq_in_normal = self.calc_word_freq('normal')
		dic_word_freq_in_spam = self.calc_word_freq('spam')

		dic_word_freq = dic_word_freq_in_normal

		for key in dic_word_freq_in_spam:
			if key not in dic_word_freq:
				dic_word_freq[key].append(self.PRE_DEFINED_WORD_FREQ)
			dic_word_freq[key].append(dic_word_freq_in_spam[key][0])

		for key in dic_word_freq: 
			if len(dic_word_freq[key]) == 1:
				dic_word_freq[key].append(self.PRE_DEFINED_WORD_FREQ)

		self.dic_word_freq = dic_word_freq
		return dic_word_freq

	def update(self, mail_type, word_list):
		if mail_type == 'normal':
			mt = 0
		else:
			mt = 1

		for word in word_list:
			if self.dic_word_freq[word][mt] == self.PRE_DEFINED_WORD_FREQ:
				self.dic_word_freq[word][mt] = 1.0 / (self.mail_count[mail_type] + 1)
			else:
				self.dic_word_freq[word][mt] = \
						(1 + self.dic_word_freq[word][mt] * self.mail_count[mail_type]) / (self.mail_count[mail_type] + 1)
			self.mail_count[mail_type] += 1

import sys

def main():
	demo = TrainModules()
	demo.build_word_list('/tmp/data')
	dic_freq = demo.build_freq_dict()
	freq_file = open('/tmp/freq_file.txt', 'w')

	for key in dic_freq:
		freq_file.write(key.encode('utf-8'))

		for v in dic_freq[key]:
			freq_file.write(' ' + str(v))

		freq_file.write('\n')

	freq_file.close()

if __name__ == '__main__':
	main()

