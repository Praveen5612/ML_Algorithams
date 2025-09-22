import streamlit as st
import os
import json
import pandas as pd
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import base64

st.set_page_config(page_title="ML Learning Hub", layout="wide")
st.title("📚 ML Learning Hub")

# ---------------- BASE PATH ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------- METADATA ----------------
metadata_file = os.path.join(BASE_DIR, "metadata.json")
if os.path.exists(metadata_file):
    with open(metadata_file, "r", encoding="utf-8") as f:
        try:
            metadata = json.load(f)
        except json.JSONDecodeError:
            metadata = {}
else:
    metadata = {}

# ---------------- RESOURCE SELECTION ----------------
resource_type = st.sidebar.selectbox(
    "Select Resource Type",
    ["Algorithms", "Datasets", "AIML Notes"]
)

# ---------------- PATHS ----------------
resource_paths = {
    "Algorithms": os.path.join(BASE_DIR, "Algorithms"),
    "Datasets": os.path.join(BASE_DIR, "Datasets"),
    "AIML Notes": os.path.join(BASE_DIR, "AIML Notes")
}

resource_path = resource_paths[resource_type]

# Check if folder exists
if not os.path.exists(resource_path):
    st.error(f"❌ Folder not found: {resource_path}")
    files = []
else:
    files = os.listdir(resource_path)

# ---------------- SEARCH BOX ----------------
search_term = st.sidebar.text_input(f"Search {resource_type}")
if search_term:
    files = [f for f in files if search_term.lower() in f.lower()]

# ---------------- SELECT FILE ----------------
selected_file = st.selectbox(f"Select {resource_type}", files)

if selected_file:
    st.header(f"{resource_type}: {selected_file}")
    file_path = os.path.join(resource_path, selected_file)

    # ---------------- ALGORITHMS ----------------
    if resource_type == "Algorithms":
        desc = metadata.get(selected_file, "No description available.")
        st.info(desc)

        if selected_file.endswith(".py"):
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
            st.code(code, language="python")

        elif selected_file.endswith(".ipynb"):
            with open(file_path, "r", encoding="utf-8") as f:
                nb = nbformat.read(f, as_version=4)

            ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
            try:
                ep.preprocess(nb, {'metadata': {'path': resource_path}})
            except Exception as e:
                st.warning(f"⚠️ Notebook execution error: {e}")

            for i, cell in enumerate(nb.cells):
                if cell.cell_type == "markdown":
                    st.markdown(cell.source)
                elif cell.cell_type == "code":
                    with st.expander(f"▶ Code Cell {i+1}"):
                        st.code(cell.source, language="python")
                        if 'outputs' in cell:
                            for output in cell.outputs:
                                if output.output_type == 'stream':
                                    st.text(output.text)
                                elif output.output_type in ('execute_result', 'display_data'):
                                    if 'text/plain' in output.data:
                                        st.text(output.data['text/plain'])

    # ---------------- DATASETS ----------------
    elif resource_type == "Datasets":
        try:
            df = pd.read_csv(file_path)
            st.write("Preview of dataset:")
            st.dataframe(df.head(10))
        except Exception as e:
            st.warning(f"⚠️ Could not read dataset: {e}")

    # ---------------- AIML NOTES ----------------
    elif resource_type == "AIML Notes":
        if selected_file.endswith(".pdf"):
            with open(file_path, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="800" type="application/pdf"></iframe>'
            st.components.v1.html(pdf_display, height=800)
        elif selected_file.endswith(".txt") or selected_file.endswith(".md"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            st.markdown(content)
        else:
            st.info("File type cannot be displayed in browser. Use download.")

    # ---------------- DOWNLOAD BUTTON ----------------
    with open(file_path, "rb") as f:
        st.download_button(
            label="📥 Download File",
            data=f,
            file_name=selected_file,
            mime="application/octet-stream"
        )

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("Made with ❤️ for ML learners | Display code, outputs, datasets & notes interactively")
