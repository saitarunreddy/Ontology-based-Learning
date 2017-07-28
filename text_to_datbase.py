
#----------------------------------------------------------------------------------
from nltk.parse import stanford
from nltk import word_tokenize
from nltk import sent_tokenize
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.stem.lancaster import LancasterStemmer
from nltk.corpus import wordnet as wn
from nltk.tag.stanford import StanfordNERTagger
stt = StanfordNERTagger('/Users/tarun/Desktop/stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz','/Users/tarun/Desktop/stanford-ner/stanford-ner.jar')
import MySQLdb as db
import codecs
import re
#----------------------------------------------------------------------------------

#connect to database and remove previous values in the database
con=db.connect("localhost","root","tarun","ontology")
cur=con.cursor()
cur.execute("truncate words_set;")

#input file which is to be converted into nouns and verbs in database 
read_file = open('pizza.txt','r')
plain_text=read_file.read().decode('utf8')
plain_text = re.sub('[^a-zA-Z0-9\n\.]', ' ', plain_text)  #replace all non alphanumeric letters with space
sents=sent_tokenize(plain_text) #tokenize into sentences
tokens=word_tokenize(plain_text) #tokenize into words
tags=pos_tag(tokens) #parts of speech tagging of every word in text


#insert proper nouns into database by converting them into common nouns using Stanford NER tagger
for s in sents:
	words_ner=stt.tag(word_tokenize(s))
	words_pos=pos_tag(word_tokenize(s))
	noun_verb_sen=['NONE','NONE','NONE','NONE']#verbs present in the same sentence
	nv_count=0
	for t in words_pos:
		if nv_count<4 and (t[1]=="VB" or t[1]=="VBD" or t[1]=="VBG" or t[1]=="VBN" or t[1]=="VBP" or t[1]=="VBZ") and len(t[0])>1:
			noun_verb_sen[nv_count]=t[0]
			nv_count = nv_count + 1
	
	#insert data into database
	for t in words_ner:
		if t[1] != 'O':
			for a in wn.synsets(t[0]):
				synonym=(a.name().split('.')[0])
				hypernym='NONE'

				if len(a.hypernyms())>0 :
					hypernym=(a.hypernyms()[0]).name().split('.')[0] 

				word_type='NNP'
				word_raw=t[0]
				word_ner_t=t[1]
				cur.execute("insert into words_set(word_raw,word_type,word,synonym,hypernym,sentence,noun_verb1,noun_verb2,noun_verb3,noun_verb4) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" %(word_raw,word_type,word_ner_t,synonym,hypernym,s,noun_verb_sen[0],noun_verb_sen[1],noun_verb_sen[2],noun_verb_sen[3]) )
				con.commit()

#----------------------------------------------------------------------------------

#insert remaning nouns and verbs into database
for s in sents:
	w=pos_tag(word_tokenize(s))
	verb_sen=['NONE','NONE','NONE','NONE']#verbs present in the same sentence as a given noun
	noun_sen=['NONE','NONE','NONE','NONE']#nouns present in the same sentence as a given verb
	
	nv_count=0
	for t in w:
		if nv_count<4 and (t[1]=="VB" or t[1]=="VBD" or t[1]=="VBG" or t[1]=="VBN" or t[1]=="VBP" or t[1]=="VBZ") and len(t[0])>1:
			verb_sen[nv_count]=t[0]
			nv_count = nv_count + 1

	nv_count=0
	for t in w:
		if nv_count<4 and (t[1]=="NN" or t[1]=="NNS") and len(t[0])>1:
			noun_sen[nv_count]=t[0]
			nv_count = nv_count + 1

	#insert data into databse		
	for t in w:
		print t
		if len(t)>1:
			if t[1]=="NN" or t[1]=="NNS" or t[1]=="VB" or t[1]=="VBD" or t[1]=="VBG" or t[1]=="VBN" or t[1]=="VBP" or t[1]=="VBZ" and len(t[0])>1:
				for a in wn.synsets(t[0]):
					synonym=(a.name().split('.')[0])
					if len(a.hypernyms())>0 :
						hypernym=(a.hypernyms()[0]).name().split('.')[0]
					word=re.sub('[^a-zA-Z0-9\n\.]', ' ',t[0])
					word_type=t[1]
					synonym = re.sub('[^a-zA-Z0-9\n\.]', ' ', synonym)
					hypernym = re.sub('[^a-zA-Z0-9\n\.]', ' ', hypernym)
					if t[1]=="NN" or t[1]=="NNS":
						cur.execute("insert into words_set(word_raw,word_type,word,synonym,hypernym,sentence,noun_verb1,noun_verb2,noun_verb3,noun_verb4) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" %(word,word_type,word,synonym,hypernym,s,verb_sen[0],verb_sen[1],verb_sen[2],verb_sen[3]) )
						con.commit()
					if t[1]=="VB" or t[1]=="VBD" or t[1]=="VBG" or t[1]=="VBN" or t[1]=="VBP" or t[1]=="VBZ":
						cur.execute("insert into words_set(word_raw,word_type,word,synonym,hypernym,sentence,noun_verb1,noun_verb2,noun_verb3,noun_verb4) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" %(word,word_type,word,synonym,hypernym,s,noun_sen[0],noun_sen[1],noun_sen[2],noun_sen[3]) )						
						con.commit()

#----------------------------------------------------------------------------------
