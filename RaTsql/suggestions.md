# Current Issues :

- Overlapping instructions from RAG: 
  - currently the DB schema is merged (union) to give the final schema, cause to overlook the overlapping part.
  - But it's not implemented in instructions so there might be cases that same instructions can pass multiple times.

# Future suggestions : 

1. Asking feedback based on retrieval score. 
   - Asking the final user for feedback to populate vector store should be based on similarity score of initial retrieval.
       - if the similarity < 0.4 : This type of question was not seen before.
         - hence it's ideal to have it in vector store for future case.
       - if similarity > 0.7 : This type of question is seen before.
         - hence it's safe to ignore it, so we don't croud the vector store cause uneven clusters. 