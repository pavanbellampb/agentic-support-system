from functools import lru_cache
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


PROJECT_ROOT = Path(__file__).resolve().parents[2]
POLICY_FILE = PROJECT_ROOT / "data" / "policies.txt"


@lru_cache(maxsize=1)
def get_vector_store() -> FAISS:
    """Load policy text and create a small FAISS vector index once per process."""
    if not POLICY_FILE.exists():
        raise FileNotFoundError(f"Policy file not found: {POLICY_FILE}")

    policy_text = POLICY_FILE.read_text(encoding="utf-8").strip()
    if not policy_text:
        raise ValueError("The policy file is empty.")

    documents = [Document(page_content=policy_text, metadata={"source": "policies.txt"})]
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80,
        separators=["\n\n", "\n", ". ", " "],
    )
    chunks = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    return FAISS.from_documents(chunks, embeddings)


def search_policies(query: str, k: int = 3) -> str:
    """Retrieve policy passages relevant to a customer question."""
    retriever = get_vector_store().as_retriever(search_kwargs={"k": k})
    docs = retriever.invoke(query)

    if not docs:
        return "No relevant policy passages were retrieved."

    formatted = []
    for index, doc in enumerate(docs, start=1):
        formatted.append(f"[Policy passage {index}]\n{doc.page_content.strip()}")
    return "\n\n".join(formatted)
