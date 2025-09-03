import { ControlledFormElement } from "@/interfaces/ControlledFormElement";
import React from "react";
import { UseFormReturn } from "react-hook-form";
import { Form, FormField, FormItem, FormLabel, FormControl, FormDescription, FormMessage } from "@/components/ui/form";
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
  additionalActions?: React.ReactNode;
  action?: Action;
}

const BasicForm = ({
  form,
  formFields,
  onSubmit,
  onCancelHref,
  isLoading,
  additionalActions,
  action,
}: BasicFormProps) => {
  return (
    <Form {...form}>
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
                  <FormLabel className="text-emerald-700 dark:text-emerald-400">{formField.label}</FormLabel>
                )}
                <FormControl className="">{getControlledInputs(formField, field, true)}</FormControl>
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
              <SubmitButton isLoading={isLoading} />
            )}
          </div>
        </div>
      </form>
    </Form>
  );
};

export default BasicForm;
