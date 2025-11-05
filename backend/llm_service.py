"""
Simple terminal chat to test Gemini API connection
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

def test_gemini_connection():
    """Test basic Gemini API connection"""
    
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not found in .env file")
        return
    
    print("✅ API Key loaded successfully")
    print("🔄 Initializing Gemini...")
    
    try:
        # Initialize LangChain Chat model (reads GOOGLE_API_KEY from env)
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.7,
        )
        
        print("✅ Gemini initialized successfully")
        print("\n" + "="*50)
        print("🤖 Gemini Terminal Chat")
        print("="*50)
        print("Type your message and press Enter")
        print("Type 'quit' or 'exit' to stop\n")
        
        # Simple chat loop
        while True:
            # Get user input
            user_input = input("You: ").strip()
            
            # Exit condition
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            # Skip empty input
            if not user_input:
                continue
            
            # Send to Gemini and get response
            print("\n🤖 Gemini: ", end="", flush=True)
            response = llm.invoke(user_input)
            print(response.content)
            print()
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check your API key in .env file")
        print("2. Verify API key is valid at https://aistudio.google.com/app/apikey")
        print("3. Ensure you have internet connection")

if __name__ == "__main__":
    test_gemini_connection()