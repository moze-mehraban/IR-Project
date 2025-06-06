from hazm import *
import os
import json
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
            for i in proccesed:
                if i not in indexed:
                    indexed[i]=[ham["id"]]
                elif ham["id"] not in indexed[i]:
                    indexed[i].append(ham["id"])
            ham=next(docs,"end")
        print(indexed)
        posting=indexed
        ham=next(docs)
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

    elif inp==9:
        with open("posting.json", "r", encoding="utf-8") as f:
            posting = json.load(f)
        print("Posting loaded from posting.json")
        print(posting)
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
    else :
        print("Wrong input! Try again :)")


