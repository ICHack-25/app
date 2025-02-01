/** Loading component to show when the chat is replying. */
export const Loading = () => {
    return (
      <div className="flex flex-col items-center justify-center space-y-2 py-4">
        {/* Spinner */}
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-600"></div>
        {/* Loading message */}
        <p className="text-sm text-gray-500">Chatbot is replying...</p>
      </div>
    )
};
  