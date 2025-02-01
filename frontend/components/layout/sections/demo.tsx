"use client"
import React from "react"
import axios from "axios"
import DemoSidebar from "@/components/custom/demoSidebar"

export default function Demo() {
  // Track which chat (or document) is currently selected
  const [selectedChatId, setSelectedChatId] = React.useState<number | null>(null)

  // Store data fetched for the selected chat
  const [chatData, setChatData] = React.useState<any>(null)

  // Whenever `selectedChatId` changes, fetch data from your API
  React.useEffect(() => {
    if (selectedChatId !== null) {
      axios
        .get(`/api/chats/${selectedChatId}`) // or any endpoint you like
        .then((res: { data: any }) => {
          setChatData(res.data)
        })
        .catch((err: any) => {
          console.error("Failed to fetch chat data:", err)
        })
    }
  }, [selectedChatId])

  return (
    <section className="container w-full">
      <div className="lg:max-w-screen-xl py-1 md:py-1 flex">
        {/* Pass a callback to the sidebar so it can set `selectedChatId` */}
        <DemoSidebar onSelectChat={(id: number) => setSelectedChatId(id)}  />

        {/* Main content area (flex-1 so it expands) */}
        
      </div>
    </section>
  )
}
