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
import { CheckCircle, AlertTriangle, XCircle } from "lucide-react";

type AlertVariant = "success" | "warning" | "danger";

interface AlertModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  variant: AlertVariant;
  title: string;
  description: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm?: () => void | Promise<void> | Promise<unknown>;
  showCancel?: boolean;
}

const variantConfig = {
  success: {
    icon: CheckCircle,
    headerBg: "bg-green-600",
    borderColor: "border-green-500",
    iconColor: "text-white",
    buttonVariant: "default" as const,
    buttonClassName: "bg-green-600 hover:bg-green-700",
  },
  warning: {
    icon: AlertTriangle,
    headerBg: "bg-yellow-600",
    borderColor: "border-yellow-500",
    iconColor: "text-white",
    buttonVariant: "default" as const,
    buttonClassName: "bg-yellow-600 hover:bg-yellow-700",
  },
  danger: {
    icon: XCircle,
    headerBg: "bg-red-600",
    borderColor: "border-red-500",
    iconColor: "text-white",
    buttonVariant: "destructive" as const,
    buttonClassName: "",
  },
};

export const AlertModal = ({
  open,
  onOpenChange,
  variant,
  title,
  description,
  confirmText = "OK",
  cancelText = "Cancel",
  onConfirm,
  showCancel = false,
}: AlertModalProps) => {
  const config = variantConfig[variant];
  const Icon = config.icon;

  const handleConfirm = async () => {
    if (onConfirm) {
      await onConfirm();
    }
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className={`w-1/3 border-2 ${config.borderColor} p-0 gap-0 overflow-hidden shadow-2xl [&>button]:text-white [&>button:hover]:text-white/80`}
      >
        <DialogHeader className={`${config.headerBg} text-white py-2 px-6`}>
          <div className="flex items-center justify-center gap-3 mb-2">
            <Icon className={`w-8 h-8 ${config.iconColor}`} strokeWidth={2.5} />
            <DialogTitle className="text-white text-xl font-bold">{title}</DialogTitle>
          </div>
        </DialogHeader>

        <div className="px-6 py-8">
          <div className={`rounded-lg p-4 mb-6`}>
            <DialogDescription className="text-center text-base text-gray-800">
              {description}
            </DialogDescription>
          </div>

          <DialogFooter className="flex gap-3 sm:gap-3">
            {showCancel && (
              <DialogClose asChild>
                <Button
                  variant="outline"
                  className="flex-1 h-11 text-base font-medium hover:bg-gray-100"
                >
                  {cancelText}
                </Button>
              </DialogClose>
            )}
            <Button
              variant={config.buttonVariant}
              onClick={handleConfirm}
              className={`${showCancel ? "flex-1" : "w-full"} h-11 text-base font-medium ${
                config.buttonClassName
              }`}
            >
              {confirmText}
            </Button>
          </DialogFooter>
        </div>
      </DialogContent>
    </Dialog>
  );
};
