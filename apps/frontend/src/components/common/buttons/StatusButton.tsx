import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ApplicationStatus } from "@/interfaces/entities/Application";
import {
  Send,
  MessageCircle,
  CheckCircle,
  XCircle,
  Clock,
  Ban,
  FileText,
  CircleQuestionMark,
  EyeOff,
  Flag,
} from "lucide-react";
import { useDispatch } from "react-redux";
import { PayloadAction } from "@reduxjs/toolkit";

interface StatusButtonProps<T> {
  entityId: number;
  updateStatus: (entityId: number, status: ApplicationStatus) => Promise<T>;
  updateSlice: (entity: T) => PayloadAction<T>;
}

export const StatusButton = <T,>({
  entityId,
  updateStatus,
  updateSlice,
}: StatusButtonProps<T>) => {
  const dispatch = useDispatch();
  const changeStatus = async (status: ApplicationStatus) => {
    const updatedEntity = await updateStatus(entityId, status);
    dispatch(updateSlice(updatedEntity));
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="tertiary">
          <Flag />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-[150px] flex flex-col items-center">
        <DropdownMenuItem>
          <Button
            variant={"ghost"}
            className="text-blue-600"
            onClick={() => changeStatus(ApplicationStatus.APPLIED)}
          >
            <Send /> Applied
          </Button>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem>
          <Button
            variant={"ghost"}
            className="text-purple-600"
            onClick={() => changeStatus(ApplicationStatus.IN_DISCUSSION)}
          >
            <MessageCircle /> In Discussion
          </Button>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem>
          <Button
            variant={"ghost"}
            className="text-green-600"
            onClick={() => changeStatus(ApplicationStatus.ACCEPTED)}
          >
            <CheckCircle /> Accepted
          </Button>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem>
          <Button
            variant={"ghost"}
            className="text-red-600"
            onClick={() => changeStatus(ApplicationStatus.REJECTED)}
          >
            <XCircle /> Rejected
          </Button>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem>
          <Button
            variant={"ghost"}
            className="text-gray-600"
            onClick={() => changeStatus(ApplicationStatus.IGNORED)}
          >
            <EyeOff /> Ignored
          </Button>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem>
          <Button
            variant={"ghost"}
            className="text-yellow-600"
            onClick={() => changeStatus(ApplicationStatus.POSTPONED)}
          >
            <Clock /> Postponed
          </Button>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem>
          <Button
            variant={"ghost"}
            className="text-orange-600"
            onClick={() => changeStatus(ApplicationStatus.CANCELLED)}
          >
            <Ban /> Cancelled
          </Button>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem>
          <Button
            variant={"ghost"}
            className="text-gray-500"
            onClick={() => changeStatus(ApplicationStatus.DRAFT)}
          >
            <FileText /> Draft
          </Button>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem>
          <Button
            variant={"ghost"}
            className="text-purple-700"
            onClick={() => changeStatus(ApplicationStatus.OTHER)}
          >
            <CircleQuestionMark /> Other
          </Button>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};