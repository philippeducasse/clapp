"use client";
import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { AlarmClock } from "lucide-react";
import { getReminderFormFields } from "./helpers/getReminderFormFields";
import BasicForm from "../form/BasicForm";
import { createZodFormSchema, getInitialValues } from "@/helpers/formHelper";
import { Reminder, ReminderCreate } from "@/interfaces/entities/Reminder";
import { OrganisationType } from "@/interfaces/Enums";

interface ReminderModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  reminderApiMethod: (reminder: ReminderCreate) => Promise<Reminder>;
  organisationType: OrganisationType;
  entityId: number;
  onReminderCreated?: (reminder: Reminder) => void;
}

export const ReminderModal = ({
  open,
  onOpenChange,
  reminderApiMethod,
  organisationType,
  entityId,
  onReminderCreated,
}: ReminderModalProps) => {
  const [isLoading, setIsLoading] = useState(false);

  const formFields = getReminderFormFields();
  const formSchema = createZodFormSchema(formFields);
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: getInitialValues(formFields),
    mode: "onSubmit",
  });

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    const selectedDate = new Date(values.remindAt as string);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (selectedDate < today) {
      form.setError("remindAt", { message: "Date cannot be in the past" });
      return;
    }

    setIsLoading(true);
    try {
      const reminderData: ReminderCreate = {
        organisationType,
        objectId: entityId,
        message: values.message as string,
        remindAt: values.remindAt as string,
      };
      const createdReminder = await reminderApiMethod(reminderData);
      onReminderCreated?.(createdReminder);
      form.reset();
      onOpenChange(false);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className={`w-1/3 p-0 gap-0 overflow-hidden shadow-2xl [&>button]:text-white [&>button:hover]:text-white/80`}
      >
        <DialogHeader className={` py-2 pt-6 -mb-12`}>
          <div className="flex items-center justify-center gap-3 mb-2">
            <AlarmClock className={`w-8 h-8 text-primary`} strokeWidth={2.5} />
            <DialogTitle className={` text-xl `}>Set reminder</DialogTitle>
          </div>
        </DialogHeader>

        <div className="px-6 py-8">
          <div className={`rounded-lg mb-6`}>
            <DialogDescription className="text-left text-sm text-gray-800 mt-4">
              Here you can set your reminder for this organisation. You will receive an email at the
              specified time with the specified message
            </DialogDescription>
            <BasicForm
              form={form}
              formFields={formFields}
              onSubmit={onSubmit}
              isLoading={isLoading}
              additionalActions={
                <DialogClose asChild>
                  <Button
                    variant="outline"
                    className="flex mr-auto text-base font-medium hover:bg-gray-100"
                  >
                    Cancel
                  </Button>
                </DialogClose>
              }
            />
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
