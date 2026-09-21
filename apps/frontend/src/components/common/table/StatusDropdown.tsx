import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ApplicationStatus } from "@/interfaces/entities/Application";
import { Flag } from "lucide-react";

interface StatusDropdownProps {
  entityId: number;
  onStatusChange: (id: number, status: ApplicationStatus) => void;
}

export const StatusDropdown = ({ entityId, onStatusChange }: StatusDropdownProps) => {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="icon"
          className="size-8 text-blue-600 hover:text-blue-500"
        >
          <Flag />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem onClick={() => onStatusChange(entityId, ApplicationStatus.APPLIED)}>
          Applied
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={() => onStatusChange(entityId, ApplicationStatus.IN_DISCUSSION)}
        >
          In Discussion
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => onStatusChange(entityId, ApplicationStatus.ACCEPTED)}>
          Accepted
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => onStatusChange(entityId, ApplicationStatus.REJECTED)}>
          Rejected
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => onStatusChange(entityId, ApplicationStatus.IGNORED)}>
          Ignored
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => onStatusChange(entityId, ApplicationStatus.POSTPONED)}>
          Postponed
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => onStatusChange(entityId, ApplicationStatus.CANCELLED)}>
          Cancelled
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => onStatusChange(entityId, ApplicationStatus.DRAFT)}>
          Draft
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
