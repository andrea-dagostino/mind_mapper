import streamlit as st

from src.logger import get_console_logger
from src.utils import hash_text, convert_timestamp_to_datetime
from src.schema import FileType
from src import db
from src.whisper import create_transcript
from src import vector_db
from src import mind_map
from src.llm import llm

from tempfile import NamedTemporaryFile

import pandas as pd

from openai import OpenAI
from upstash_vector import Index

logger = get_console_logger("frontend")

# CONSTANTS # TODO
AUDIO_FILE_TYPES = ["mp3", "wav"]
PAGE_TITLE = "Mind Mapper | Create mind maps from your files"
PAGE_ICON = "🧠"
LAYOUT = "wide"
SIDEBAR_STATE = "expanded"
SYSTEM_PROMPT = """You are an AI assistant helping a user navigate a knowledge base.
The user asks you a question and you provide an answer based on the knowledge base. 
Always be as clear as possible, avoid ambiguity and provide the most accurate information possible without adding any additional information that is not present in the knowledge base.
"""

if "OPENAI_API_KEY" not in st.session_state:
    st.session_state["OPENAI_API_KEY"] = ""
if "UPSTASH_VECTOR_DB_REST_URL" not in st.session_state:
    st.session_state["UPSTASH_VECTOR_DB_REST_URL"] = ""
if "UPSTASH_VECTOR_DB_TOKEN" not in st.session_state:
    st.session_state["UPSTASH_VECTOR_DB_TOKEN"] = ""


def setup_page():
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=LAYOUT,
        initial_sidebar_state=SIDEBAR_STATE,
    )


def setup_hero():
    st.markdown(
        """
        # Mind Mapper 🧠
        _A simple tool of knowledge intelligence and visualization_ tool powered by <b>OpenAI</b>, <b>Upstash Vector DB</b> and a bit of magic ✨
        """,
        unsafe_allow_html=True,
    )


def setup_sidebar():
    with st.sidebar:
        st.markdown("### 🔑 API Keys")
        # Example for setting up an API key input for OpenAI
        openai_api_key = st.text_input(label="OpenAI API Key", type="password")
        # Example for setting up an API key input for Upstash Vector DB
        upstash_vector_db_rest_url = st.text_input(
            label="Upstash Vector DB REST url", type="default"
        )
        upstash_vector_db_token = st.text_input(
            label="Upstash Vector DB Token", type="password"
        )

        # Add a button to confirm the API keys setup
        if st.button("Set API Keys"):
            st.session_state["OPENAI_API_KEY"] = openai_api_key
            st.session_state["UPSTASH_VECTOR_DB_REST_URL"] = upstash_vector_db_rest_url
            st.session_state["UPSTASH_VECTOR_DB_TOKEN"] = upstash_vector_db_token
            st.success("API keys set successfully")


openai_client = OpenAI(api_key=st.session_state["OPENAI_API_KEY"])
vector_db_index = Index(
    url=st.session_state["UPSTASH_VECTOR_DB_REST_URL"],
    token=st.session_state["UPSTASH_VECTOR_DB_TOKEN"],
)


def ingest(hash_id: str):  # Pass the uploaded file as an argument
    # TODO
    with st.spinner("Ingesting file..."):
        # Assuming 'row' is defined elsewhere and accessible here
        q = db.read_one(hash_id)
        if not q.embedded:
            chunks = vector_db.create_chunks(q.text)
            vector_db.add_chunks_to_vector_db(
                vector_db_index, chunks, metadata={"source_hash_id": q.hash_id}
            )
            db.update_one(q.hash_id, {"embedded": True})
            st.success(f"Item {hash_id} ingested")
        else:
            st.warning(f"Item {hash_id} already ingested")


