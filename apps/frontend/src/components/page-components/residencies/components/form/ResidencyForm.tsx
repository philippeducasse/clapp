'use client';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { useEffect, useState } from 'react';
import { Residency } from '@/interfaces/Residency';
import {
  createZodFormSchema,
  sanitizeFormData,
  getInitialValues,
} from '@/helpers/formHelper';
import { getResidencyFormFields } from '../../helpers/getResidencyFormFields';
import { residencyApiService } from '@/api/residencyApiService';
import { useRouter } from 'next/navigation';
import { useDispatch, useSelector } from 'react-redux';
import { updateResidency, selectResidency, addResidency } from '@/redux/slices/residencySlice';
import { AppDispatch, RootState } from '@/redux/store';
import { refreshResidency } from '../../helpers/refreshResidency';
import { Skeleton } from '@/components/ui/skeleton';
import FormHeader from '@/components/common/form/FormHeader';
import BasicForm from '@/components/common/form/BasicForm';
import { Action, EntityName } from '@/interfaces/Enums';

interface ResidencyFormProps {
  id?: number;
}

const ResidencyForm = ({ id }: ResidencyFormProps) => {
  const dispatch: AppDispatch = useDispatch();
  const router = useRouter();
  const residency = useSelector((state: RootState) =>
    selectResidency(state, id)
  );
  const formFields = getResidencyFormFields(residency);
  const formSchema = createZodFormSchema(formFields);
  const [isLoading, setIsLoading] = useState(false);
  const [initialDataLoaded, setInitialDataLoaded] = useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: getInitialValues(formFields, residency),
    mode: 'onSubmit',
  });

  // Fetch residency data if not available
  useEffect(() => {
    if (!residency && id) {
      refreshResidency(id, dispatch);
      setInitialDataLoaded(true);
    }
  }, [id, residency, dispatch]);

  // Reset form when residency data changes (but only once)
  useEffect(() => {
    if (residency && initialDataLoaded) {
      form.reset(sanitizeFormData(residency));
      setInitialDataLoaded(false);
    }
  }, [residency, form, initialDataLoaded]);

  const action = id ? Action.EDIT : Action.CREATE;

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setIsLoading(true);
    try {
      if (action === Action.EDIT) {
        const updatedResidency = { ...values, id: id } as Residency;
        await residencyApiService.updateResidency(id, updatedResidency);
        dispatch(updateResidency(updatedResidency));
        router.push(`/residencies/${residency?.id}`);
      } else {
        const newResidency = await residencyApiService.createResidency(
          values as Residency
        );
        dispatch(addResidency(newResidency));
        router.push(`/residencies`);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!residency && id) {
    return <Skeleton />;
  }

  const onCancelHref = id ? `/residencies/${residency?.id}` : '/residencies';

  return (
    <>
      <FormHeader action={action} entityName={EntityName.RESIDENCY} />
      <BasicForm
        form={form}
        formFields={formFields}
        onSubmit={onSubmit}
        onCancelHref={onCancelHref}
        isLoading={isLoading}
        entity={residency}
      />
    </>
  );
};
export default ResidencyForm;
