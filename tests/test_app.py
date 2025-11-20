def test_import_ui():
    # Basic smoke test to ensure the Streamlit UI module imports without errors
    import importlib
    import sys
    import pathlib

    root = pathlib.Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    mod = importlib.import_module("frontend.streamlit_chat_canvas")
    assert mod is not None
