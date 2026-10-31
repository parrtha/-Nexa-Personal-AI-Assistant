
function ChatHistory({
  conversations,
  onOpen,
  onDelete,
  onNewChat
}) {
  return (
    <section className="feature-page">
      <div className="feature-page-heading">
        <div>
          <span className="eyebrow">YOUR ASSISTANT</span>
          <h1>Chat History</h1>
          <p>Your previously saved conversations.</p>
        </div>

        <button onClick={onNewChat}>
          + New chat
        </button>
      </div>

      {conversations.length === 0 ? (
        <div className="feature-empty">
          <span>◷</span>
          <strong>No saved conversations</strong>
          <p>Your conversations will appear here.</p>
        </div>
      ) : (
        <div className="history-list">
          {conversations.map((conversation) => (
            <article
              key={conversation.id}
              className="history-item"
            >
              <button
                className="history-open"
                onClick={() => onOpen(conversation.id)}
              >
                <strong>{conversation.title}</strong>

                <span>
                  {new Date(
                    conversation.updatedAt
                  ).toLocaleString()}
                </span>

                <small>
                  {conversation.messages.length} messages
                </small>
              </button>

              <button
                className="history-delete"
                onClick={() => onDelete(conversation.id)}
                aria-label="Delete conversation"
              >
                Delete
              </button>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

export default ChatHistory;
