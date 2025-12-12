import React from "react";
import { Slider } from "@/components/ui/slider";
import { SliderOptions } from "@/interfaces/forms/ControlledFormElement";
import { BaseControlledProps } from "@/interfaces/forms/ControlledFormFieldsProps";

interface ControlledSliderProps extends BaseControlledProps {
  sliderOptions: SliderOptions;
}

const ControlledSlider = ({ field, sliderOptions }: ControlledSliderProps) => {
  const { min, max, step, labels } = sliderOptions;

  const currentValue = field.value as number;
  const labelIndex = Math.round((currentValue - min) / step);
  const currentLabel = labels?.[labelIndex];

  return (
    <div className="max-w-[200px]">
      <Slider
        className="my-4 [&_[role=slider]]:bg-emerald-800 [&_[role=slider]]:border-emerald-600"
        value={[currentValue]}
        onValueChange={(value) => field.onChange(value[0])}
        min={min}
        max={max}
        step={step}
      />
      {currentLabel && (
        <div className="text-xs text-muted-foreground text-center mt-1">{currentLabel}</div>
      )}
    </div>
  );
};

export default ControlledSlider;
