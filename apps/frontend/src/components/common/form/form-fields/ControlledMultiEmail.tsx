import React, { useState, KeyboardEvent } from "react";
import { Input } from "@/components/ui/input";
import { X } from "lucide-react";
import { BaseControlledProps } from "@/interfaces/forms/ControlledFormFieldsProps";
import { AddToContactsOptions } from "@/interfaces/forms/ControlledFormElement";
import { getNewContactEmails } from "@/helpers/contactHelper";

interface ControlledMultiEmailProps extends BaseControlledProps {
  addToContacts?: AddToContactsOptions;
}

const ControlledMultiEmail = ({ field, addToContacts }: ControlledMultiEmailProps) => {
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

  const toggleAddToContacts = (email: string, checked: boolean) => {
    if (!addToContacts) return;
    const { selected, onChange } = addToContacts;
    onChange(checked ? [...selected, email] : selected.filter((e) => e !== email));
  };

  if (!values) return;

  const newEmails = addToContacts ? getNewContactEmails(values, addToContacts.knownEmails) : [];

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap gap-2 border rounded-md">
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
      {newEmails.map((email) => (
        <label key={email} className="flex items-center gap-2 text-sm cursor-pointer">
          <input
            type="checkbox"
            className="accent-primary"
            checked={addToContacts?.selected.includes(email) ?? false}
            onChange={(e) => toggleAddToContacts(email, e.target.checked)}
          />
          Add <span className="font-medium">{email}</span> to contacts?
        </label>
      ))}
    </div>
  );
};

export default ControlledMultiEmail;
