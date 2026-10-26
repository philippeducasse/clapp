"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRightLeft } from "lucide-react";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { OrganisationType } from "@/interfaces/Enums";
import { organisationApiService } from "@/api/organisationApiService";
import {
  getDetailsLostOnConversion,
  ORGANISATION_ROUTES,
  ORGANISATION_TYPE_LABELS,
} from "@/helpers/organisationRoutes";

interface ChangeTypeButtonProps {
  organisationType: OrganisationType;
  entityId: number;
}

/** Button + dialog to convert an organisation to another type (e.g. festival -> venue). */
const ChangeTypeButton = ({ organisationType, entityId }: ChangeTypeButtonProps) => {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [targetType, setTargetType] = useState<OrganisationType | undefined>();
  const [loading, setLoading] = useState(false);

  const otherTypes = Object.values(OrganisationType).filter((type) => type !== organisationType);
  const lostDetails = targetType ? getDetailsLostOnConversion(organisationType, targetType) : [];
  const fromLabel = ORGANISATION_TYPE_LABELS[organisationType].toLowerCase();

  const handleOpenChange = (next: boolean) => {
    setOpen(next);
    if (!next) setTargetType(undefined);
  };

  const handleConfirm = async () => {
    if (!targetType) return;
    setLoading(true);
    try {
      const converted = await organisationApiService.convert(organisationType, entityId, targetType);
      setOpen(false);
      router.push(`${ORGANISATION_ROUTES[converted.organisationType]}/${converted.id}`);
    } catch (error) {
      // fetchHelper already shows an error toast
      console.error("Change type failed:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Button variant="secondary" onClick={() => setOpen(true)}>
        <ArrowRightLeft className="text-primary" /> Change type
      </Button>
      <Dialog open={open} onOpenChange={handleOpenChange}>
        <DialogContent className="w-1/3">
          <DialogHeader>
            <DialogTitle>Change type</DialogTitle>
            <DialogDescription>
              Move this {fromLabel} to another type. Contacts, comments, tags, applications and
              reminders are kept.
            </DialogDescription>
          </DialogHeader>

          <Select
            value={targetType ?? ""}
            onValueChange={(value) => setTargetType(value as OrganisationType)}
          >
            <SelectTrigger aria-label="New type">
              <SelectValue placeholder="Select new type" />
            </SelectTrigger>
            <SelectContent>
              {otherTypes.map((type) => (
                <SelectItem key={type} value={type}>
                  {ORGANISATION_TYPE_LABELS[type]}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {lostDetails.length > 0 && (
            <p className="text-sm text-destructive">
              The {fromLabel}&apos;s {lostDetails.join(", ")} will be lost.
            </p>
          )}

          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">Cancel</Button>
            </DialogClose>
            <Button onClick={handleConfirm} disabled={!targetType || loading}>
              {loading ? "Changing..." : "Change type"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default ChangeTypeButton;
