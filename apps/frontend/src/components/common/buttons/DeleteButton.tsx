import { Button } from "../../ui/button";
import React from "react";
import { Trash2 } from "lucide-react";

interface DeleteButtonProps {
  onDelete: () => void;
  label?: string;
  icon?: boolean;
}

const DeleteButton = ({ label, onDelete, icon = true }: DeleteButtonProps) => {
  return (
    <Button size="default" variant="destructive" onClick={onDelete} type="button">
      {icon && <Trash2 />}
      {label ?? "Delete"}
    </Button>
  );
};

export default DeleteButton;
