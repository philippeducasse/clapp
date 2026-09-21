import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { TagAction } from "@/interfaces/Enums";
import { Bookmark, Eye, Star, TriangleAlert, X, CircleQuestionMark, EyeOff } from "lucide-react";
import { useDispatch } from "react-redux";
import { PayloadAction } from "@reduxjs/toolkit";

interface TagsButtonProps<T> {
  entityId: number;
  tag: (entityId: number, action: TagAction) => Promise<T>;
  updateSlice: (entity: T) => PayloadAction<T>;
}

export const TagsButton = <T,>({ entityId, tag, updateSlice }: TagsButtonProps<T>) => {
  const dispatch = useDispatch();
  const markEntity = async (action: TagAction) => {
    const updatedEntity = await tag(entityId, action);
    dispatch(updateSlice(updatedEntity));
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="secondary">
          <Bookmark className="text-primary" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-[100px] flex flex-col items-center">
        <DropdownMenuItem>
          <Button
            variant={"ghost"}
            className="text-yellow-500"
            onClick={() => markEntity(TagAction.STAR)}
          >
            <Star /> Star
          </Button>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem>
          <Button
            variant={"ghost"}
            className="text-blue-700"
            onClick={() => markEntity(TagAction.WATCH)}
          >
            <Eye /> Watch
          </Button>
        </DropdownMenuItem>
        <DropdownMenuSeparator />

        <DropdownMenuItem>
          <Button
            variant={"ghost"}
            className="text-orange-700"
            onClick={() => markEntity(TagAction.WARNING)}
          >
            <TriangleAlert /> Warning
          </Button>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem>
          <Button
            variant={"ghost"}
            className="text-gray-700"
            onClick={() => markEntity(TagAction.INACTIVE)}
          >
            <X /> Inactive
          </Button>
        </DropdownMenuItem>
        <DropdownMenuItem>
          <Button
            variant={"ghost"}
            className="text-gray-700"
            onClick={() => markEntity(TagAction.IRRELEVANT)}
          >
            <EyeOff /> Irrelevant
          </Button>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem>
          <Button
            variant={"ghost"}
            className="text-purple-700"
            onClick={() => markEntity(TagAction.OTHER)}
          >
            <CircleQuestionMark /> Other
          </Button>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
