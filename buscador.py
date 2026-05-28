import pandas as pd
from mcp.server.fastmcp import FastMCP
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

mcp = FastMCP("buscador_livros")

base_livros = Path(__file__).parent / "GoodReads_100k_books.csv"

@mcp.tool()
def buscador(genero: str, numero_pg: int) -> dict:
    """
    descricao:
    Função para buscar livros dentro de uma base de dados
    a partir de um genero e numero de páginas.
    Importante que genero seja passado em inglês.

    Args:
        genero (string): nome do genero (inglês)
        numero_pg (int): numero de paginas do livro

    Returns:
        dict: Resultado estruturado com lista de livros
        {
            "books": [{"title":..., "author":..., "pages":..., "genre":..., "rating":..., "desc":...}],
            "count": int
        }
    """

    base = pd.read_csv(base_livros, encoding= 'utf-8')
    base['pages'] = base['pages'].astype(int)
    base['rating'] = base['rating'].astype(float)
    base = base[(base['genre'].str.contains(genero, case=False)) & ((numero_pg-20)<base['pages']) & (base['pages']<(numero_pg+20))]

    if len(base)>100:
        base_4 = base[base['rating']>4]
        if len(base_4) >0:
            base = base_4

    base = base.sort_values(by="rating", ascending=False)
    books_df = base[['title', 'author', 'pages', 'genre', 'rating', 'desc']].head(10)

    # Convert DataFrame to structured dictionaries
    books = []
    for _, row in books_df.iterrows():
        books.append({
            "title": str(row['title']),
            "author": str(row['author']),
            "pages": int(row['pages']),
            "genre": str(row['genre']),
            "rating": float(row['rating']),
            "desc": str(row['desc'])
        })

    return {
        "books": books,
        "count": len(books)
    }

@mcp.tool()
def buscar_por_nome(titulo: str) -> dict:
    """
    descricao:
    Função para buscar as informações de um
    livro dentro de uma base de dados
    a partir do nome dele.
    Importante que o nome do livro seja passado em inglês.

    Args:
        title (string): nome do livro (inglês)

    Returns:
        dict: Informações do livro encontrado ou erro
        {
            "book": {"title":..., "author":..., "pages":..., "genre":..., "rating":..., "desc":...},
            "found": bool
        }
        ou
        {
            "found": false,
            "message": "Livro não encontrado"
        }
    """
    base = pd.read_csv(base_livros, encoding='utf-8')
    base['rating'] = base['rating'].astype(float)
    base['pages'] = base['pages'].astype(int)

    livro_df = base[base['title'].str.contains(titulo, case=False, na=False)]

    if len(livro_df) == 0:
        return {
            "found": False,
            "message": f"Livro '{titulo}' não encontrado na base de dados"
        }

    # Pega o livro com melhor avaliação
    livro_melhor = livro_df.sort_values(by="rating", ascending=False).head(1)

    row = livro_melhor.iloc[0]
    return {
        "book": {
            "title": str(row['title']),
            "author": str(row['author']),
            "pages": int(row['pages']),
            "genre": str(row['genre']) if pd.notna(row['genre']) else "N/A",
            "rating": float(row['rating']),
            "desc": str(row['desc']) if pd.notna(row['desc']) else "No description available"
        },
        "found": True
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")