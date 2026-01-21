"use client";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useState, Dispatch, SetStateAction } from "react";
import { Hammer, X } from "lucide-react";
import SubmitButton from "../buttons/SubmitButton";
import { DynamicProgress } from "../DynamicProgress";
import { cn } from "@/lib/utils";

export interface UpdateDialogProps<T> {
  entity: T | undefined;
  entityName: string;
  DiffTableComponent: React.ComponentType<{
    original: T;
    updated: T;
    setUpdated: Dispatch<SetStateAction<T | undefined>>;
  }>;
  onEnrich: () => Promise<T>;
  onUpdate: (updated: T) => Promise<void>;
}

export const UpdateDialog = <T,>({
  entity,
  entityName,
  DiffTableComponent,
  onEnrich,
  onUpdate,
}: UpdateDialogProps<T>) => {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [updatedFields, setUpdatedFields] = useState<T | undefined>();

  const handleUpdate = async () => {
    setLoading(true);
    try {
      if (entity && !updatedFields) {
        const response = await onEnrich();
        setUpdatedFields(response);
      }
    } catch (error) {
      console.error(`Error: could not update ${entityName.toLowerCase()}: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (updatedFields) {
      setLoading(true);
      try {
        await onUpdate(updatedFields);
        setOpen(false);
      } catch (error) {
        console.error(`Error: could not update ${entityName.toLowerCase()}: ${error}`);
      } finally {
        setLoading(false);
      }
    }
  };

  if (!entity) {
    return null;
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="secondary" onClick={handleUpdate}>
          <Hammer />
          Update
        </Button>
      </DialogTrigger>
      <DialogContent
        className={cn(
          "overflow-y-auto transition-all duration-300",
          updatedFields ? "h-[90vh]  w-full md:w-[90vw] max-w-full" : "w-md h-fit",
        )}
      >
        <DialogHeader>
          <DialogTitle className="text-2xl text-emerald-600">Update {entityName}</DialogTitle>
          <DialogDescription>
            {updatedFields ? "Review changes" : "Updating information...."}
          </DialogDescription>
        </DialogHeader>
        {updatedFields ? (
          <DiffTableComponent
            original={entity}
            updated={updatedFields}
            setUpdated={setUpdatedFields}
          />
        ) : (
          <DynamicProgress />
        )}
        <DialogFooter className="items-end">
          <DialogClose asChild>
            <Button variant="outline">
              <X className="text-red-500" /> Cancel
            </Button>
          </DialogClose>
          <SubmitButton isLoading={loading} onClick={handleSubmit} label="Save changes" />
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
