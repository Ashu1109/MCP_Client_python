import streamlit as st
import requests
import os
import json

# Path to conversations directory
conv_dir = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "api", "conversations"
)

# Initialize chat history in session state if not already present
if "messages" not in st.session_state:
    st.session_state.messages = []
if "loaded_conversation_file" not in st.session_state:
    st.session_state.loaded_conversation_file = None


# Function to render chat messages
def render_chat(messages):
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    with st.chat_message(role):
                        st.markdown(part.get("text", ""))
                elif isinstance(part, str):
                    with st.chat_message(role):
                        st.markdown(part)
        else:
            with st.chat_message(role):
                st.markdown(content)


selected_option = "New Chat"  # Initialize with a default value


def load_conversation_from_file(conv_file_name):
    conv_path = os.path.join(conv_dir, conv_file_name)
    try:
        with open(conv_path, "r") as f:
            conv_data = json.load(f)
        st.session_state.messages = conv_data.get("messages", [])
        st.session_state.loaded_conversation_file = conv_file_name
    except Exception as e:
        st.sidebar.error(f"Failed to load conversation: {e}")
        st.session_state.messages = []
        st.session_state.loaded_conversation_file = None


if os.path.exists(conv_dir):
    conv_files = sorted(
        [
            f
            for f in os.listdir(conv_dir)
            if f.startswith("conversation_") and f.endswith(".json")
        ],
        reverse=True,
    )
    options = ["New Chat"] + conv_files

    current_selection_index = 0  # Default to "New Chat"
    if (
        st.session_state.loaded_conversation_file
        and st.session_state.loaded_conversation_file in options
    ):
        current_selection_index = options.index(
            st.session_state.loaded_conversation_file
        )
    elif (
        not st.session_state.loaded_conversation_file and st.session_state.messages
    ):  # In a new chat with messages
        current_selection_index = 0  # Stay on "New Chat"

    selected_option = st.sidebar.selectbox(
        "Select or Start New Chat", options, index=current_selection_index
    )

    if selected_option == "New Chat":
        if (
            st.session_state.loaded_conversation_file is not None
        ):  # If a file was previously loaded
            st.session_state.messages = []
            st.session_state.loaded_conversation_file = None
            st.experimental_rerun()
    elif (
        selected_option and selected_option != st.session_state.loaded_conversation_file
    ):
        load_conversation_from_file(selected_option)
        st.experimental_rerun()
elif (
    not st.session_state.messages
):  # If conv_dir doesn't exist and no messages in session
    st.sidebar.write("No conversation history found.")
    st.session_state.messages = []
    st.session_state.loaded_conversation_file = None

# Main chat area
st.title("GPT Query Interface")
render_chat(
    st.session_state.messages
)  # Use the existing render_chat with session state

# Chat input at the bottom
if prompt := st.chat_input("Type your message and press Enter..."):
    user_message = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_message)

    # If a historical chat was loaded, interacting means it's now a new/modified chat
    if st.session_state.loaded_conversation_file is not None:
        st.session_state.loaded_conversation_file = None
        # This will cause the selectbox to default to "New Chat" on the next full rerun if not handled by index logic

    # Display the user's message immediately (Streamlit reruns on chat_input, so render_chat above will show it)
    # For an even more immediate feel without waiting for the full rerun logic for the new user message:
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Getting response..."):
        try:
            response = requests.post(
                "http://localhost:8000/query", json={"query": prompt}, timeout=60
            )
            response.raise_for_status()
            data = response.json()

            api_response_messages = data.get("messages", [])
            final_assistant_message_object = None
            for msg_content in reversed(api_response_messages):
                if msg_content.get("role") == "assistant":
                    final_assistant_message_object = msg_content
                    break

            if final_assistant_message_object:
                st.session_state.messages.append(final_assistant_message_object)
                # Display assistant's response (Streamlit will rerun and render_chat above will show it)
                # For immediate display:
                with st.chat_message("assistant"):
                    content = final_assistant_message_object.get("content", "")
                    if isinstance(content, list):
                        for part in content:
                            if isinstance(part, dict) and part.get("type") == "text":
                                st.markdown(part.get("text", ""))
                            elif isinstance(part, str):
                                st.markdown(part)
                    else:
                        st.markdown(content)

            else:
                st.warning("No assistant message found in the latest API response.")
        except Exception as e:
            st.error(f"Error: {e}")

    # After processing, if loaded_conversation_file became None, ensure UI updates if needed
    # st.chat_input already triggers a rerun. If selectbox needs to reflect "New Chat",
    # the index logic for selectbox should handle it on the rerun.
    if (
        st.session_state.loaded_conversation_file is None
        and selected_option != "New Chat"
    ):
        st.experimental_rerun()  # Force rerun to update sidebar if needed
