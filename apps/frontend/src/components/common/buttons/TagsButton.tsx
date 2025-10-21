import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { EntityApiService } from "@/interfaces/api/ApiService";
import { MarkAction } from "@/interfaces/Enums";
import { Bookmark, Eye, Star, TriangleAlert, X, CircleQuestionMark } from "lucide-react";

interface TagsButtonProps<T> {
  entityId: number;
  apiService: EntityApiService<T>;
}

export const TagsButton = <T,>({ entityId, apiService }: TagsButtonProps<T>) => {
  const patch = async (action: MarkAction) => {
    await apiService.mark(entityId, action);
  };

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
            onClick={() => patch(MarkAction.STAR)}
          >
            <Star /> Star
          </Button>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem>
          <Button variant={"ghost"} className="text-blue-700">
            <Eye /> Watch
          </Button>
        </DropdownMenuItem>
        <DropdownMenuSeparator />

        <DropdownMenuItem>
          <Button variant={"ghost"} className="text-orange-700">
            <TriangleAlert /> Warning
          </Button>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem>
          <Button variant={"ghost"} className="text-gray-700">
            <X /> Inactive
          </Button>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem>
          <Button variant={"ghost"} className="text-purple-700">
            <CircleQuestionMark /> Other
          </Button>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
