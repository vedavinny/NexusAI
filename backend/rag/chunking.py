"""
Improved PDF extraction and chunking.

Instead of chunking each page independently, the entire document is combined
and then split using RecursiveCharacterTextSplitter. This produces more
meaningful chunks while still preserving page metadata.
"""

from dataclasses import dataclass
import unicodedata
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from backend.config.settings import settings


@dataclass
class Chunk:
    text: str
    chunk_index: int
    page_number: int | None = None


def process_pdf(file_path: str) -> list[Chunk]:
    """
    Extract text from the whole PDF and split into semantic chunks.

    Returns:
        list[Chunk]
    """

    reader = PdfReader(file_path)

    pages: list[tuple[int, str]] = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text() or ""
        text = unicodedata.normalize("NFKC", text)

        if text.strip():
            pages.append((page_number, text))

    if not pages:
        return []

    # -------------------------------------------------------
    # Build one large document while remembering page offsets
    # -------------------------------------------------------

    full_document = ""

    page_offsets = []

    current_offset = 0

    for page_number, text in pages:

        page_offsets.append((current_offset, page_number))

        full_document += text + "\n\n"

        current_offset = len(full_document)

    # -------------------------------------------------------
    # Better splitter
    # -------------------------------------------------------

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=settings.CHUNK_SIZE,

        chunk_overlap=settings.CHUNK_OVERLAP,

        separators=[
            "\n\n",
            "\n",
            ". ",
            "? ",
            "! ",
            "; ",
            ", ",
            " ",
            "",
        ],

        length_function=len,

        add_start_index=True,
    )

    split_docs = splitter.create_documents([full_document])

    chunks: list[Chunk] = []

    for idx, doc in enumerate(split_docs):

        start = doc.metadata.get("start_index", 0)

        page_number = 1

        for offset, page in page_offsets:

            if offset <= start:
                page_number = page
            else:
                break

        chunks.append(

            Chunk(

                text=doc.page_content.strip(),

                chunk_index=idx,

                page_number=page_number,

            )

        )

    print("=" * 80)
    print("DOCUMENT CHUNKING")
    print("=" * 80)
    print(f"Pages          : {len(pages)}")
    print(f"Chunks Created : {len(chunks)}")
    print(f"Chunk Size     : {settings.CHUNK_SIZE}")
    print(f"Overlap        : {settings.CHUNK_OVERLAP}")
    print("=" * 80)

    return chunks