import { Button } from "../../ui/button";
import { useRouter } from "next/navigation";
import React from "react";
import { Undo2 } from "lucide-react";

interface BackButtonProps {
  href: string;
  label?: string;
  icon?: boolean;
}

const BackButton = ({ label, href, icon = true }: BackButtonProps) => {
  const router = useRouter();

  const handleClick = () => {
    router.push(href);
  };

  return (
    <Button size="lg" variant="outline" onClick={handleClick} type="button">
      {icon && <Undo2 />}
      {label ?? "Go back"}
    </Button>
  );
};

export default BackButton;
