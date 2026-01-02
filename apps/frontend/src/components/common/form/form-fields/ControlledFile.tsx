import React, { useRef, useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { X } from "lucide-react";
import { BaseControlledProps } from "@/interfaces/forms/ControlledFormFieldsProps";
import { Dossier } from "@/interfaces/entities/Performance";

const ControlledFile = ({ field }: BaseControlledProps) => {
  const [files, setFiles] = useState<Array<File | Dossier>>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  useEffect(() => {
    if (Array.isArray(field.value) && field.value.length > 0) {
      setFiles(field.value);
    }
  }, [field]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newFiles = e.target.files ? Array.from(e.target.files) : [];
    setFiles(newFiles);
    field.onChange(newFiles);
  };

  const handleRemoveFile = (index: number) => {
    const newFiles = files.filter((_, i) => i !== index);
    setFiles(newFiles);
    field.onChange(newFiles);
  };

  const getFileName = (file: File | Dossier): string => {
    if (file instanceof File) {
      return file.name;
    }
    return file.file.split("/").pop() || file.file;
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
          className="hidden"
        />
        <Button
          type="button"
          variant="outline"
          onClick={() => inputRef.current?.click()}
          className="flex-1"
        >
          Choose Files
        </Button>
      </div>
      {files.length > 0 && (
        <div>
          <p className="mb-1">Existing files:</p>
          <div className="flex flex-wrap gap-2">
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between text-sm border rounded-md px-3 py-2  w-[calc(50%-0.25rem)]"
              >
                <span className="truncate">{getFileName(file)}</span>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={() => handleRemoveFile(index)}
                  className="shrink-0 h-6 w-6 flex"
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ControlledFile;
