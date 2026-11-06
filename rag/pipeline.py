
from flask import current_app
from groq import Groq, APIStatusError, APIConnectionError
from rag.retriever import retrieve


def answer_question(question, user):

    hits = retrieve(question, user)

    if not hits:
        return {
            "answer": "I could not find relevant information in the institute documents you can access.",
            "sources": []
        }

    sources = []
    context = []

    for i, hit in enumerate(hits, 1):
        chunk = hit["chunk"]

        sources.append({
            "marker": f"S{i}",
            "document": chunk.document.filename,
            "page": chunk.page_number
        })

        context.append(
            f"[S{i}] {chunk.document.filename}, "
            f"page {chunk.page_number}:\n{chunk.content}"
        )

    api_key = current_app.config["GROQ_API_KEY"]

    if not api_key:
        return {
            "answer": "Groq API key is missing. Configure GROQ_API_KEY in .env.",
            "sources": sources
        }

    try:
        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model=current_app.config["GROQ_MODEL"],
            temperature=0.1,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an institute knowledge assistant. "
                        "Answer only using the provided institute documents. "
                        "Cite facts using [S1], [S2]. "
                        "If information is unavailable, clearly say so. "
                        "Never invent institute policies."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Question: {question}\n\n"
                        f"Institute documents:\n"
                        + "\n\n".join(context)
                    )
                }
            ]
        )

        answer = response.choices[0].message.content

        return {
            "answer": answer or "No answer generated.",
            "sources": sources
        }

    except APIStatusError as error:
        current_app.logger.error(
            "Groq API error %s: %s",
            error.status_code,
            error.message
        )

        return {
            "answer": (
                "The AI service rejected the request. "
                "Please check your Groq model ID and API permissions."
            ),
            "sources": sources
        }

    except APIConnectionError:
        current_app.logger.exception("Groq connection failed")

        return {
            "answer": "Could not connect to the AI service. Please try again.",
            "sources": sources
        }
