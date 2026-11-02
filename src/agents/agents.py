from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.tools.tools import web_search, scrape_url
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_API_BASE_URL")
llm = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0,
    openai_api_key=api_key,
    openai_api_base=base_url
)


def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search],
        
    )



def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url],
        
    )

#writer chain
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.
Topic: {topic}
Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources(listallURLsfoundintheresearch)

Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()

#critic_chain

critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research crittic. Be honest and specific."),
    ("human", """Review the research report below and evaluate itstrictly.
Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...
Areas to Improve:
- ...
- ...
One line verdict:
- ..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()