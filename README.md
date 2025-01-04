# Graph-Based Analytics for Stock Market Dynamics

*Integrating Neo4j, LangChain and Financial Data*

**Project Overview:**
This project explores the integration of graph databases and AI-driven tools to analyze financial market data. Using Neo4j for graph analytics and LangChain for natural language interaction. 

This was the final project for the Class: Knowledge Graph at University of Lausanne.

**Key Features:**
- Graph Database Integration: Utilized Neo4j for advanced graph analytics, enabling visualization and exploration of stock relationships.
- AI Integration with LangChain: This allow natural language querying of financial data.
- Financial Market Analysis: Analyzed the S&P 100 dataset to uncover sectoral dependencies and influential stocks (Financial Sector) using techniques like distance correlation and community detection.
- Scalability and Usability: Designed the system to be scalable, with potential extensions for larger datasets, real-time analytics and a user friendly interface.

**Installation Instructions:**
1. Clone the repository 

```BASH
git clone https://github.com/your-repo/GraphMarketAnalysis.git
cd GraphMarketAnalysis
```

2. Set Up a Virtual Environment

#### Code Block:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Dependencies:
```bash
pip install -r requirements.txt
```

3. Set Up Neo4j:
- Install Neo4j Desktop or run a Neo4j instance.
- Import the project dataset into Neo4j.

4. Configure Environment Variables:

- Create a .env file in the project root.
- Add your OpenAI and Neo4j credentials:

```bash
OPENAI_API_KEY=openai_key
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=your_username
NEO4J_PASSWORD=your_password
```

**Future Work:**
Expand the dataset to include global indices for a broader market analysis.