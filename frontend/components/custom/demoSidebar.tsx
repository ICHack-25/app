"use client"
import React from "react"
import { z } from "zod"
import { SidebarProvider, SidebarTrigger, SidebarInset } from "../ui/sidebar"
import { AppSidebar } from "../app-sidebar"
import Axios from 'axios'
import { DataObject } from "../dataobject"
import {ClusterNetwork} from "@/components/ui/clusternetwork";

const mockNodesData: DataObject[] = [
  new DataObject('File1', 'txt', 'https://arxiv.org/pdf/2501.18455'),
  new DataObject('File2', 'pdf', '/path/to/file2.pdf'),
  new DataObject('File3', 'jpg', '/path/to/file3.jpg'),
  new DataObject('File4', 'docx', '/path/to/file4.docx')
];

const plainData = mockNodesData.map(obj => obj.toPlainObject());

// Mocked chat data keyed by chat ID:
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

let currentChatData = {}

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
  const [isFileMode, setIsFileMode] = React.useState(true)
  const [fileValue, setFileValue] = React.useState<File | null>(null)
  const [linkValue, setLinkValue] = React.useState("")
  // Additional text input that we’ll use as the query
  const [inputText, setInputText] = React.useState("")

  // (Optional) Initial fetch if you need some data on mount.
  React.useEffect(() => {
    const fetchData = async () => {
      try {
        const payload = {
          "query": inputText,
          "links": linkValue,
          "files": fileValue,
        }
        const response = await Axios.post('http://ichack25-flask.containers.uwcs.co.uk/submit-prompt', payload)
        console.log('Data:', response.data)
        currentChatData = response.data
      } catch (error) {
        console.error('Error fetching data:', error)
      }
    };

    fetchData();
  }, []);

  // Load the chat data when a different chat is selected
  React.useEffect(() => {
    if (selectedId !== null) {
      setChatMessages(mockChatData[selectedId] || [])
    }
  }, [selectedId])

  /** Called when user submits the form. */
  async function handleParameterForm(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()

    // Validate additional text (max 500 characters)
    const textSchema = z.string().max(500, "Additional text must be 500 characters or less.")
    const textValidation = textSchema.safeParse(inputText)
    if (!textValidation.success) {
      alert(textValidation.error.errors[0].message)
      return
    }

    // Build the payload based on mode:
    const payload = {
      // Here, we use the additional text as the query.
      query: inputText,
      // If not in file mode, include the link (if provided) in an array.
      links: !isFileMode && linkValue ? [linkValue] : [],
      // In file mode, if a file is provided, send its name (in a real app, use FormData for the actual file).
      files: isFileMode && fileValue ? [fileValue.name] : []
    }

    console.log("Submitting payload:", payload)

    try {
      const response = await Axios.post('http://ichack25-flask.containers.uwcs.co.uk/submit-prompt', payload)
      console.log("Response data:", response.data)

      // Append the returned data as a new chat message.
      setChatMessages(prev => [
        ...prev,
        { user: "assistant", message: response.data }
      ])
    } catch (error) {
      console.error("Error submitting prompt:", error)
      setChatMessages(prev => [
        ...prev,
        { user: "assistant", message: "Error submitting prompt" }
      ])
    }
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
          {selectedId ? (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {/* Left column: The Chat */}
              <div>
                <ChatWindow messages={chatMessages} />
              </div>

              {/* Right column: A "card" that could display a graph or other info */}
              <div className="border rounded-md p-4 shadow">
                <h2 className="text-lg font-semibold mb-2">Files / Graph</h2>
                <ClusterNetwork data={plainData}/>

                <p className="text-sm text-gray-500">
                  This is where you might display a graph or data about the uploaded file(s).
                </p>
              </div>
            </div>
          ) : (
            <p>No item selected. Click one in the sidebar!</p>
          )}

          {/* Only show the parameter row if we have a selection */}
          {selectedId !== null && (
            <div className="max-w-2xl">
              <ParameterForm
                temperature={temperature}
                setTemperature={setTemperature}
                maxTokens={maxTokens}
                setMaxTokens={setMaxTokens}
                isFileMode={isFileMode}
                setIsFileMode={setIsFileMode}
                fileValue={fileValue}
                setFileValue={setFileValue}
                linkValue={linkValue}
                setLinkValue={setLinkValue}
                inputText={inputText}
                setInputText={setInputText}
                onSubmit={handleParameterForm}
              />
            </div>
          )}
        </main>
      </SidebarInset>
    </SidebarProvider>
  )
}

