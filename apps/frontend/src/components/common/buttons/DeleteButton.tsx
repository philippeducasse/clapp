import { Button } from "../../ui/button";
import React from "react";
import { Trash2 } from "lucide-react";

interface DeleteButtonProps {
  onDelete: () => void;
  label?: string;
  icon?: boolean;
  variant?: "destructive" | "outline";
}

const DeleteButton = ({
  label,
  onDelete,
  icon = true,
  variant = "destructive",
}: DeleteButtonProps) => {
  return (
    <Button size="default" variant={variant} onClick={onDelete} type="button">
      {icon && <Trash2 />}
      {label ?? "Delete"}
    </Button>
  );
};

export default DeleteButton;
