

#-------------------------------------------------------------------------------------------------------
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from nltk.corpus import wordnet as wn
from gensim import corpora, models, similarities
from gensim.models import Word2Vec
from gensim.models import word2vec

#_____________TRAINING_____________
# sentences = word2vec.Text8Corpus('/Users/tarun/Desktop/untitled/phishing_training.txt') #training input data
# model = word2vec.Word2Vec(sentences, min_count=0,size=300,hs=1,negative=0,window=10,sg=1) #training parameters(negative=0,hs=1 required for phrase_sim)
# model.save('/Users/tarun/Desktop/untitled/phishing.model') #saving the model
model = Word2Vec.load('/Users/tarun/Desktop/untitled/pizza.model')

#phrase_sim is used retrieve similarity score of two phrases
import phrase_sim

from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

import MySQLdb as db

#-------------------------------------------------------------------------------------------------------


#Extract verbs and concepts from the databases
con1=db.connect("localhost","root","tarun","ontology")
cur1=con1.cursor()
con2=db.connect("localhost","root","tarun","SecOnto")
cur2=con2.cursor()

query1="select word from words_set where word_type='VB' or word_type='VBD' or word_type='VBG' or word_type='VBN' or word_type='VBP' or word_type='VBZ';"
cur1.execute(query1)
verbs=cur1.fetchall()

query2="select Concept1 from Ontology;"
cur2.execute(query2)
concepts1=cur2.fetchall()

query2="select Concept2 from Ontology;"
cur2.execute(query2)
concepts2=cur2.fetchall()

verb=[]
for x in verbs:
    if x not in verb:
        verb.append(x)  


concept1=[]
for x in concepts1:
    if x not in concept1:
        concept1.append(x)

for x in concepts2:
    if x not in concept1:
        concept1.append(x)


#----------------------------------------------------------------------------------
#function to check whether a given verb 'a' and concept 'b' are present in same sentence in the text
def check_in_sentence(a,b):
    query1="select count(*) from words_set where (word = '%s') and (sentence like '%s' or hypernym like '%s' or synonym like '%s')" % (a,"%"+b+"%","%"+b+"%","%"+b+"%")
    cur1.execute(query1)
    count=cur1.fetchall()
    # sent=[]
    # for x in sents:
    #   if x not in sent:
    #       sent.append(x)
    # for x in sent:
    #   if b in x[0].split():
    #       return True
    # return False
    if count[0][0]>0:
        return True
    else:
        return False
#----------------------------------------------------------------------------------


# Main Algorithm

for v in verb:
#for every verb we find the best two concepts with highest 
#similarity score of the verb and context of concept
#max_sim_1,max_sim_2=[similarity score,verb,]
    max_sim_1=[-1,'','','']
    max_sim_2=[-1,'','','']
    for c1 in concept1:
        vx=lemmatizer.lemmatize(v[0],'v')
        z=""
        for y in c1[0].split():
            if len(wn.synsets(y))>0:
                for w in wn.synsets(y)
                    z=z+" "+w.definition()
        
        sim = phrase_sim.phrase_similarity(vx,z)
        
        if sim>max_sim_1[0]:
            max_sim_1=[sim,vx,c1[0],z]
        if sim>max_sim_2[0] and sim<max_sim_1[0]:
            max_sim_2=[sim,vx,c1[0],z]

    #extracting nouns for the given verb which are present in same sentence in the text
    query1="select distinct noun_verb1,noun_verb2,noun_verb3,noun_verb4 from words_set where word='%s'" % (v[0])
    cur1.execute(query1)
    nouns=cur1.fetchall()

    noun=[]
    for a in nouns:
        for b in a:
            if b != 'NONE' and b not in noun:
                noun.append(b)

    #finding noun with maximum similarity with verb
    noun_sim=[-1,'']
    for a in noun:
        if phrase_sim.phrase_similarity(v[0],a) > noun_sim[0]:
            noun_sim[0]=phrase_sim.phrase_similarity(v[0],a)
            noun_sim[1]=a


    if max_sim_1[0]>-1 and check_in_sentence(max_sim_1[1],max_sim_1[2]) and max_sim_2[0]>-1 and check_in_sentence(max_sim_2[1],max_sim_2[2]):
        #case 1
        #if both concepts are present and relation doesn't exist, then update
        query2="select * from Ontology where Concept1='%s' and Concept2='%s' and Relation='%s'" % (max_sim_1[2],max_sim_2[2],max_sim_1[1])
        cur2.execute(query2)
        count=cur2.fetchall()
        if len(count)==0:
            #add relation between max_sim_1[2],v[0],max_sim_2[2]
            print "case1"


    if max_sim_1[0]>-1 and max_sim_2[0]>-1 and (check_in_sentence(max_sim_1[1],max_sim_1[2]) ^ check_in_sentence(max_sim_2[1],max_sim_2[2])):
        #case 2
        #only if one of the concept(c1) is present in the text then
        
        #if sim(c1)>sim(n) then add relation between max(sim(n)) and c1
        if phrase_sim.phrase_similarity(v[0],max_sim_1[2]) > phrase_sim.phrase_similarity(v[0],noun_sim[1]):
            #add relation between max_sim_1[2],v[0],noun_sim[1]
            print "case2"
        #else do nothing


    if max_sim_1[0]>-1 and max_sim_2[0]>-1 and not (check_in_sentence(max_sim_1[1],max_sim_1[2]) and check_in_sentence(max_sim_2[1],max_sim_2[2])) :
        #case 3
        #if both concepts are not present then
        
        #if sim(c1)>sim(n) and sim(c2)>sim(n) then c1--v--c2
        if phrase_sim.phrase_similarity(v[0],max_sim_1[3])>0.7 and phrase_sim.phrase_similarity(v[0],max_sim_2[3])>0.7 and (phrase_sim.phrase_similarity(v[0],max_sim_1[3]) > phrase_sim.phrase_similarity(v[0],noun_sim[1])) and (phrase_sim.phrase_similarity(v[0],max_sim_2[3]) > phrase_sim.phrase_similarity(v[0],noun_sim[1])):
            #add relation between max_sim_1[2],v[0],max_sim_2[2]
            print "case3.1"
            print (max_sim_1[2],noun_sim[1],max_sim_2[2],v[0],phrase_sim.phrase_similarity(v[0],max_sim_1[3]),phrase_sim.phrase_similarity(v[0],noun_sim[1]),phrase_sim.phrase_similarity(v[0],max_sim_2[3]))
        
        #if sim(c1)>sim(n) then c1--v--n
        if (phrase_sim.phrase_similarity(v[0],max_sim_1[3]) > phrase_sim.phrase_similarity(v[0],noun_sim[1])) and (phrase_sim.phrase_similarity(v[0],max_sim_2[3]) < phrase_sim.phrase_similarity(v[0],noun_sim[1])) :
            #add relation between max_sim_1[2],v[0],noun_sim[1]
            print "case3.2"
        
        #if sim(n)>sim(c1,c2)
        if (phrase_sim.phrase_similarity(v[0],max_sim_1[3]) < phrase_sim.phrase_similarity(v[0],noun_sim[1])) and (phrase_sim.phrase_similarity(v[0],max_sim_2[3]) < phrase_sim.phrase_similarity(v[0],noun_sim[1])):
            #if freq(n)>th then n--v--c1
            print "case3.3"
        
