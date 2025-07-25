from langchain.memory import ConversationBufferMemory

def get_memory():
    """
    Returns a ConversationBufferMemory instance for use in the QA pipeline.
    """
    return ConversationBufferMemory(return_messages=True) 