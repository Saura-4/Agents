import math

def tokenize(text):
    text = text.lower()
    tokenized_text=text.split()

    return tokenized_text

def document_frequency(term, documents):

    count=0
    for i in documents:
        memo = tokenize(i["memory"])

        for  j in memo:
            if term == j :
                count=count+1
                break
        
    return count

def idf(term, documents):

    N=len(documents)
    df=document_frequency(term,documents)

    return math.log((N-df+0.5)/(df+0.5))

def term_frequency(query, memory):

    t_query=tokenize(query)
    t_memory=tokenize(memory)

    tf = {}
    for term in t_query:
        count = 0

        for word in t_memory:
            if term == word:
                count += 1

        tf[term] = count

    return tf

def average_document_length(doucments):

    N=len(doucments)
    s=0
    for doc in doucments:
        s += len(tokenize(doc["memory"]))
    return s/N

def normalized_document_length(memory, documents):
    document_length = len(tokenize(memory))
    avgdl = average_document_length(documents)

    return document_length / avgdl

def bm25_score(query, memory, documents):

    term_freq=term_frequency(query,memory)
    t_query= tokenize(query)
    NDL = normalized_document_length(memory,documents)
    k1=1.5
    b=0.75

    bm_scroes = 0
    for term in t_query:

        IDF = idf(term,documents)
        TF = term_freq[term]

        NUM = IDF*( TF * (k1 + 1))
        DN =  TF + k1 * (1 - b + b * NDL)

        score = NUM/DN

        bm_scroes += score

    return bm_scroes

def retrieve_memories_bm25(query, documents, top_k=3):

    ranking=[]
    for doc in documents:
        memory=doc["memory"]
        id = doc["id"]
        score=bm25_score(query,memory,documents)
        ranking.append(
            {
                "memory": memory,
                "id": id,
                "score": score
            }
        )
    ranking.sort(key=lambda x: x["score"], reverse=True)

    return ranking[:top_k]

