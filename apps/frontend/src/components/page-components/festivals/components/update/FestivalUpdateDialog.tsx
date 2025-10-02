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
import { Festival } from "@/interfaces/entities/Festival";
import { useState } from "react";
import { Hammer } from "lucide-react";
import { festivalApiService } from "@/api/festivalApiService";
import SubmitButton from "../../../../common/buttons/SubmitButton";
import { DynamicProgress } from "../../../../common/DynamicProgress";
import { useDispatch, useSelector } from "react-redux";
import { selectFestival, updateFestival } from "@/redux/slices/festivalSlice";
import { useParams } from "next/navigation";
import { RootState } from "@/redux/store";
import { X } from "lucide-react";
import GenericButton from "@/components/common/buttons/GenericButton";

export const FestivalUpdateDialog = () => {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [updatedFields, setUpdatedFields] = useState<Festival | undefined>();

  const dispatch = useDispatch();
  const params = useParams();
  const festivalId = Number(params.id);
  const festival = useSelector((state: RootState) =>
    selectFestival(state, festivalId)
  );

  const handleUpdate = async () => {
    setLoading(true);
    try {
      if (festival && !updatedFields) {
        const response = await festivalApiService.enrichFestival(festival.id);
        setUpdatedFields(response);
      }
    } catch (error) {
      console.error(`Error: could not update festival: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (updatedFields) {
      setLoading(true);
      try {
        await festivalApiService.updateFestival(updatedFields);
        dispatch(updateFestival(updatedFields));
        setOpen(false);
      } catch (error) {
        console.error(`Error: could not update festival: ${error}`);
      } finally {
        setLoading(false);
      }
    }
  };

  if (!festival) {
    return null;
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <GenericButton
          variant="secondary"
          icon={<Hammer />}
          label="Update"
          onClick={handleUpdate}
        />
      </DialogTrigger>
      <DialogContent className="w-full md:w-[90vw] max-w-full h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Update Festival</DialogTitle>
          <DialogDescription>Review changes</DialogDescription>
        </DialogHeader>
        {updatedFields ? (
          <FestivalDiffTable
            original={festival}
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
