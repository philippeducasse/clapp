import React from "react";
import { ControllerRenderProps } from "react-hook-form";

interface ControlledTextProps {
  field: ControllerRenderProps<Record<string, unknown>, string>;
}

const ControlledTextArea = ({ field }: ControlledTextProps) => {
  return <textarea {...field} value={field.value as string} />;
};

export default ControlledTextArea;
