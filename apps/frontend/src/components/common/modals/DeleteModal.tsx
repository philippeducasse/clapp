import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import DeleteButton from "../buttons/DeleteButton";
import { AlertTriangle } from "lucide-react";

interface DeleteModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void | Promise<void>;
  description?: string;
  itemName: string;
}

export const DeleteModal = ({
  open,
  onOpenChange,
  onConfirm,
  description = "This cannot be undone",
  itemName,
}: DeleteModalProps) => {
  const [loading, setLoading] = useState(false);

  const handleConfirm = async () => {
    setLoading(true);
    try {
      await onConfirm();
      onOpenChange(false);
    } catch (error) {
      console.error("Delete failed:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="w-1/3 border-2 border-red-500 p-0 gap-0 overflow-hidden shadow-2xl [&>button]:text-white [&>button:hover]:text-white/80">
        <DialogHeader className="bg-red-600  text-white py-2 px-6">
          <div className="flex items-center justify-center gap-3 mb-2">
            <AlertTriangle className="w-8 h-8 text-white" strokeWidth={2.5} />
            <DialogTitle className="text-white text-xl font-bold">Delete {itemName}</DialogTitle>
          </div>
        </DialogHeader>

        <div className="px-6 py-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-center text-lg font-semibold text-gray-800 mb-2">
              Are you sure you want to delete this {itemName}?
            </p>
            <DialogDescription className="text-center text-base text-gray-600">
              {description}
            </DialogDescription>
          </div>

          <DialogFooter className="flex gap-3 sm:gap-3">
            <DialogClose asChild>
              <Button
                variant="outline"
                className="flex-1 h-11 text-base font-medium hover:bg-gray-100"
              >
                Cancel
              </Button>
            </DialogClose>
            <DeleteButton
              variant="destructive"
              onDelete={handleConfirm}
              loading={loading}
              label={loading ? "Deleting..." : "Delete"}
              className="flex-1 h-11 text-base font-medium"
            />
          </DialogFooter>
        </div>
      </DialogContent>
    </Dialog>
  );
};
