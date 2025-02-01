"use client"
import React from "react"
import { SidebarProvider, SidebarTrigger, SidebarInset } from "../ui/sidebar"
import { AppSidebar } from "../app-sidebar"

const mockChatData: Record<number, Array<{ user: string; message: string }>> = {
  1: [
    { user: "system", message: "Doc #1: Preliminary classification details." },
    { user: "assistant", message: "Sure, let's check that doc for more info..." },
  ],
  2: [
    { user: "system", message: "Doc #2: Another document with some notes." },
    { user: "assistant", message: "Sure, I'm analyzing #2 now." },
  ],
  3: [
    { user: "system", message: "Doc #3: Final classification details." },
    { user: "assistant", message: "Got it, let's finalize the classification." },
  ],
}

type DemoSidebarProps = {
  onSelectChat?: (id: number) => void
}

export default function DemoSidebar({ onSelectChat }: DemoSidebarProps) {
  const [selectedId, setSelectedId] = React.useState<number | null>(null)
  const [chatMessages, setChatMessages] = React.useState<
    Array<{ user: string; message: string }>
  >([])

  // Parameters
  const [temperature, setTemperature] = React.useState(0.7)
  const [maxTokens, setMaxTokens] = React.useState(1000)

  // Load the chat data when we pick a different chat
  React.useEffect(() => {
    if (selectedId != null) {
      setChatMessages(mockChatData[selectedId] || [])
    }
  }, [selectedId])

  function handleSubmitParameters() {
    console.log("Submitting parameters to LLM/Claude:")
    console.log("  Temperature:", temperature)
    console.log("  Max tokens:", maxTokens)
    console.log("Selected chat ID:", selectedId)
    // e.g. axios.post("/api/claude", { selectedId, temperature, maxTokens, topP })
  }

  return (
    <SidebarProvider>
      <AppSidebar onSelectItem={(id) => setSelectedId(id)} />

      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 border-b">
          <div className="flex flex-row items-center gap-2 px-3">
            <SidebarTrigger />
            <p>Previous Classifications</p>
          </div>
        </header>

        <main className="p-4 space-y-6">
          <div>
            {selectedId ? (
              <ChatWindow messages={chatMessages} />
            ) : (
              <p>No item selected. Click one in the sidebar!</p>
            )}
          </div>

          {/* Parameter Row (like a chat input bar) */}
          <div className="max-w-2xl">
            <LLMParameterInputs
              temperature={temperature}
              setTemperature={setTemperature}
              maxTokens={maxTokens}
              setMaxTokens={setMaxTokens}
              onSubmit={handleSubmitParameters}
            />
          </div>
        </main>
      </SidebarInset>
    </SidebarProvider>
  )
}

function ChatWindow({
  messages,
}: {
  messages: Array<{ user: string; message: string }>
}) {
  return (
    <div className="space-y-2 max-w-xl">
      {messages.map((msg, index) => {
        const isSystem = msg.user === "system"
        return (
          <div
            key={index}
            className={`w-fit rounded-md px-3 py-2 ${
              isSystem
                ? "bg-gray-200 text-black dark:bg-gray-800 dark:text-gray-100"
                : "bg-blue-500 text-white"
            }`}
          >
            {msg.message}
          </div>
        )
      })}
    </div>
  )
}

/** A row with 3 parameter inputs + Submit button, each input labeled *below* the field. */
function LLMParameterInputs({
  temperature,
  setTemperature,
  maxTokens,
  setMaxTokens,

  onSubmit,
}: {
  temperature: number
  setTemperature: (val: number) => void
  maxTokens: number
  setMaxTokens: (val: number) => void
  onSubmit: () => void
}) {
  return (
    <div className="flex items-end gap-4 rounded-md border border-gray-700 bg-gray-900 p-3 fixed 
             bottom-5 ">
      {/* Temperature Input */}
      <div className="flex flex-col items-center">
        <input
          type="number"
          step="0.01"
          min={0}
          max={1}
          placeholder="Temp"
          value={temperature}
          onChange={(e) => setTemperature(parseFloat(e.target.value))}
          className="w-16 rounded-md bg-transparent px-2 py-1 text-sm text-gray-100 
                     placeholder-gray-400 ring-0 focus:outline-none 
                     border border-transparent focus:border-gray-600
                     text-center"
        />
        <label className="mt-1 text-xs text-gray-400">Temperature</label>
      </div>

      {/* Max Tokens Input */}
      <div className="flex flex-col items-center">
        <input
          type="number"
          min={0}
          max={4000}
          placeholder="MaxTokens"
          value={maxTokens}
          onChange={(e) => setMaxTokens(parseInt(e.target.value, 10))}
          className="w-20 rounded-md bg-transparent px-2 py-1 text-sm text-gray-100 
                     placeholder-gray-400 ring-0 focus:outline-none 
                     border border-transparent focus:border-gray-600
                     text-center"
        />
        <label className="mt-1 text-xs text-gray-400">Max Tokens</label>
      </div>

      {/* Submit Button */}
      <button
        onClick={onSubmit}
        className="ml-auto rounded-md bg-blue-600 px-4 py-1 text-sm text-white 
                   hover:bg-blue-700 focus:outline-none"
      >
        Submit
      </button>
    </div>
  )
}
