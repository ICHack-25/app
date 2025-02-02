"use client"

import * as React from "react"
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarHeader,
  SidebarMenu,
  SidebarRail,
} from "@/components/ui/sidebar"

import { Plus } from "lucide-react"

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog"

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"

// The reusable row we created
import { ItemRow } from "./ItemRow"
import Link from "next/link"

// Example initial data
const INITIAL_ITEMS = [
  { id: 1, title: "Previous Chat #1" },
  { id: 2, title: "Previous Chat #2" },
  { id: 3, title: "Previous Chat #3" },
]

type AppSidebarProps = {
  onSelectItem?: (id: number) => void
}

export function AppSidebar({ onSelectItem, ...props }: AppSidebarProps) {
  const [items, setItems] = React.useState(INITIAL_ITEMS)

  // CREATE
  function handleCreateItem() {
    // (POST request placeholder)
    const newId = items.length ? items[items.length - 1].id + 1 : 1
    const newItem = { id: newId, title: `Previous Chat #${newId}` }
    setItems((prev) => [...prev, newItem])
    // Optionally select the newly created item
    onSelectItem?.(newId)
  }

  // EDIT DIALOG
  const [editDialogOpen, setEditDialogOpen] = React.useState(false)
  const [currentEditItemId, setCurrentEditItemId] = React.useState<number | null>(null)
  const [editTitle, setEditTitle] = React.useState("")

  function openEditDialog(itemId: number, currentTitle: string) {
    setCurrentEditItemId(itemId)
    setEditTitle(currentTitle)
    setEditDialogOpen(true)
  }

  function handleSaveEdit() {
    if (currentEditItemId == null) return
    // (PATCH request placeholder)
    setItems((prev) =>
      prev.map((item) =>
        item.id === currentEditItemId ? { ...item, title: editTitle } : item
      )
    )
    setEditDialogOpen(false)
  }

  // DELETE ALERT DIALOG
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false)
  const [currentDeleteItemId, setCurrentDeleteItemId] = React.useState<number | null>(null)

  function openDeleteDialog(itemId: number) {
    setCurrentDeleteItemId(itemId)
    setDeleteDialogOpen(true)
  }

  function handleConfirmDelete() {
    if (currentDeleteItemId == null) return
    // (DELETE request placeholder)
    setItems((prev) => prev.filter((i) => i.id !== currentDeleteItemId))
    setDeleteDialogOpen(false)
  }

  return (
    <Sidebar {...props}>
      {/* Sidebar Header (Create Button) */}
      <SidebarHeader>
        <div className="flex items-center justify-between p-4">
          <span className="font-bold">
            <Link href={"/"}>
            RAGGuard
            </Link>
          </span>
          <button
            onClick={handleCreateItem}
            className="flex items-center gap-1 p-1"
            title="Create New"
          >
            <Plus className="h-4 w-4" />
          </button>
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarMenu>
            {items.map((item) => (
              <ItemRow
                key={item.id}
                item={item}
                onSelect={(id) => onSelectItem?.(id)}
                onEdit={openEditDialog}
                onDelete={openDeleteDialog}
              />
            ))}
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>
      <SidebarRail />

      {/* ---- EDIT DIALOG ---- */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Item</DialogTitle>
          </DialogHeader>
          <div className="flex flex-col gap-2">
            <label>Title:</label>
            <input
              className="border p-2"
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
            />
          </div>
          <DialogFooter>
            <DialogClose asChild>
              <button className="px-3 py-1 border rounded">Cancel</button>
            </DialogClose>
            <button
              onClick={handleSaveEdit}
              className="px-3 py-1 border rounded bg-blue-500 text-white"
            >
              OK
            </button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ---- DELETE ALERT DIALOG ---- */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              Are you sure you want to delete this item?
            </AlertDialogTitle>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="px-3 py-1 border rounded">
              No
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirmDelete}
              className="px-3 py-1 border rounded bg-red-500 text-white"
            >
              Yes, Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Sidebar>
  )
}
