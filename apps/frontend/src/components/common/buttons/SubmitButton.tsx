import { Button } from "../../ui/button";
import { Loader2Icon } from "lucide-react";
import React from "react";
import { Save } from "lucide-react";

interface SubmitButtonProps {
  isLoading: boolean;
  onClick?: () => void;
  label?: string;
  submissionLabel?: string;
}

const SubmitButton = ({ onClick, isLoading, label, submissionLabel }: SubmitButtonProps) => {
  return (
    <Button size="default" disabled={isLoading} onClick={onClick}>
      {isLoading ? (
        <>
          <Loader2Icon className="animate-spin" />
          {submissionLabel ?? "Loading..."}
        </>
      ) : (
        <>
          <Save />
          {label ?? "Submit"}
        </>
      )}
    </Button>
  );
};

export default SubmitButton;
