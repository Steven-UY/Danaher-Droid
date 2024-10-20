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
    ```

---

## Future Enhancements
- Improve transcript processing by implementing more advanced splitting techniques.
- Fine-tune the LLM for better emulation of John Danaher's speech style.
- Add a user-friendly graphical interface for easier interaction.

---

This document outlines the core technical components of the Danaher-Droid. For further details on setup and usage, refer to the main [README](../README.md).
