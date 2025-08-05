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
import { Progress } from "@/components/ui/progress";

export const FestivalUpdateDialog = () => {
  const [open, setOpen] = useState(false);
  const [_loading, setLoading] = useState(false);
  const [updatedFields, setUpdatedFields] = useState<Festival | undefined>();

  const { festival, setFestival } = useFestival();

  const handleUpdate = async () => {
    setLoading(true);
    try {
      const response = await festivalApiService.enrichFestival(festival);
      setUpdatedFields(response);
    } catch (error) {
      console.error(`Error: could not update festival: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (updatedFields) {
      setLoading(true);
      await festivalApiService.updateFestival(updatedFields);
      setOpen(false);
      setLoading(false);
      setFestival(updatedFields);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="default" onClick={handleUpdate}>
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
            <Progress />
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
