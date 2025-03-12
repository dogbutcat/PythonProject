from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
import lancedb
import pyarrow as pa

import numpy as np
import os
import uuid
import uvicorn
import ast

from jina_embeddings_model import load_model, process_text  # Assuming you have this file
from jina_reranker_model import load_model as r_load_model, create_index
from code_splitter import parse_code_chunks

app = FastAPI()

# --- Configuration ---
DB_PATH = "./code_index_db"  # Path to store LanceDB database
TABLE_NAME = "code_index"
EMBEDDING_DIM = 1024
DEFAULT_MODEL_NAME = "jina-embeddings-v3"

# --- Load embedding model ---
try:
    embed_v3_model, embed_v3_tokenizer = load_model()
except Exception as e:
    print(f"Error loading embedding model: {e}")
    exit(1)

try:
    rerank_model = r_load_model()
    rerank_index, rerank_retriever = create_index(index_folder=DB_PATH, index_name=TABLE_NAME)
except Exception as e:
    print(f"Error loading reranker model: {e}")
    exit(1)


# --- Data Models ---
class CodeDocument(BaseModel):
    file_path: str
    content: str
    project_name: str  # Add project_name
    code_blocks: List[Dict[str, str]] = []  # List of dictionaries: {"block_id": str, "content": str}

class EmbeddingRequest(BaseModel):
    input: Union[str, List[str]]
    model: Optional[str] = DEFAULT_MODEL_NAME

class EmbeddingResponse(BaseModel):
    object: str = "list"
    data: List[Dict[str, Any]]
    model: str
    usage: Dict[str, int]

class SearchRequest(BaseModel):
    fullInput: str
    query: str
    top_k: int = 500
    model: Optional[str] = DEFAULT_MODEL_NAME
    project_name: Optional[str] = None # add project_name

class SearchResult(BaseModel):
    # file_path: str
    content: str
    score: float
    code_block_content: str = None
    code_block_id: str = None
    project_name: str #add project_name
    name: str  # Add name
    description: str  # Add description
    # text: str # Add text (content)
    uri:Dict[str, str]

class BlockIndex(BaseModel):
    block_id: str
    file_path: str
    content: str
    project_name: str #add project_name

# --- Database Initialization ---
db = lancedb.connect(DB_PATH)

def get_or_create_table(db, table_name, data=None, schema=None):
    """
    尝试获取 LanceDB 中的表，如果表不存在则创建它。

    Args:
        db: LanceDB 数据库连接对象。
        table_name: 表名。
        data: 用于初始化表的数据，可选。
        schema: 表的 schema，可选。

    Returns:
        LanceTable: LanceTable 对象。
    """
    try:
        # 尝试打开表
        table = db[table_name]  # 或 db.open_table(table_name)
        print(f"Table '{table_name}' already exists. Returning existing table.")
        return table
    except ValueError as e:
        # 捕获表不存在的异常, 检查异常信息中是否包含 "Table 'table_name' was not found"
        if f"Table '{table_name}' was not found" in str(e):
            print(f"Table '{table_name}' not found. Creating a new table.")
            # 创建新表
            if data is None and schema is None:
                raise ValueError("Must provide data or schema to create a new table.")
            table = db.create_table(table_name, data=data, schema=schema)
            print(f"Table '{table_name}' created successfully.")
            return table
        else:
            # 如果是其他类型的 ValueError，则重新抛出异常
            raise e
    except Exception as e:
        # 捕获其他异常
        print(f"An unexpected error occurred: {e}")
        raise  # 重新抛出异常，以便进一步调试

schema = pa.schema(
    [
        pa.field("embedding", lancedb.vector(EMBEDDING_DIM)),
        pa.field("file_path", pa.string()),
        pa.field("content", pa.string()),
        pa.field("code_block_content", pa.string(), nullable=True),
        pa.field("code_block_id", pa.string(), nullable=True),
        pa.field("id", pa.string()),
        pa.field("project_name", pa.string()),
        pa.field("block_start_line", pa.string(), nullable=True),
        pa.field("block_end_line", pa.string(), nullable=True),
        pa.field("block_type", pa.string(), nullable=True),
    ]
)
table = get_or_create_table(db, TABLE_NAME, schema=schema)


