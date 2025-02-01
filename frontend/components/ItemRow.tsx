import React from "react"
import {
  SidebarMenuItem,
  SidebarMenuButton,
} from "@/components/ui/sidebar"

import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu"
import { MoreHorizontal } from "lucide-react"

type ItemRowProps = {
  item: { id: number; title: string }
  onSelect: (id: number) => void
  onEdit: (itemId: number, currentTitle: string) => void
  onDelete: (itemId: number) => void
}

export function ItemRow({
  item,
  onSelect,
  onEdit,
  onDelete,
}: ItemRowProps) {
  // Control the dropdown’s open/close
  const [open, setOpen] = React.useState(false)

  return (
    <SidebarMenuItem key={item.id}>
      <div className="flex items-center justify-between w-full pr-3">
        {/* Clicking the main button => select the item */}
        <SidebarMenuButton asChild onClick={() => onSelect(item.id)}>
          <button className="grow text-left font-medium">
            {item.title}
          </button>
        </SidebarMenuButton>

        {/* "..." Dropdown */}
        <DropdownMenu open={open} onOpenChange={setOpen}>
          <DropdownMenuTrigger asChild>
            <button className="ml-2 p-1" aria-label="Options">
              <MoreHorizontal className="h-4 w-4" />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {/* EDIT */}
            <DropdownMenuItem
              onClick={() => {
                // Close the dropdown manually
                setOpen(false)
                onEdit(item.id, item.title)
              }}
            >
              Edit
            </DropdownMenuItem>
            {/* DELETE */}
            <DropdownMenuItem
              onClick={() => {
                // Close the dropdown manually
                setOpen(false)
                onDelete(item.id)
              }}
              className="text-red-500"
            >
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </SidebarMenuItem>
  )
}
