import React, { ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { Send } from "lucide-react";
interface GenericButtonProps {
  onClick?: () => void;
  label?: string;
  icon?: ReactNode;
  isLoading?: boolean;
  variant?:
    | "link"
    | "default"
    | "destructive"
    | "outline"
    | "secondary"
    | "tertiary"
    | "ghost"
    | null
    | undefined;
}

const GenericButton = ({ onClick, label, isLoading, icon, variant }: GenericButtonProps) => {
  return (
    <Button onClick={onClick} disabled={isLoading} variant={variant ?? "default"}>
      {icon ?? <Send />}
      {label}
    </Button>
  );
};

export default GenericButton;
