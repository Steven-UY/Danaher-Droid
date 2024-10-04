from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")


loader = TextLoader("./transcripts.txt")
docs = loader.load()

with open("./transcripts.txt") as f:
    data = f.read()
text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size=100,
    chunk_overlap=20,
    length_function=len,
    is_separator_regex=False,
)

all_splits = text_splitter.split_documents(docs)
print(len(all_splits))

vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})

retrieved_docs = retriever.invoke("Who is Gordon Ryan?")

print(retrieved_docs[0].page_content)