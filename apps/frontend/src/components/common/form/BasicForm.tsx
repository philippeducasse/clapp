import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import React from "react";
import { UseFormReturn } from "react-hook-form";
import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage,
} from "@/components/ui/form";
import BackButton from "../buttons/BackButton";
import SubmitButton from "../buttons/SubmitButton";
import { getControlledInputs } from "@/helpers/formHelper";
import { Action } from "@/interfaces/Enums";
import SendButton from "../buttons/GenericButton";

interface BasicFormProps {
  form: UseFormReturn;
  formFields: ControlledFormElement[];
  onSubmit: (values: Record<string, unknown>) => Promise<void>;
  onCancelHref: string;
  isLoading: boolean;
  entity?: unknown;
  formTitle?: string;
  formSubtitle?: string;
  additionalActions?: React.ReactNode;
  action?: Action;
}

const BasicForm = ({
  form,
  formFields,
  onSubmit,
  onCancelHref,
  isLoading,
  formTitle,
  formSubtitle,

  additionalActions,
  action,
}: BasicFormProps) => {
  const organisationType = form.watch("organisationType") ?? "";

  return (
    <Form {...form}>
      <div className="flex">
        <div className="flex flex-col max-w-[200px]  mt-8 ml-8">
          {formTitle && <h3 className="text-xl text-bold text-emerald-600">{formTitle}</h3>}
          {formSubtitle && <p className="text-base">{formSubtitle}</p>}
        </div>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="w-full caption-bottom text-sm space-y-6 max-w-4xl mx-auto mt-6 border py-6 px-12 rounded-2xl shadow"
        >
          {formFields.map((formField) => (
            <FormField
              control={form.control}
              name={formField.fieldName as string}
              key={formField.fieldName}
              render={({ field }) => (
                <FormItem>
                  {!formField.hidden && (
                    <FormLabel className="text-emerald-700 dark:text-emerald-400">
                      {formField.label}
                    </FormLabel>
                  )}
                  <FormControl className="">
                    {getControlledInputs(formField, field, true, organisationType)}
                  </FormControl>
                  <FormDescription>{formField.helpText}</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
          ))}
          <div className="flex justify-between mt-6">
            <BackButton href={onCancelHref} />
            <div className="flex gap-4">
              {additionalActions}
              {action === Action.APPLY ? (
                <SendButton label="Send application" isLoading={isLoading} />
              ) : (
                <SubmitButton
                  label={action === Action.CREATE ? "Next" : undefined}
                  isLoading={isLoading}
                  showIcon={action !== Action.CREATE}
                />
              )}
            </div>
          </div>
        </form>
      </div>
    </Form>
  );
};

export default BasicForm;
