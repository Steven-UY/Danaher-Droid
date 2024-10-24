from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dotenv import load_dotenv
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
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

# Prompt template we use for the RAG template 
prompt_template = """
You are an AI assistant knowledgeable about Jiu-Jitsu.

{chat_history}

Context:
{context}

Question:
{question}

Provide a detailed answer using the context and your knowledge.
"""

prompt = PromptTemplate(
    input_variables=["chat_history", "context", "question"],
    template=prompt_template
)

# Create LLMChain without memory
rag_chain = LLMChain(
    llm=llm,
    prompt=prompt
)

#Prompt that we use for relevance checking
relevance_prompt = PromptTemplate(
    input_variables=["question", "topic"],
    template="""
You are an AI assistant designed to determine if a question is relevant to a specific topic.

Topic: {topic}
Question: {question}

Is this question relevant to the topic? Respond with only 'Yes' or 'No'.
"""
)

# Create a chain for relevance checking
relevance_chain = LLMChain(llm=llm, prompt=relevance_prompt)

#checks if the question is relevant to the topic
def is_question_relevant(question, topic):
    response = relevance_chain.run(question=question, topic=topic)
    return response.strip().lower() == 'yes'

#formats list of docs into a single string, prepares inputs for the RAG chain
def format_docs(docs):
    return "\n".join([doc.page_content for doc in docs])

# Initialize conversation history
conversation_history = []

topic = "Jiu-Jitsu"  # Replace with your actual topic

def process_query(user_query):
    # Check relevance
    if not is_question_relevant(user_query, topic):
        return "I'm sorry, but that question doesn't seem to be related to Jiu-Jitsu. Could you please ask a question related to Jiu-Jitsu?"

    # Retrieve documents
    docs = retriever.get_relevant_documents(user_query)

    # Format conversation history (you might need to adjust this part)
    chat_history_formatted = ""  # You may want to pass conversation history from the frontend

    # Prepare inputs for the chain
    chain_inputs = {
        "question": user_query,
        "context": format_docs(docs),
        "chat_history": chat_history_formatted
    }

    # Get the AI response
    response = rag_chain(chain_inputs)

    return response['text']
