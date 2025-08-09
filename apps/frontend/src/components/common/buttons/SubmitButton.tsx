import { Button } from "../../ui/button";
import { Loader2Icon } from "lucide-react";
import React from "react";

interface SubmitButtonProps {
  isLoading: boolean;
  onClick?: () => void;
  label?: string;
  submissionLabel?: string;
}

const SubmitButton = ({ onClick, isLoading, label, submissionLabel }: SubmitButtonProps) => {
  return (
    <Button size="sm" disabled={isLoading} onClick={onClick}>
      {isLoading ? (
        <>
          <Loader2Icon className="animate-spin" />
          {submissionLabel ?? "Loading..."}
        </>
      ) : (
        label ?? "Submit"
      )}
    </Button>
  );
};

export default SubmitButton;
