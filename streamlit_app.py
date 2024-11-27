import streamlit as st
from openperplex import OpenperplexSync

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

class VoiceChatbot:
    def __init__(self, api_key):
        # Initialize OpenPerplex client
        self.client = OpenperplexSync(api_key)
        
        # Initialize chat history in session state
        if 'messages' not in st.session_state:
            st.session_state.messages = []
    
    def transcribe_audio(self):
        """Transcribe audio from microphone input"""
        if not SPEECH_RECOGNITION_AVAILABLE:
            st.warning("Speech recognition is not available. Please use text input.")
            return None
        
        try:
            recognizer = sr.Recognizer()
            
            with sr.Microphone() as source:
                st.info("Listening... Speak now.")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source)
            
            text = recognizer.recognize_google(audio)
            return text
        except Exception as e:
            st.error(f"Speech recognition error: {e}")
            return None
    
    def generate_response(self, query):
        """Generate response using OpenPerplex search"""
        try:
            # Using custom_search for more flexible interaction
            response = self.client.custom_search(
                system_prompt="You are a helpful AI assistant. Provide clear and concise answers.",
                user_prompt=query,
                location="us",
                pro_mode=False,
                search_type="general",
                return_sources=True,  # Enable sources for credibility
                temperature=0.7,  # Add some creativity
                recency_filter="recent"  # Focus on recent information
            )
            return response
        except Exception as e:
            st.error(f"Error generating response: {e}")
            return f"I'm sorry, I encountered an error: {e}"
    
    def run(self):
        # Streamlit UI
        st.title("🤖 OpenPerplex Chatbot")
        
        # Sidebar for Voice Input
        with st.sidebar:
            st.header("Interaction Options")
            
            # Conditionally show voice input based on availability
            if SPEECH_RECOGNITION_AVAILABLE:
                # Voice Input Button
                if st.button("🎤 Start Voice Input"):
                    voice_input = self.transcribe_audio()
                    
                    if voice_input:
                        # Display transcribed text
                        st.write(f"You said: {voice_input}")
                        
                        # Generate response
                        response = self.generate_response(voice_input)
                        
                        # Store conversation
                        st.session_state.messages.append({
                            "role": "user", 
                            "content": voice_input
                        })
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response
                        })
            else:
                st.warning("Speech recognition is not available.")
        
        # Display Chat History
        st.header("Chat History")
        for msg in st.session_state.messages:
            with st.chat_message(msg['role']):
                st.write(msg['content'])
        
        # Text Input Fallback
        user_input = st.chat_input("Type your message here...")
        if user_input:
            # Generate response for text input
            response = self.generate_response(user_input)
            
            # Store conversation
            st.session_state.messages.append({
                "role": "user", 
                "content": user_input
            })
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response
            })
            
            # Rerun to update display
            st.experimental_rerun()

def main():
    st.set_page_config(page_title="OpenPerplex Chatbot")
    
    # API Key input
    api_key = st.text_input("Enter your OpenPerplex API Key", type="password")
    
    if api_key:
        try:
            chatbot = VoiceChatbot(api_key)
            chatbot.run()
        except Exception as e:
            st.error(f"Failed to initialize chatbot: {e}")

if __name__ == "__main__":
    main()
