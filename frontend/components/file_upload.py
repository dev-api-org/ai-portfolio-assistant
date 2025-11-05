import streamlit as st


def render_upload():
    """Render the file upload component."""
    uploaded = st.file_uploader(
        "Upload file (drag & drop supported)",
        type=["pdf", "png", "jpg", "jpeg", "txt", "md"],
        help="Accepted: pdf, png, jpg, jpeg, txt, md"
    )

    if uploaded is None:
        st.info("No file uploaded yet. Use the uploader above to add a file.")
        return

    # Acknowledge receipt and show details
    st.success(f"Received: {uploaded.name}")
    st.write("File details:")
    st.json({"name": uploaded.name, "type": uploaded.type, "size": uploaded.size})

    # Preview image files inline
    try:
        if uploaded.type.startswith("image"):
            st.image(uploaded)
    except Exception:
        # some non-image files may not have a .type set; ignore preview errors
        pass

    # Placeholder for upload processing status
    st.info("File uploaded. Next: the file will be sent to the backend for indexing and analysis (when available).")
    st.caption("Tip: you can upload multiple files over time to build richer context for the assistant.")