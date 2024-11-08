import pytest
from unittest.mock import patch, MagicMock
from langchain.memory import ConversationSummaryMemory
from rag import process_query

#sample data for testing
RELEVANT_QUERY = "How can I improve my Jiu-Jitsu guard?"
NON_RELEVANT_QUERY = "What is the capital of France?"
MOCKED_DOCS = [
    MagicMock(page_content="Guard techniques and strategies."),
    MagicMock(page_content="Advanced Jiu-Jitsu maneuvers.")
]
MOCKED_RESPONSE = "Improving your guard involves practicing these techniques..."

@pytest.fixture
def mock_memory():
    """
    Fixture to create a mock ConversationSummaryMemory instance
    """
    return MagicMock(spec=ConversationSummaryMemory)

@pytest.fixture
def mock_retriever():
    """
    Fixture to create a mock retriever instance
    """
    with patch('rag.retriever') as mock_retriever:
        mock_retriever.get_relevant_documents.return_value = MOCKED_DOCS
        yield mock_retriever
        
@pytest.fixture
def mock_conversation_chain():
    """
    Fixture to mock the ConversationChain and its predict method
    """
    with patch('rag.ConversationChain') as MockChain:
        instance = MockChain.return_value
        instance.predict.return_value = MOCKED_RESPONSE
        yield instance

def test_process_query_relevant_query(mock_memory, mock_retriever, mock_conversation_chain):
    """
    Test the process_query function with a relevant query
    """
    user_query = RELEVANT_QUERY

    response = process_query(user_query, mock_memory)

    assert response == MOCKED_RESPONSE
    mock_retriever.get_relevant_documents.assert_called_once_with(user_query)
    mock_conversation_chain.predict.assert_called_once_with(question=user_query, context="\n".join([doc.page_content for doc in MOCKED_DOCS]))
    mock_memory.save_context.assert_called_once_with({"input": user_query}, {"output": MOCKED_RESPONSE})


def test_process_query_non_relevant(mock_memory, mock_retriever, mock_conversation_chain):
    """
    Test processing a non-relevant user query.
    """
    user_query = NON_RELEVANT_QUERY

    response = process_query(user_query, mock_memory)
    
    # Assertions
    assert response == "I'm sorry, but that question isn't relevant to making you a better grappler. Can you ask a more relevant question?"
    mock_retriever.get_relevant_documents.assert_not_called()
    mock_conversation_chain.predict.assert_not_called()
    mock_memory.save_context.assert_not_called()