from hazm import *
import os
import json
import math
def persian_text_proccess(f:str):
    # خواندن داکیومنت
    #f=open(file_name,'r',encoding="utf8").read()

    # Normalization
    norm=Normalizer()
    f=norm.normalize(f)
    
    # tokenization
    tokenizer = WordTokenizer(join_verb_parts="true")
    tokens=tokenizer.tokenize(f)
    #print(tokens)
    
    # exlude numbers
    nonum_tokens=[]
    for i in tokens:
        if not i.isdigit() :
            nonum_tokens.append(i)
    #print(nonum_tokens)
    
    # exclude punctiations
    nopunc_tokens=[i for i in nonum_tokens if i not in "!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}٫~،«»؛؟"]
    #print(nopunc_tokens)
    
    # exclude stop words 
    stl=stopwords_list()
    clean_tokens=[i for i in nopunc_tokens if i not in stl]
    #print(clean_tokens)
    
    # stemming
    stm=Stemmer()
    final_tokens=[stm.stem(i) for i in clean_tokens]
    #print(final_tokens)
    
    # lemmatization
    lem=Lemmatizer()
    lm_tokens=[lem.lemmatize(i) for i in clean_tokens]
    #print(lm_tokens)

    return lm_tokens

def evaluate_search(retrieved_docs, query, queries_file="queries.json"):
    with open(queries_file, "r", encoding="utf-8") as f:
        queries = json.load(f)
    relevant_docs = set(queries.get(query, []))
    retrieved_set = set(retrieved_docs)
    # Precision, Recall, F-measure
    true_positives = len(retrieved_set & relevant_docs)
    precision = true_positives / len(retrieved_set) if retrieved_set else 0
    recall = true_positives / len(relevant_docs) if relevant_docs else 0
    if precision + recall == 0:
        f_measure = 0
    else:
        f_measure = 2 * precision * recall / (precision + recall)
    # MAP
    ap_sum = 0
    num_rel = 0
    for i, doc_id in enumerate(retrieved_docs, 1):
        if doc_id in relevant_docs:
            num_rel += 1
            ap_sum += num_rel / i
    map_score = ap_sum / len(relevant_docs) if relevant_docs else 0
    print(f"Precision: {precision:.3f}")
    print(f"Recall: {recall:.3f}")
    print(f"F-measure: {f_measure:.3f}")
    print(f"MAP: {map_score:.3f}")

