import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { AlarmClock } from "lucide-react";
// import BasicForm from "../form/BasicForm";

interface ReminderModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm?: () => void | Promise<void> | Promise<unknown>;
}

export const ReminderModal = ({ open, onOpenChange, onConfirm }: ReminderModalProps) => {
  const handleConfirm = async () => {
    if (onConfirm) {
      await onConfirm();
    }
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className={`w-1/3 p-0 gap-0 overflow-hidden shadow-2xl [&>button]:text-white [&>button:hover]:text-white/80`}
      >
        <DialogHeader className={`text-white py-2 pt-6`}>
          <div className="flex items-center justify-center gap-3 mb-2">
            <AlarmClock className={`w-8 h-8`} strokeWidth={2.5} />
            <DialogTitle className={`text-white text-xl font-bold`}>
              Set reminder for {}
            </DialogTitle>
          </div>
        </DialogHeader>

        <div className="px-6 py-8">
          <div className={`rounded-lg p-4 mb-6`}>
            <DialogDescription className="text-center text-base text-gray-800">
              Here you can set your reminder for this organisation. You will receive an email at the
              specified time with the specified message
            </DialogDescription>
            {/* <BasicForm /> */}
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
            <Button onClick={handleConfirm} className=" h-11 text-base font-medium ">
              Set reminder
            </Button>
          </DialogFooter>
        </div>
      </DialogContent>
    </Dialog>
  );
};