def text_input_area():
    st.markdown("### 🔡 Inputs")
    st.markdown(
        "_Specify the knowledge source to process. Inputs will be stored in a local database and ingested using Upstash Vector DB for RAG purposes_"
    )
    st.markdown("#### 📝 Copy-Paste Content")
    text = st.text_area(
        "Paste in the knowledge you want to process", height=50, key="text_area", disabled=True
    )
    title = st.text_input("Provide title", key="title_text_area", disabled=True)
    # save to db
    if st.button("Save to database", key="text_area_save", disabled=True):
        if text and title:
            hash_id = hash_text(text)
            db.add_one(
                {
                    "filename": "*manual_input*",
                    "title": title,
                    "file_type": FileType.TEXT,
                    "hash_id": hash_id,
                    "text": text,
                }
            )
            ingest(hash_id)
            st.success("Text saved to database")
        else:
            st.warning("Please enter text and title to proceed.")


def upload_text_file():
    st.markdown("#### 📄 Upload a Text File")
    uploaded_text_file = st.file_uploader(
        "Upload a text file",
        type=["txt"],  # Use the constant for file types
        accept_multiple_files=True,
        disabled=True
    )
    # save to db
    if st.button("Save to database", key="upload_text_save", disabled=True):
        progress_text = "Saving text files to database..."
        progress_bar = st.progress(0, text=progress_text)
        if uploaded_text_file is not None:
            if len(uploaded_text_file) == 1:
                with NamedTemporaryFile(suffix=".txt") as temp_text_file:
                    temp_text_file.write(uploaded_text_file.getvalue())
                    temp_text_file.seek(0)
                    progress_bar.progress(int((1 / len(uploaded_text_file)) * 100))
                    hash_id = hash_text(temp_text_file.name)
                    db.add_one(
                        {
                            "filename": uploaded_text_file.name,
                            "title": uploaded_text_file.name,
                            "file_type": FileType.TEXT,
                            "hash_id": hash_id,
                            "text": temp_text_file.read().decode("utf-8"),
                        }
                    )
                    ingest(hash_id)
                    st.success("Text file saved to database")
            else:
                for file in uploaded_text_file:
                    with NamedTemporaryFile(suffix=".txt") as temp_text_file:
                        temp_text_file.write(file.getvalue())
                        temp_text_file.seek(0)

                        progress_bar.progress(
                            int(
                                (uploaded_text_file.index(file) + 1)
                                / len(uploaded_text_file)
                                * 100
                            )
                        )
                        hash_id = hash_text(temp_text_file.name)
                        db.add_one(
                            {
                                "filename": file.name,
                                "title": file.name,
                                "file_type": FileType.TEXT,
                                "hash_id": hash_id,
                                "text": temp_text_file.read().decode("utf-8"),
                            }
                        )
                        ingest(hash_id)
                        st.success("Text file saved to database")
        else:
            st.warning("Please upload a text file to proceed.")


def upload_audio_file():
    st.markdown("#### 🔊 Upload an Audio File")
    uploaded_audio_file = st.file_uploader(
        "Upload an audio file",
        type=AUDIO_FILE_TYPES,  # Use the constant for file types
        disabled=True
    )
    if st.button("Transcribe & Save to database", key="transcribe", disabled=True):
        if uploaded_audio_file is not None:
            extension = "." + uploaded_audio_file.name.split(".")[-1]
            with NamedTemporaryFile(suffix=extension) as temp_audio_file:
                temp_audio_file.write(uploaded_audio_file.getvalue())
                temp_audio_file.seek(0)
                # TODO: check if item exists before processing with Whisper
                with st.spinner("Transcribing audio track..."):
                    transcript = create_transcript(openai_client, temp_audio_file.name)
                    # Check if the transcript already exists in the database
                    existing_item = db.read_one(hash_text(transcript))
                    if existing_item is None:
                        hash_id = hash_text(transcript)
                        db.add_one(
                            {
                                "filename": uploaded_audio_file.name,
                                "title": uploaded_audio_file.name,
                                "file_type": FileType.AUDIO,
                                "hash_id": hash_id,
                                "text": transcript,
                            }
                        )
                        ingest(hash_id)
                        st.success("Transcription complete - item saved in database")
                        # TODO: remove success message after 5 seconds
                    else:
                        st.warning("Transcription already exists in the database.")
        else:
            st.warning("Please upload an audio file to proceed.")