# --- Helper Functions ---
def get_embedding(texts: List[str], model_name:str = DEFAULT_MODEL_NAME) -> np.ndarray:
    """
    Gets the embedding for a given text using the specified model.
    Currently only supports jina-embeddings-v3, but can be extended.
    """
    if model_name == DEFAULT_MODEL_NAME:
        embeddings = process_text(embed_v3_model, embed_v3_tokenizer, texts, "retrieval.passage")
        return embeddings
    else:
        raise ValueError(f"Unsupported model: {model_name}")

def rerank(query_embeddings: List[float], results: List[dict], k: int = 10):

    documents_ids = []
    documents_embeddings = []
    documents_contents = []
    # print(results)
    for v in results:
        documents_ids.append(v["id"])
        documents_embeddings.append(v["embedding"])
        documents_contents.append(v["content"])


    documents_embeddings = rerank_model.encode(
        documents_contents,
        # batch_size=2000,
        is_query=False, # Encoding documents
        show_progress_bar=True,
        # device="mps",
    )
    # print(len(documents_embeddings[1][0]))
    # print((documents_embeddings[0][0]))
    # print(len(documents_embeddings[1]))
    # print((documents_embeddings[0]))
    # print(len(documents_embeddings))
    # print()

    # Add the documents ids and embeddings to the Voyager index
    rerank_index.add_documents(
        documents_ids=documents_ids,
        documents_embeddings=documents_embeddings,
    )

    # print(type(query_embeddings))
    queries_embeddings = rerank_model.encode(
        [query_embeddings],
        # batch_size=2000,
        is_query=True, # Encoding queries
        show_progress_bar=True,
        # device="mps",
    )

    # print()
    # print()
    # print(queries_embeddings)
    scores = rerank_retriever.retrieve(
        queries_embeddings=queries_embeddings,
        k=k,
    )
    scores_map = {}
    for v in scores[0]:
        id, score = v
        scores_map[v[id]] = v[score]
    # print("scores_map")
    # print(scores_map)

    rerank_results = []
    for result in results:
        id = result['id']
        if id in scores_map:
            rerank_result = result.copy()
            rerank_result["score"] = scores_map[id]
            rerank_results.append(rerank_result)
    rerank_results.sort(key=lambda x: x["score"], reverse=True)
    return rerank_results

# --- API Endpoints ---

