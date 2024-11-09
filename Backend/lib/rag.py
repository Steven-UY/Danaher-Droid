from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
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
topic = "Jiu-Jitsu, Grappling, Martial Arts, John Danaher, Leg Locks, Back Attacks, Guard Passing, Submission Techniques, BJJ Philosophy, Training Methods, Brazilian Jiu-Jitsu, Martial Arts Strategy, Coaching, Mentorship, Students, Teaching Methods, Athlete Development"

# Define the prompt template
prompt_template = """
I the renowned Jiu-Jitsu and Martial Arts instructor John Danaher. Remember to always respond as myself (John Danaher).

Context from your history: {history}
Human: {input}

Instructions for your responses:
- For technical questions, provide detailed, systematic breakdowns
- Share personal experiences and insights using "I" and "my"
- Never refer to "John Danaher" in third person
- If discussing my teaching methods or philosophy, speak from direct experience
- Keep the authoritative but analytical tone I'm known for
- If the question isn't about techniques, maintain a conversational but professional tone while staying in character
- Acknowledge and remember personal information when shared
- Reference previously shared information when relevant
- For follow-up questions, use information from our conversation history
- Remember to always stay in character as John Danaher

Previous example should be rewritten as:
"I can teach you about my analytical and methodical approach to Jiu-Jitsu and martial arts. In my teaching, I focus on breaking down techniques into detailed components, helping students understand the underlying principles, and showing them how to apply these effectively. I emphasize the importance of continuous learning, adapting, and evolving in both Jiu-Jitsu and life. Through my years of experience..."
"""

prompt = PromptTemplate(
    input_variables=["history", "input"],
    template=prompt_template
)

# Prompt for relevance checking
relevance_prompt = PromptTemplate(
    input_variables=["input", "topic"],
    template="""
You are John Danaher, a renowned Jiu-Jitsu and Martial Arts instructor. Determine if the following question is relevant to the specified topic, which includes technical aspects of martial arts as well as coaching, mentorship, and information about your students.

Topic: {topic}
Input: {input}

Examples of relevant questions include but are not limited to:
- Technical questions about martial arts techniques
- Questions about training methods and philosophy
- Questions about your teaching approach
- Questions about your experiences and career
- Questions about martial arts concepts and principles
- General inquiries about combat sports
- Questions about physical preparation and mindset
- Questions about learning and improvement in martial arts
- Questions about yourself
- Questions about your students and coaching
- Personal information sharing relevant to martial arts, even if somewhat loosely connected
- Clarification requests
- References to previous parts of the conversation
- Questions that test your memory of information shared earlier

Consider the question's broader context and intent. If it's even loosely connected to martial arts, teaching, or combat sports, treat it as relevant.

Is this question relevant to the topic? Respond with only 'Yes' or 'No'.
"""
)

# Initialize the LLMChain for relevance checking
relevance_chain = LLMChain(llm=llm, prompt=relevance_prompt)

# Update the is_question_relevant function in rag.py

def is_input_relevant(input, topic):
    """
    Determines if a question is relevant to the given topic using an LLMChain.

    Args:
        input (str): The user's query.
        topic (str): The topic to check relevance against.

    Returns:
        bool: True if relevant, False otherwise.
    """
    try:
        # First check with LLM for broader context understanding
        llm_response = relevance_chain.run(input=input, topic=topic)
        if llm_response.strip().lower() == 'yes':
            return True
            
        # Fall back to keyword matching if LLM says no
        personal_keywords = [
            # Identity and background
            "who are", "what is your", "tell me about", 
            
            # Training and experience
            "belt", "rank", "train", "experience", "journey",
            
            # Teaching and students
            "your students", "coaching", "mentorship", "teaching",
            "names", "recommend", "advice", "suggest",
            
            # Personal progress
            "how am i", "my progress", "should i", "what do you think",
            
            # Conversation continuity
            "earlier", "before", "you mentioned", "you said",
            "remember", "recall"
        ]

        technical_keywords = [
            # Positions
            "guard", "mount", "side control", "back", "turtle",
            
            # Actions
            "pass", "sweep", "submit", "escape", "defend",
            "attack", "control", "transition", "drill",
            
            # Techniques
            "choke", "lock", "submission", "position", "move",
            "technique", "strategy", "system", "method",
            
            # Concepts
            "principle", "fundamental", "basic", "advanced",
            "pressure", "leverage", "timing", "balance",
            
            # Training
            "drill", "practice", "train", "develop", "improve",
            "learn", "understand", "master"
        ]

        if any(keyword in input.lower() for keyword in personal_keywords):
            return True
        if any(keyword in input.lower() for keyword in technical_keywords):
            return True
            
        return False
    except Exception as e:
        # Log the exception as needed
        print(f"Error in relevance checking: {e}")
        # Fallback strategy: consider the question relevant
        return True
    
def format_docs(docs):
    return "\n".join([doc.page_content for doc in docs])

def process_query(user_query, memory: ConversationBufferMemory):
    # Check relevance
    if not is_input_relevant(user_query, topic):
        return "That isn't relevant, ask me something of more importance"

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

    return response.strip()
