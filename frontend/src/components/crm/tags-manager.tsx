'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { X, Plus, Tag } from 'lucide-react';
import type { Tag as TagType } from '@/lib/types/crm';

interface TagsManagerProps {
  tags: string[];
  availableTags: TagType[];
  onUpdate: (tags: string[]) => void;
  disabled?: boolean;
}

export function TagsManager({
  tags,
  availableTags,
  onUpdate,
  disabled = false,
}: TagsManagerProps) {
  const [newTag, setNewTag] = useState('');
  const [isAdding, setIsAdding] = useState(false);

  const handleAddTag = () => {
    if (newTag.trim() && !tags.includes(newTag.trim())) {
      onUpdate([...tags, newTag.trim()]);
      setNewTag('');
      setIsAdding(false);
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    onUpdate(tags.filter((t) => t !== tagToRemove));
  };

  const handleToggleTag = (tagToToggle: string) => {
    if (tags.includes(tagToToggle)) {
      handleRemoveTag(tagToToggle);
    } else {
      onUpdate([...tags, tagToToggle]);
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => (
          <Badge key={tag} variant="secondary" className="gap-1">
            <Tag className="h-3 w-3" />
            {tag}
            {!disabled && (
              <button
                type="button"
                onClick={() => handleRemoveTag(tag)}
                className="ml-1 hover:bg-primary-foreground/20 rounded"
              >
                <X className="h-3 w-3" />
              </button>
            )}
          </Badge>
        ))}

        {!disabled && (
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => setIsAdding(!isAdding)}
            className="h-6"
          >
            <Plus className="h-3 w-3 mr-1" />
            Add Tag
          </Button>
        )}
      </div>

      {isAdding && !disabled && (
        <div className="space-y-2 p-3 border rounded-lg">
          <div className="flex gap-2">
            <Input
              placeholder="New tag name"
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
              autoFocus
            />
            <Button type="button" size="sm" onClick={handleAddTag}>
              Add
            </Button>
          </div>

          {availableTags.length > 0 && (
            <div className="space-y-1">
              <p className="text-xs text-muted-foreground">Or select existing tags:</p>
              <ScrollArea className="h-24">
                <div className="flex flex-wrap gap-1">
                  {availableTags
                    .filter((t) => !tags.includes(t.name))
                    .map((tag) => (
                      <Badge
                        key={tag.id}
                        variant="outline"
                        className="cursor-pointer hover:bg-secondary"
                        onClick={() => handleToggleTag(tag.name)}
                        style={{ borderColor: tag.color }}
                      >
                        {tag.name}
                      </Badge>
                    ))}
                </div>
              </ScrollArea>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
