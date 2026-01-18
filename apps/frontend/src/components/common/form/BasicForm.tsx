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
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { useFormPersist } from "@/hooks/useFormPersist";
interface BasicFormProps {
  form: UseFormReturn;
  formFields: ControlledFormElement[];
  onSubmit: (values: Record<string, unknown>) => Promise<void>;
  onCancelHref?: string;
  isLoading: boolean;
  entity?: unknown;
  formTitle?: string;
  formSubtitle?: string;
  additionalActions?: React.ReactNode;
  action?: Action;
  submitButtonLabel?: string;
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
  submitButtonLabel,
}: BasicFormProps) => {
  const organisationType = form.watch("organisationType") ?? "";
  const showIcon = action === Action.EDIT || action === Action.APPLY;
  const shouldPersist =
    !!formTitle && action !== Action.EDIT && action !== Action.LOGIN && action !== Action.REGISTER;

  const { clearStorage } = useFormPersist(formTitle || "", form, shouldPersist);

  const handleSubmit = async (values: Record<string, unknown>) => {
    await onSubmit(values);
    if (shouldPersist) clearStorage();
  };

  return (
    <Form {...form}>
      <div className="flex">
        <div className="flex flex-col max-w-[200px]  mt-8 ml-8">
          {formTitle && <h3 className="text-xl text-bold text-emerald-600">{formTitle}</h3>}
          {formSubtitle && (
            <p className="text-base mt-2">
              {typeof formSubtitle === "string" && formSubtitle.includes("<a ") ? (
                <span dangerouslySetInnerHTML={{ __html: formSubtitle }} />
              ) : (
                formSubtitle
              )}
            </p>
          )}
        </div>
        <form
          onSubmit={form.handleSubmit(handleSubmit)}
          className="w-full caption-bottom text-sm space-y-6 max-w-4xl mx-auto mt-6 border py-6 px-12 rounded-2xl shadow"
        >
          {formFields.map(
            (formField) =>
              !formField.hidden &&
              (!formField.action || action === formField.action) && (
                <FormField
                  control={form.control}
                  name={formField.fieldName as string}
                  key={formField.fieldName}
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-emerald-700 dark:text-emerald-400">
                        {formField.label}
                        {formField.required &&
                          action !== Action.LOGIN &&
                          action !== Action.REGISTER && (
                            <span
                              className={`-ml-1 ${
                                form.formState.errors[formField.fieldName]
                                  ? "text-red-600"
                                  : "text-emerald-700"
                              }`}
                            >
                              *
                            </span>
                          )}
                      </FormLabel>
                      <FormControl>
                        {getControlledInputs(formField, field, true, organisationType)}
                      </FormControl>
                      <FormDescription>
                        {formField.helpText?.includes("<a ") ? (
                          <span dangerouslySetInnerHTML={{ __html: formField.helpText }} />
                        ) : (
                          formField.helpText
                        )}
                      </FormDescription>
                      <FormMessage className="text-left" />
                    </FormItem>
                  )}
                />
              ),
          )}
          <div className="flex justify-between mt-6">
            {action === Action.LOGIN ? (
              <Button variant={"outline"}>
                <Link href="/register">Register</Link>
              </Button>
            ) : action === Action.REGISTER ? (
              <Button variant={"outline"}>
                <Link href="/login">Login</Link>
              </Button>
            ) : onCancelHref ? (
              <BackButton href={onCancelHref} />
            ) : null}
            <div className="flex gap-4">
              {additionalActions}
              {action === Action.APPLY ? (
                <Button disabled={isLoading}>Send application</Button>
              ) : (
                <SubmitButton
                  label={submitButtonLabel ?? "Save"}
                  isLoading={isLoading}
                  showIcon={showIcon}
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