@app.post("/v1/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(request: EmbeddingRequest):
    try:
        # 打印完整的请求参数
        print("\n=== Request Parameters ===")
        print(f"Raw request model dump: {request.model_dump()}")  # 完整模型转储
        # print(f"JSON compatible dict: {request.model_dump_json()}")  # JSON格式的数据
        print("========================\n")

        texts = request.input if isinstance(request.input, list) else [request.input]

        embeddings = get_embedding(texts)
        print(len(embeddings), len(embeddings[0]))
       
        # 构造响应
        data = []
        for i, embedding in enumerate(embeddings):
            data.append({
                "object": "embedding",
                "embedding": embedding.tolist(),
                "index": i
            })
        
        # 计算token使用量（简化版）
        total_tokens = sum(len(embed_v3_tokenizer.encode(text)) for text in texts)
        
        return EmbeddingResponse(
            data=data,
            model=request.model,
            usage={
                "prompt_tokens": total_tokens,
                "total_tokens": total_tokens
            }
        )

    except ValueError as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/index")
async def index_code(document: CodeDocument, model: Optional[str] = DEFAULT_MODEL_NAME):
    """Indexes a code document into the database."""
    try:
        blocks = parse_code_chunks(document.content, get_file_ext(document.file_path)[1:]) # exlucde \.
        block_data = []
        if len(blocks) > 0:
            for block in blocks:
                if block["type"] in ("function", "class", "expression", "decoed"):
                    # type in TYPE_MAP
                    content_embedding = get_embedding(block["content"], model)
                    document_id = str(uuid.uuid4())
                    data = {
                        "id": document_id,
                        "file_path": document.file_path,
                        "content": block["content"],
                        "embedding": content_embedding,
                        "block_start_line": block["start_line"],
                        "block_end_line": block["end_line"],
                        "block_type": block["type"],
                        # "code_block_content": block["content"],
                        "project_name": document.project_name, #add project name
                    }
                    block_data.append(data)
        else:
            document_id = str(uuid.uuid4())
            content_embedding = get_embedding(document.content, model)
            block_data = [{
                        "id": document_id,
                        "file_path": document.file_path,
                        "content": document.content,
                        "embedding": content_embedding,
                        "project_name": document.project_name, #add project name
                    }]
        table.add(block_data)
        return {"message": "Document indexed successfully"}
    except ValueError as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_file_name_from_path(file_path: str):
    return os.path.basename(file_path)

def get_file_ext(file_path: str):
    return os.path.splitext(file_path)[1]

@app.post("/retrieve", response_model=List[SearchResult])
async def search_code(request: SearchRequest):
    """Searches the indexed code based on a query."""
    try:
        print("\n=== Request Parameters ===")
        print(f"Raw request model dump: {request.model_dump()}")  # 完整模型转储
        # print(f"JSON compatible dict: {request.model_dump_json()}")  # JSON格式的数据
        print("========================\n")
        query_embedding = get_embedding(request.fullInput)
        print(query_embedding)
        
        where_clause = None
        if request.project_name:
            where_clause = f"project_name = '{request.project_name}'"
            
        results = table.search(query_embedding).where(where_clause).limit(request.top_k).to_list()
        
        print("search result: %d" % len(results))
        # print()
        # print(query_embedding)
        rerank_results = rerank(request.fullInput, results,)
        # print(rerank_results)

        search_results = []
        for item in rerank_results[:]:
            line_append = ""
            if item["block_start_line"] is not None:
                line_append = f' ({item["block_start_line"]}-{item["block_end_line"]})'
            search_results.append(SearchResult(
                # file_path=item["file_path"],
                # content=item["content"],
                # score=item["_distance"],
                # code_block_content=item["code_block_content"],
                # code_block_id=item["code_block_id"],
                project_name=item["project_name"], #add project name
                # text=item["content"],
                # description=item["file_path"],
                name=get_file_name_from_path(item["file_path"])+line_append,
                description=(item["file_path"]),
                content=f'```{item["file_path"]}\n{item["content"]}\n```',
                # content=f'{item["file_path"]}\n{item["content"]}\n',
                uri = {
                    'type': "file",
                    'value': item["file_path"],
                },
                score=item["score"]
            ))
        return search_results
    except ValueError as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/index_files")
async def index_files(files: List[UploadFile] = File(...), model: Optional[str] = DEFAULT_MODEL_NAME, project_name: str = "default"):
    """
    Indexes a list of uploaded files.
    """
    for file in files:
        try:
            file_content = await file.read()
            file_content = file_content.decode('utf-8')
            file_path = os.path.abspath(file.filename)
            document = CodeDocument(file_path=file_path, content=file_content, project_name=project_name)
            await index_code(document, model)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            print(f"Error indexing file {file.filename}: {e}")

    return {"message": "Files indexed successfully"}

@app.get("/block/{block_id}", response_model=BlockIndex)
async def get_block(block_id: str):
    """
    Retrieves a specific code block by its ID.
    """
    try:
        results = table.search("id").where(f"code_block_id = '{block_id}'").limit(1).to_list()
        if not results:
            raise HTTPException(status_code=404, detail="Block not found")
        result = results[0]
        return BlockIndex(block_id=result['code_block_id'], file_path=result['file_path'], content=result['code_block_content'], project_name=result["project_name"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7001)
