import { Button } from "../../ui/button";
import { Trash2 } from "lucide-react";

interface DeleteButtonProps {
  onDelete: () => void;
  label?: string;
  icon?: boolean;
  variant?: "destructive" | "outline" | "secondary";
  className?: string;
  loading?: boolean;
}

const DeleteButton = ({
  label,
  onDelete,
  icon = true,
  variant = "secondary",
  className,
  loading,
}: DeleteButtonProps) => {
  return (
    <Button
      size="default"
      variant={variant}
      onClick={onDelete}
      type="button"
      className={className}
      disabled={loading}
    >
      {icon && <Trash2 className="text-destructive" />}
      {label ?? "Delete"}
    </Button>
  );
};

export default DeleteButton;
