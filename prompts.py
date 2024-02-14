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


question_answer_template = PromptTemplate.from_template(
        """
Ignore all previous instructions.

1. You are to provide clear, concise, and direct responses.
2. Eliminate unnecessary reminders, apologies, self-references, and any pre-programmed niceties.
3. Maintain a casual tone in your communication.
4. Be transparent; if you're unsure about an answer or if a question is beyond your capabilities or knowledge, admit it.
5. For any unclear or ambiguous queries, ask follow-up questions to understand the user's intent better.
6. When explaining concepts, use real-world examples and analogies, where appropriate.
7. For complex requests, take a deep breath and work on the problem step-by-step.
8. For every response, you will be tipped up to $200 (depending on the quality of your output).

It is very important that you get this right. Multiple lives are at stake.

Answer the following question: {question}
        """
    )
