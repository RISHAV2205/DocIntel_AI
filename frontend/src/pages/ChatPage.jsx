// React hooks
import { useEffect, useState } from "react";

// Axios API instance
import API from "../services/api";

function ChatPage() {

    // =========================================
    // STATE VARIABLES
    // =========================================

    // Store all chats of logged-in user
    const [chats, setChats] = useState([]);

    // Store currently selected chat id
    const [chatId, setChatId] = useState(null);

    // Store all messages of active chat
    const [messages, setMessages] = useState([]);

    // Store current user input
    const [message, setMessage] = useState("");

    // Store selected file
    const [file, setFile] = useState(null);


    // =========================================
    // LOAD ALL CHATS
    // =========================================

    // Calls:
    // GET /chat/
    //
    // Loads all previous chats
    // of current logged-in user
    const loadChats = async () => {

        try {

            const response = await API.get("/chat/");

            console.log(response.data);

            // Save chats in state
            setChats(response.data);

        } catch (error) {

            console.log(error.response?.data);
        }
    };


    // =========================================
    // LOAD ALL MESSAGES OF CHAT
    // =========================================

    // Calls:
    // GET /chat/{chat_id}/messages
    //
    // Loads old conversation messages
    const loadMessages = async (id) => {

        try {

            const response = await API.get(
                `/chat/${id}/messages`
            );

            console.log(response.data);

            // Save all chat messages
            setMessages(response.data);

            // Set active chat id
            setChatId(id);

        } catch (error) {

            console.log(error.response?.data);
        }
    };


    // =========================================
    // CREATE NEW CHAT
    // =========================================

    // Calls:
    // POST /chat/create/
    //
    // Creates new chat session
    const createChat = async () => {

        try {

            const response = await API.post(
                "/chat/create/",
                {
                    title: "New Chat"
                }
            );

            console.log(response.data);

            // Newly created chat
            const newChat = response.data;

            // Add new chat in sidebar
            setChats((prev) => [
                newChat,
                ...prev
            ]);

            // Set active chat
            setChatId(
                newChat.id || newChat.chat_id
            );

            // Clear previous messages
            setMessages([]);

            alert("Chat Created");

        } catch (error) {

            console.log(error.response?.data);

            alert("Chat Creation Failed");
        }
    };
    // =========================================
// DELETE CHAT
// =========================================

const deleteChat = async (id) => {

    const confirmDelete = window.confirm(
        "Are you sure you want to delete this chat?"
    );

    if (!confirmDelete) {
        return;
    }

    try {

        await API.delete(`/chat/${id}`);

        // Remove deleted chat from sidebar

        setChats((prev) =>
            prev.filter(
                (chat) =>
                    (chat.id || chat.chat_id) !== id
            )
        );

        // If current chat was deleted

        if (chatId === id) {

            setChatId(null);

            setMessages([]);
        }

        alert("Chat Deleted");

    } catch (error) {

        console.log(error.response?.data);

        alert("Delete Failed");
    }
};

    // =========================================
    // UPLOAD DOCUMENT
    // =========================================

    // Calls:
    // POST /documents/upload
    //
    // Uploads document for RAG pipeline
    const uploadDocument = async () => {

        // Check file selected or not
        if (!file) {

            alert("Select a file first");

            return;
        }

        // Create form data
        const formData = new FormData();

        formData.append("file", file);

        try {

            const response = await API.post(
                "/documents/upload",
                formData,
                {
                    headers: {
                        "Content-Type":
                            "multipart/form-data"
                    }
                }
            );

            console.log(response.data);

            alert("Document Uploaded");

        } catch (error) {

            console.log(error.response?.data);

            alert("Upload Failed");
        }
    };


    // =========================================
    // SEND MESSAGE TO AI
    // =========================================

    // Calls:
    // POST /chat/{chat_id}/message
    //
    // Backend performs:
    // - embedding generation
    // - vector search
    // - reranking
    // - conversation memory
    // - LLM generation
    const sendMessage = async () => {

        // Check chat selected
        if (!chatId) {

            alert("Create chat first");

            return;
        }

        // Prevent empty messages
        if (!message.trim()) {

            return;
        }

        try {

            // Store current user message
            const currentMessage = message;

            // Create user message object
            const userMessage = {

                role: "user",

                content: currentMessage
            };

            // Instantly show user message
            setMessages((prev) => [
                ...prev,
                userMessage
            ]);

            // Clear input box
            setMessage("");

            // Send query to backend
            const response = await API.post(
                `/chat/${chatId}/message`,
                {
                    query: currentMessage
                }
            );

            console.log(response.data);

            // AI response object
            const aiMessage = {

                role: "assistant",

                content: response.data.response
            };

            // Add AI response in chat
            setMessages((prev) => [
                ...prev,
                aiMessage
            ]);

        } catch (error) {

            console.log(error.response?.data);

            alert("Message Failed");
        }
    };


    // =========================================
    // LOAD CHATS ON PAGE LOAD
    // =========================================

    useEffect(() => {

        loadChats();

    }, []);


    // =========================================
    // UI SECTION
    // =========================================

    return (

        <div
            style={{
                display: "flex",
                height: "100vh"
            }}
        >

            {/* =====================================
                SIDEBAR SECTION
            ===================================== */}

            <div
                style={{
                    width: "25%",
                    borderRight: "1px solid gray",
                    padding: "10px",
                    overflowY: "auto"
                }}
            >

                <h2>Chats</h2>

                {/* CREATE CHAT BUTTON */}

                <button
                    onClick={createChat}
                    style={{
                        width: "100%",
                        padding: "10px"
                    }}
                >
                    + New Chat
                </button>

                <hr />

                {/* DISPLAY ALL CHATS */}

                {
    chats.map((chat) => (

        <div
            key={chat.id || chat.chat_id}

            style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "10px",
                borderBottom: "1px solid #ccc",
                marginBottom: "5px"
            }}
        >

            <span
                style={{
                    cursor: "pointer",
                    flex: 1
                }}

                onClick={() =>
                    loadMessages(
                        chat.id || chat.chat_id
                    )
                }
            >
                {chat.title}
            </span>

            <button
                onClick={() =>
                    deleteChat(
                        chat.id || chat.chat_id
                    )
                }

                style={{
                    cursor: "pointer"
                }}
            >
                🗑
            </button>

        </div>
    ))
}

            </div>


            {/* =====================================
                CHAT WINDOW SECTION
            ===================================== */}

            <div
                style={{
                    width: "75%",
                    padding: "20px",
                    display: "flex",
                    flexDirection: "column"
                }}
            >

                <h2>AI Document Chat</h2>


                {/* =====================================
                    MESSAGE DISPLAY AREA
                ===================================== */}

                <div
                    style={{
                        flex: 1,
                        overflowY: "auto",
                        border: "1px solid #ccc",
                        padding: "10px",
                        marginBottom: "15px"
                    }}
                >

                    {/* DISPLAY ALL CHAT MESSAGES */}

                    {
                        messages.map((msg, index) => (

                            <div
                                key={index}

                                style={{
                                    marginBottom: "15px",
                                    padding: "10px",
                                    borderRadius: "5px",
                                    backgroundColor:
                                        msg.role === "user"
                                            ? "#f1f1f1"
                                            : "#dbeafe"
                                }}
                            >

                                {/* Message role */}

                                <b>
                                    {
                                        msg.role === "user"
                                            ? "You"
                                            : "AI"
                                    }
                                    :
                                </b>

                                {/* Message content */}

                                <p>{msg.content}</p>

                            </div>
                        ))
                    }

                </div>


                {/* =====================================
                    DOCUMENT UPLOAD SECTION
                ===================================== */}

                <div
                    style={{
                        marginBottom: "15px"
                    }}
                >

                    <input
                        type="file"

                        onChange={(e) =>
                            setFile(e.target.files[0])
                        }
                    />

                    <button
                        onClick={uploadDocument}

                        style={{
                            marginLeft: "10px"
                        }}
                    >
                        Upload Document
                    </button>

                </div>


                {/* =====================================
                    INPUT SECTION
                ===================================== */}

                <div>

                    {/* USER INPUT BOX */}

                    <textarea
                        rows="3"

                        style={{
                            width: "100%",
                            padding: "10px"
                        }}

                        placeholder="Ask something..."

                        value={message}

                        onChange={(e) =>
                            setMessage(e.target.value)
                        }
                    />

                    <br /><br />

                    {/* SEND BUTTON */}

                    <button
                        onClick={sendMessage}

                        style={{
                            padding: "10px 20px"
                        }}
                    >
                        Send
                    </button>

                </div>

            </div>

        </div>
    );
}

export default ChatPage;

