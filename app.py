from fastapi import Body, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, constr
import json
from pyserini.search.lucene import LuceneSearcher
from pyserini.index import IndexReader
from transformers import BertTokenizerFast,BertForQuestionAnswering,AutoTokenizer,AutoModelForQuestionAnswering
from udicOpenData.dictionary import *
from udicOpenData.stopwords import *
import torch


#中文反向索引表(用BM25)
searcher = LuceneSearcher('sample_collection_jsonl')
index_reader = IndexReader('sample_collection_jsonl')

#Retriever
def Retreiver(quesion):
  searcher.set_language('zh')
  hits = searcher.search(quesion, k=30)
  # for hit in hits:
    # print(hit.raw)
  return hits

#Question-Answering 中文
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
Chinese_tokenizer = BertTokenizerFast.from_pretrained("nyust-eb210/braslab-bert-drcd-384")
Chinese_model = BertForQuestionAnswering.from_pretrained("nyust-eb210/braslab-bert-drcd-384").to(device)


#Reader
def simpleReader(text, query):
  device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
  tokenizer = AutoTokenizer.from_pretrained("nyust-eb210/braslab-bert-drcd-384")
  model = AutoModelForQuestionAnswering.from_pretrained("nyust-eb210/braslab-bert-drcd-384").to(device)
  encoded_input = tokenizer(text, query, return_tensors="pt").to(device)
  qa_outputs = model(**encoded_input)

  start = torch.argmax(qa_outputs.start_logits).item()
  end = torch.argmax(qa_outputs.end_logits).item()
  answer = encoded_input.input_ids.tolist()[0][start : end + 1]
  answer = "".join(tokenizer.decode(answer).split())

  start_prob = torch.max(torch.nn.Softmax(dim=-1)(qa_outputs.start_logits)).item()
  end_prob = torch.max(torch.nn.Softmax(dim=-1)(qa_outputs.end_logits)).item()
  confidence = (start_prob + end_prob) / 2
  return answer


print(len(Retreiver("中興大學")))

class ZHQARequest(BaseModel):
    maintext: constr(max_length=512)

app = FastAPI(
    title="Open-Domain Question Answering",
    description="Open-Domain Question Answering",
    version="0.1.0",
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")



@app.get("/")
async def root():
    return RedirectResponse("docs")


@app.get("/page/{page_name}", response_class=HTMLResponse)
async def page(request: Request, page_name: str):
    return templates.TemplateResponse(f"{page_name}.html", {"request": request})


@app.post("/zhqa")
async def zhqa(
    zhqa_request: ZHQARequest = Body(
        None,
        
    )
):
    print(zhqa_request)

    query = zhqa_request.maintext
    print("Query = ",query)
    hits = Retreiver(query)
    #hits = Retreiver("中興大學在哪裡?")
    word = list(rmsw(query,flag=False))
    result = []
    print(word)
    answer = "XD"

    for i in hits:
        context = json.loads(i.raw)["contents"]
        if len(context) >= 256 and len(context) <= 490:
            if "中興大學" in context and "中興" in context:
                answer = simpleReader(context,query)
                result.append(answer)
            # for token in word:
            #     if token not in context:
            #         break
            #     if token == word[-1] and token in context:
            #         answer = simpleReader(context,query)
            #         result.append(answer)

    print(result)
            
               

    
    return answer