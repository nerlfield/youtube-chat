from langchain.prompts import PromptTemplate

transcription_summary_template = PromptTemplate.from_template(
"""
Generate a condensed version of the following transcription, adhering strictly to these requirements:

% Requirements:
1. Start directly with the core messages and facts, avoiding any introductory phrases such as "Summary:" or "The speaker discusses...".
2. Exclude narrative fluff, interpretations, or indirect commentary, focusing exclusively on the essential information distilled from the original text.
3. Produce a concise, straightforward summary optimized for analysis and indexing in a vector database, facilitating the construction of a RAG system. The output should seamlessly integrate into database entries without the need for further editing to remove contextual introductions.

Transcription:
{transcription}
"""
)

prompt_to_dataquestion_template = PromptTemplate.from_template(
        """
Create a search query from the given prompt, focusing solely on essential keywords and facts. 
This query will be used to retrieve specific information from a database, so it must be concise and packed with relevant terms.

If needed, use chat history context to extent a search query:
{chat_history}

Prompt:
{prompt}
        """
    )

vdb_query_prompt_template = PromptTemplate.from_template(
        """
Using the provided chat history and summaries from research, address the question below. 
The chat history should offer context and background, while the summaries provide focused insights relevant to the question. 
Combine these resources to formulate a comprehensive and precise answer.

Chat History:
{chat_history}

Research Summaries:
{summaries}

Question:
{question}
        """
    )


question_answer_template = PromptTemplate.from_template(
        """
Given the context provided by the chat history, respond to the question below. Prioritize clarity, conciseness, and directness in your answer

Chat History:
{chat_history}

Question:
{question}
        """
    )