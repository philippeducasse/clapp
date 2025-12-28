import { useEffect } from "react";
import { UseFormReturn } from "react-hook-form";

export const useFormPersist = (
  storageKey: string,
  form: UseFormReturn,
  enabled: boolean = true
) => {
  useEffect(() => {
    if (!enabled) return;
    const savedFormData = localStorage.getItem(storageKey);

    if (savedFormData) {
      try {
        form.reset(JSON.parse(savedFormData));
      } catch (e) {
        console.error("Could not retrieve form data.", e);
      }
    }
    /* eslint-disable react-hooks/exhaustive-deps*/
  }, [storageKey, enabled]);

  useEffect(() => {
    if (!enabled) return;

    const subscription = form.watch((data) => {
      localStorage.setItem(storageKey, JSON.stringify(data));
    });

    return () => subscription.unsubscribe();
  }, [form, storageKey, enabled]);

  const clearStorage = () => {
    localStorage.removeItem(storageKey);
  };

  return { clearStorage };
};