def visualize_db():
    st.markdown("### 📊 Database")
    all_files = db.read_all()
    db_data = []
    if len(all_files) > 0:
        for file in all_files:
            struct = file.model_dump()
            db_data.append(
                {
                    "id": struct["hash_id"],
                    "title": struct["title"],
                    "filename": struct["filename"],
                    "file_type": struct["file_type"].value,
                    "created_at": convert_timestamp_to_datetime(struct["created_at"]),
                    "text": struct["text"][0:50] + "...",
                }
            )
        df = pd.DataFrame(db_data).rename(
            columns={
                "id": "ID",
                "title": "Title",
                "file_type": "Type",
                "text": "Text",
                "created_at": "Date",
            }
        )
        st.dataframe(df, use_container_width=True)
        # check if items are in db

        items_selected = st.multiselect(
            "Perform actions on:",
            # [str(i) + " - " + str(j) for i, j in zip(df["title"], df["filename"])],
            df["Title"].to_list(),
            max_selections=10,
        )
        # delete selections from db
        if st.button("Delete selected items", key="delete"):
            for item in items_selected:
                item_id = df[df["Title"] == item]["ID"].values[0]
                db.delete_one(item_id)
                ids_to_delete = vector_db.fetch_by_source_hash_id(
                    vector_db_index, item_id
                )
                st.success(f"Item {item_id} deleted from database")
                try:
                    vector_db_index.delete(ids_to_delete)
                    st.success(f"Item {item_id} deleted from vector database")
                except Exception as e:
                    st.error(f"Vector database deletion failed - {e}")

    else:
        st.info("No items in database")


def create_mind_map():
    st.markdown("### 🧠 Interrogate Knowledge Base")
    # get all document titles from db
    all_files = db.read_all()
    db_data = []
    data = None
    if len(all_files) > 0:
        for file in all_files:
            struct = file.model_dump()
            db_data.append(
                {
                    "hash_id": struct["hash_id"],
                    "title": struct["title"],
                    "created_at": convert_timestamp_to_datetime(struct["created_at"]),
                }
            )
        df = pd.DataFrame(db_data).rename(
            columns={
                "hash_id": "hash_id",
                "title": "title",
                "created_at": "Date",
            }
        )

        prompt = st.chat_input("Ask something about your knowledge base")
        comment = "No data found."
        llm_data = None
        if prompt:
            with st.chat_message("assistant"):
                with st.status("Processing request...", expanded=True):
                    st.write("- Querying vector database...")
                    data = vector_db.query_vector_db(
                        index=vector_db_index,
                        openai_client=openai_client,
                        question=prompt,
                        system_prompt=SYSTEM_PROMPT,
                        top_n=5,
                    )
                    if data:
                        st.write("- Extracting mind map...")
                        llm_data = llm.extract_mind_map_data(openai_client, data)
                        llm_data = eval(llm_data)
                        st.write("- Evaluating results...")
                        comment = llm.extract_information_from_mind_map_data(
                            openai_client, llm_data
                        )
            with st.chat_message("assistant"):
                st.write(comment)
                st.plotly_chart(
                    mind_map.create_plotly_mind_map(llm_data),
                    use_container_width=True,
                )
    else:
        st.info("No items in database")


def start_frontend():
    setup_page()
    setup_hero()
    setup_sidebar()
    with st.container(border=True):
        create_mind_map()
    with st.expander("**🔡 Inputs**", expanded=True):
        text_input_area()
        col1, col2 = st.columns(2)
        with col1:
            upload_text_file()
        with col2:
            upload_audio_file()
    with st.expander("**📊 Database**", expanded=False):
        visualize_db()


if __name__ == "__main__":
    start_frontend()
