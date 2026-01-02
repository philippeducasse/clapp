"use client";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useEffect, useMemo, useState } from "react";
import { Profile } from "@/interfaces/entities/Profile";
import {
  createZodFormSchema,
  sanitizeFormData,
  getInitialValues,
  prepareFormDataForSubmission,
} from "@/helpers/formHelper";
import { getProfileFormFields } from "../../helpers/form/getProfileFormFields";
import { profileApiService } from "@/api/profileApiService";
import { useRouter } from "next/navigation";
import { useDispatch, useSelector } from "react-redux";
import { updateProfile, selectProfile } from "@/redux/slices/authSlice";
import { AppDispatch, RootState } from "@/redux/store";
import { Skeleton } from "@/components/ui/skeleton";
import FormHeader from "@/components/common/form/FormHeader";
import BasicForm from "@/components/common/form/BasicForm";
import { Action, EmailHost } from "@/interfaces/Enums";
import { EntityName } from "@/interfaces/Enums";
import { getEmailSettingsFormFields } from "../../helpers/form/getEmailSettingsFormFields";

interface ProfileFormProps {
  action: Action;
  isEmailConfig: boolean;
}

const ProfileForm = ({ action, isEmailConfig = false }: ProfileFormProps) => {
  const dispatch: AppDispatch = useDispatch();
  const router = useRouter();
  const profile = useSelector((state: RootState) => selectProfile(state));
  const [isLoading, setIsLoading] = useState(false);
  const [initialDataLoaded, setInitialDataLoaded] = useState(false);
  const [isOtherEmailHost, setIsOtherEmailHost] = useState(profile?.emailHost === "OTHER");
  const [selectedEmailHost, setSelectedEmailHost] = useState<EmailHost | null | undefined>(
    profile?.emailHost
  );

  const formFields = useMemo(
    () =>
      isEmailConfig
        ? getEmailSettingsFormFields(isOtherEmailHost, selectedEmailHost)
        : getProfileFormFields(),
    [isEmailConfig, isOtherEmailHost, selectedEmailHost]
  );

  const formSchema = useMemo(() => createZodFormSchema(formFields), [formFields]);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: getInitialValues(formFields, profile ?? undefined),
    mode: "onSubmit",
  });

  const emailHost = form.watch("emailHost") as EmailHost;

  useEffect(() => {
    if (emailHost === "OTHER") {
      setIsOtherEmailHost(true);
    } else {
      setIsOtherEmailHost(false);
    }
    setSelectedEmailHost(emailHost as EmailHost);
  }, [emailHost]);

  useEffect(() => {
    if (isOtherEmailHost) {
      // Use setTimeout to ensure focus is set after form has finished re-rendering
      setTimeout(() => {
        form.setFocus("otherEmailHost");
      }, 0);
    }
  }, [isOtherEmailHost, form]);

  useEffect(() => {
    const fetchProfile = async () => {
      if (!profile) {
        try {
          const fetchedProfile = await profileApiService.get();
          dispatch(updateProfile(fetchedProfile));
          setInitialDataLoaded(true);
        } catch (error) {
          console.error("Error fetching profile:", error);
        }
      }
    };
    fetchProfile();
  }, [profile, dispatch]);

  useEffect(() => {
    if (profile && initialDataLoaded) {
      form.reset(sanitizeFormData(profile));
      setInitialDataLoaded(false);
    }
  }, [profile, form, initialDataLoaded]);

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setIsLoading(true);
    try {
      if (profile) {
        let updatedProfile;
        if (isEmailConfig) {
          updatedProfile = { ...profile, ...values } as Profile;
          console.log("updated profile: ", updatedProfile);
        } else {
          updatedProfile = { ...values, id: profile.id } as Profile;
        }
        const sanitisedData = prepareFormDataForSubmission(updatedProfile, formFields);

        await profileApiService.update(sanitisedData);
        dispatch(updateProfile(updatedProfile));
        const tabHash = isEmailConfig ? "#email-settings" : "#basic-information";
        router.push(`/profile${tabHash}`);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!profile) {
    return <Skeleton />;
  }

  return (
    <>
      <FormHeader action={action} entityName={EntityName.PROFILE} />
      <BasicForm
        form={form}
        formFields={formFields}
        onSubmit={onSubmit}
        onCancelHref={isEmailConfig ? "/profile#email-settings" : "/profile#basic-information"}
        isLoading={isLoading}
        entity={profile}
        action={action}
        formTitle={isEmailConfig ? "Email Settings" : "Profile Information"}
        submitButtonLabel="Save"
        formSubtitle={
          isEmailConfig
            ? 'Configure the app to connect with your email account. Please fill these fields out carefully! <a href="/help/email-settings" target="_blank" class="text-blue-600 hover:text-blue-800 underline">View guide</a>'
            : "Update your profile information and contact details"
        }
      />
    </>
  );
};
export default ProfileForm;
