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
import { ResidencyDiffTable } from "./ResidencyDiffTable";
import { Residency } from "@/interfaces/entities/Residency";
import { useState } from "react";
import { Hammer } from "lucide-react";
import { residencyApiService } from "@/api/residencyApiService";
import SubmitButton from "../../../../common/buttons/SubmitButton";
import { DynamicProgress } from "../../../../common/DynamicProgress";
import { useDispatch, useSelector } from "react-redux";
import { selectResidency, updateResidency } from "@/redux/slices/residencySlice";
import { useParams } from "next/navigation";
import { RootState } from "@/redux/store";
import { X } from "lucide-react";

export const ResidencyUpdateDialog = () => {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [updatedFields, setUpdatedFields] = useState<Residency | undefined>();

  const dispatch = useDispatch();
  const params = useParams();
  const residencyId = Number(params.id);
  const residency = useSelector((state: RootState) => selectResidency(state, residencyId));

  const handleUpdate = async () => {
    setLoading(true);
    try {
      if (residency && !updatedFields) {
        const response = await residencyApiService.enrich(residency.id);
        setUpdatedFields(response);
      }
    } catch (error) {
      console.error(`Error: could not update residency: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (updatedFields) {
      setLoading(true);
      try {
        await residencyApiService.update(updatedFields);
        dispatch(updateResidency(updatedFields));
        setOpen(false);
      } catch (error) {
        console.error(`Error: could not update residency: ${error}`);
      } finally {
        setLoading(false);
      }
    }
  };

  if (!residency) {
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
      <DialogContent className="w-full md:w-[90vw] max-w-full h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Update Residency</DialogTitle>
          <DialogDescription>Review changes</DialogDescription>
        </DialogHeader>
        {updatedFields ? (
          <ResidencyDiffTable
            original={residency}
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
          <SubmitButton
            isLoading={loading}
            onClick={handleSubmit}
            label="Save changes"
          />
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
