import { Button } from "../../ui/button";
import { Loader2Icon } from "lucide-react";
import React from "react";

interface SubmitButtonProps {
  isLoading: boolean;
  label?: string;
  submissionLabel?: string;
}

const SubmitButton = ({ isLoading, label, submissionLabel }: SubmitButtonProps) => {
  return (
    <Button size="sm" disabled={isLoading}>
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
