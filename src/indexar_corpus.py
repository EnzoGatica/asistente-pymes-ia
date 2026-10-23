"""Indexa los documentos de corpus/ en un vector store Chroma persistido en vectorstore/.

Splitter recursivo con chunk_size=400: cada documento del negocio tiene 2 o 3 párrafos de un solo tema,
y el separador por párrafo ("\\n\\n") los corta por tema sin partir oraciones. Overlap de 60 para que
una oración que quede en el borde (ej. "48 horas de anticipación") aparezca en ambos chunks.
"""
import shutil
from pathlib import Path

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter

RAIZ = Path(__file__).resolve().parent.parent
CARPETA_CORPUS = RAIZ / "corpus"
PERSIST_DIRECTORY = str(RAIZ / "vectorstore")
MODELO_EMBEDDINGS = "text-embedding-3-small"
CHUNK_SIZE = 400
CHUNK_OVERLAP = 60


def crear_embeddings():
    from langchain_openai import OpenAIEmbeddings

    return OpenAIEmbeddings(model=MODELO_EMBEDDINGS)


def cargar_corpus(carpeta=CARPETA_CORPUS):
    archivos = sorted(carpeta.glob("*.md"))
    return [archivo.read_text(encoding="utf-8") for archivo in archivos], [{"fuente": a.name} for a in archivos]


def partir_en_chunks(textos, metadatas):
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = splitter.create_documents(textos, metadatas=metadatas)
    contador = {}
    ids = []
    for chunk in chunks:
        fuente = chunk.metadata["fuente"]
        contador[fuente] = contador.get(fuente, 0) + 1
        ids.append(f"{fuente}#{contador[fuente]}")
    return chunks, ids


def indexar(persist_directory=PERSIST_DIRECTORY):
    from langchain_chroma import Chroma

    shutil.rmtree(persist_directory, ignore_errors=True)  # from_documents agrega, no reemplaza
    textos, metadatas = cargar_corpus()
    chunks, ids = partir_en_chunks(textos, metadatas)
    Chroma.from_documents(documents=chunks, embedding=crear_embeddings(), ids=ids, persist_directory=persist_directory)
    return len(textos), ids


if __name__ == "__main__":
    load_dotenv()
    from langchain_chroma import Chroma

    n_documentos, ids = indexar()
    print(f"Indexados {len(ids)} chunks de {n_documentos} documentos en vectorstore/")
    print("ids:", ids)
    recargado = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=crear_embeddings())
    print("chunks al reconectar sin reindexar:", recargado._collection.count())
