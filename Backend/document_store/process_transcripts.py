from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter 

loader = TextLoader("./data.txt")
loader.load()

with open("./data.txt") as f:
    data = f.read()
text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size=100,
    chunk_overlap=20,
    length_function=len,
    is_separator_regex=False,
)

texts = text_splitter.create_documents([data])
print(texts[0])
print(texts[1])