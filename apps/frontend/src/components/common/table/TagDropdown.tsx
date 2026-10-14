"use client";
import { Bookmark, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { TagAction } from "@/interfaces/Enums";
import { TAG_ICONS } from "@/components/common/TagBadge";
import { capitalizeFirst } from "@/utils/stringUtils";
import { cn } from "@/lib/utils";

const TAG_TEXT_COLORS: Record<TagAction, string> = {
  [TagAction.STAR]: "text-yellow-500",
  [TagAction.WATCH]: "text-blue-700 dark:text-blue-400",
  [TagAction.WARNING]: "text-orange-700 dark:text-orange-400",
  [TagAction.INACTIVE]: "text-gray-700 dark:text-gray-300",
  [TagAction.IRRELEVANT]: "text-gray-700 dark:text-gray-300",
  [TagAction.OTHER]: "text-purple-700 dark:text-purple-400",
};

interface TagDropdownProps {
  currentTag?: string;
  onTag: (action: TagAction) => void;
}

/** Compact tag picker for table rows. Picking the current tag removes it (backend toggles). */
const TagDropdown = ({ currentTag, onTag }: TagDropdownProps) => (
  <DropdownMenu>
    <DropdownMenuTrigger asChild>
      <Button
        variant="outline"
        size="icon"
        className="size-8 text-primary hover:text-primary/80"
        aria-label="Tag"
      >
        <Bookmark />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end">
      {Object.values(TagAction).map((action) => {
        const Icon = TAG_ICONS[action];
        const isActive = currentTag === action;
        return (
          <DropdownMenuItem
            key={action}
            className={TAG_TEXT_COLORS[action]}
            onSelect={() => onTag(action)}
          >
            <Icon />
            <span className="flex-1">{capitalizeFirst(action)}</span>
            <Check className={cn(!isActive && "invisible")} />
          </DropdownMenuItem>
        );
      })}
    </DropdownMenuContent>
  </DropdownMenu>
);

export { TagDropdown };
