import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { MarkAction } from "@/interfaces/Enums";
import { Bookmark, Eye, Star, TriangleAlert, X, CircleQuestionMark } from "lucide-react";

interface TagsButtonProps<T> {
  entityId: number;
  mark: (entityId: number, action: MarkAction) => Promise<T>;
}

export const TagsButton = <T,>({ entityId, mark }: TagsButtonProps<T>) => {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="tertiary">
          <Bookmark />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-[100px] flex flex-col items-center">
        <DropdownMenuItem>
          <Button
            variant={"ghost"}
            className="text-yellow-500"
            onClick={() => mark(entityId, MarkAction.STAR)}
          >
            <Star /> Star
          </Button>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem>
          <Button
            variant={"ghost"}
            className="text-blue-700"
            onClick={() => mark(entityId, MarkAction.WATCH)}
          >
            <Eye /> Watch
          </Button>
        </DropdownMenuItem>
        <DropdownMenuSeparator />

        <DropdownMenuItem>
          <Button
            variant={"ghost"}
            className="text-orange-700"
            onClick={() => mark(entityId, MarkAction.WARNING)}
          >
            <TriangleAlert /> Warning
          </Button>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem>
          <Button
            variant={"ghost"}
            className="text-gray-700"
            onClick={() => mark(entityId, MarkAction.INACTIVE)}
          >
            <X /> Inactive
          </Button>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem>
          <Button
            variant={"ghost"}
            className="text-purple-700"
            onClick={() => mark(entityId, MarkAction.OTHER)}
          >
            <CircleQuestionMark /> Other
          </Button>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
