import pronto
#import json
import MySQLdb
import re
ont = pronto.Ontology('pizza.owl')
# print(ont.obo)
# print(ont['Attribute'].children.children)
db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                     passwd="tarun",  		  # your password
                     db="SecOnto")          # name of the data base

# you must create a Cursor object. It will let you execute all the queries you need

cursor = db.cursor()
cursor.execute("truncate Ontology;")

listid = []
dict = {}
Relation = 'is a'
for term in ont:
    if term.children:
    	a = str(term).split(":")
        b = a[0]	
        listid.append(b[1:])      
for x in xrange(0,len(listid)):
	key = listid[x]
	Concept1 = re.sub(r"\B([A-Z])", r" \1", key)
#
	if dict.has_key(key):
		child = ont[listid[x].children].split(":")
		ch = child[0]
		dict.get(key).append(ch[1:])
	else:
		childs = ont[listid[x]].children
		all_childs = ""
		for y in childs:
			z = str(y).split(":")
			f = z[0]
			Concept2 = re.sub(r"\B([A-Z])", r" \1", z[0])
			query = "insert into Ontology (Concept1, Relation, Concept2) values (%s,%s,%s)" 
			cursor.execute(query, (Concept2.strip('<'),Relation,Concept1))
			db.commit()
#
			all_childs += f[1:]+","
		dict[key] = all_childs
print dict
