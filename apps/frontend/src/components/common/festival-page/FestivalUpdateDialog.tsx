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

import { FestivalDiffTable } from "./FestivalDiffTable";
import { Festival } from "@/interfaces/Festival";
import { useState } from "react";

import festivalApiService from "@/api/festivalApiService";
import { useFestival } from "@/context/FestivalContext";
import { Skeleton } from "../../ui/skeleton";

export const FestivalUpdateDialog = () => {
  const [open, setOpen] = useState(false);
  const [updatedFields, setUpdatedFields] = useState<Festival | undefined>();
  const festival = useFestival();

  const handleUpdate = async () => {
    const response = await festivalApiService.enrichFestival(festival);
    if (response) {
      setUpdatedFields(response);
    }
  };

  const handleSubmit = async () => {
    if (updatedFields) {
      await festivalApiService.updateFestival(updatedFields);
      setOpen(false);
    }
  };
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" onClick={handleUpdate}>
          Update
        </Button>
      </DialogTrigger>
      <DialogContent className="w-full md:w-[90vw] max-w-full h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Update Festival</DialogTitle>
          <DialogDescription>Review changes</DialogDescription>
        </DialogHeader>
        {updatedFields ? (
          <FestivalDiffTable original={festival} updated={updatedFields} />
        ) : (
          <>
            <Skeleton className="h-4 w-[200px]" />
            <Skeleton className="h-4 w-[200px]" />
            <Skeleton className="h-4 w-[200px]" />
          </>
        )}

        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Cancel</Button>
          </DialogClose>
          <Button onClick={handleSubmit}>Save changes</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
