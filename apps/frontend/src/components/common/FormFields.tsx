import React, { useEffect, useState } from "react";
import { Control, FieldError, FieldValues, UseFormGetValues, FieldErrors } from "react-hook-form";
import { ControlledFormElement } from "@/interfaces/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/ControlledFormElementType";

interface ControlledFormFieldsProps<T> {
  fields: ControlledFormElement[];
  errors: FieldErrors<any>;
  control: Control<T, object> | any;
  isLoading?: boolean;
  disabled?: boolean;
}

const ControlledFormFields = <T extends FieldValues>({ control, isLoading, fields }: ControlledFormFieldsProps<T>) => {
  const renderElements = () => fields.map((field) => renderField(field));

  const renderField = (field: ControlledFormElement) => {
    switch (field.type) {
      case ControlledFormElementType.SELECT:
        return <ControlledSelect />;
      default:
        return <ControlledInput />;
    }
  };
};
