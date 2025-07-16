import React, { useEffect, useState } from "react";
import { Control, FieldError, FieldValues, UseFormGetValues, FieldErrors } from "react-hook-form";
import { ControlledFormElement } from "@/interfaces/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/ControlledFormElementType";
import { ControlledFormFieldsProps } from "@/interfaces/ControlledFormFieldsProps";

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
