from lc_config import get_vectorstore

store = get_vectorstore()

questions = [
    "How much is the late fee for paying fees after the due date?",
    "What time should hostel students return?",
    "Can I write the exam with 70% attendance?",
    "What CGPA do I need to be eligible for placements?",
    "What is the capital of France?",
]

for q in questions:
    print(f"\nQ: {q}")

    for doc, score in store.similarity_search_with_score(q, k=3):
        print(
            f"  {score:.3f} "
            f"[{doc.metadata['source']}] "
            f"{doc.page_content[:100]!r}"
        )