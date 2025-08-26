import React from "react";
import { Button } from "@/components/ui/button";
import { Send } from "lucide-react";

interface SendButtonProps {
  onClick?: () => void;
  label?: string;
  isLoading: boolean;
}

const SendButton = ({ onClick, label, isLoading }: SendButtonProps) => {
  return (
    <Button onClick={onClick} disabled={isLoading}>
      <Send />
      {label}
    </Button>
  );
};

export default SendButton;
