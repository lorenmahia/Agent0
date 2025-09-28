from langchain.tools import Tool, tool

@tool
def pdf_to_txt(filename:str):
    """This tool provides the text file to the agent to summarize"""
    import fitz
    pdf_to_summarize = fitz.open(filename)
    text = ""
    for page in pdf_to_summarize:
        text += page.get_text()
    return text

summary_tool = Tool(
    name = "summary_tool",
    func = pdf_to_txt,
    description = "This tool provides the text file to the agent to summarize",
)