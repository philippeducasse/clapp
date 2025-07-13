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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { FestivalDiffTable } from "./FestivalDiffTable";
import { Festival } from "@/interfaces/Festival";
import { useState } from "react";

import festivalApiService from "@/api/festivalApiService";
import { useFestival } from "@/context/FestivalContext";
import { LoadingSpinner } from "../ui/spinner";
import { Skeleton } from "../ui/skeleton";

interface FestivalUpdateDialogProps {
  updatedFields: any;
  originalFields: Festival;
}

export function FestivalUpdateDialog() {
  const [openDiffTable, setOpenDiffTable] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [updatedFields, setUpdatedFields] = useState();
  const festival = useFestival();

  const handleUpdate = async () => {
    console.log("Click", openDiffTable);
    setOpenDiffTable(true);
    setIsLoading(true);
    const response = await festivalApiService.enrichFestival(festival);
    if (response) {
      setIsLoading(false);
      setUpdatedFields(response);
    }
  };
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" onClick={handleUpdate}>
          Update
        </Button>
      </DialogTrigger>
      <DialogContent className="w-full max-w-full h-[90vh] overflow-y-auto">
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
          <Button type="submit">Save changes</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