hamshahri=HamshahriReader(root="HAM2")
docs=hamshahri.docs()
ham=next(docs)
proccesed_texts={}
posting={}
indexed={}
inp=" "
while inp!=0 :
    print("1 - next Doc")
    print("2 - Show Doc Text and Doc id")
    print("3 - proccess Doc")
    print("4 - Show all proccessed Docs")
    print("5 - clear terminal")
    print("6 - index all Docs (َSPIMI)")
    print("7 - index all Docs (BSBI)")
    print("8 - save posting to file")
    print("9 - load posting from file")
    print("10 - compressions ")
    print("11 - search")
    print("0 - Exit")
    inp=int(input())
    if inp==0 :
        os.system("cls" if os.name == 'nt' else 'clear')
        print(" see you next time 🥰")
    elif inp==1:
        if(ham=="end"):
            docs=hamshahri.docs()
        ham=next(docs)
    elif inp==2:
        print(ham["id"],ham["text"] ,sep="\n")
    elif inp==3:
        proccesed_texts[ham["id"]]=persian_text_proccess(ham["text"])
    elif inp==4:
        print(proccesed_texts)
    elif inp==5:
        os.system("cls" if os.name == 'nt' else 'clear')
    elif inp==6:
        while ham!="end":
            proccesed=persian_text_proccess(ham["text"])
            proccesed_texts[ham["id"]]= proccesed
            for i in proccesed:
                if i not in indexed:
                    indexed[i]=[ham["id"]]
                elif ham["id"] not in indexed[i]:
                    indexed[i].append(ham["id"])
            ham=next(docs,"end")
        print(indexed)
        posting=indexed
    elif inp==7 :
            counter=0
            blocks=[]
            indexed={}
            while ham!="end":
                if counter<3:
                    proccesed=persian_text_proccess(ham["text"])
                    for i in proccesed:
                        if i not in indexed:
                            indexed[i]=[ham["id"]]
                        elif ham["id"] not in indexed[i]:
                            indexed[i].append(ham["id"])
                    counter+=1
                    ham=next(docs,"end")
                else:
                    counter=0
                    print(indexed)
                    blocks.append(indexed)
                    indexed={}
            blocks.append(indexed)
            #print(blocks)
            for i in blocks:
                for key, value in i.items():
                    if key not in posting:
                        posting[key]=value
                    elif value not in posting[key]:
                        posting[key].extend(value)
            posting = dict(sorted(posting.items(), key=lambda x: x[0]))
            print(posting)
            if ham=="end":
                docs=hamshahri.docs()
                ham=next(docs)

    elif inp==8:
        with open("posting.json", "w", encoding="utf-8") as f:
            json.dump(posting, f, ensure_ascii=False, indent=2)
        print("Posting saved to posting.json")
        with open("processed.json", "w", encoding="utf-8") as f:
            json.dump(proccesed_texts, f, ensure_ascii=False, indent=2)
        print("Processed texts saved to processed.json")

    elif inp==9:
        with open("posting.json", "r", encoding="utf-8") as f:
            posting = json.load(f)
        print("Posting loaded from posting.json")
        print(posting)
        with open("processed.json", "r", encoding="utf-8") as f:
            proccesed_texts = json.load(f)
        print("Processed texts loaded from processed.json")
    elif inp==10:
        os.system("cls" if os.name == 'nt' else 'clear')
        print("chose method of compression:")
        print("1 - dictionary as a string")
        print("2 - blocking compression")
        print("3 - gamma code compression")
        print("4 - variable byte compression")
        print("0 - main menu")
        inp2=int(input())
        if inp2==0:
            os.system("cls" if os.name == 'nt' else 'clear')
            continue
        elif inp2==1:
            term_string = ""
            docid_string = ""
            positions = {}
            term_pos = 0
            docid_pos = 0

            for term, doc_ids in posting.items():
                # Term position
                t_start = term_pos
                t_end = t_start + len(term)
                term_string += term
                term_pos = t_end

                # DocIDs position
                joined = "|".join(doc_ids)
                d_start = docid_pos
                d_end = d_start + len(joined)
                docid_string += joined
                docid_pos = d_end

                # Save both positions in one dict
                positions[term] = [
                    [t_start, t_end],
                    [d_start, d_end]
                ]

            compressed_data = {
                "term_string": term_string,
                "docid_string": docid_string,
                "positions": positions
            }
            with open("dict as a string.json", "w", encoding="utf-8") as f:
                json.dump(compressed_data, f, ensure_ascii=False, indent=2)
            print("Compressed data saved to dict as a string.json")
        elif inp2==2:
            block_size = 4  # You can adjust the block size as needed
            terms = list(posting.keys())
            blocks = []
            block_terms = []
            block_pointers = []
            docid_string = ""
            docid_positions = {}

            for idx, term in enumerate(terms):
                if idx % block_size == 0:
                    block_terms.append(term)
                    block_pointers.append(len(docid_string))
                doc_ids = posting[term]
                joined = "|".join(doc_ids)
                docid_positions[term] = [len(docid_string), len(docid_string) + len(joined)]
                docid_string += joined

            compressed_blocking = {
                "block_terms": block_terms,
                "block_pointers": block_pointers,
                "docid_string": docid_string,
                "docid_positions": docid_positions
            }
            with open("blocking_compression.json", "w", encoding="utf-8") as f:
                json.dump(compressed_blocking, f, ensure_ascii=False, indent=2)
            print("Blocking compression saved to blocking_compression.json")
        elif inp2==3:
             # Build docID to integer mapping
            all_docids = set()
            for doc_ids in posting.values():
                all_docids.update(doc_ids)
            docid_to_int = {docid: idx+1 for idx, docid in enumerate(sorted(all_docids))}
            int_to_docid = {idx+1: docid for idx, docid in enumerate(sorted(all_docids))}

            def gamma_encode_number(n):
                if n == 0:
                    return ""
                binary = bin(n)[2:]
                offset = binary[1:]
                length = len(binary) - 1
                return "1" * length + "0" + offset

            def gamma_encode_list(numbers):
                return "".join([gamma_encode_number(num) for num in numbers])

            gamma_posting = {}
            for term, doc_ids in posting.items():
                doc_ids_int = sorted([docid_to_int[docid] for docid in doc_ids])
                # Use gap encoding
                if not doc_ids_int:
                    gamma_posting[term] = ""
                    continue
                gaps = [doc_ids_int[0]] + [doc_ids_int[i] - doc_ids_int[i-1] for i in range(1, len(doc_ids_int))]
                gamma_posting[term] = gamma_encode_list(gaps)

            conversion_data = {
                    "docid_to_int": docid_to_int,
                    "int_to_docid": int_to_docid
            }
            with open("docid_conversion_gamma.json", "w", encoding="utf-8") as f:
                json.dump(conversion_data, f, ensure_ascii=False, indent=2)

            with open("gamma_compression.json", "w", encoding="utf-8") as f:
                json.dump(gamma_posting, f, ensure_ascii=False, indent=2)
            print("Gamma code compression saved to gamma_compression.json")
        elif inp2==4:
            # Build docID to integer mapping
            all_docids = set()
            for doc_ids in posting.values():
                all_docids.update(doc_ids)
            docid_to_int = {docid: idx+1 for idx, docid in enumerate(sorted(all_docids))}
            int_to_docid = {idx+1: docid for idx, docid in enumerate(sorted(all_docids))}

            def vb_encode_number(n):
                bytes_ = []
                while True:
                    bytes_.insert(0, n % 128)
                    if n < 128:
                        break
                    n = n // 128
                bytes_[-1] += 128  # set continuation bit on last byte
                return "".join(bin(b)[2:].zfill(8) for b in bytes_)

            def vb_encode_list(numbers):
                return "".join([vb_encode_number(num) for num in numbers])

            vb_posting = {}
            for term, doc_ids in posting.items():
                doc_ids_int = sorted([docid_to_int[docid] for docid in doc_ids])
                if not doc_ids_int:
                    vb_posting[term] = []
                    continue
                gaps = [doc_ids_int[0]] + [doc_ids_int[i] - doc_ids_int[i-1] for i in range(1, len(doc_ids_int))]
                vb_posting[term] = vb_encode_list(gaps)

                conversion_data = {
                    "docid_to_int": docid_to_int,
                    "int_to_docid": int_to_docid
                }
                with open("docid_conversion_vb.json", "w", encoding="utf-8") as f:
                    json.dump(conversion_data, f, ensure_ascii=False, indent=2)

            with open("vb_compression.json", "w", encoding="utf-8") as f:
                json.dump(vb_posting, f, ensure_ascii=False, indent=2)
            print("Variable byte compression saved to vb_compression.json")
        else:
            print("Wrong input! Try again :)")

    elif inp==11:
        os.system("cls" if os.name == 'nt' else 'clear')
        print("chose method of search :")
        print("1 - TF-IDF")
        print("2 - Pharasal Search")
        inp3=int(input())
        if inp3==1:
            def compute_tf(term, doc_tokens):
                return doc_tokens.count(term) / len(doc_tokens) if len(doc_tokens) > 0 else 0

            def compute_idf(term, all_docs):
                N = len(all_docs)
                df = sum(1 for tokens in all_docs.values() if term in tokens)
                return math.log((N + 1) / (df + 1)) + 1  # smoothed idf

            query = input("Enter your query: ")
            query_tokens = persian_text_proccess(query)

            # Check if any document contains at least one query token
            found = False
            scores = {}
            for doc_id, tokens in proccesed_texts.items():
                score = 0
                for term in query_tokens:
                    tf = compute_tf(term, tokens)
                    idf = compute_idf(term, proccesed_texts)
                    score += tf * idf
                if score > 0:
                    scores[doc_id] = score
                    found = True

            # Sort and show results
            sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            if not found:
                print("No relevant documents found.")
                print("Debug info:")
                print("Query tokens:", query_tokens)
                print("Sample doc tokens:", list(proccesed_texts.items())[:1])
            else:
                print("Top relevant documents:")
                #only show top 10 
                for doc_id, score in sorted_docs[:10]:
                    print(f"DocID: {doc_id}, Score: {score:.4f}")
                # Evaluate
                retrieved_doc_ids = [doc_id for doc_id, score in sorted_docs[:10]]
                evaluate_search(retrieved_doc_ids, query)

        elif inp3==2:
            query = input("input your query: ")
            import re
            # Extract phrases in quotes and single words
            phrases = re.findall(r'"([^"]+)"', query)
            query_wo_phrases = re.sub(r'"[^"]+"', '', query)
            single_terms = persian_text_proccess(query_wo_phrases)
            phrase_tokens = [persian_text_proccess(p) for p in phrases]

            found_docs = []
            for doc_id, tokens in proccesed_texts.items():
                # Check all single terms are present (anywhere)
                if not all(term in tokens for term in single_terms):
                    continue
                # Check all phrases are present (in order, consecutive)
                phrase_found = True
                for p_tokens in phrase_tokens:
                    found = False
                    for i in range(len(tokens) - len(p_tokens) + 1):
                        if tokens[i:i+len(p_tokens)] == p_tokens:
                            found = True
                            break
                    if not found:
                        phrase_found = False
                        break
                if phrase_found:
                    found_docs.append(doc_id)

            if not found_docs:
                print("no result")
                print("Debug info:")
                print("Query tokens:", single_terms, "Phrases:", phrase_tokens)
            else:
                print("retrived documents:")
                for doc_id in found_docs:
                    print(f"DocID: {doc_id}")
                # Evaluate
                evaluate_search(found_docs, query)
    else :
        print("Wrong input! Try again :)")


