'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { formatRelativeTime } from '@/lib/utils';
import { PushPin, MoreVertical, Edit, Trash2 } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import type { Note } from '@/lib/types/crm';

interface NoteEditorProps {
  notes: Note[];
  onAdd: (content: string) => void;
  onUpdate?: (noteId: string, content: string) => void;
  onDelete?: (noteId: string) => void;
  onTogglePin?: (noteId: string) => void;
  currentUserId?: string;
  disabled?: boolean;
}

export function NoteEditor({
  notes,
  onAdd,
  onUpdate,
  onDelete,
  onTogglePin,
  currentUserId,
  disabled = false,
}: NoteEditorProps) {
  const [newNote, setNewNote] = useState('');
  const [editingNoteId, setEditingNoteId] = useState<string | null>(null);
  const [editContent, setEditContent] = useState('');

  const handleAddNote = () => {
    if (newNote.trim()) {
      onAdd(newNote.trim());
      setNewNote('');
    }
  };

  const handleStartEdit = (note: Note) => {
    setEditingNoteId(note.id);
    setEditContent(note.content);
  };

  const handleSaveEdit = () => {
    if (editingNoteId && editContent.trim()) {
      onUpdate?.(editingNoteId, editContent.trim());
      setEditingNoteId(null);
      setEditContent('');
    }
  };

  const handleCancelEdit = () => {
    setEditingNoteId(null);
    setEditContent('');
  };

  // Sort notes: pinned first, then by date
  const sortedNotes = [...notes].sort((a, b) => {
    if (a.is_pinned && !b.is_pinned) return -1;
    if (!a.is_pinned && b.is_pinned) return 1;
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });

  return (
    <div className="space-y-4">
      {!disabled && (
        <Card>
          <CardHeader>
            <h3 className="font-semibold">Add a note</h3>
          </CardHeader>
          <CardContent className="space-y-3">
            <Textarea
              placeholder="Write your note here..."
              value={newNote}
              onChange={(e) => setNewNote(e.target.value)}
              rows={4}
            />
            <div className="flex justify-end">
              <Button onClick={handleAddNote} disabled={!newNote.trim()}>
                Add Note
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="space-y-3">
        {sortedNotes.map((note) => (
          <Card key={note.id} className={note.is_pinned ? 'border-primary' : ''}>
            <CardContent className="p-4">
              <div className="flex gap-3">
                <Avatar className="h-8 w-8">
                  <AvatarImage src="" />
                  <AvatarFallback>
                    {note.created_by[0]}
                  </AvatarFallback>
                </Avatar>

                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-sm">
                        {note.created_by}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {formatRelativeTime(note.created_at)}
                      </span>
                      {note.is_pinned && (
                        <PushPin className="h-3 w-3 text-primary" />
                      )}
                    </div>

                    {!disabled && (
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => onTogglePin?.(note.id)}>
                            <PushPin className="mr-2 h-4 w-4" />
                            {note.is_pinned ? 'Unpin' : 'Pin'}
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleStartEdit(note)}>
                            <Edit className="mr-2 h-4 w-4" />
                            Edit
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={() => onDelete?.(note.id)}
                            className="text-destructive"
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    )}
                  </div>

                  {editingNoteId === note.id ? (
                    <div className="space-y-2">
                      <Textarea
                        value={editContent}
                        onChange={(e) => setEditContent(e.target.value)}
                        rows={4}
                      />
                      <div className="flex gap-2">
                        <Button size="sm" onClick={handleSaveEdit}>
                          Save
                        </Button>
                        <Button size="sm" variant="outline" onClick={handleCancelEdit}>
                          Cancel
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm whitespace-pre-wrap">{note.content}</p>
                  )}

                  {note.mentions && note.mentions.length > 0 && (
                    <div className="mt-2 flex gap-1">
                      {note.mentions.map((mention) => (
                        <Badge key={mention} variant="secondary" className="text-xs">
                          @{mention}
                        </Badge>
                      ))}
                    </div>
                  )}

                  {note.attachments && note.attachments.length > 0 && (
                    <div className="mt-2 flex gap-2">
                      {note.attachments.map((attachment) => (
                        <Badge key={attachment.id} variant="outline" className="text-xs">
                          {attachment.file_name}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}

        {notes.length === 0 && !disabled && (
          <Card className="p-8 text-center">
            <p className="text-sm text-muted-foreground">
              No notes yet. Add your first note above.
            </p>
          </Card>
        )}
      </div>
    </div>
  );
}
