# Virtual Assistant for Bulding Management
Imagine yourself receiving the keys of your newly bought apartment for the first time. All you want is enjoy your home and start this new beautiful cycle of your life and live happy forever.  

Some time after the realisation, a defect on your gas system suddenly comes up. Do you have an ensurance for that? Guarantees? Did you perform all maintenance tasks required so you can have the right to claim for a free intervention from the constructor?  
You open the usage manual and all you can find is a bunch of technical terms about materials and structures you had never seen. At this moment, the dream of the "home sweet home" is about to become a nightmare.

Not anymore. Not with Bob, your virtual assistant 24h available on your whatsapp to answer all your questions about how to take care of your home in a language you can understand. The assistant receives all the information existent in the usage & operations manual and can clarify questions about service providers, maintenance, and guarantees.

## Technical Descrption
The vistual assistant leverages all the power from Generative AI to process documents, interpret it, adn bring relevant answers for each question. This solution is based on a RAG architecture where the system retrieves information from documents and rank it accordingly to the relevance to the query before answering it.  
<img width="577" height="304" alt="image" src="https://github.com/user-attachments/assets/579cd855-e144-429f-b0cb-ba3d01c5787f" />  

## How it works as a product
This solution was developed for a company called Facilitat, that has a software that manages digitally all the stuff related to guarantees and maintenance. They have a portfolio with many buildings. To initiate the implementation of this new solution, they chose a building for a test and made the assistante available for users from 300 different apartments.

The solution's success is being measured by reduction and the number of service tickets opening and increasement on NPS. 

## Resources
The main technologies used here are the GPT model to generate queries for the retrieval and the final answer and Document Intelligence from Azure to process pdf documents and extract text from these files.

## Utilization
The bot was made available through a phone number from Brazil on whatsapp and work like the following:

## Reproducibility
Feel free to clone the repo and use the code available here, but the application itself is not available to be exactly reproduced because of restrictions like:
* All the users accesses are stored in a REDIS database. This is a private resource from the product;
* All the chat history used as memory for the RAG system is also stored in the same REDIS database;
* The API keys and meta accounts to connect with whatsapp are all private resources.
