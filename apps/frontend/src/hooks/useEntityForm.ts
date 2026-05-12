import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { AppDispatch } from "@/redux/store";
import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { createZodFormSchema, sanitizeFormData, getInitialValues } from "@/helpers/formHelper";

export const useEntityForm = <T extends Record<string, unknown>>(
  entity: T | undefined,
  entityId: number,
  formFields: ControlledFormElement[],
  refreshEntity: (id: number, dispatch: AppDispatch) => void,
  dispatch: AppDispatch
) => {
  const formSchema = createZodFormSchema(formFields);
  const [isLoading, setIsLoading] = useState(false);
  const [initialDataLoaded, setInitialDataLoaded] = useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: getInitialValues(formFields, entity),
    mode: "onSubmit",
  });

  useEffect(() => {
    if (!entity && entityId) {
      refreshEntity(entityId, dispatch);
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setInitialDataLoaded(true);
    }
  }, [entityId, entity, dispatch, refreshEntity]);

  useEffect(() => {
    if (entity && initialDataLoaded) {
      form.reset(sanitizeFormData(entity));
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setInitialDataLoaded(false);
    }
  }, [entity, form, initialDataLoaded]);

  return { form, formSchema, isLoading, setIsLoading };
};