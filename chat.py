from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

TAVILY_KEY = os.getenv("TAVILY_API_KEY")
GOOGLE_API_KEY= os.getenv("GOOGLE_API_KEY")


buscador_path = Path(__file__).parent / "buscador.py"

client = MultiServerMCPClient(
    {
        "buscador_livros": {
            "command": "python",
            "args": [str(Path(__file__).parent / "buscador.py")],
            "transport": "stdio",
        },
        # "tavily": {
        #     "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_KEY}",
        #     "transport": "streamable_http",
        # }
    }
)


async def chat():
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GOOGLE_API_KEY)
    tools = await client.get_tools()
    agent = create_react_agent(
        model=llm,
        tools = tools,
        checkpointer= InMemorySaver(),
        prompt="Você é um agente que ajuda usuários a encontrar livros com base em suas solicitações. " \
        "Você pode usar tools para buscar informações sobre livros. Lembre-se de traduzir o gênero do livro para o inglês antes de fazer a busca na tool." \
        "Conside livros curtos os livros que tem no máximo 130 páginas." \
        "Considere livros longos os livros que tem mais de 400 páginas." \
        "Na hora de responder escolha os 5 melhores livros baseados nas avaliações dos usuários." \
        "Para encontrar informações de um livro específico, passe o nome em inglês, do jeito que o usuário escreveu e com codificação UTF-8 para a tool de buscar por nome." \
        # "Se o usuário pesquisar livros com algum termo específico, use a ferramenta de busca do Tavily e passe o search term em inglês." 
    )

    print("Digite sua solicitação (ex: 'quero um romance curto'). Use /q para sair.\n")

    while True:
            # try:
        user_input = input("> ")

        if user_input.lower() == "/q":
            print("Saindo...")
            break

        config = {
            "configurable": {
                "thread_id": "1"
            }
            }
        try:
            response = await agent.ainvoke(
                {"messages": [{"role": "user", "content": user_input}]}, config=config,
            )
            print("\nResposta do agente:\n")
            print(response["messages"][-1].content[0]['text'])
            print("\n")
        except Exception as e: 
            print(f"Ocorreu um erro {e}")
            break

if __name__ == "__main__":
    asyncio.run(chat())