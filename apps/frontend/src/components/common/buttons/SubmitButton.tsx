import { Button } from "../../ui/button";
import { Loader2Icon } from "lucide-react";
import React from "react";
import { Save } from "lucide-react";

interface SubmitButtonProps {
  isLoading: boolean;
  onClick?: () => void;
  label?: string;
  submissionLabel?: string;
  showIcon?: boolean;
}

const SubmitButton = ({
  onClick,
  isLoading,
  label,
  submissionLabel,
  showIcon = true,
}: SubmitButtonProps) => {
  return (
    <Button size="default" disabled={isLoading} onClick={onClick}>
      {isLoading ? (
        <>
          <Loader2Icon className="animate-spin text-primary dark:text-foreground" />
          {submissionLabel ?? "Loading..."}
        </>
      ) : (
        <>
          {showIcon && <Save className="text-primary dark:text-foreground" />} {label ?? "Submit"}
        </>
      )}
    </Button>
  );
};

export default SubmitButton;
