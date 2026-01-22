import React, { useRef, useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { X } from "lucide-react";
import { BaseControlledProps } from "@/interfaces/forms/ControlledFormFieldsProps";

interface ControlledSingleFileProps extends BaseControlledProps {
  accept?: string;
}

const ControlledSingleFile = ({ field, accept }: ControlledSingleFileProps) => {
  const [file, setFile] = useState<File | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (field.value instanceof File) {
      setFile(field.value);
    }
  }, [field]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newFile = e.target.files?.[0] || null;
    setFile(newFile);
    field.onChange(newFile);
  };

  const handleRemoveFile = () => {
    setFile(null);
    field.onChange(null);
    if (inputRef.current) {
      inputRef.current.value = "";
    }
  };

  return (
    <div className="grid w-full items-center gap-2">
      <div className="flex items-center gap-2">
        <Input
          ref={inputRef}
          id={field.name}
          type="file"
          accept={accept}
          onChange={handleFileChange}
          className="hidden"
        />
        <Button
          type="button"
          variant="outline"
          onClick={() => inputRef.current?.click()}
          className="flex-1"
        >
          Choose File
        </Button>
      </div>
      {file && (
        <div className="flex items-center justify-between text-sm border rounded-md px-3 py-2">
          <span className="truncate">{file.name}</span>
          <Button
            type="button"
            variant="ghost"
            size="icon"
            onClick={handleRemoveFile}
            className="shrink-0 h-6 w-6 flex"
          >
            <X className="h-3 w-3" />
          </Button>
        </div>
      )}
    </div>
  );
};

export default ControlledSingleFile;