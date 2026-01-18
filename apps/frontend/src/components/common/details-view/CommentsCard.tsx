"use client";

import React, { useState } from "react";
import { Card, CardContent, CardTitle } from "@/components/ui/card";
import { MessageSquare, Pencil, Check, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface CommentsCardProps {
  comments: string;
  onSave: (comments: string) => Promise<void>;
}

const CommentsCard = ({ comments, onSave }: CommentsCardProps) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedComments, setEditedComments] = useState(comments);
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await onSave(editedComments);
      setIsEditing(false);
    } catch (error) {
      console.error("Failed to save comments:", error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setEditedComments(comments);
    setIsEditing(false);
  };

  return (
    <Card className="h-fit">
      <CardContent>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <MessageSquare className="text-emerald-600 dark:text-emerald-400" size={20} />
            <CardTitle className="text-lg font-semibold text-black dark:text-foreground">
              Comments
            </CardTitle>
          </div>
          {!isEditing && (
            <Button
              variant="ghost"
              size="sm"
              className="h-8 w-8 p-0 text-gray-400 hover:text-emerald-600"
              onClick={() => setIsEditing(true)}
            >
              <Pencil size={16} />
            </Button>
          )}
        </div>

        {isEditing ? (
          <div className="space-y-3">
            <Textarea
              value={editedComments}
              onChange={(e) => setEditedComments(e.target.value)}
              placeholder="Add your comments..."
              className="min-h-24 resize-none"
            />
            <div className="flex justify-end gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCancel}
                disabled={isSaving}
              >
                <X size={16} className="mr-1" />
                Cancel
              </Button>
              <Button
                size="sm"
                onClick={handleSave}
                disabled={isSaving}
              >
                <Check size={16} className="mr-1" />
                {isSaving ? "Saving..." : "Save"}
              </Button>
            </div>
          </div>
        ) : (
          <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
            {comments || (
              <span className="text-gray-500 dark:text-gray-400 italic">No comments</span>
            )}
          </p>
        )}
      </CardContent>
    </Card>
  );
};

export default CommentsCard;