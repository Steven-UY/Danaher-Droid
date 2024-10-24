# Danaher-Droid

## Overview

I **suck** at Jiu-Jitsu and hate having to sift through all the instructionals online—my attention span is too bad. Hence, I wanted to design a tool that could help me not be so bad. With Danaher-Droid, I hope that I can effectively perform retrieval augmented generation (RAG) on transcripts contained within the BJJ Fanatics YouTube channel. 

So, it's not really Danaher-Droid—more like BJJ Fanatics Droid—but whatever, Danaher sounds better.

### Goals:
- Have the LLM respond with accurate answers when asked about any BJJ position.
- Have responses in John Danaher’s voice.
- Create a tool that looks somewhat presentable.

---

## Tech Stack

### Backend

### 1. YouTube Data API
- Retrieve video IDs from the BJJ Fanatics channel using the YouTube Data API.

### 2. YouTube Transcript API
- Scrape transcripts from YouTube videos.

### 3. Langchain and Chroma
- Split and embed transcripts using Langchain.
- Store transcripts in a vector database using Chroma.
- Implement the RAG chain to generate LLM responses.

For more details on each step, see the [Technical Documentation](docs/tech_docs.md).

### Frontend

### Next.js
- **Next.js**: The frontend of the project is built using Next.js, a React framework that provides server-side rendering and static site generation for enhanced performance and SEO.
  - **React**: For building reusable UI components.
  - **API Routes**: Used for handling requests from the frontend to the backend, such as querying the transcript database and interacting with the RAG chain.
  - **Styling**: (Specify if you're using any CSS framework or styling solution like Tailwind CSS, styled-components, or plain CSS).

---

## Image

![John Danaher teaching Brazilian Jiu-Jitsu](https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fbjjfanatics.com%2Fcdn%2Fshop%2Farticles%2FJohn-Danaher_1024x1024.jpg%3Fv%3D1547846343&f=1&nofb=1&ipt=862a15c76eaabc76cb5947675f934a0b76f093a22f76af2ad26315467c3f2fa0&ipo=images)
