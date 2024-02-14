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

Prompt:
{prompt}
        """
    )

vdb_query_prompt_template = PromptTemplate.from_template(
        """
Giving these summaries from the research {summaries}
Answer the following question: {question}
        """
    )