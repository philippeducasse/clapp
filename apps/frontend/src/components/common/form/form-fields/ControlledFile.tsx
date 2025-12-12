import React, { useRef, useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ControllerRenderProps } from "react-hook-form";
import { X } from "lucide-react";

interface ControlledFileProps {
  field: ControllerRenderProps<Record<string, unknown>, string>;
}

const ControlledFile = ({ field }: ControlledFileProps) => {
  const [files, setFiles] = useState<File[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newFiles = e.target.files ? Array.from(e.target.files) : [];
    setFiles(newFiles);
    field.onChange(newFiles);
  };

  const handleClear = () => {
    setFiles([]);
    field.onChange([]);
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
          multiple
          onChange={handleFileChange}
          className="flex-1 pt-1.5 hover:cursor-pointer"
        />
        {files.length > 0 && (
          <Button
            type="button"
            variant="outline"
            size="icon"
            onClick={handleClear}
            className="shrink-0"
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>
      {files.length > 0 && (
        <div className="text-sm text-muted-foreground">
          {files.length} file{files.length !== 1 ? "s" : ""} selected:{" "}
          {files.map((f) => f.name).join(", ")}
        </div>
      )}
    </div>
  );
};

export default ControlledFile;
