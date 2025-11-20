"""
Basic test suite for AI Portfolio Assistant
"""
import pytest
import sys
import pathlib

# Add project root to path
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_app_imports():
    """Test that main app components can be imported without errors"""
    try:
        import frontend.streamlit_chat_canvas
        import backend.chat_core
        import backend.config
        import backend.session_memory
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import core modules: {e}")


def test_config_loading():
    """Test that configuration loads properly"""
    from backend import config
    
    # Test that required config attributes exist
    assert hasattr(config, 'MODEL_NAME')
    assert hasattr(config, 'TEMPERATURE')
    assert hasattr(config, 'GLOBAL_SYSTEM_PROMPT')
    
    # Test default values
    assert config.MODEL_NAME is not None
    assert isinstance(config.TEMPERATURE, (int, float))


def test_chat_core_functions():
    """Test that chat core functions are available"""
    from backend import chat_core
    
    # Test that main functions exist
    assert hasattr(chat_core, 'chat_with_history')
    assert hasattr(chat_core, 'generate_generic_content')
    assert callable(chat_core.chat_with_history)
    assert callable(chat_core.generate_generic_content)


def test_session_memory():
    """Test session memory functionality"""
    from backend import session_memory
    
    # Test basic memory operations
    test_session = "test_session_123"
    
    # Should start empty
    history = session_memory.get_history(test_session)
    assert isinstance(history, list)
    
    # Should be able to append messages
    session_memory.append_message(test_session, "user", "Hello test")
    history = session_memory.get_history(test_session)
    assert len(history) > 0
    assert history[-1]["role"] == "user"
    assert history[-1]["content"] == "Hello test"


if __name__ == "__main__":
    # Run tests with: python -m pytest tests/test_app.py -v
    pytest.main([__file__, "-v"])
