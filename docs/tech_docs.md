# Danaher-Droid Technical Documentation

## Overview
This document provides detailed technical explanations and code snippets for how the Danaher-Droid works, including the RAG (Retrieval-Augmented Generation) pipeline and the specific tools and libraries used (YouTube Data API, youtube_transcript_api, Langchain, and Chroma).

---

## RAG Pipeline

### 1. YouTube Data API - Retrieving Video IDs

#### a. API Client Setup
- Use the `googleapiclient` library to build the API client for making authorized requests to YouTube's API.
    ```python
    youtube = build('youtube', 'v3', developerKey=api_key)
    ```

#### b. Fetching the Uploads Playlist
- Get the uploads playlist ID from the channel using the channel ID.
    ```python
    res = youtube.channels().list(id=channel_id, part='contentDetails').execute()
    ```

#### c. Fetching Video IDs from the Playlist
- Use a loop to retrieve 50 video IDs per request until all videos in the playlist are fetched.
    ```python
    next_page_token = None
    while True:
        pl_request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        pl_response = pl_request.execute()

        for item in pl_response['items']:
            video_ids.append(item['contentDetails']['videoId'])

        next_page_token = pl_response.get('nextPageToken')
        if not next_page_token:
            break

    return video_ids
    ```

---

### 2. YouTube Transcript API - Scraping Transcripts
- Use the `youtube_transcript_api` to scrape transcripts from the retrieved YouTube video IDs. This API makes it easy to retrieve captions or subtitles from YouTube videos for further processing.

---

### 3. Langchain and Chroma - Storing and Processing the Transcripts

#### a. Loading Transcripts
- Use Langchain to load transcripts from a local text file or any other source.
    ```python
    loader = TextLoader("./transcripts.txt")
    docs = loader.load()
    ```

#### b. Splitting Transcripts into Manageable Chunks
- Langchain’s `RecursiveCharacterTextSplitter` is used to split the text into chunks that are manageable for embedding.
    ```python
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=500)
    docs = text_splitter.split_documents(docs)
    ```

#### c. Storing and Embedding Text with Chroma
- The text chunks are embedded and stored using Chroma, which allows for efficient retrieval.
    ```python
    vectorstore = Chroma.from_documents(
        documents=all_splits, 
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=persist_directory
    )
    ```

#### d. Defining the Prompt Template for the LLM
- A custom prompt is defined to give the LLM context for responding to Jiu-Jitsu questions using the retrieved transcripts.
    ```python
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
    ```

#### e. Implementing the RAG Chain
- The `LLMChain` is built to implement retrieval-augmented generation by integrating the LLM with the context provided by the embedded transcripts.
    ```python
    rag_chain = LLMChain(
        llm=llm,
        prompt=prompt
    )
    ```

#### f. Checking for Relevance (Optional)
- An additional relevance-checking prompt ensures that responses are relevant to the topic at hand.
    ```python
    # Prompt that we use for relevance checking
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

    #outline topic
    topic = "Jiu-Jitsu"  
    ```

#### g. Implement conversation history
- Create conversation history
    ```python
    conversation_history = []
    ```
- Update conversation history concurrently
    ```python
    conversation_history.append({'role': 'user', 'content': user_query})
    conversation_history.append({'role': 'assistant', 'content': response['text']})
    ```

#### h. Main Conversation Loop
- Putting everything together, the conversation loop manages the interaction between the user and the AI.
```python
while True:
    user_query = input("Enter your question (or 'quit' to exit): ")
    if user_query.lower() == 'quit':
        break

    # Check relevance
    if not is_question_relevant(user_query, topic):
        print("\nAI Response:")
        print("I'm sorry, but that question doesn't seem to be related to the topic I'm knowledgeable about. Could you please ask a question related to Jiu-Jitsu?")
        continue

    # Retrieve documents
    docs = retriever.get_relevant_documents(user_query)

    # Format conversation history
    chat_history_formatted = ""
    for message in conversation_history:
        role = "User" if message['role'] == 'user' else "Assistant"
        chat_history_formatted += f"{role}: {message['content']}\n"

    # Prepare inputs for the chain
    chain_inputs = {
        "question": user_query,
        "context": format_docs(docs),
        "chat_history": chat_history_formatted
    }

    # Get the AI response
    response = rag_chain(chain_inputs)

    # Print the response
    print("\nAI Response:")
    print(response['text'])    
```

## Flask API

The Flask API serves as the backend for processing the user queries through the RAG pipeline.
It also handles Cross-Origin Resource Sharing (CORS) for communication with the frontend by processing
incoming requests to generate a response from the RAG pipeline.

#### Base URL
- Localhost: **http://127.0.0.1:5000**

#### Endpoints

- `/chat` Endpoint


This endpoint processes user queries via the GET request sent by the frontend and returns a response.








---

This document outlines the core technical components of the Danaher-Droid. For further details on setup and usage, refer to the main [README](../README.md).
