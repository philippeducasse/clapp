"use client";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useEffect, useState } from "react";
import { Festival } from "@/interfaces/entities/Festival";
import { createZodFormSchema, sanitizeFormData, getInitialValues } from "@/helpers/formHelper";
import { getFestivalContactFormFields } from "../../helpers/form/getFestivalContactsFormField";
import { festivalApiService } from "@/api/festivalApiService";
import { useRouter, useParams } from "next/navigation";
import { useDispatch, useSelector } from "react-redux";
import { updateFestival, selectFestival } from "@/redux/slices/festivalSlice";
import { AppDispatch, RootState } from "@/redux/store";
import { refreshFestival } from "../../helpers/refreshFestival";
import { Skeleton } from "@/components/ui/skeleton";
import FormHeader from "@/components/common/form/FormHeader";
import BasicForm from "@/components/common/form/BasicForm";
import { Action } from "@/interfaces/Enums";
import { EntityName } from "@/interfaces/Enums";
import { OrganisationContact } from "@/interfaces/entities/OrganisationContact";

interface FestivalContactsFormProps {
  action: string;
}

const FestivalContactsForm = ({ action }: FestivalContactsFormProps) => {
  const dispatch: AppDispatch = useDispatch();
  const router = useRouter();
  const params = useParams();
  const [festivalId, contactIndex] = [Number(params?.id) || -1, Number(params?.index)];
  const festival = useSelector((state: RootState) => selectFestival(state, festivalId ?? -1));
  const formFields = getFestivalContactFormFields(action === Action.EDIT);
  const formSchema = createZodFormSchema(formFields);
  const [isLoading, setIsLoading] = useState(false);
  const [initialDataLoaded, setInitialDataLoaded] = useState(false);

  const contactToEdit =
    action === Action.EDIT && festival?.contacts?.[contactIndex]
      ? festival.contacts[contactIndex]
      : undefined;

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: getInitialValues(
      formFields,
      contactToEdit as unknown as Record<string, unknown>
    ),
    mode: "onSubmit",
  });

  // Fetch festival data if not available
  useEffect(() => {
    if (!festival && festivalId) {
      refreshFestival(festivalId, dispatch);
      setInitialDataLoaded(true);
    }
  }, [festivalId, festival, dispatch]);

  // Reset form when festival data changes (but only once)
  useEffect(() => {
    if (festival && initialDataLoaded) {
      form.reset(sanitizeFormData(festival));
      setInitialDataLoaded(false);
    }
  }, [festival, form, initialDataLoaded]);

  // Reset form when contact data is loaded (edit mode only)
  useEffect(() => {
    if (action === Action.EDIT && contactToEdit) {
      form.reset(contactToEdit as unknown as Record<string, unknown>);
    }
  }, [contactToEdit, form, action]);

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setIsLoading(true);
    try {
      const isContactEmpty = !values.email && !values.name && !values.role && !values.phone;

      if (action === Action.EDIT) {
        const updatedContacts = [...(festival?.contacts ?? [])];
        updatedContacts[contactIndex] = values as unknown as OrganisationContact;

        const updatedFestival = {
          ...festival,
          contacts: updatedContacts,
        } as Festival;
        await festivalApiService.update(updatedFestival);
        dispatch(updateFestival(updatedFestival));
        router.push(`/festivals/${festival?.id}`);
      } else {
        const existingContacts = festival?.contacts ?? [];

        const updatedContacts = isContactEmpty ? existingContacts : [...existingContacts, values];
        console.log("UP", updatedContacts);
        const festivalWithContacts = {
          ...festival,
          contacts: updatedContacts,
        };
        console.log("fes", festivalWithContacts);

        const newFestival = await festivalApiService.create(
          festivalWithContacts as unknown as Festival
        );
        router.push(`/festivals/${newFestival?.id}`);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!festival && festivalId) {
    return <Skeleton />;
  }

  const onCancelHref =
    action === Action.CREATE
      ? `/festivals/create`
      : festivalId
      ? `/festivals/${festival?.id}`
      : "/festivals";

  return (
    <>
      <FormHeader action={action} entityName={EntityName.FESTIVAL} />
      <BasicForm
        form={form}
        formFields={formFields}
        onSubmit={onSubmit}
        onCancelHref={onCancelHref}
        isLoading={isLoading}
        entity={festival}
        formTitle="Contacts"
        formSubtitle="here you can provide contact information"
      />
    </>
  );
};
export default FestivalContactsForm;
