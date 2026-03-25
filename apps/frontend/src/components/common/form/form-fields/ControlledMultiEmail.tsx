import React, { useState, KeyboardEvent } from "react";
import { Input } from "@/components/ui/input";
import { X } from "lucide-react";
import { BaseControlledProps } from "@/interfaces/forms/ControlledFormFieldsProps";

const ControlledMultiEmail = ({ field }: BaseControlledProps) => {
  const [inputValue, setInputValue] = useState("");
  const values = (field.value as string[]) ?? [];

  const addValue = (value: string) => {
    const trimmed = value.trim();
    if (trimmed && !values.includes(trimmed)) {
      field.onChange([...values, trimmed]);
      setInputValue("");
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addValue(inputValue);
    } else if (e.key === "Backspace" && !inputValue && values.length > 0) {
      field.onChange(values.slice(0, -1));
    }
  };

  const removeValue = (index: number) => {
    field.onChange(values.filter((_, i) => i !== index));
  };

  if (!values) return;

  return (
    <div className="flex flex-wrap gap-2 p-2 border rounded-md">
      {values.map((value, index) => (
        <span
          key={index}
          className="flex items-center gap-1 border border-primary bg-primary/5 px-2 py-1 rounded"
        >
          {value}
          <X size={14} className="cursor-pointer" onClick={() => removeValue(index)} />
        </span>
      ))}
      <Input
        type="text"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleKeyDown}
        onBlur={() => addValue(inputValue)}
        className="border-none flex-1 min-w-[120px]"
      />
    </div>
  );
};

export default ControlledMultiEmail;
