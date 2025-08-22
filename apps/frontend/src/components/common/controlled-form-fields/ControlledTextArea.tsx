import React from "react";
import { ControllerRenderProps } from "react-hook-form";

interface ControlledTextAreaProps {
  field: ControllerRenderProps<Record<string, unknown>, string>;
  showLabels: boolean;
}

const ControlledTextArea = ({ field, showLabels }: ControlledTextAreaProps) => {
  return showLabels ? (
    <textarea
      className="h-42 fit file:text-foreground placeholder:text-muted-foreground selection:bg-primary selection:text-primary-foreground dark:bg-input/30 border-input flex w-full min-w-0 rounded-md border bg-transparent px-3 text-base shadow-xs transition-[color,box-shadow] outline-none file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm
        focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]
        aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive"
      {...field}
      value={field.value as string}
    />
  ) : (
    <textarea className="p-2 " {...field} value={field.value as string} />
  );
};

export default ControlledTextArea;
