from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import os

load_dotenv()

api_key = os.getenv("API_KEY")

persist_directory = "./chroma_db"
collection_name = "your_collection_name"

embeddings = OpenAIEmbeddings()

# Check if the vectorstore already exists
if os.path.exists(persist_directory):
    # Load existing vectorstore
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_directory
    )
else:
    # Create new vectorstore
    loader = TextLoader("./transcripts.txt")
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=500,
        length_function=len,
        is_separator_regex=False,
    )

    all_splits = text_splitter.split_documents(docs)
    print(f"Number of splits: {len(all_splits)}")

    vectorstore = Chroma.from_documents(
        documents=all_splits, 
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=persist_directory
    )
    print("Created and persisted new vectorstore")

# Use the vectorstore
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 50})

llm = ChatOpenAI(model="gpt-4-0125-preview", temperature=0.3, max_tokens=1000)

prompt = hub.pull("rlm/rag-prompt")

example_messages = prompt.invoke(
    {"context": "filler context", "question": "filler question"}
).to_messages()

def format_docs(docs):
    return "\n".join([doc.page_content for doc in docs])

#come back to this
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

#
def print_retrieved_docs(query, threshold=0.3):
    docs = retriever.get_relevant_documents(query)
    print(f"\nRetrieved {len(docs)} documents for query: '{query}'\n")
    for i, doc in enumerate(docs, 1):
        print(f"Document {i}:")
        print(f"Content: {doc.page_content[:200]}...")  # Print first 200 characters
        print(f"Metadata: {doc.metadata}")
        if hasattr(doc, 'similarity_score'):
            print(f"Similarity score: {doc.similarity_score}")
        else:
            print("No similarity score available")
        print()

# Modify the main conversation loop
while True:
    user_query = input("Enter your question (or 'quit' to exit): ")
    if user_query.lower() == 'quit':
        break

    # Retrieve documents
    docs = retriever.get_relevant_documents(user_query)
    
    # Check if any documents were retrieved
    if not docs:
        print("\nAI Response:")
        print("I'm sorry, but I don't have relevant information to answer that question. Could you please rephrase or ask a different question?")
        continue

    # Print retrieved documents
    print_retrieved_docs(user_query)

    # Proceed with RAG for queries with retrieved documents
    print("\nAI Response:")
    for chunk in rag_chain.stream(user_query):
        print(chunk, end="", flush=True)

    print("\n")

print("Conversation ended.")
