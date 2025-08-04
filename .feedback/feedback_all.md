## Feedback & Requirements
- Make sure to review the other feedback files

### Main

#### Main
- Automatically capture and save new Lyra journal entries from other vers.
    - This will need to have a json or other parser baked in
    - Would like this to be rerankable on CPU
- Generate embeddings for each journal entry using the selected model.
    - The chromadb server does this for us.
- Store embeddings and metadata in the vector database for semantic search.
    - Use Langchains docs to find out how to install chromadb vector store
    - Make sure that the on vector store follows the docs from Langchain
- Add tests to verify saving, embedding, and search functionality.

#### Integration
- No comments at this time

#### Stretch Goal
- Implement a selection mechanism for publishing journal entries externally (manual or automated).

---

**General Guidance:**
- All requirements must be implemented in a way that is visually consistent, accessible, and testable.
- If any requirement is unclear, please request clarification before implementation.
- Variable and file references are provided for clarity and to assist future contributors.