/** Displays the selected chat's messages in bubble form. */
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

type ParameterFormProps = {
  temperature: number
  setTemperature: (val: number) => void
  maxTokens: number
  setMaxTokens: (val: number) => void
  isFileMode: boolean
  setIsFileMode: (val: boolean) => void
  fileValue: File | null
  setFileValue: (val: File | null) => void
  linkValue: string
  setLinkValue: (val: string) => void
  inputText: string
  setInputText: (val: string) => void
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void
}

/**
 * A fixed bar at the bottom with a toggle for file/link,
 * plus temperature + maxTokens, additional text input, and a Submit button.
 */
function ParameterForm({
  temperature,
  setTemperature,
  maxTokens,
  setMaxTokens,
  isFileMode,
  setIsFileMode,
  fileValue,
  setFileValue,
  linkValue,
  setLinkValue,
  inputText,
  setInputText,
  onSubmit,
}: ParameterFormProps) {
  return (
    <form
      onSubmit={onSubmit}
      className="flex flex-wrap items-end gap-4 rounded-md border border-gray-700 bg-gray-900 
                 p-3 fixed bottom-5 max-w-4xl"
    >
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

      {/* Toggle: File or Link */}
      <div className="flex flex-col items-center">
        <input
          type="checkbox"
          checked={isFileMode}
          onChange={(e) => setIsFileMode(e.target.checked)}
          className="h-4 w-4 rounded-sm border-gray-600 bg-gray-800 
                     text-blue-600 focus:outline-none"
        />
        <label className="mt-1 text-xs text-gray-400">
          {isFileMode ? "File Mode" : "Link Mode"}
        </label>
      </div>

      {/* Conditionally show file input or link input */}
      {isFileMode ? (
        <div className="flex flex-col items-center">
          <input
            type="file"
            onChange={(e) => {
              if (e.target.files?.[0]) {
                setFileValue(e.target.files[0])
              }
            }}
            className="w-32 text-sm text-gray-100
                       file:mr-2 file:rounded-md file:border-0 file:bg-gray-700 
                       file:px-2 file:py-1 file:text-sm file:text-gray-100 
                       hover:file:bg-gray-600"
          />
          <label className="mt-1 text-xs text-gray-400">Upload File</label>
        </div>
      ) : (
        <div className="flex flex-col items-center">
          <input
            type="text"
            placeholder="https://example.com"
            value={linkValue}
            onChange={(e) => setLinkValue(e.target.value)}
            className="w-36 rounded-md bg-transparent px-2 py-1 text-sm text-gray-100 
                       placeholder-gray-400 ring-0 focus:outline-none 
                       border border-transparent focus:border-gray-600
                       text-center"
          />
          <label className="mt-1 text-xs text-gray-400">Link</label>
        </div>
      )}

      {/* Additional Text Input */}
      <div className="flex flex-col items-center">
        <textarea
          placeholder="Enter additional text..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          className="w-64 h-20 rounded-md bg-transparent px-2 py-1 text-sm text-gray-100 
                     placeholder-gray-400 ring-0 focus:outline-none 
                     border border-transparent focus:border-gray-600"
        />
        <label className="mt-1 text-xs text-gray-400">
          Additional Text (max 500 chars)
        </label>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        className="ml-auto rounded-md bg-blue-600 px-4 py-1 text-sm text-white 
                   hover:bg-blue-700 focus:outline-none"
      >
        Submit
      </button>
    </form>
  )
}
