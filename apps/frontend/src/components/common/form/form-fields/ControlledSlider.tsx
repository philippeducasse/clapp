import React from "react";
import { ControllerRenderProps } from "react-hook-form";
import { Slider } from "@/components/ui/slider";
import { SliderOptions } from "@/interfaces/forms/ControlledFormElement";

interface ControlledSliderProps {
  field: ControllerRenderProps<Record<string, unknown>, string>;
  sliderOptions: SliderOptions;
}

const ControlledSlider = ({ field, sliderOptions }: ControlledSliderProps) => {
  return (
    <Slider
      className="my-4 max-w-[200px] [&_[role=slider]]:bg-emerald-800 [&_[role=slider]]:border-emerald-600"
      value={[field.value as number]}
      onValueChange={(value) => field.onChange(value[0])}
      min={sliderOptions.min}
      max={sliderOptions.max}
      step={sliderOptions.step}
    />
  );
};

export default ControlledSlider;
