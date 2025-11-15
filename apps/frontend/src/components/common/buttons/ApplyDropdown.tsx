import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { TagAction } from "@/interfaces/Enums";
import { useDispatch } from "react-redux";
import { PayloadAction } from "@reduxjs/toolkit";

interface ApplyDropdownProps<T> {
  entityId: number;
  tag: (entityId: number, action: TagAction) => Promise<T>;
  updateSlice: (entity: T) => PayloadAction<T>;
}

export const ApplyDropdown = <T,>({ entityId, tag, updateSlice }: ApplyDropdownProps<T>) => {
  const dispatch = useDispatch();
  const markEntity = async (action: TagAction) => {
    const updatedEntity = await tag(entityId, action);
    dispatch(updateSlice(updatedEntity));
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="tertiary"></Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-[100px] flex flex-col items-center">
        <DropdownMenuItem>
          <Button
            variant={"ghost"}
            className="text-yellow-500"
            onClick={() => markEntity(TagAction.STAR)}
          ></Button>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
