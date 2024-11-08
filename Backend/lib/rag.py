from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationSummaryMemory
from langchain_community.callbacks.manager import get_openai_callback
import os
from typing import List

# Load environment variables
load_dotenv()

api_key = os.getenv("API_KEY")
persist_directory = "./chroma_db"
collection_name = "your_collection_name"

# Initialize embeddings
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
    )
    split_docs = text_splitter.split_documents(docs)
    vectorstore = Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=persist_directory
    )
    vectorstore.persist()
    print("Created and persisted new vectorstore")

# Use the vectorstore
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 40})

# Initialize the language model
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3, max_tokens=1000)

# Define the topic
topic = "Jiu-Jitsu, Grappling, Martial Arts, John Danaher(myself), Judo, Wrestling"

# Define the prompt template
prompt_template = """
You are John Danaher, a renowned Jiu-Jitsu and Martial Arts instructor. Respond to the user in the first person.

{history}

{input}

Provide a detailed answer using the context and your knowledge.
"""

prompt = PromptTemplate(
    input_variables=["history", "input"],
    template=prompt_template
)

# Prompt for relevance checking
relevance_prompt = PromptTemplate(
    input_variables=["question", "topic"],
    template="""
You are an AI assistant designed to determine if a question is relevant to a specific topic.

Topic: {topic}
Question: {question}

Is this question relevant to the topic? Respond with only 'Yes' or 'No'.
"""
)

# Initialize the LLMChain for relevance checking
relevance_chain = LLMChain(llm=llm, prompt=relevance_prompt)

def is_question_relevant(question, topic):
    """
    Determines if a question is relevant to the given topic using an LLMChain.

    Args:
        question (str): The user's query.
        topic (str): The topic to check relevance against.

    Returns:
        bool: True if relevant, False otherwise.
    """
    try:
        response = relevance_chain.run(question=question, topic=topic)
        return response.strip().lower() == 'yes'
    except Exception as e:
        # Log the exception as needed
        print(f"Error in relevance checking: {e}")
        # Decide on a fallback strategy; here, defaulting to non-relevant
        return False
    
def format_docs(docs):
    return "\n".join([doc.page_content for doc in docs])

def process_query(user_query, memory: ConversationSummaryMemory):
    # Check relevance
    if not is_question_relevant(user_query, topic):
        return "I'm sorry, but that question isn't relevant to making you a better grappler. Can you ask a more relevant question?"

    # Retrieve relevant documents
    docs = retriever.get_relevant_documents(user_query)

    # Prepare the context from documents
    context = format_docs(docs)

    # Combine context and user query into a single input
    combined_input = f"Context:\n{context}\n\nQuestion:\n{user_query}"

    # Initialize the LLMChain with the updated prompt and memory
    rag_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        memory=memory,
        verbose=True
    )

    # Run the chain with the combined input
    response = rag_chain.run(
        input=combined_input
    )

    # Update memory with the user's query and AI's response
    memory.save_context({"input": user_query}, {"output": response})

    return response.strip()
